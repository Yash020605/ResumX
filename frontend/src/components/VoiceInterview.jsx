import React, { useState, useEffect, useRef, useCallback } from 'react'

const VOICES_PREF = ['Google UK English Male', 'Google US English', 'Microsoft David', 'Daniel']

function getBestVoice() {
  const voices = window.speechSynthesis?.getVoices() || []
  for (const pref of VOICES_PREF) {
    const v = voices.find((v) => v.name.includes(pref))
    if (v) return v
  }
  return voices.find((v) => v.lang?.startsWith('en')) || voices[0] || null
}

function speak(text, onEnd) {
  if (!window.speechSynthesis) { onEnd?.(); return }
  window.speechSynthesis.cancel()
  const utt = new SpeechSynthesisUtterance(text)
  utt.voice = getBestVoice()
  utt.rate = 0.9
  utt.pitch = 1.0
  if (onEnd) utt.onend = onEnd
  window.speechSynthesis.speak(utt)
}

function scoreAnswer(question, answer) {
  if (!answer || answer.trim().length < 15)
    return { score: 0, feedback: '❌ Answer too short — please speak more.' }
  const q = question.toLowerCase()
  const a = answer.toLowerCase()
  const keywords = q.split(/\W+/).filter((w) => w.length > 4)
  const hits = keywords.filter((k) => a.includes(k)).length
  const ratio = keywords.length ? hits / keywords.length : 0
  const wordCount = answer.trim().split(/\s+/).length
  let score = Math.round(ratio * 55 + Math.min(wordCount * 1.5, 45))
  score = Math.min(100, Math.max(5, score))
  const feedback =
    score >= 80 ? '✅ Excellent — detailed and on-point.'
    : score >= 60 ? '👍 Good answer. Add specific examples for more impact.'
    : score >= 40 ? '⚠️ Partial. Address the question more directly using STAR method.'
    : '❌ Needs work. Structure: Situation → Task → Action → Result.'
  return { score, feedback }
}

export default function VoiceInterview({ questions = [], behavioralQuestions = [], technicalQuestions = [] }) {
  const allQ = [
    ...behavioralQuestions.map((q) => ({ q: typeof q === 'object' ? q.question || q : q, type: 'Behavioral' })),
    ...technicalQuestions.map((q) => ({ q: typeof q === 'object' ? q.question || q : q, type: 'Technical' })),
    ...(behavioralQuestions.length === 0 && technicalQuestions.length === 0
      ? questions.map((q) => ({ q: typeof q === 'object' ? q.question || q : q, type: 'General' }))
      : []),
  ]

  const [idx, setIdx]             = useState(0)
  const [phase, setPhase]         = useState('idle')  // idle|speaking|listening|scored|done
  const [transcript, setTranscript] = useState('')
  const [interim, setInterim]     = useState('')
  const [result, setResult]       = useState(null)
  const [history, setHistory]     = useState([])
  const [supported, setSupported] = useState(true)
  const [voicesReady, setVoicesReady] = useState(false)

  const recogRef    = useRef(null)
  const phaseRef    = useRef('idle')   // always in sync with phase for closures
  const finalTxRef  = useRef('')       // accumulates final transcript segments

  // keep phaseRef in sync
  useEffect(() => { phaseRef.current = phase }, [phase])

  // detect support + load voices
  useEffect(() => {
    const hasTTS = !!window.speechSynthesis
    const hasSTT = !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    if (!hasTTS || !hasSTT) { setSupported(false); return }

    const loadVoices = () => {
      if (window.speechSynthesis.getVoices().length > 0) setVoicesReady(true)
    }
    loadVoices()
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices)
    return () => window.speechSynthesis.removeEventListener('voiceschanged', loadVoices)
  }, [])

  const currentQ = allQ[idx]

  // ── Step 1: speak the question ──────────────────────────────────────────────
  const handleReadQuestion = useCallback(() => {
    if (!currentQ) return
    finalTxRef.current = ''
    setTranscript('')
    setInterim('')
    setResult(null)
    setPhase('speaking')
    speak(`Question ${idx + 1}. ${currentQ.q}`, () => {
      setPhase('listening')
      startRecognition()
    })
  }, [currentQ, idx])

  // ── Step 2: start mic ───────────────────────────────────────────────────────
  const startRecognition = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) return

    // stop any existing session
    recogRef.current?.abort()

    const recog = new SR()
    recog.lang = 'en-US'
    recog.continuous = true
    recog.interimResults = true
    recog.maxAlternatives = 1

    recog.onresult = (e) => {
      let fin = finalTxRef.current
      let inter = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          fin += e.results[i][0].transcript + ' '
          finalTxRef.current = fin
        } else {
          inter += e.results[i][0].transcript
        }
      }
      setTranscript(fin.trim())
      setInterim(inter)
    }

    recog.onerror = (e) => {
      console.warn('Speech recognition error:', e.error)
      if (phaseRef.current === 'listening') doScore()
    }

    recog.onend = () => {
      // only auto-score if we're still in listening phase (not manually stopped)
      if (phaseRef.current === 'listening') doScore()
    }

    recogRef.current = recog
    recog.start()
  }, [])

  // ── Step 3: stop mic + score ────────────────────────────────────────────────
  const handleStopAndScore = useCallback(() => {
    recogRef.current?.stop()
    recogRef.current = null
    doScore()
  }, [])

  const doScore = useCallback(() => {
    if (phaseRef.current === 'scored') return  // prevent double-fire
    setPhase('scored')
    const answer = finalTxRef.current.trim()
    setTranscript(answer)
    setInterim('')
    const r = scoreAnswer(currentQ?.q || '', answer)
    setResult(r)
    speak(r.feedback)
  }, [currentQ])

  // ── Step 4: next question ───────────────────────────────────────────────────
  const handleNext = useCallback(() => {
    window.speechSynthesis.cancel()
    const answer = finalTxRef.current.trim()
    const r = result || scoreAnswer(currentQ?.q || '', answer)
    setHistory((h) => [...h, {
      q: currentQ.q, type: currentQ.type, answer, ...r
    }])
    if (idx < allQ.length - 1) {
      setIdx((i) => i + 1)
      setPhase('idle')
      setTranscript('')
      setInterim('')
      setResult(null)
      finalTxRef.current = ''
    } else {
      setPhase('done')
    }
  }, [result, currentQ, idx, allQ.length])

  const avgScore = history.length
    ? Math.round(history.reduce((s, h) => s + h.score, 0) / history.length)
    : null

  // ── Not supported ───────────────────────────────────────────────────────────
  if (!supported) return (
    <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
      <p className="text-2xl mb-2">🎤</p>
      <p className="text-amber-700 font-semibold">Voice interview requires Chrome or Edge.</p>
      <p className="text-amber-600 text-sm mt-1">Open this page in Chrome to use voice features.</p>
    </div>
  )

  if (allQ.length === 0) return (
    <div className="text-center text-gray-400 py-8">Run the full pipeline first to generate interview questions.</div>
  )

  // ── Done screen ─────────────────────────────────────────────────────────────
  if (phase === 'done') return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-violet-600 to-indigo-500 rounded-2xl p-8 text-white text-center">
        <p className="text-5xl mb-3">🎉</p>
        <h3 className="text-2xl font-black">Interview Complete!</h3>
        <p className="text-violet-200 text-sm mt-1">{history.length} questions answered</p>
        {avgScore !== null && (
          <div className="mt-4">
            <span className="text-6xl font-black">{avgScore}</span>
            <span className="text-2xl text-violet-200">/100</span>
            <p className="text-violet-200 text-sm mt-1">
              {avgScore >= 75 ? '🌟 Interview Ready!' : avgScore >= 50 ? '📈 Keep Practising' : '💪 More Practice Needed'}
            </p>
          </div>
        )}
      </div>

      <div className="space-y-3">
        {history.map((h, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold px-2 py-0.5 bg-violet-100 text-violet-700 rounded-full">{h.type}</span>
              <span className={`text-lg font-black ${h.score >= 70 ? 'text-green-600' : h.score >= 40 ? 'text-amber-500' : 'text-red-500'}`}>
                {h.score}/100
              </span>
            </div>
            <p className="text-sm font-semibold text-gray-800 mb-1">{h.q}</p>
            {h.answer && <p className="text-xs text-gray-500 italic mb-1">"{h.answer}"</p>}
            <p className="text-xs text-gray-600">{h.feedback}</p>
          </div>
        ))}
      </div>

      <button onClick={() => { setIdx(0); setPhase('idle'); setHistory([]); setTranscript(''); setResult(null); finalTxRef.current = '' }}
        className="w-full py-3 bg-violet-100 text-violet-700 font-bold rounded-xl hover:bg-violet-200 transition">
        🔄 Restart Interview
      </button>
    </div>
  )

  // ── Main interview UI ───────────────────────────────────────────────────────
  return (
    <div className="space-y-4">

      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 bg-gray-100 rounded-full h-2">
          <div className="bg-gradient-to-r from-violet-500 to-indigo-400 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(idx / allQ.length) * 100}%` }} />
        </div>
        <span className="text-xs text-gray-500 font-semibold whitespace-nowrap">{idx + 1} / {allQ.length}</span>
      </div>

      {/* Question card */}
      <div className="bg-gradient-to-br from-violet-50 to-indigo-50 border border-violet-200 rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-bold px-2 py-0.5 bg-violet-200 text-violet-700 rounded-full">
            {currentQ?.type}
          </span>
          <span className="text-xs text-gray-400">Q{idx + 1}</span>
        </div>
        <p className="text-gray-800 font-semibold text-base leading-relaxed">{currentQ?.q}</p>
      </div>

      {/* Phase controls */}
      {phase === 'idle' && (
        <button onClick={handleReadQuestion}
          className="w-full py-4 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-black text-base rounded-2xl hover:opacity-90 shadow-lg flex items-center justify-center gap-3 transition">
          🔊 Read Question &amp; Start Recording
        </button>
      )}

      {phase === 'speaking' && (
        <div className="w-full py-4 bg-violet-100 text-violet-700 font-bold rounded-2xl text-center flex items-center justify-center gap-2 animate-pulse">
          <span className="w-3 h-3 bg-violet-500 rounded-full animate-bounce" />
          Speaking question…
        </div>
      )}

      {phase === 'listening' && (
        <div className="space-y-3">
          {/* Mic indicator */}
          <div className="w-full py-4 bg-red-50 border-2 border-red-300 rounded-2xl text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <span className="w-3 h-3 bg-red-500 rounded-full animate-ping" />
              <span className="text-red-600 font-bold">Recording your answer…</span>
            </div>
            <p className="text-xs text-red-400">Speak clearly — click Stop when done</p>
          </div>
          <button onClick={handleStopAndScore}
            className="w-full py-3 bg-gray-800 hover:bg-gray-900 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition">
            ⏹ Stop &amp; Score Answer
          </button>
          {/* Live transcript */}
          {(transcript || interim) && (
            <div className="bg-white border border-gray-200 rounded-xl p-3">
              <p className="text-xs text-gray-400 font-semibold mb-1">LIVE TRANSCRIPT</p>
              <p className="text-sm text-gray-700">{transcript} <span className="text-gray-400 italic">{interim}</span></p>
            </div>
          )}
        </div>
      )}

      {phase === 'scored' && (
        <div className="space-y-3">
          {/* Final transcript */}
          {transcript && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <p className="text-xs text-gray-400 font-semibold mb-1">YOUR ANSWER</p>
              <p className="text-sm text-gray-700 italic">"{transcript}"</p>
            </div>
          )}

          {/* Score card */}
          {result && (
            <div className={`rounded-2xl p-5 border-2 ${
              result.score >= 70 ? 'bg-green-50 border-green-300'
              : result.score >= 40 ? 'bg-amber-50 border-amber-300'
              : 'bg-red-50 border-red-300'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-gray-700">AI Score</span>
                <span className={`text-3xl font-black ${
                  result.score >= 70 ? 'text-green-600'
                  : result.score >= 40 ? 'text-amber-500' : 'text-red-500'}`}>
                  {result.score}<span className="text-base font-normal text-gray-400">/100</span>
                </span>
              </div>
              <p className="text-sm text-gray-700">{result.feedback}</p>
            </div>
          )}

          <button onClick={handleNext}
            className="w-full py-4 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-black text-base rounded-2xl hover:opacity-90 shadow-lg transition">
            {idx < allQ.length - 1 ? `Next Question (${idx + 2}/${allQ.length}) →` : '🏁 Finish Interview'}
          </button>
        </div>
      )}

      {/* Score history pills */}
      {history.length > 0 && (
        <div className="flex gap-2 flex-wrap pt-1">
          {history.map((h, i) => (
            <span key={i} className={`text-xs px-2.5 py-1 rounded-full font-bold ${
              h.score >= 70 ? 'bg-green-100 text-green-700'
              : h.score >= 40 ? 'bg-amber-100 text-amber-700'
              : 'bg-red-100 text-red-700'}`}>
              Q{i + 1}: {h.score}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
