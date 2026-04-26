/**
 * AnalyticsStatCard – Cyber Green neon counter for the TPO Dashboard.
 *
 * Features:
 *  - Animated "count-up" on mount and on each refresh
 *  - Auto-refreshes every 60 seconds without a full page reload
 *  - Shows total_count, last-24h activity, and recent 10 runs
 */
import React, { useEffect, useRef, useState, useCallback } from 'react'
import apiClient, { getUser } from '../services/api'

// ── Count-up hook ─────────────────────────────────────────────────────────────
function useCountUp(target, duration = 1200) {
  const [display, setDisplay] = useState(0)
  const raf = useRef(null)

  useEffect(() => {
    if (target === null || target === undefined) return
    const start = performance.now()
    const from = 0

    const tick = (now) => {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(from + (target - from) * eased))
      if (progress < 1) raf.current = requestAnimationFrame(tick)
    }

    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [target, duration])

  return display
}

// ── Main component ────────────────────────────────────────────────────────────
export default function AnalyticsStatCard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const intervalRef = useRef(null)

  const user = getUser()
  const orgId = user?.org_id

  const fetchStats = useCallback(async () => {
    if (!orgId) { setLoading(false); return }
    try {
      const res = await apiClient.get(`/tpo/stats/${orgId}`)
      setStats(res.data)
      setError('')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [orgId])

  // Initial fetch + 60-second auto-refresh
  useEffect(() => {
    fetchStats()
    intervalRef.current = setInterval(fetchStats, 60_000)
    return () => clearInterval(intervalRef.current)
  }, [fetchStats])

  const animatedTotal = useCountUp(stats?.total_count ?? 0)

  // ── Render ──────────────────────────────────────────────────────────────────
  if (!orgId) return null

  return (
    <div
      className="rounded-2xl p-5 space-y-4"
      style={{
        background: 'linear-gradient(135deg, #0d1117 0%, #0f1f0f 100%)',
        border: '1.5px solid #39ff14',
        boxShadow: '0 0 18px 2px rgba(57,255,20,0.25), inset 0 0 30px rgba(57,255,20,0.04)',
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold tracking-widest uppercase" style={{ color: '#39ff14' }}>
            Resumes Analyzed
          </p>
          <p className="text-xs text-gray-500 mt-0.5">All-time · auto-refreshes every 60s</p>
        </div>
        <button
          onClick={fetchStats}
          title="Refresh now"
          className="text-lg hover:scale-110 transition-transform"
          style={{ color: '#39ff14' }}
        >
          ↻
        </button>
      </div>

      {/* Big animated counter */}
      {loading ? (
        <div className="flex items-center gap-2">
          <div
            className="w-6 h-6 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: '#39ff14', borderTopColor: 'transparent' }}
          />
          <span className="text-sm text-gray-500">Loading…</span>
        </div>
      ) : error ? (
        <p className="text-sm text-red-400">{error}</p>
      ) : (
        <>
          <p
            className="text-6xl font-black tabular-nums leading-none"
            style={{
              color: '#39ff14',
              textShadow: '0 0 20px rgba(57,255,20,0.7)',
            }}
          >
            {animatedTotal.toLocaleString()}
          </p>

          {/* Daily stat pill */}
          <div className="flex items-center gap-2">
            <span
              className="text-xs font-bold px-2.5 py-1 rounded-full"
              style={{
                background: 'rgba(57,255,20,0.12)',
                color: '#39ff14',
                border: '1px solid rgba(57,255,20,0.3)',
              }}
            >
              +{stats?.daily_stats?.last_24h ?? 0} in last 24h
            </span>
          </div>

          {/* Recent activity table */}
          {(stats?.recent_activity?.length ?? 0) > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Recent Activity</p>
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {stats.recent_activity.map((row, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs rounded-lg px-3 py-1.5"
                    style={{ background: 'rgba(57,255,20,0.06)', border: '1px solid rgba(57,255,20,0.1)' }}
                  >
                    <span className="text-gray-300 truncate max-w-[120px]">{row.student_name}</span>
                    <span
                      className="font-bold"
                      style={{ color: row.match_score >= 70 ? '#39ff14' : row.match_score >= 40 ? '#fbbf24' : '#f87171' }}
                    >
                      {row.match_score != null ? `${row.match_score}%` : '—'}
                    </span>
                    <span className="text-gray-600">
                      {new Date(row.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
