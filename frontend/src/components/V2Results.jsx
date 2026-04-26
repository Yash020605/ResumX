import React, { useState } from 'react'
import VoiceInterview from './VoiceInterview'

// ── Match Score Ring ──────────────────────────────────────────────────────────
function ScoreRing({ pct }) {
  const r = 36, c = 2 * Math.PI * r
  const dash = (pct / 100) * c
  const color = pct >= 70 ? '#7c3aed' : pct >= 40 ? '#f59e0b' : '#ef4444'
  return (
    <div className="relative flex items-center justify-center w-24 h-24 flex-shrink-0">
      <svg width="96" height="96" className="-rotate-90 absolute inset-0">
        <circle cx="48" cy="48" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle cx="48" cy="48" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${dash} ${c}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease' }} />
      </svg>
      <div className="relative text-center z-10">
        <span className="text-2xl font-black" style={{ color }}>{pct}%</span>
        <p className="text-[10px] text-gray-400 leading-none">match</p>
      </div>
    </div>
  )
}

// ── Skill Badge ───────────────────────────────────────────────────────────────
function Badge({ label, variant }) {
  const cls = {
    green:  'bg-green-100 text-green-700',
    red:    'bg-red-100 text-red-700',
    violet: 'bg-violet-100 text-violet-700',
    gray:   'bg-gray-100 text-gray-600',
  }[variant] || 'bg-gray-100 text-gray-600'
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{label}</span>
}

// ── Section wrapper ───────────────────────────────────────────────────────────
function Section({ title, icon, children }) {
  return (
    <div className="mb-8">
      <h3 className="text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
        <span>{icon}</span>{title}
      </h3>
      {children}
    </div>
  )
}

// ── Tab bar ───────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'overview',  label: '📊 Overview' },
  { id: 'resume',    label: '✨ Improved Resume' },
  { id: 'career',    label: '💼 Career' },
  { id: 'projects',  label: '🚀 Projects' },
  { id: 'interview', label: '🎤 Interview' },
]

export default function V2Results({ result }) {
  const [tab, setTab] = useState('overview')
  if (!result) return null

  const {
    match_percentage: pct = 0,
    matching_skills = [], missing_skills = [], skill_gaps = [],
    career_fields = [], job_titles = [], industries = [],
    improved_resume, improvement_status,
    suggested_projects = [],
    interview_questions = [], behavioral_questions = [], technical_questions = [],
    completed_agents = [],
  } = result

  return (
    <div className="space-y-4">
      {/* Tab bar */}
      <div className="flex flex-wrap gap-2 bg-white rounded-xl p-3 shadow-sm border border-gray-100">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition
              ${tab === t.id ? 'bg-gradient-to-r from-violet-600 to-indigo-500 text-white shadow' : 'text-gray-500 hover:bg-gray-100'}`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">

        {/* ── Overview ── */}
        {tab === 'overview' && (
          <div>
            <div className="flex flex-col sm:flex-row items-center gap-8 mb-8">
              <ScoreRing pct={pct} />
              <div className="flex-1">
                <p className="text-sm text-gray-500 mb-1">Agents completed: {completed_agents.join(' → ')}</p>
                <div className="flex flex-wrap gap-1 mb-2">
                  {matching_skills.map((s) => <Badge key={s} label={s} variant="green" />)}
                </div>
                <div className="flex flex-wrap gap-1">
                  {missing_skills.map((s) => <Badge key={s} label={s} variant="red" />)}
                </div>
              </div>
            </div>

            {skill_gaps.length > 0 && (
              <Section title="Skill Gaps" icon="⚠️">
                <div className="space-y-2">
                  {skill_gaps.map((g, i) => {
                    const skill = typeof g === 'string' ? g : g.skill
                    const imp = typeof g === 'object' ? g.importance : 'medium'
                    const w = imp === 'high' ? 'w-full' : imp === 'medium' ? 'w-2/3' : 'w-1/3'
                    const col = imp === 'high' ? 'bg-red-400' : imp === 'medium' ? 'bg-amber-400' : 'bg-blue-400'
                    return (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-xs w-32 truncate text-gray-700">{skill}</span>
                        <div className="flex-1 bg-gray-100 rounded-full h-2">
                          <div className={`${w} ${col} h-2 rounded-full transition-all duration-700`} />
                        </div>
                        <Badge label={imp} variant={imp === 'high' ? 'red' : 'gray'} />
                      </div>
                    )
                  })}
                </div>
              </Section>
            )}
          </div>
        )}

        {/* ── Improved Resume ── */}
        {tab === 'resume' && (
          <div>
            {improved_resume ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-gray-500">{improvement_status}</p>
                  <button onClick={() => navigator.clipboard.writeText(improved_resume)}
                    className="text-xs px-3 py-1.5 bg-violet-100 text-violet-700 rounded-lg hover:bg-violet-200 font-semibold">
                    📋 Copy
                  </button>
                </div>
                <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 rounded-xl p-4 border border-gray-200 max-h-[500px] overflow-y-auto font-mono leading-relaxed">
                  {improved_resume}
                </pre>
              </>
            ) : <p className="text-gray-400 text-center py-8">No improved resume yet.</p>}
          </div>
        )}

        {/* ── Career ── */}
        {tab === 'career' && (
          <div>
            <Section title="Career Fields" icon="💼">
              <div className="space-y-4">
                {career_fields.map((f, i) => {
                  const name  = typeof f === 'string' ? f : f.field
                  const exp   = typeof f === 'object' ? f.explanation : ''
                  const dem   = typeof f === 'object' ? f.market_demand : ''
                  const salIn = typeof f === 'object' ? f.avg_salary_inr : ''
                  const salUs = typeof f === 'object' ? f.avg_salary_usd : ''
                  const cos   = typeof f === 'object' ? (f.top_companies || []) : []
                  const road  = typeof f === 'object' ? (f.roadmap || []) : []
                  const certs = typeof f === 'object' ? (f.certifications || []) : []
                  const ttr   = typeof f === 'object' ? f.time_to_ready : ''
                  return (
                    <div key={i} className="border border-violet-100 rounded-2xl p-5 bg-gradient-to-br from-violet-50 to-indigo-50">
                      {/* Header */}
                      <div className="flex items-start justify-between gap-2 mb-3">
                        <h4 className="font-black text-violet-800 text-base">{name}</h4>
                        <div className="flex gap-2 flex-shrink-0">
                          {dem && <Badge label={`${dem} demand`} variant={dem === 'high' ? 'green' : 'gray'} />}
                          {ttr && <Badge label={ttr} variant="violet" />}
                        </div>
                      </div>
                      {exp && <p className="text-sm text-gray-600 mb-4">{exp}</p>}

                      {/* Salary */}
                      {(salIn || salUs) && (
                        <div className="flex gap-3 mb-4">
                          {salIn && (
                            <div className="bg-white rounded-xl px-4 py-2 border border-violet-100 text-center">
                              <p className="text-[10px] text-gray-400 font-semibold">INDIA</p>
                              <p className="text-sm font-black text-violet-700">{salIn}</p>
                            </div>
                          )}
                          {salUs && (
                            <div className="bg-white rounded-xl px-4 py-2 border border-violet-100 text-center">
                              <p className="text-[10px] text-gray-400 font-semibold">GLOBAL</p>
                              <p className="text-sm font-black text-indigo-700">{salUs}</p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Top Companies */}
                      {cos.length > 0 && (
                        <div className="mb-4">
                          <p className="text-xs font-bold text-gray-500 mb-2">🏢 TOP COMPANIES</p>
                          <div className="flex flex-wrap gap-1.5">
                            {cos.map((c) => <Badge key={c} label={c} variant="violet" />)}
                          </div>
                        </div>
                      )}

                      {/* Roadmap */}
                      {road.length > 0 && (
                        <div className="mb-4">
                          <p className="text-xs font-bold text-gray-500 mb-2">🗺️ ROADMAP</p>
                          <ol className="space-y-1">
                            {road.map((s, j) => (
                              <li key={j} className="flex items-start gap-2 text-xs text-gray-600">
                                <span className="w-5 h-5 rounded-full bg-violet-200 text-violet-700 font-bold flex items-center justify-center flex-shrink-0 text-[10px]">{j+1}</span>
                                {s.replace(/^Step \d+:\s*/i, '')}
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}

                      {/* Certifications */}
                      {certs.length > 0 && (
                        <div>
                          <p className="text-xs font-bold text-gray-500 mb-2">🎓 CERTIFICATIONS</p>
                          <div className="flex flex-wrap gap-1.5">
                            {certs.map((c) => <Badge key={c} label={c} variant="gray" />)}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </Section>
            {job_titles.length > 0 && (
              <Section title="Job Titles" icon="🏷️">
                <div className="flex flex-wrap gap-2">
                  {job_titles.map((t) => <Badge key={t} label={t} variant="violet" />)}
                </div>
              </Section>
            )}
            {industries.length > 0 && (
              <Section title="Industries" icon="🏭">
                <div className="flex flex-wrap gap-2">
                  {industries.map((t) => <Badge key={t} label={t} variant="gray" />)}
                </div>
              </Section>
            )}
          </div>
        )}

        {/* ── Projects ── */}
        {tab === 'projects' && (
          <div className="space-y-4">
            {suggested_projects.length === 0
              ? <p className="text-gray-400 text-center py-8">No projects suggested yet.</p>
              : suggested_projects.map((p, i) => {
                const title = typeof p === 'string' ? p : p.title
                const desc  = typeof p === 'object' ? p.description : ''
                const stack = typeof p === 'object' ? (p.tech_stack || []) : []
                const diff  = typeof p === 'object' ? p.difficulty : ''
                const why   = typeof p === 'object' ? p.why_recommended : ''
                const steps = typeof p === 'object' ? (p.first_steps || []) : []
                return (
                  <div key={i} className="border border-indigo-100 rounded-xl p-5 bg-indigo-50">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="font-bold text-indigo-800">{title}</h4>
                      {diff && <Badge label={diff} variant="violet" />}
                    </div>
                    {desc && <p className="text-sm text-gray-600 mb-3">{desc}</p>}
                    {stack.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {stack.map((s) => <Badge key={s} label={s} variant="gray" />)}
                      </div>
                    )}
                    {why && <p className="text-xs text-indigo-600 italic mb-2">💡 {why}</p>}
                    {steps.length > 0 && (
                      <ol className="text-xs text-gray-500 space-y-0.5 list-decimal list-inside">
                        {steps.map((s, j) => <li key={j}>{s}</li>)}
                      </ol>
                    )}
                  </div>
                )
              })}
          </div>
        )}

        {/* ── Interview ── */}
        {tab === 'interview' && (
          <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <div>
                <h3 className="text-lg font-black text-gray-800">🎤 Interview Prep</h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  {(result.behavioral_questions_rich?.length || 0) + (result.technical_questions_rich?.length || 0) + (result.aptitude_questions?.length || 0) || interview_questions.length} questions · behavioral · technical · aptitude
                </p>
              </div>
              <div className="flex gap-2 flex-wrap">
                {result.focus_areas?.slice(0,3).map((a,i) => (
                  <span key={i} className="text-xs bg-violet-100 text-violet-700 px-3 py-1 rounded-full font-semibold">{a}</span>
                ))}
              </div>
            </div>

            {/* Prep tips */}
            {result.prep_tips?.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6">
                <p className="text-xs font-bold text-amber-700 mb-2">💡 PREP TIPS</p>
                <ul className="space-y-1">
                  {result.prep_tips.map((t,i) => (
                    <li key={i} className="text-xs text-amber-800 flex gap-2"><span>→</span>{t}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Behavioral Questions */}
            {(result.behavioral_questions_rich?.length > 0) && (
              <div className="mb-8">
                <h4 className="text-sm font-black text-gray-700 mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-black">B</span>
                  Behavioral Questions
                  <span className="text-xs text-gray-400 font-normal">({result.behavioral_questions_rich.length})</span>
                </h4>
                <div className="space-y-3">
                  {result.behavioral_questions_rich.map((q, i) => {
                    const question = typeof q === 'string' ? q : q.question
                    const why      = typeof q === 'object' ? q.why_asked : ''
                    const impact   = typeof q === 'object' ? q.impact : ''
                    const hint     = typeof q === 'object' ? q.hint : ''
                    return (
                      <div key={i} className="bg-white border border-purple-100 rounded-2xl p-5 shadow-sm">
                        <div className="flex gap-3 mb-3">
                          <span className="w-7 h-7 rounded-full bg-purple-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0">{i+1}</span>
                          <p className="text-sm font-semibold text-gray-800 leading-relaxed">{question}</p>
                        </div>
                        {why && (
                          <div className="ml-10 mb-2 flex gap-2 items-start">
                            <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wide flex-shrink-0 mt-0.5">Why asked</span>
                            <p className="text-xs text-gray-500">{why}</p>
                          </div>
                        )}
                        {impact && (
                          <div className="ml-10 mb-2 bg-green-50 border border-green-200 rounded-xl px-3 py-2 flex gap-2 items-start">
                            <span className="text-[10px] font-bold text-green-600 uppercase tracking-wide flex-shrink-0 mt-0.5">Impact</span>
                            <p className="text-xs text-green-700">{impact}</p>
                          </div>
                        )}
                        {hint && (
                          <div className="ml-10 flex gap-2 items-start">
                            <span className="text-[10px] font-bold text-amber-500 uppercase tracking-wide flex-shrink-0 mt-0.5">Hint</span>
                            <p className="text-xs text-amber-700">{hint}</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Technical Questions */}
            {(result.technical_questions_rich?.length > 0) && (
              <div className="mb-8">
                <h4 className="text-sm font-black text-gray-700 mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-black">T</span>
                  Technical Questions
                  <span className="text-xs text-gray-400 font-normal">({result.technical_questions_rich.length})</span>
                </h4>
                <div className="space-y-3">
                  {result.technical_questions_rich.map((q, i) => {
                    const question = typeof q === 'string' ? q : q.question
                    const why      = typeof q === 'object' ? q.why_asked : ''
                    const impact   = typeof q === 'object' ? q.impact : ''
                    const topic    = typeof q === 'object' ? q.topic : ''
                    const depth    = typeof q === 'object' ? q.expected_depth : ''
                    return (
                      <div key={i} className="bg-white border border-indigo-100 rounded-2xl p-5 shadow-sm">
                        <div className="flex gap-3 mb-3">
                          <span className="w-7 h-7 rounded-full bg-indigo-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0">{i+1}</span>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-gray-800 leading-relaxed mb-1">{question}</p>
                            <div className="flex gap-2 flex-wrap">
                              {topic && <span className="text-[10px] bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded-full font-semibold">{topic}</span>}
                              {depth && <span className="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-semibold">{depth}</span>}
                            </div>
                          </div>
                        </div>
                        {why && (
                          <div className="ml-10 mb-2 flex gap-2 items-start">
                            <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wide flex-shrink-0 mt-0.5">Why asked</span>
                            <p className="text-xs text-gray-500">{why}</p>
                          </div>
                        )}
                        {impact && (
                          <div className="ml-10 bg-green-50 border border-green-200 rounded-xl px-3 py-2 flex gap-2 items-start">
                            <span className="text-[10px] font-bold text-green-600 uppercase tracking-wide flex-shrink-0 mt-0.5">Impact</span>
                            <p className="text-xs text-green-700">{impact}</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Common Mistakes */}
            {result.common_mistakes?.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
                <p className="text-xs font-bold text-red-600 mb-2">⚠️ COMMON MISTAKES TO AVOID</p>
                <ul className="space-y-1">
                  {result.common_mistakes.map((m,i) => (
                    <li key={i} className="text-xs text-red-700 flex gap-2"><span>✗</span>{m}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Aptitude Questions */}
            {result.aptitude_questions?.length > 0 && (
              <div className="mb-8">
                <h4 className="text-sm font-black text-gray-700 mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-xs font-black">A</span>
                  Aptitude Questions
                  <span className="text-xs text-gray-400 font-normal">({result.aptitude_questions.length})</span>
                </h4>
                <div className="space-y-3">
                  {result.aptitude_questions.map((q, i) => {
                    const question   = typeof q === 'string' ? q : q.question
                    const category   = typeof q === 'object' ? q.category : ''
                    const difficulty = typeof q === 'object' ? q.difficulty : ''
                    const answer     = typeof q === 'object' ? q.answer : ''
                    const explanation = typeof q === 'object' ? q.explanation : ''
                    const tip        = typeof q === 'object' ? q.tip : ''
                    const catColor = {
                      quantitative:       'bg-orange-100 text-orange-700',
                      logical_reasoning:  'bg-blue-100 text-blue-700',
                      verbal:             'bg-green-100 text-green-700',
                      data_interpretation:'bg-purple-100 text-purple-700',
                    }[category] || 'bg-gray-100 text-gray-600'
                    const diffColor = {
                      easy:   'bg-green-100 text-green-600',
                      medium: 'bg-amber-100 text-amber-600',
                      hard:   'bg-red-100 text-red-600',
                    }[difficulty] || 'bg-gray-100 text-gray-500'
                    return (
                      <div key={i} className="bg-white border border-amber-100 rounded-2xl p-5 shadow-sm">
                        <div className="flex gap-3 mb-3">
                          <span className="w-7 h-7 rounded-full bg-amber-500 text-white text-xs font-black flex items-center justify-center flex-shrink-0">{i+1}</span>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-gray-800 leading-relaxed mb-2">{question}</p>
                            <div className="flex gap-2 flex-wrap">
                              {category && (
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${catColor}`}>
                                  {category.replace('_', ' ')}
                                </span>
                              )}
                              {difficulty && (
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${diffColor}`}>
                                  {difficulty}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        {(answer || explanation || tip) && (
                          <details className="ml-10">
                            <summary className="cursor-pointer text-xs text-amber-600 font-semibold hover:text-amber-700 select-none">
                              View answer & explanation →
                            </summary>
                            <div className="mt-3 space-y-2">
                              {answer && (
                                <div className="bg-green-50 border border-green-200 rounded-xl px-3 py-2">
                                  <span className="text-[10px] font-bold text-green-600 uppercase tracking-wide">Answer</span>
                                  <p className="text-xs text-green-800 mt-0.5 font-semibold">{answer}</p>
                                </div>
                              )}
                              {explanation && (
                                <div className="bg-blue-50 border border-blue-200 rounded-xl px-3 py-2">
                                  <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wide">Explanation</span>
                                  <p className="text-xs text-blue-800 mt-0.5 leading-relaxed">{explanation}</p>
                                </div>
                              )}
                              {tip && (
                                <div className="bg-amber-50 border border-amber-200 rounded-xl px-3 py-2 flex gap-2 items-start">
                                  <span className="text-[10px] font-bold text-amber-600 uppercase tracking-wide flex-shrink-0 mt-0.5">Tip</span>
                                  <p className="text-xs text-amber-700">{tip}</p>
                                </div>
                              )}
                            </div>
                          </details>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Voice Interview */}
            <div className="border-t border-gray-100 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-base font-black text-gray-800">🎙️ Practice with Voice AI</span>
                <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full font-semibold">Chrome/Edge only</span>
              </div>
              <VoiceInterview
                questions={interview_questions}
                behavioralQuestions={behavioral_questions}
                technicalQuestions={technical_questions}
              />
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
