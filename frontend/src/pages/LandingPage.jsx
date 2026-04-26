import React, { useEffect, useRef } from 'react'
import { useAnalysisStore } from '../store/analysisStore'

const FEATURES = [
  { icon: '🔍', title: 'Skill Gap Audit',  desc: "Pinpoints exactly what you're missing for your target role" },
  { icon: '✍️', title: 'Resume Rewrite',   desc: 'AI rewrites your bullets to match the JD — no hallucinations' },
  { icon: '💼', title: 'Career Roadmap',   desc: 'Salary ranges, top companies, certifications & step-by-step path' },
  { icon: '🚀', title: 'Project Ideas',    desc: 'Portfolio projects that bridge your specific skill gaps' },
  { icon: '🎤', title: 'Voice Interview',  desc: 'Practice with AI — speaks questions, scores your answers live' },
  { icon: '🏫', title: 'TPO Dashboard',    desc: 'Batch readiness reports for placement cells & colleges' },
]

const STATS = [
  { v: '5',   l: 'AI Agents',     s: 'working in sequence' },
  { v: '60s', l: 'Full Analysis', s: 'avg pipeline time'   },
  { v: '10+', l: 'Interview Qs',  s: 'with impact context' },
]

export default function LandingPage({ onChoice }) {
  const canvasRef = useRef(null)
  const mouse     = useRef({ x: -999, y: -999 })
  const user = useAnalysisStore((s) => s.user)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId

    const resize = () => {
      canvas.width  = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // More particles, brighter on dark bg
    const pts = Array.from({ length: 110 }, () => ({
      x:  Math.random() * window.innerWidth,
      y:  Math.random() * window.innerHeight,
      ox: (Math.random() - 0.5) * 0.45,
      oy: (Math.random() - 0.5) * 0.45,
      r:  Math.random() * 2.2 + 0.5,
      o:  Math.random() * 0.55 + 0.15,
    }))

    const onMove = e => {
      const t = e.touches?.[0] || e
      mouse.current = { x: t.clientX, y: t.clientY }
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('touchmove', onMove, { passive: true })

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const mx = mouse.current.x, my = mouse.current.y

      // Cursor spotlight
      if (mx > 0) {
        const grad = ctx.createRadialGradient(mx, my, 0, mx, my, 220)
        grad.addColorStop(0,   'rgba(139,92,246,0.12)')
        grad.addColorStop(0.5, 'rgba(99,102,241,0.05)')
        grad.addColorStop(1,   'rgba(0,0,0,0)')
        ctx.fillStyle = grad
        ctx.fillRect(0, 0, canvas.width, canvas.height)
      }

      pts.forEach(p => {
        const dx = p.x - mx, dy = p.y - my
        const d  = Math.hypot(dx, dy)
        if (d < 130 && d > 0) {
          const f = (130 - d) / 130 * 2.5
          p.ox += (dx / d) * f
          p.oy += (dy / d) * f
        }
        p.ox *= 0.91; p.oy *= 0.91
        p.x  += p.ox; p.y  += p.oy
        if (p.x < 0 || p.x > canvas.width)  p.ox *= -1
        if (p.y < 0 || p.y > canvas.height) p.oy *= -1

        // particles near cursor glow brighter
        const dm = Math.hypot(p.x - mx, p.y - my)
        const boost = dm < 150 ? 1 + (150 - dm) / 150 * 1.5 : 1
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r * (dm < 150 ? 1 + (150 - dm) / 300 : 1), 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,255,255,${Math.min(1, p.o * boost)})`
        ctx.fill()
      })

      // Lines — vivid violet near cursor
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const d = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y)
          if (d < 130) {
            const midX = (pts[i].x + pts[j].x) / 2
            const midY = (pts[i].y + pts[j].y) / 2
            const dm   = Math.hypot(midX - mx, midY - my)
            const alpha = (dm < 180 ? 0.5 : 0.08) * (1 - d / 130)
            const color = dm < 180 ? `rgba(196,181,253,${alpha})` : `rgba(255,255,255,${alpha})`
            ctx.beginPath()
            ctx.moveTo(pts[i].x, pts[i].y)
            ctx.lineTo(pts[j].x, pts[j].y)
            ctx.strokeStyle = color
            ctx.lineWidth = dm < 180 ? 0.9 : 0.5
            ctx.stroke()
          }
        }
      }
      animId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('touchmove', onMove)
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#06030f] relative overflow-x-hidden">

      {/* Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none z-0" />

      {/* Static ambient glows */}
      <div className="absolute top-[-150px] left-[-150px] w-[650px] h-[650px] bg-violet-800/25 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute bottom-[-100px] right-[-100px] w-[550px] h-[550px] bg-indigo-700/20 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[250px] bg-violet-950/30 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center px-4 py-16">

        {/* ── Hero ── */}
        <div className="text-center mb-14 max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-white/8 border border-white/15 rounded-full px-4 py-1.5 mb-6 backdrop-blur-sm">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-white/70 text-xs font-semibold tracking-wide">Powered by Groq · LangGraph · Gemini</span>
          </div>

          <h1 className="text-7xl sm:text-8xl font-black text-white tracking-tight leading-none mb-4">
            Resum<span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-300">X</span>
          </h1>

          <p className="text-white/50 text-base sm:text-lg font-medium tracking-[0.25em] uppercase mb-5">
            Analyze · Improve · Interview · Succeed
          </p>

          <p className="text-white/35 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
            The sovereign AI career platform built for students and placement cells.
            5 specialized agents analyze your resume, close skill gaps, and prep you for interviews — in under 60 seconds.
          </p>
        </div>

        {/* ── CTA Cards ── */}
        <div className="grid sm:grid-cols-2 gap-5 w-full max-w-2xl mb-16">

          <button onClick={() => onChoice('create')}
            className="group relative bg-white/5 hover:bg-white/10 backdrop-blur-sm
              border border-white/10 hover:border-violet-400/40
              rounded-3xl p-8 text-left transition-all duration-300
              hover:scale-[1.04] hover:shadow-[0_0_60px_rgba(139,92,246,0.2)]
              overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 to-transparent
              opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
            <div className="relative">
              <div className="text-5xl mb-4">📝</div>
              <h2 className="text-2xl font-black text-white mb-2">Create Resume</h2>
              <p className="text-white/45 text-sm leading-relaxed mb-6">
                No resume yet? Our AI interviews you across 7 steps and builds a professional resume from scratch — in minutes.
              </p>
              <div className="flex items-center gap-2 text-violet-400 text-sm font-bold group-hover:text-violet-300 transition-colors">
                Start building
                <span className="group-hover:translate-x-2 transition-transform duration-200">→</span>
              </div>
            </div>
          </button>

          <button onClick={() => onChoice('analyze')}
            className="group relative bg-white/5 hover:bg-white/10 backdrop-blur-sm
              border border-white/10 hover:border-indigo-400/40
              rounded-3xl p-8 text-left transition-all duration-300
              hover:scale-[1.04] hover:shadow-[0_0_60px_rgba(99,102,241,0.2)]
              overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 to-transparent
              opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
            <div className="relative">
              <div className="text-5xl mb-4">⚡</div>
              <h2 className="text-2xl font-black text-white mb-2">Analyze Resume</h2>
              <p className="text-white/45 text-sm leading-relaxed mb-6">
                Have a resume? Get a full AI analysis — skill gaps, career paths, improved version, projects & voice interview prep.
              </p>
              <div className="flex items-center gap-2 text-indigo-400 text-sm font-bold group-hover:text-indigo-300 transition-colors">
                Analyze now
                <span className="group-hover:translate-x-2 transition-transform duration-200">→</span>
              </div>
            </div>
          </button>

          {(user?.role === 'tpo' || user?.role === 'admin') && (
            <button onClick={() => onChoice('tpo-dashboard')}
              className="group relative bg-white/5 hover:bg-white/10 backdrop-blur-sm
                border border-white/10 hover:border-violet-400/40
                rounded-3xl p-8 text-left transition-all duration-300
                hover:scale-[1.04] hover:shadow-[0_0_60px_rgba(139,92,246,0.2)]
                overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 to-transparent
                opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
              <div className="relative">
                <div className="text-5xl mb-4">🏫</div>
                <h2 className="text-2xl font-black text-white mb-2">TPO Dashboard</h2>
                <p className="text-white/45 text-sm leading-relaxed mb-6">
                  Start a live session, track student analyses in real time, and view batch readiness reports.
                </p>
                <div className="flex items-center gap-2 text-violet-400 text-sm font-bold group-hover:text-violet-300 transition-colors">
                  Open dashboard
                  <span className="group-hover:translate-x-2 transition-transform duration-200">→</span>
                </div>
              </div>
            </button>
          )}

          {user?.role === 'student' && (
            <button onClick={() => onChoice('join-session')}
              className="group relative bg-white/5 hover:bg-white/10 backdrop-blur-sm
                border border-white/10 hover:border-green-400/40
                rounded-3xl p-8 text-left transition-all duration-300
                hover:scale-[1.04] hover:shadow-[0_0_60px_rgba(34,197,94,0.15)]
                overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-green-600/10 to-transparent
                opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl" />
              <div className="relative">
                <div className="text-5xl mb-4">🎓</div>
                <h2 className="text-2xl font-black text-white mb-2">Join Session</h2>
                <p className="text-white/45 text-sm leading-relaxed mb-6">
                  Enter your TPO's session code to join a live placement session and have your analysis tracked.
                </p>
                <div className="flex items-center gap-2 text-green-400 text-sm font-bold group-hover:text-green-300 transition-colors">
                  Join now
                  <span className="group-hover:translate-x-2 transition-transform duration-200">→</span>
                </div>
              </div>
            </button>
          )}
        </div>

        {/* ── Stats ── */}
        <div className="grid grid-cols-3 gap-4 w-full max-w-xl mb-16">
          {STATS.map(s => (
            <div key={s.l} className="bg-white/4 border border-white/8 rounded-2xl p-4 text-center backdrop-blur-sm
              hover:bg-white/8 hover:border-violet-500/30 hover:scale-105 transition-all duration-300 cursor-default">
              <p className="text-3xl font-black text-white mb-0.5">{s.v}</p>
              <p className="text-violet-300/80 text-xs font-bold uppercase tracking-wide">{s.l}</p>
              <p className="text-white/25 text-[10px] mt-0.5">{s.s}</p>
            </div>
          ))}
        </div>

        {/* ── Features ── */}
        <div className="w-full max-w-3xl mb-12">
          <p className="text-center text-white/20 text-xs font-bold uppercase tracking-widest mb-6">
            What ResumX does for you
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {FEATURES.map(f => (
              <div key={f.title}
                className="group bg-white/3 border border-white/8 rounded-2xl p-5
                  hover:bg-violet-500/10 hover:border-violet-500/25 hover:scale-[1.03]
                  transition-all duration-300 cursor-default backdrop-blur-sm">
                <span className="text-2xl mb-2 block group-hover:scale-110 transition-transform duration-200">{f.icon}</span>
                <p className="text-white/90 text-sm font-bold mb-1">{f.title}</p>
                <p className="text-white/30 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Footer ── */}
        <p className="text-white/15 text-xs text-center">
          ResumX V2 · Built for ADYPU, MMIT & placement cells across India
        </p>
      </div>
    </div>
  )
}
