import React, { useRef, useState } from 'react'
import {
  parseResume,
  TemplateTeal,
  TemplateClassic,
  TemplateModern,
  TemplateMinimal,
  TemplateProfessional,
} from './ResumeTemplates'

// ── Template registry ─────────────────────────────────────────────────────────
const TEMPLATES = [
  {
    id:        'teal',
    label:     'Teal Classic',
    indicator: '🔵',
    color:     '#1a6b8a',
    component: TemplateTeal,
  },
  {
    id:        'classic',
    label:     'Black & White',
    indicator: '⚫',
    color:     '#000000',
    component: TemplateClassic,
  },
  {
    id:        'modern',
    label:     'Modern Navy',
    indicator: '🔷',
    color:     '#1e293b',
    component: TemplateModern,
  },
  {
    id:        'minimal',
    label:     'Minimal',
    indicator: '🟣',
    color:     '#6366f1',
    component: TemplateMinimal,
  },
  {
    id:        'professional',
    label:     'Corporate',
    indicator: '🏢',
    color:     '#1e3a5f',
    component: TemplateProfessional,
  },
]

// ── Main component ────────────────────────────────────────────────────────────
export default function ResumeTemplate({ resumeText, onBack }) {
  const printRef             = useRef(null)
  const [selectedTemplate, setSelectedTemplate] = useState('teal')

  const data     = parseResume(resumeText || '')
  const active   = TEMPLATES.find(t => t.id === selectedTemplate) || TEMPLATES[0]
  const ActiveComponent = active.component

  // ── Download: captures the currently rendered template HTML ──────────────
  const handleDownload = () => {
    const style = `
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; font-size: 11px; color: #1a1a2e; }
      </style>`

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${data.name || 'Resume'} — ResumX</title>
  ${style}
</head>
<body>
  ${printRef.current ? printRef.current.innerHTML : ''}
</body>
</html>`

    const blob = new Blob([html], { type: 'text/html' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `${data.name || 'resume'}_ResumX_${active.id}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleCopy  = () => {
    navigator.clipboard.writeText(resumeText)
      .then(() => alert('Resume copied to clipboard!'))
  }

  const handlePrint = () => window.print()

  return (
    <div className="min-h-screen bg-gray-100">

      {/* ── Action bar ── */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10 shadow-sm print:hidden">
        <button
          onClick={onBack}
          className="text-sm text-gray-500 hover:text-gray-700 font-semibold"
        >
          ← Edit
        </button>
        <span className="text-sm font-black bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent">
          ResumX — Your Resume
        </span>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-4 py-1.5 text-xs font-bold bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            📋 Copy Text
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-1.5 text-xs font-bold bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-lg transition"
          >
            💾 Download HTML
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-1.5 text-xs font-bold bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            🖨️ Print / PDF
          </button>
          <button
            onClick={onBack}
            className="px-4 py-1.5 text-xs font-bold bg-gradient-to-r from-violet-600 to-indigo-500 text-white rounded-lg hover:opacity-90 transition"
          >
            ⚡ Analyze Resume →
          </button>
        </div>
      </div>

      {/* ── Template picker bar ── */}
      <div className="max-w-[820px] mx-auto mt-6 mb-2 px-2 print:hidden">
        <p className="text-xs text-gray-400 font-semibold uppercase tracking-widest mb-2 text-center">
          Choose a Template
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          {TEMPLATES.map(t => (
            <button
              key={t.id}
              onClick={() => setSelectedTemplate(t.id)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-xl border-2 text-sm font-semibold
                transition-all duration-200 bg-white shadow-sm
                ${selectedTemplate === t.id
                  ? 'border-violet-500 ring-2 ring-violet-300 text-violet-700 shadow-md'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300 hover:shadow'}
              `}
            >
              <span>{t.indicator}</span>
              <span>{t.label}</span>
              {selectedTemplate === t.id && (
                <span className="ml-1 w-2 h-2 rounded-full bg-violet-500 inline-block" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ── Resume paper ── */}
      <div
        ref={printRef}
        className="max-w-[820px] mx-auto my-6 bg-white shadow-xl print:shadow-none print:my-0"
      >
        <ActiveComponent resumeText={resumeText || ''} />
      </div>

      {/* Print styles */}
      <style>{`
        @media print {
          body { margin: 0; }
          .print\\:hidden { display: none !important; }
          .print\\:shadow-none { box-shadow: none !important; }
          .print\\:my-0 { margin: 0 !important; }
        }
      `}</style>
    </div>
  )
}
