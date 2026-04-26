import React, { useState, useEffect, useRef } from 'react'
import { useAnalysisStore } from '../store/analysisStore'
import { agentsAPI, analysisAPI, clearToken, clearUser } from '../services/api'
import { ResumeInput } from '../components/ResumeInput'
import { JobDescriptionInput } from '../components/JobDescriptionInput'
import { ErrorMessage } from '../components/Common'
import { ChatBot } from '../components/ChatBot'
import { JobListings } from '../components/JobListings'
import AgentPipeline from '../components/AgentPipeline'
import V2Results from '../components/V2Results'
import TPODashboard from '../components/TPODashboard'
import AuthModal from '../components/AuthModal'

const AGENT_ORDER = ['analyzer', 'career', 'improvement', 'project', 'interview']
// Approximate time each agent takes (ms) — used for progress animation only
const AGENT_DURATIONS = [12000, 10000, 14000, 10000, 10000]

export const HomePage = ({ onBack }) => {
  const store = useAnalysisStore()
  const [showAuth, setShowAuth] = useState(false)
  const [mainTab, setMainTab] = useState('analyze')
  const [liveCompleted, setLiveCompleted] = useState([])
  const loadingRef = useRef(false)
  const isTpo = store.user?.role === 'tpo' || store.user?.role === 'admin'

  // Animate agent progress while pipeline runs
  useEffect(() => {
    if (!store.loading) {
      setLiveCompleted([])
      return
    }
    setLiveCompleted([])
    loadingRef.current = true
    let elapsed = 0
    const timers = AGENT_DURATIONS.map((dur, i) => {
      elapsed += dur
      return setTimeout(() => {
        if (loadingRef.current) {
          setLiveCompleted((prev) => [...prev, AGENT_ORDER[i]])
        }
      }, elapsed)
    })
    return () => {
      loadingRef.current = false
      timers.forEach(clearTimeout)
    }
  }, [store.loading])

  const handleRunPipeline = async () => {
    if (!store.resume.trim() || !store.jobDescription.trim()) {
      store.setError('Please provide both resume and job description')
      return
    }
    loadingRef.current = true
    store.setLoading(true)
    store.clearError()
    store.setPipelineResult(null)
    try {
      const res = await agentsAPI.run(store.resume, store.jobDescription)
      store.setPipelineResult(res.data)
    } catch (e) {
      const msg = e.message || ''
      if (msg.includes('quota') || msg.includes('503') || msg.includes('token limit')) {
        store.setError('⏳ Groq daily token quota reached. Please try again in ~1 hour. (100k tokens/day limit)')
      } else {
        store.setError(msg)
      }
    } finally {
      loadingRef.current = false
      store.setLoading(false)
    }
  }

  const resultsRef = useRef(null)

  // Scroll to results when pipeline completes
  useEffect(() => {
    if (store.pipelineResult && !store.loading && resultsRef.current) {
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
    }
  }, [store.pipelineResult, store.loading])

  const handleFileUpload = async (file) => {
    try {
      const res = await analysisAPI.uploadPDF(file)
      store.setResume(res.data.text)
    } catch (e) {
      store.setError(e.message)
    }
  }

  const handleLogout = () => {
    clearToken(); clearUser()
    store.clearAuth()
  }

  const completedAgents = store.pipelineResult?.completed_agents ||
    (store.loading ? liveCompleted : [])

  return (
    <div className="min-h-screen bg-gray-50">

      {/* ── Header ── */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <button onClick={onBack} className="text-xs text-violet-400 hover:text-violet-600 mb-1 block">← Home</button>
            <span className="text-2xl font-black bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent tracking-tight">
              ResumX
            </span>
            <span className="ml-2 text-[10px] font-semibold text-violet-400 uppercase tracking-widest hidden sm:inline">
              Analyze · Improve · Interview · Succeed
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Nav tabs */}
            {isTpo && (
              <div className="flex rounded-lg bg-gray-100 p-1">
                {[['analyze', '🔍 Analyze'], ['tpo', '🏫 TPO Dashboard']].map(([id, label]) => (
                  <button key={id} onClick={() => setMainTab(id)}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition
                      ${mainTab === id ? 'bg-white shadow text-violet-600' : 'text-gray-500'}`}>
                    {label}
                  </button>
                ))}
              </div>
            )}

            {/* Auth */}
            {store.user ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 hidden sm:block">
                  {store.user.email}
                  {store.user.role === 'tpo' && <span className="ml-1 text-violet-500 font-bold">[TPO]</span>}
                </span>
                <button onClick={handleLogout}
                  className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg font-semibold">
                  Log out
                </button>
              </div>
            ) : (
              <button onClick={() => setShowAuth(true)}
                className="text-sm px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold rounded-xl hover:opacity-90 shadow">
                Log In
              </button>
            )}
          </div>
        </div>
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {store.error && (
          <div className="mb-6">
            <ErrorMessage error={store.error} onDismiss={() => store.clearError()} />
          </div>
        )}

        {/* ── TPO Dashboard ── */}
        {mainTab === 'tpo' && isTpo ? (
          <TPODashboard />
        ) : (

          <div className="space-y-6">
            {/* ── Input grid ── */}
            <div className="grid md:grid-cols-2 gap-5">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <ResumeInput
                  resume={store.resume}
                  onResumeChange={(t) => store.setResume(t)}
                  onFileUpload={handleFileUpload}
                />
              </div>
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <JobDescriptionInput
                  jobDescription={store.jobDescription}
                  onJobDescriptionChange={(t) => store.setJobDescription(t)}
                />
              </div>
            </div>

            {/* ── Run button ── */}
            <div className="flex justify-center">
              <button onClick={handleRunPipeline} disabled={store.loading}
                className="px-10 py-3.5 bg-gradient-to-r from-violet-600 to-indigo-500 hover:opacity-90
                  disabled:opacity-50 text-white font-black text-base rounded-2xl shadow-lg
                  transition transform hover:scale-105 active:scale-95 flex items-center gap-2">
                {store.loading
                  ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Running Pipeline…</>
                  : '⚡ Run Full Analysis'}
              </button>
            </div>

            {/* ── Agent pipeline tracker ── */}
            {(store.loading || store.pipelineResult) && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                <p className="text-xs text-center text-gray-400 mb-2 font-semibold uppercase tracking-widest">
                  {store.loading ? 'Pipeline Running…' : 'Pipeline Complete'}
                </p>
                <AgentPipeline
                  completed={completedAgents}
                  running={store.loading}
                />
              </div>
            )}

            {/* ── V2 Results ── */}
            {store.pipelineResult && !store.loading && (
              <div ref={resultsRef}>
                <V2Results result={store.pipelineResult} />
              </div>
            )}

            {/* ── Empty state ── */}
            {!store.pipelineResult && !store.loading && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
                <p className="text-4xl mb-4">⚡</p>
                <p className="text-gray-500 text-lg font-medium">
                  Paste your resume and job description, then hit <span className="text-violet-600 font-bold">Run Full Analysis</span>
                </p>
                <p className="text-gray-400 text-sm mt-2">
                  All 5 agents run in sequence — Analyzer → Career → Improvement → Projects → Interview
                </p>
              </div>
            )}

            {/* ── Job listings + Chat ── */}
            <JobListings resume={store.resume} jobDescription={store.jobDescription} />
          </div>
        )}
      </main>

      <ChatBot />
    </div>
  )
}

export default HomePage
