import React, { useEffect, useState } from 'react'
import { useTpoSessionStore } from '../store/tpoSessionStore'

export default function JoinSessionPage({ onNavigate, onBack }) {
  const [code, setCode] = useState('')

  const { joinSession, joinedSession, loading, error, clearSession, clearError } = useTpoSessionStore()

  // Clear any previous joined session on mount
  useEffect(() => {
    clearSession()
  }, [])

  const handleJoin = async () => {
    if (!code.trim()) return
    await joinSession(code.trim())
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleJoin()
  }

  // Map store error to user-friendly message
  const friendlyError = () => {
    if (!error) return null
    if (error.includes('No active session') || error.includes('not found')) {
      return 'No active session found with that code'
    }
    if (error.includes('not for your organisation') || error.includes('org')) {
      return 'This session is not for your organisation'
    }
    if (error.includes('ended')) {
      return 'This session has ended'
    }
    return error
  }

  return (
    <div className="min-h-screen bg-[#06030f] flex items-center justify-center px-4 relative overflow-hidden">
      {/* Ambient glows */}
      <div className="absolute top-[-150px] left-[-150px] w-[500px] h-[500px] bg-violet-800/20 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-[-100px] right-[-100px] w-[450px] h-[450px] bg-indigo-700/15 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md">
        {/* Back button */}
        <button
          onClick={onBack}
          className="mb-6 flex items-center gap-2 text-white/50 hover:text-white/80 text-sm font-medium transition-colors"
        >
          ← Back
        </button>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          {!joinedSession ? (
            <>
              {/* Header */}
              <div className="text-center mb-8">
                <div className="text-5xl mb-3">🎓</div>
                <h1 className="text-2xl font-black text-gray-900 mb-2">Join Session</h1>
                <p className="text-gray-500 text-sm">Enter the session code shared by your TPO</p>
              </div>

              {/* Input */}
              <div className="mb-4">
                <input
                  type="text"
                  value={code}
                  onChange={(e) => {
                    setCode(e.target.value.toUpperCase())
                    if (error) clearError()
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g. ADYPU-2025-A1"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-900 font-mono text-base
                    placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent
                    transition-all"
                  disabled={loading}
                  autoFocus
                />
              </div>

              {/* Error message */}
              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
                  <p className="text-red-600 text-sm font-medium">❌ {friendlyError()}</p>
                </div>
              )}

              {/* Join button */}
              <button
                onClick={handleJoin}
                disabled={loading || !code.trim()}
                className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold
                  rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all text-base shadow-lg shadow-violet-500/25"
              >
                {loading ? '⏳ Joining…' : 'Join Session'}
              </button>
            </>
          ) : (
            /* Success state */
            <div className="text-center">
              <div className="bg-green-50 border border-green-200 rounded-2xl p-6 mb-6">
                <div className="text-4xl mb-3">✅</div>
                <h2 className="text-lg font-black text-green-800 mb-2">Session Joined!</h2>
                <p className="text-green-700 text-sm">
                  You've joined session{' '}
                  <span className="font-mono font-bold">{joinedSession.session_code}</span>.
                  Start your analysis!
                </p>
              </div>

              <button
                onClick={() => onNavigate('analyze')}
                className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold
                  rounded-xl hover:opacity-90 transition-all text-base shadow-lg shadow-violet-500/25"
              >
                ⚡ Analyze Resume
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
