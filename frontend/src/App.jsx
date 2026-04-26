import React, { useState } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import AuthModal from './components/AuthModal'
import LandingPage from './pages/LandingPage'
import CreateResumePage from './pages/CreateResumePage'
import { HomePage } from './pages/HomePage'
import { useAnalysisStore } from './store/analysisStore'
import TPODashboard from './components/TPODashboard'
import JoinSessionPage from './pages/JoinSessionPage'
import SessionSummaryPage from './pages/SessionSummaryPage'
import TypingIntro from './components/TypingIntro'

/*
  App flow:
    1. Not logged in  → AuthModal (mandatory, cannot dismiss)
    2. Logged in      → LandingPage ("Create Resume" | "Analyze Resume")
    3a. Create Resume → CreateResumePage (7-step wizard)
    3b. Analyze       → HomePage (full V2 pipeline UI)
*/

function App() {
  const user = useAnalysisStore((s) => s.user)
  const [introShown, setIntroShown] = useState(false)
  const [screen, setScreen] = useState(user ? 'landing' : 'auth')
  const [summarySessionId, setSummarySessionId] = useState(null)

  // Show typing intro once on first load
  if (!introShown) {
    return <TypingIntro onDone={() => setIntroShown(true)} />
  }

  const handleAuthDone = () => setScreen('landing')
  const handleChoice   = (c, sessionId) => {
    if (c === 'session-summary' && sessionId) {
      setSummarySessionId(sessionId)
    }
    setScreen(c)
  }
  const handleCreated  = () => setScreen('analyze')    // after wizard → go to analyze

  return (
    <ErrorBoundary>
      {screen === 'auth' && (
        <AuthModal
          onClose={handleAuthDone}
          mandatory   // prop to disable the × button
        />
      )}

      {screen === 'landing' && user && (
        <LandingPage onChoice={handleChoice} />
      )}

      {screen === 'create' && user && (
        <CreateResumePage
          onDone={handleCreated}
          onBack={() => setScreen('landing')}
        />
      )}

      {screen === 'analyze' && user && (
        <HomePage onBack={() => setScreen('landing')} />
      )}

      {screen === 'tpo-dashboard' && user && (user.role === 'tpo' || user.role === 'admin') && (
        <TPODashboard
          onNavigate={handleChoice}
          onBack={() => setScreen('landing')}
        />
      )}

      {screen === 'join-session' && user && user.role === 'student' && (
        <JoinSessionPage
          onNavigate={handleChoice}
          onBack={() => setScreen('landing')}
        />
      )}

      {screen === 'session-summary' && user && (
        <SessionSummaryPage
          sessionId={summarySessionId}
          onNavigate={handleChoice}
        />
      )}
    </ErrorBoundary>
  )
}

export default App
