import React from 'react'

const AGENTS = [
  { id: 'analyzer',    label: 'Analyzer',    icon: '🔍', desc: 'Skill gap audit' },
  { id: 'career',      label: 'Career',      icon: '💼', desc: 'Career mapping' },
  { id: 'improvement', label: 'Improvement', icon: '✍️',  desc: 'Resume rewrite' },
  { id: 'project',     label: 'Projects',    icon: '🚀', desc: 'Portfolio ideas' },
  { id: 'interview',   label: 'Interview',   icon: '🎤', desc: 'Prep questions' },
]

export default function AgentPipeline({ completed = [], running = false }) {
  return (
    <div className="flex items-center gap-1 flex-wrap justify-center py-4">
      {AGENTS.map((a, i) => {
        const done = completed.includes(a.id)
        const active = running && !done && completed.length === i
        return (
          <React.Fragment key={a.id}>
            <div className={`flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-all duration-500
              ${done ? 'bg-violet-100 text-violet-700' : active ? 'bg-indigo-50 text-indigo-600 ring-2 ring-indigo-400 animate-pulse' : 'bg-gray-100 text-gray-400'}`}>
              <span className="text-xl">{a.icon}</span>
              <span className="text-xs font-semibold">{a.label}</span>
              <span className="text-[10px] opacity-70">{done ? '✓ done' : active ? 'running…' : a.desc}</span>
            </div>
            {i < AGENTS.length - 1 && (
              <div className={`h-0.5 w-6 rounded ${done ? 'bg-violet-400' : 'bg-gray-200'}`} />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
