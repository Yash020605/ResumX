import React, { useEffect, useState } from 'react'
import { useTpoSessionStore } from '../store/tpoSessionStore'

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

// ── Sub-view: No active session ───────────────────────────────────────────────

function NoSessionView({ onNavigate }) {
  const { createSession, listSessions, sessionList, loading, error } =
    useTpoSessionStore()

  useEffect(() => {
    listSessions()
  }, [])

  const handleStart = async () => {
    try {
      await createSession()
      // activeSession is now set in the store — parent re-renders to ActiveSessionView
    } catch {
      // error is already set in the store
    }
  }

  return (
    <div className="space-y-6">
      {/* Start session card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col items-center gap-4">
        <p className="text-gray-500 text-sm text-center">
          No active session. Start one to let students join and track their analyses in real time.
        </p>
        <button
          onClick={handleStart}
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold rounded-xl hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {loading ? '⏳ Starting…' : '🚀 Start Session'}
        </button>
        {error && (
          <p className="text-red-500 text-sm text-center">{error}</p>
        )}
      </div>

      {/* Recent sessions table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <h3 className="font-bold text-gray-800 mb-4">📋 Recent Sessions</h3>

        {loading && sessionList.length === 0 ? (
          <div className="flex justify-center py-8">
            <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : sessionList.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-6">No sessions yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b">
                  <th className="pb-2 pr-4">Session Code</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Started At</th>
                  <th className="pb-2 pr-4">Participants</th>
                  <th className="pb-2 pr-4">Analyses</th>
                  <th className="pb-2" />
                </tr>
              </thead>
              <tbody>
                {sessionList.map((s) => (
                  <tr key={s.session_id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-mono font-semibold text-violet-700">
                      {s.session_code}
                    </td>
                    <td className="py-2 pr-4">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          s.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-gray-500 text-xs">{fmt(s.started_at)}</td>
                    <td className="py-2 pr-4 text-gray-700">{s.participant_count ?? 0}</td>
                    <td className="py-2 pr-4 text-gray-700">{s.analyses_completed ?? 0}</td>
                    <td className="py-2">
                      <button
                        onClick={() => onNavigate('session-summary', s.session_id)}
                        className="text-xs text-violet-600 hover:text-violet-800 font-semibold"
                      >
                        View Summary
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Sub-view: Active session ──────────────────────────────────────────────────

function ActiveSessionView({ onNavigate }) {
  const { activeSession, dashboardData, endSession, fetchDashboard, loading, error } =
    useTpoSessionStore()

  const [copied, setCopied] = useState(false)
  const [confirmEnd, setConfirmEnd] = useState(false)
  const [ending, setEnding] = useState(false)

  // ── Polling (Task 10.3) ───────────────────────────────────────────────────
  useEffect(() => {
    if (!activeSession?.id || activeSession?.status !== 'active') return

    fetchDashboard(activeSession.id)

    const interval = setInterval(() => {
      fetchDashboard(activeSession.id)
    }, 10_000)

    return () => clearInterval(interval)
  }, [activeSession?.id, activeSession?.status])

  const handleCopy = () => {
    navigator.clipboard.writeText(activeSession.session_code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const handleEndConfirm = async () => {
    setEnding(true)
    try {
      await endSession(activeSession.id)
      onNavigate('session-summary', activeSession.id)
    } catch {
      // error is set in the store
    } finally {
      setEnding(false)
      setConfirmEnd(false)
    }
  }

  const participants = dashboardData?.participants || []
  const participantCount = dashboardData?.participant_count ?? activeSession?.participant_count ?? 0
  const analysesCompleted = dashboardData?.analyses_completed ?? activeSession?.analyses_completed ?? 0

  return (
    <div className="space-y-6">
      {/* Session code card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <p className="text-xs text-gray-500 mb-1 font-semibold uppercase tracking-wide">
          Live Session Code
        </p>
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-4xl font-black text-violet-700 font-mono tracking-widest">
            {activeSession?.session_code}
          </span>
          <button
            onClick={handleCopy}
            title="Copy to clipboard"
            className="flex items-center gap-1 px-3 py-1.5 bg-violet-50 hover:bg-violet-100 text-violet-700 rounded-lg text-sm font-semibold transition-colors"
          >
            {copied ? (
              <span className="text-green-600">✅ Copied!</span>
            ) : (
              <span>📋 Copy</span>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Share this code with students so they can join the session.
        </p>
      </div>

      {/* Live stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-violet-500 to-indigo-500 text-white rounded-2xl p-5 shadow">
          <p className="text-xs opacity-80 mb-1">Participants</p>
          <p className="text-3xl font-black">{participantCount}</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-emerald-500 text-white rounded-2xl p-5 shadow">
          <p className="text-xs opacity-80 mb-1">Analyses Completed</p>
          <p className="text-3xl font-black">{analysesCompleted}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 rounded-xl p-4 text-sm">{error}</div>
      )}

      {/* Participant table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <h3 className="font-bold text-gray-800 mb-4">
          👥 Participants ({participants.length})
        </h3>
        {participants.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-6">
            Waiting for students to join…
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b">
                  <th className="pb-2 pr-4">Name</th>
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Joined At</th>
                  <th className="pb-2">Analyses</th>
                </tr>
              </thead>
              <tbody>
                {participants.map((p) => (
                  <tr key={p.student_id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium text-gray-800">{p.full_name}</td>
                    <td className="py-2 pr-4 text-gray-500">{p.email}</td>
                    <td className="py-2 pr-4 text-gray-400 text-xs">{fmt(p.joined_at)}</td>
                    <td className="py-2 text-gray-700 font-semibold">{p.analyses_completed}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* End session button */}
      <div className="flex justify-end">
        <button
          onClick={() => setConfirmEnd(true)}
          disabled={loading || ending}
          className="px-5 py-2.5 bg-gradient-to-r from-red-500 to-rose-500 text-white font-bold rounded-xl hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          ⏹ End Session
        </button>
      </div>

      {/* Confirmation dialog */}
      {confirmEnd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="font-black text-gray-800 text-lg mb-2">End Session?</h3>
            <p className="text-sm text-gray-600 mb-6">
              Are you sure you want to end this session? Students will no longer be able to join.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setConfirmEnd(false)}
                disabled={ending}
                className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleEndConfirm}
                disabled={ending}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-rose-500 text-white font-bold rounded-xl hover:opacity-90 disabled:opacity-50"
              >
                {ending ? '⏳ Ending…' : 'End Session'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function TPOSessionPanel({ onNavigate }) {
  const { activeSession } = useTpoSessionStore()

  if (activeSession && activeSession.status === 'active') {
    return <ActiveSessionView onNavigate={onNavigate} />
  }

  return <NoSessionView onNavigate={onNavigate} />
}
