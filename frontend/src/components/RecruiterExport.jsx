/**
 * RecruiterExport – One-click "Recruiter Match" ZIP export.
 * TPO pastes a JD → backend runs vector similarity → downloads ZIP of top-50 resumes.
 */
import React, { useState } from 'react'
import apiClient from '../services/api'

const GREEN = '#39ff14'

export default function RecruiterExport() {
  const [jd, setJd]           = useState('')
  const [topN, setTopN]       = useState(50)
  const [loading, setLoading] = useState(false)
  const [manifest, setManifest] = useState(null)
  const [error, setError]     = useState('')

  const handleExport = async () => {
    if (!jd.trim()) { setError('Please paste a Job Description first.'); return }
    setLoading(true); setError(''); setManifest(null)

    try {
      const res = await apiClient.post(
        '/tpo/export/recruiter',
        { job_description: jd, top_n: topN },
        { responseType: 'blob' }
      )

      // Trigger browser download
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/zip' }))
      const a = document.createElement('a')
      a.href = url
      a.download = res.headers['content-disposition']?.split('filename=')[1] || 'matched_resumes.zip'
      a.click()
      URL.revokeObjectURL(url)

      // Try to parse manifest from response headers or show generic success
      setManifest({ count: topN, downloaded: true })
    } catch (e) {
      // If blob response, try to read error text
      if (e.response?.data instanceof Blob) {
        const text = await e.response.data.text()
        try { setError(JSON.parse(text).error || text) } catch { setError(text) }
      } else {
        setError(e.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl p-5 space-y-4"
      style={{
        background: 'linear-gradient(135deg, #0d1117 0%, #0f0f1a 100%)',
        border: '1.5px solid #39ff14',
        boxShadow: '0 0 18px 2px rgba(57,255,20,0.15)',
      }}
    >
      {/* Header */}
      <div>
        <p className="text-sm font-black text-white">Recruiter Match Export</p>
        <p className="text-xs text-gray-500 mt-0.5">
          Paste a JD → get a ZIP of the top matching student resumes
        </p>
      </div>

      {/* JD textarea */}
      <textarea
        value={jd}
        onChange={e => setJd(e.target.value)}
        placeholder="Paste the Job Description here…"
        rows={6}
        className="w-full rounded-xl p-3 text-xs text-gray-200 resize-none outline-none transition-all"
        style={{
          background: 'rgba(255,255,255,0.04)',
          border: `1px solid ${jd.trim() ? 'rgba(57,255,20,0.4)' : '#374151'}`,
          caretColor: GREEN,
        }}
      />

      {/* Top-N selector */}
      <div className="flex items-center gap-3">
        <label className="text-xs text-gray-400">Top</label>
        {[10, 25, 50].map(n => (
          <button key={n} onClick={() => setTopN(n)}
            className="px-3 py-1 rounded-lg text-xs font-bold transition-colors"
            style={{
              background: topN === n ? 'rgba(57,255,20,0.15)' : 'rgba(255,255,255,0.04)',
              color: topN === n ? GREEN : '#6b7280',
              border: `1px solid ${topN === n ? 'rgba(57,255,20,0.4)' : '#374151'}`,
            }}>
            {n}
          </button>
        ))}
        <span className="text-xs text-gray-500">students</span>
      </div>

      {/* Error */}
      {error && (
        <p className="text-xs text-red-400 rounded-lg p-2"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.2)' }}>
          {error}
        </p>
      )}

      {/* Success */}
      {manifest?.downloaded && (
        <div className="text-xs rounded-lg p-3 flex items-center gap-2"
          style={{ background: 'rgba(57,255,20,0.08)', border: '1px solid rgba(57,255,20,0.25)', color: GREEN }}>
          ✓ ZIP downloaded — top {topN} matched resumes + manifest.csv
          <span className="text-gray-500 ml-1">· logged for audit</span>
        </div>
      )}

      {/* Export button */}
      <button
        onClick={handleExport}
        disabled={loading || !jd.trim()}
        className="w-full py-2.5 rounded-xl text-sm font-black transition-all disabled:opacity-40"
        style={{
          background: loading ? 'rgba(57,255,20,0.1)' : 'rgba(57,255,20,0.15)',
          color: GREEN,
          border: `1.5px solid ${GREEN}`,
          boxShadow: loading ? 'none' : '0 0 12px rgba(57,255,20,0.2)',
        }}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: GREEN, borderTopColor: 'transparent' }} />
            Matching resumes…
          </span>
        ) : (
          '⬇ Export Top Matches as ZIP'
        )}
      </button>

      <p className="text-xs text-gray-600 text-center">
        Export events are logged to the audit trail for privacy compliance.
      </p>
    </div>
  )
}
