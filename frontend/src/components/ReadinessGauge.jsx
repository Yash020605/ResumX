/**
 * ReadinessGauge – Circular gauge chart for Placement Readiness Score.
 * Built with a pure SVG arc so there's no extra chart library dependency.
 * Recharts RadialBarChart is used for the sub-metric breakdown.
 */
import React, { useEffect, useRef, useState } from 'react'
import {
  RadialBarChart, RadialBar, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import apiClient from '../services/api'

const GREEN  = '#39ff14'
const AMBER  = '#fbbf24'
const RED    = '#f87171'

// ── SVG arc gauge ─────────────────────────────────────────────────────────────
function ArcGauge({ score }) {
  const animRef = useRef(null)
  const [displayed, setDisplayed] = useState(0)

  useEffect(() => {
    const start = performance.now()
    const duration = 1400
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplayed(Math.round(score * eased))
      if (t < 1) animRef.current = requestAnimationFrame(tick)
    }
    animRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animRef.current)
  }, [score])

  // Arc geometry
  const R = 80, cx = 100, cy = 100
  const startAngle = 210  // degrees
  const sweepTotal = 300  // degrees of arc
  const pct = Math.min(displayed / 100, 1)

  const toRad = (deg) => (deg * Math.PI) / 180
  const arcX = (angle) => cx + R * Math.cos(toRad(angle))
  const arcY = (angle) => cy + R * Math.sin(toRad(angle))

  const bgEnd   = startAngle + sweepTotal
  const fillEnd = startAngle + sweepTotal * pct

  const describeArc = (from, to) => {
    const large = to - from > 180 ? 1 : 0
    return `M ${arcX(from)} ${arcY(from)} A ${R} ${R} 0 ${large} 1 ${arcX(to)} ${arcY(to)}`
  }

  const color = score >= 75 ? GREEN : score >= 50 ? AMBER : RED

  return (
    <svg viewBox="0 0 200 200" className="w-48 h-48 mx-auto">
      {/* Background track */}
      <path d={describeArc(startAngle, bgEnd)}
        fill="none" stroke="#1f2937" strokeWidth="14" strokeLinecap="round" />
      {/* Filled arc */}
      <path d={describeArc(startAngle, fillEnd)}
        fill="none" stroke={color} strokeWidth="14" strokeLinecap="round"
        style={{ filter: `drop-shadow(0 0 6px ${color})` }} />
      {/* Score text */}
      <text x="100" y="96" textAnchor="middle" dominantBaseline="middle"
        fontSize="32" fontWeight="900" fill={color}>{displayed}</text>
      <text x="100" y="118" textAnchor="middle" fontSize="10" fill="#6b7280">
        / 100
      </text>
      <text x="100" y="134" textAnchor="middle" fontSize="9" fill="#4b5563">
        READINESS
      </text>
    </svg>
  )
}

// ── Sub-metric radial bars ────────────────────────────────────────────────────
function SubMetrics({ data }) {
  const chartData = [
    { name: 'ATS Match',     value: data.avg_ats_match,          fill: GREEN },
    { name: 'Projects',      value: data.project_completeness,   fill: '#818cf8' },
    { name: 'Interviews',    value: data.interview_participation, fill: AMBER },
  ]
  return (
    <ResponsiveContainer width="100%" height={120}>
      <RadialBarChart cx="50%" cy="50%" innerRadius="30%" outerRadius="90%"
        data={chartData} startAngle={90} endAngle={-270}>
        <RadialBar dataKey="value" cornerRadius={4} background={{ fill: '#1f2937' }} />
        <Tooltip
          contentStyle={{ background: '#0d1117', border: '1px solid #39ff14', borderRadius: 8 }}
          labelStyle={{ color: GREEN }}
          formatter={(v) => [`${v.toFixed(1)}%`]}
        />
        <Legend iconSize={8} wrapperStyle={{ fontSize: 10, color: '#9ca3af' }} />
      </RadialBarChart>
    </ResponsiveContainer>
  )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ReadinessGauge() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  useEffect(() => {
    apiClient.get('/tpo/readiness')
      .then(r => setData(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="rounded-2xl p-5 space-y-4"
      style={{
        background: 'linear-gradient(135deg, #0d1117 0%, #0a0f1a 100%)',
        border: '1.5px solid #39ff14',
        boxShadow: '0 0 18px 2px rgba(57,255,20,0.15)',
      }}
    >
      <p className="text-sm font-black text-white">Placement Readiness Score</p>

      {loading && (
        <div className="flex items-center gap-2 py-6 justify-center">
          <div className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: GREEN, borderTopColor: 'transparent' }} />
          <span className="text-xs text-gray-500">Calculating…</span>
        </div>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}

      {data && !loading && (
        <>
          <ArcGauge score={data.readiness_score} />
          <SubMetrics data={data} />

          {/* Actionable insight */}
          <div className="rounded-xl p-3 text-xs leading-relaxed"
            style={{
              background: 'rgba(57,255,20,0.06)',
              border: '1px solid rgba(57,255,20,0.2)',
              color: '#d1fae5',
            }}>
            💡 {data.insight}
          </div>

          {/* Score breakdown pills */}
          <div className="grid grid-cols-3 gap-2 text-center">
            {[
              { label: 'ATS Match',  val: data.avg_ats_match,          weight: '60%' },
              { label: 'Projects',   val: data.project_completeness,   weight: '30%' },
              { label: 'Interviews', val: data.interview_participation, weight: '10%' },
            ].map((m) => (
              <div key={m.label} className="rounded-lg p-2"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1f2937' }}>
                <p className="text-xs text-gray-500">{m.label}</p>
                <p className="text-base font-black" style={{ color: GREEN }}>
                  {m.val.toFixed(0)}%
                </p>
                <p className="text-xs text-gray-600">weight {m.weight}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
