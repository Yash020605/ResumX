import React, { useEffect } from 'react'
import { useTpoSessionStore } from '../store/tpoSessionStore'

function StatCard({ label, value, color = 'violet' }) {
  const colors = {
    violet: 'from-violet-500 to-indigo-500',
    green:  'from-green-500 to-emerald-500',
    amber:  'from-amber-500 to-orange-500',
    blue:   'from-blue-500 to-cyan-500',
  }
  return (
    <div className={`bg-gradient-to-br ${colors[color]} text-white rounded-2xl p-5 shadow`}>
      <p className="text-xs opacity-80 mb-1">{label}</p>
      <p className="text-3xl font-black">{value ?? 'N/A'}</p>
    </div>
  )
}

function StatusBadge({ status }) {
  if (status === 'active') {
    return (
      <span className="inline-flex items-center gap-1.5 bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full">
        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
        Active
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1 rounded-full">
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
      Ended
    </span>
  )
}

function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

export default function SessionSummaryPage({ sessionId, onNavigate }) {
  const { fetchSummary, summaryData, loading, error } = useTpoSessionStore()

  useEffect(() => {
    if (sessionId) fetchSummary(sessionId)
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
          <p className="text-red-600 font-medium">❌ {error}</p>
          <button
            onClick={() => onNavigate('tpo-dashboard')}
            className="mt-4 px-4 py-2 bg-gray-100 text-gray-700 text-sm font-bold rounded-xl hover:bg-gray-200 transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  if (!summaryData) return null

  const {
    session_code,
    status,
    started_at,
    ended_at,
    duration_minutes,
    participant_count,
    analyses_completed,
    avg_match_score,
    participants = [],
  } = summaryData

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      {/* ── Header ── */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-black text-gray-900 mb-2">📊 Session Summary</h1>
            <p className="font-mono text-3xl font-black text-violet-700 tracking-widest">{session_code}</p>
          </div>
          <StatusBadge status={status} />
        </div>
      </div>

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          label="Duration (min)"
          value={duration_minutes != null ? Math.round(duration_minutes) : 'N/A'}
          color="violet"
        />
        <StatCard
          label="Participants"
          value={participant_count ?? 0}
          color="blue"
        />
        <StatCard
          label="Analyses Completed"
          value={analyses_completed ?? 0}
          color="amber"
        />
        <StatCard
          label="Avg Match Score"
          value={avg_match_score != null ? `${avg_match_score.toFixed(1)}%` : 'N/A'}
          color="green"
        />
      </div>

      {/* ── Session info ── */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h2 className="font-bold text-gray-800 mb-4">🗓 Session Info</h2>
        <div className="grid sm:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide mb-1">Started At</p>
            <p className="text-gray-800 font-medium">{formatDateTime(started_at)}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide mb-1">Ended At</p>
            <p className="text-gray-800 font-medium">
              {ended_at ? formatDateTime(ended_at) : <span className="text-green-600">In Progress</span>}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide mb-1">Session Code</p>
            <p className="text-gray-800 font-mono font-bold">{session_code}</p>
          </div>
        </div>
      </div>

      {/* ── Per-student table ── */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h2 className="font-bold text-gray-800 mb-4">👥 Participants ({participants.length})</h2>
        {participants.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-6">No participants joined this session.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-gray-100">
                  <th className="pb-3 pr-4 font-semibold">Name</th>
                  <th className="pb-3 pr-4 font-semibold">Email</th>
                  <th className="pb-3 pr-4 font-semibold">Joined At</th>
                  <th className="pb-3 pr-4 font-semibold text-center">Analyses</th>
                  <th className="pb-3 font-semibold text-center">Avg Match Score</th>
                </tr>
              </thead>
              <tbody>
                {participants.map((p, i) => (
                  <tr key={p.student_id ?? i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td className="py-3 pr-4 font-medium text-gray-800">{p.full_name || '—'}</td>
                    <td className="py-3 pr-4 text-gray-500">{p.email || '—'}</td>
                    <td className="py-3 pr-4 text-gray-500 text-xs">{formatDateTime(p.joined_at)}</td>
                    <td className="py-3 pr-4 text-center">
                      <span className="bg-indigo-50 text-indigo-700 text-xs font-bold px-2 py-0.5 rounded-full">
                        {p.analyses_completed ?? 0}
                      </span>
                    </td>
                    <td className="py-3 text-center">
                      {p.avg_match_score != null ? (
                        <span className={`text-xs font-bold ${
                          p.avg_match_score >= 70 ? 'text-green-600' :
                          p.avg_match_score >= 40 ? 'text-amber-600' : 'text-red-500'
                        }`}>
                          {p.avg_match_score.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-gray-300 text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Back button ── */}
      <div className="flex justify-start pb-4">
        <button
          onClick={() => onNavigate('tpo-dashboard')}
          className="px-6 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-500 text-white text-sm font-bold
            rounded-xl hover:opacity-90 transition-all shadow-lg shadow-violet-500/20"
        >
          ← Back to Dashboard
        </button>
      </div>
    </div>
  )
}
