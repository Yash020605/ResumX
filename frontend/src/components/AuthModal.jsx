import React, { useState } from 'react'
import { authAPI, setToken, setUser } from '../services/api'
import { useAnalysisStore } from '../store/analysisStore'

export default function AuthModal({ onClose, mandatory = false }) {
  const [mode, setMode] = useState('login')   // 'login' | 'signup'
  const [form, setForm] = useState({ email: '', password: '', fullName: '', orgDomain: '', role: 'student' })
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)
  const setAuth = useAnalysisStore((s) => s.setAuth)

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setErr(''); setLoading(true)
    try {
      let res
      if (mode === 'login') {
        res = await authAPI.login(form.email, form.password)
      } else {
        res = await authAPI.signup(form.email, form.password, form.fullName, form.orgDomain, form.role)
      }
      const { access_token, user } = res.data
      setToken(access_token)
      setUser(user)
      setAuth(user, access_token)
      onClose()
    } catch (e) {
      setErr(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={mandatory
      ? "min-h-screen bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700 flex items-center justify-center px-4"
      : "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 relative">
        {!mandatory && (
          <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">×</button>
        )}

        {/* Logo */}
        <div className="text-center mb-6">
          <span className="text-3xl font-black bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent">ResumX</span>
          <p className="text-xs text-gray-400 mt-1">Analyze. Improve. Interview. Succeed.</p>
        </div>

        {/* Toggle */}
        <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
          {['login', 'signup'].map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`flex-1 py-2 rounded-md text-sm font-semibold transition ${mode === m ? 'bg-white shadow text-violet-600' : 'text-gray-500'}`}>
              {m === 'login' ? 'Log In' : 'Sign Up'}
            </button>
          ))}
        </div>

        <form onSubmit={submit} className="space-y-4">
          {mode === 'signup' && (
            <>
              <input required placeholder="Full Name" value={form.fullName}
                onChange={(e) => update('fullName', e.target.value)}
                className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400" />
              <input required placeholder="College domain (e.g. adypu.edu.in)" value={form.orgDomain}
                onChange={(e) => update('orgDomain', e.target.value)}
                className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400" />
              <select value={form.role} onChange={(e) => update('role', e.target.value)}
                className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400">
                <option value="student">Student</option>
                <option value="tpo">TPO / Placement Officer</option>
              </select>
            </>
          )}
          <input required type="email" placeholder="Email" value={form.email}
            onChange={(e) => update('email', e.target.value)}
            className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400" />
          <input required type="password" placeholder="Password" value={form.password}
            onChange={(e) => update('password', e.target.value)}
            className="w-full border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400" />

          {err && <p className="text-red-500 text-xs">{err}</p>}

          <button type="submit" disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold rounded-lg hover:opacity-90 disabled:opacity-50 transition">
            {loading ? '...' : mode === 'login' ? 'Log In' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
