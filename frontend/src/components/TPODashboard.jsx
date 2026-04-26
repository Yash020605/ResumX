import React, { useEffect, useState } from 'react'
import { tpoAPI } from '../services/api'
import AnalyticsStatCard from './AnalyticsStatCard'
import SkillHeatmap from './SkillHeatmap'
import ReadinessGauge from './ReadinessGauge'
import RecruiterExport from './RecruiterExport'
import TPOSessionPanel from './TPOSessionPanel'

function StatCard({ label, value, sub, color = 'violet' }) {
  const colors = {
    violet: 'from-violet-500 to-indigo-500',
    green:  'from-green-500 to-emerald-500',
    amber:  'from-amber-500 to-orange-500',
    red:    'from-red-500 to-rose-500',
  }
  return (
    <div className={`bg-gradient-to-br ${colors[color]} text-white rounded-2xl p-5 shadow`}>
      <p className="text-xs opacity-80 mb-1">{label}</p>
      <p className="text-3xl font-black">{value ?? '—'}</p>
      {sub && <p className="text-xs opacity-70 mt-1">{sub}</p>}
    </div>
  )
}

export default function TPODashboard({ onNavigate = () => {} }) {
  const [activeTab, setActiveTab] = useState('batch')
  const [report, setReport] = useState(null)
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [err, setErr] = useState('')

  const load = async () => {
    setLoading(true); setErr('')
    try {
      // getReport returns 404 when no report exists yet — treat that as null, not an error
      const [reportResult, sRes] = await Promise.allSettled([
        tpoAPI.getReport(),
        tpoAPI.getStudents(),
      ])

      if (reportResult.status === 'fulfilled') {
        setReport(reportResult.value.data)
      } else {
        // Only surface the error if it's not a "no report yet" 404
        const msg = reportResult.reason?.message || ''
        if (!msg.includes('No report generated yet')) {
          setErr(msg)
        }
        setReport(null)
      }

      if (sRes.status === 'fulfilled') {
        setStudents(sRes.value.data.students || [])
      } else {
        setErr(sRes.reason?.message || 'Failed to load students')
      }
    } catch (e) {
      setErr(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const generate = async () => {
    setGenerating(true); setErr('')
    try {
      const res = await tpoAPI.generateReport()
      setReport(res.data)
      await load()
    } catch (e) {
      setErr(e.message)
    } finally {
      setGenerating(false)
    }
  }

  const exportCSV = () => {
    window.open('/api/tpo/export/csv', '_blank')
  }

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  const rd = report?.report_data || {}

  return (
    <div className="space-y-6">
      {/* Tab bar */}
      <div className="flex gap-2 border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('batch')}
          className={`px-4 py-2 text-sm font-bold rounded-t-lg transition-colors ${
            activeTab === 'batch'
              ? 'bg-white border border-b-white border-gray-200 text-violet-700 -mb-px'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          📊 Batch Report
        </button>
        <button
          onClick={() => setActiveTab('live')}
          className={`px-4 py-2 text-sm font-bold rounded-t-lg transition-colors ${
            activeTab === 'live'
              ? 'bg-white border border-b-white border-gray-200 text-violet-700 -mb-px'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          🔴 Live Session
        </button>
      </div>

      {activeTab === 'batch' && (
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h2 className="text-xl font-black text-gray-800">🏫 Placement Cell Dashboard</h2>
              <p className="text-sm text-gray-500">Batch Readiness Report</p>
            </div>
            <div className="flex gap-2">
              <button onClick={generate} disabled={generating}
                className="px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-500 text-white text-sm font-bold rounded-xl hover:opacity-90 disabled:opacity-50">
                {generating ? '⏳ Generating…' : '⚡ Generate Report'}
              </button>
              <button onClick={exportCSV}
                className="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-bold rounded-xl hover:bg-gray-200">
                📥 Export CSV
              </button>
            </div>
          </div>

          {err && <div className="bg-red-50 text-red-600 rounded-xl p-4 text-sm">{err}</div>}

          {!report && !err && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-700">
              No report generated yet. Click <strong>⚡ Generate Report</strong> to analyse your batch.
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard label="Total Students" value={report?.total_students ?? students.length} color="violet" />
            <StatCard label="Avg Match %" value={report?.avg_match_pct ? `${report.avg_match_pct.toFixed(1)}%` : '—'} color="green" />
            <StatCard label="Readiness Score" value={report?.readiness_score ? `${report.readiness_score}/100` : '—'} color="amber" />
            <StatCard label="Ready (>80%)" value={rd.match_distribution?.above_80 ?? '—'} color="green" />
          </div>

          {/* Analytics Counter */}
          <AnalyticsStatCard />

          {/* Command Center Row: Heatmap + Gauge + Export */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <SkillHeatmap />
            <ReadinessGauge />
            <RecruiterExport />
          </div>

          {/* Executive Summary */}
          {rd.executive_summary && (
            <div className="bg-violet-50 border border-violet-200 rounded-2xl p-5">
              <h3 className="font-bold text-violet-800 mb-2">📋 Executive Summary</h3>
              <p className="text-sm text-gray-700">{rd.executive_summary}</p>
            </div>
          )}

          {/* Top Skill Gaps */}
          {(rd.top_skill_gaps || report?.top_skill_gaps || []).length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="font-bold text-gray-800 mb-4">⚠️ Top Skill Gaps Across Batch</h3>
              <div className="space-y-2">
                {(rd.top_skill_gaps || report?.top_skill_gaps || []).slice(0, 8).map((g, i) => {
                  const skill = g.skill || g
                  const count = g.affected_students || g.count || 0
                  const total = report?.total_students || students.length || 1
                  const pct = Math.round((count / total) * 100)
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs w-36 truncate text-gray-700 font-medium">{skill}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                        <div className="bg-gradient-to-r from-violet-500 to-indigo-400 h-2.5 rounded-full"
                          style={{ width: `${pct}%`, transition: 'width 0.8s ease' }} />
                      </div>
                      <span className="text-xs text-gray-500 w-16 text-right">{count} students</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Match Distribution */}
          {rd.match_distribution && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="font-bold text-gray-800 mb-4">📊 Match % Distribution</h3>
              <div className="grid grid-cols-4 gap-3 text-center">
                {[
                  { label: '< 40%', key: 'below_40', color: 'bg-red-100 text-red-700' },
                  { label: '40–60%', key: '40_to_60', color: 'bg-amber-100 text-amber-700' },
                  { label: '60–80%', key: '60_to_80', color: 'bg-blue-100 text-blue-700' },
                  { label: '> 80%', key: 'above_80', color: 'bg-green-100 text-green-700' },
                ].map((b) => (
                  <div key={b.key} className={`rounded-xl p-4 ${b.color}`}>
                    <p className="text-2xl font-black">{rd.match_distribution[b.key] ?? 0}</p>
                    <p className="text-xs font-medium mt-1">{b.label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Interventions */}
          {(rd.recommended_interventions || []).length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="font-bold text-gray-800 mb-4">🎯 Recommended Interventions</h3>
              <div className="grid sm:grid-cols-2 gap-3">
                {rd.recommended_interventions.map((r, i) => (
                  <div key={i} className="bg-indigo-50 rounded-xl p-4 border border-indigo-100">
                    <p className="font-semibold text-indigo-800 text-sm">{r.skill}</p>
                    <p className="text-xs text-gray-600 mt-1">{r.resource}</p>
                    {r.duration && <p className="text-xs text-indigo-500 mt-1">⏱ {r.duration}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Student Table */}
          {students.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="font-bold text-gray-800 mb-4">👥 Student Overview ({students.length})</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 border-b">
                      <th className="pb-2 pr-4">Name</th>
                      <th className="pb-2 pr-4">Match %</th>
                      <th className="pb-2 pr-4">Top Gaps</th>
                      <th className="pb-2">Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((s, i) => (
                      <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                        <td className="py-2 pr-4 font-medium text-gray-800">{s.full_name}</td>
                        <td className="py-2 pr-4">
                          <span className={`font-bold ${s.match_pct >= 70 ? 'text-green-600' : s.match_pct >= 40 ? 'text-amber-600' : 'text-red-500'}`}>
                            {s.match_pct?.toFixed(0) ?? '—'}%
                          </span>
                        </td>
                        <td className="py-2 pr-4 text-gray-500 text-xs">
                          {(s.skill_gaps || []).slice(0, 3).map((g) =>
                            typeof g === 'string' ? g : g.skill
                          ).join(', ') || '—'}
                        </td>
                        <td className="py-2 text-xs text-gray-400">
                          {(s.completed_agents || []).length}/5 agents
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'live' && <TPOSessionPanel onNavigate={onNavigate} />}
    </div>
  )
}
