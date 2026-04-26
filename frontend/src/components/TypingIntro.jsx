import React, { useEffect, useState } from 'react'

const LINES = [
  'Analyzing your resume...',
  'Mapping skill gaps...',
  'Crafting your career path...',
  'Preparing interview questions...',
  'ResuMX is ready.',
]

export default function TypingIntro({ onDone }) {
  const [lineIdx, setLineIdx]   = useState(0)
  const [charIdx, setCharIdx]   = useState(0)
  const [displayed, setDisplayed] = useState('')
  const [done, setDone]         = useState(false)

  useEffect(() => {
    if (done) return
    const line = LINES[lineIdx]

    if (charIdx < line.length) {
      const t = setTimeout(() => {
        setDisplayed(line.slice(0, charIdx + 1))
        setCharIdx(c => c + 1)
      }, 38)
      return () => clearTimeout(t)
    }

    // Line finished — pause then move to next
    if (lineIdx < LINES.length - 1) {
      const t = setTimeout(() => {
        setLineIdx(i => i + 1)
        setCharIdx(0)
        setDisplayed('')
      }, 700)
      return () => clearTimeout(t)
    }

    // All lines done
    const t = setTimeout(() => {
      setDone(true)
      onDone?.()
    }, 1200)
    return () => clearTimeout(t)
  }, [charIdx, lineIdx, done])

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: '#000',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 9999,
    }}>
      <p style={{
        fontFamily: '"Courier New", Courier, monospace',
        fontSize: 'clamp(14px, 2.5vw, 22px)',
        color: '#e2e8f0',
        letterSpacing: '0.04em',
        margin: 0,
        whiteSpace: 'pre',
      }}>
        {displayed}
        <span style={{
          display: 'inline-block',
          width: '2px', height: '1.1em',
          background: '#a78bfa',
          marginLeft: '3px',
          verticalAlign: 'text-bottom',
          animation: 'blink 0.9s step-end infinite',
        }} />
      </p>
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0; }
        }
      `}</style>
    </div>
  )
}
