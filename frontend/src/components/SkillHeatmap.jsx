/**
 * SkillHeatmap – Batch skill frequency visualization using Recharts.
 * Cyber Green (strong) → Deep Grey (weak) gradient for the ResumX brand.
 */
import React, { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import apiClient from '../services/api'

// Cyber green → grey gradient stops
const GREEN = '#39ff14'
const MID   = '#1a7a0a'
const GREY  = '#2d2d2d'

function barColor(pct) {
  if (pct >= 70) return GREEN
  if (pct >= 40) return MID
  return GREY
}

function HorizontalBar({ data, label }) {
  if (!data?.length) return (
    <p className="text-xs text-gray-500 py-4 text-center">No data yet</p>
  )
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: GREEN }}>
        {label}
      </p>
      <ResponsiveContainer width="100%" height={data.length * 36}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 0, right: 40, left: 0, bottom: 0 }}
        >
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }}
            tickFormatter={v => `${v}%`} />
          <YAxis type="category" dataKey="skill" width={110}
            tick={{ fill: '#d1d5db', fontSize: 11 }} />
          <Tooltip
            cursor={{ fill: 'rgba(57,255,20,0.05)' }}
            contentStyle={{ background: '#0d1117', border: '1px solid #39ff14', borderRadius: 8 }}
            labelStyle={{ color: GREEN, fontWeight: 700 }}
            formatter={(val, _name, props) => [`${val}% (${props.payload.count} students)`, 'Coverage']}
          />
          <Bar dataKey="pct" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={barColor(entry.pct)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function SkillHeatmap() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')
  const [tab, setTab]       = useState('missing') // 'matching' | 'missing'

  useEffect(() => {
    apiClient.get('/tpo/heatmap')
      .then(r => setData(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="rounded-2xl p-5 space-y-4"
      style={{
        background: 'linear-gradient(135deg, #0d1117 0%, #0f1a0f 100%)',
        border: '1.5px solid #39ff14',
        boxShadow: '0 0 18px 2px rgba(57,255,20,0.15)',
      }}
    >
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <p className="text-sm font-black text-white">Batch Skill Heatmap</p>
          <p className="text-xs text-gray-500">
            {data?.total_students ?? '—'} students · top 10 skills
          </p>
        </div>
        <div className="flex rounded-lg overflow-hidden border"
          style={{ borderColor: 'rgba(57,255,20,0.3)' }}>
          {['missing', 'matching'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              className="px-3 py-1 text-xs font-bold transition-colors"
              style={{
                background: tab === t ? 'rgba(57,255,20,0.15)' : 'transparent',
                color: tab === t ? GREEN : '#6b7280',
              }}>
              {t === 'missing' ? '⚠ Gaps' : '✓ Strengths'}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center gap-2 py-4">
          <div className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: GREEN, borderTopColor: 'transparent' }} />
          <span className="text-xs text-gray-500">Loading heatmap…</span>
        </div>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}
      {data && !loading && (
        tab === 'missing'
          ? <HorizontalBar data={data.top_missing_skills}  label="Top Missing Skills (Gaps)" />
          : <HorizontalBar data={data.top_matching_skills} label="Top Matching Skills (Strengths)" />
      )}
    </div>
  )
}
