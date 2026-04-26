import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// ── Auth token helpers ────────────────────────────────────────────────────────
export const getToken = () => localStorage.getItem('resumx_token')
export const setToken = (t) => localStorage.setItem('resumx_token', t)
export const clearToken = () => localStorage.removeItem('resumx_token')
export const getUser = () => {
  try { return JSON.parse(localStorage.getItem('resumx_user') || 'null') }
  catch { return null }
}
export const setUser = (u) => localStorage.setItem('resumx_user', JSON.stringify(u))
export const clearUser = () => localStorage.removeItem('resumx_user')

// ── Axios instance ────────────────────────────────────────────────────────────
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000,   // 3 min — pipeline can take 60-90s
})

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json'
  return config
})

apiClient.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg =
      err.response?.data?.error ||
      (err.response?.status === 401 ? 'Session expired. Please log in again.' : null) ||
      (err.request ? 'Network error. Check your connection.' : 'Unexpected error.')
    if (err.response?.status === 401) { clearToken(); clearUser() }
    return Promise.reject(new Error(msg))
  }
)

// ── V2 Agent pipeline ─────────────────────────────────────────────────────────
export const agentsAPI = {
  run: (resume, jobDescription, agents = []) =>
    apiClient.post('/agents/run', { resume, job_description: jobDescription, agents }),
  status: () => apiClient.get('/agents/status'),
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  signup: (email, password, fullName, orgDomain, role = 'student') =>
    apiClient.post('/auth/signup', { email, password, full_name: fullName, org_domain: orgDomain, role }),
  login: (email, password) =>
    apiClient.post('/auth/login', { email, password }),
  refresh: (refreshToken) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
}

// ── TPO ───────────────────────────────────────────────────────────────────────
export const tpoAPI = {
  getReport: () => apiClient.get('/tpo/report'),
  generateReport: () => apiClient.post('/tpo/report/generate'),
  exportJSON: () => apiClient.get('/tpo/export/json'),
  exportCSV: () => apiClient.get('/tpo/export/csv'),
  getStudents: () => apiClient.get('/tpo/students'),
  getStats: (orgId) => apiClient.get(`/tpo/stats/${orgId}`),
}

// ── Sessions ──────────────────────────────────────────────────────────────────
export const sessionsAPI = {
  getLatest: () => apiClient.get('/sessions/latest'),
  resume: (sessionId, message = '') =>
    apiClient.post('/sessions/resume', { session_id: sessionId, message }),
}

// ── TPO Live Sessions ─────────────────────────────────────────────────────────
export const tpoSessionAPI = {
  createSession: () =>
    apiClient.post('/tpo/sessions'),
  endSession: (sessionId) =>
    apiClient.post(`/tpo/sessions/${sessionId}/end`),
  getDashboard: (sessionId) =>
    apiClient.get(`/tpo/sessions/${sessionId}/dashboard`),
  getSummary: (sessionId) =>
    apiClient.get(`/tpo/sessions/${sessionId}/summary`),
  listSessions: (params = {}) =>
    apiClient.get('/tpo/sessions', { params }),
  joinSession: (sessionCode) =>
    apiClient.post('/sessions/join', { session_code: sessionCode }),
}

// ── Legacy V1 endpoints (kept for backward compat) ───────────────────────────
export const analysisAPI = {
  analyzeResume: (resume, jobDescription) =>
    apiClient.post('/analyze', { resume, job_description: jobDescription }),
  improveResume: (resume, jobDescription, improvements) =>
    apiClient.post('/improve-resume', { resume, job_description: jobDescription, improvements }),
  getCareerFields: (resume) => apiClient.post('/career-fields', { resume }),
  getInterviewPrep: (resume, jobDescription) =>
    apiClient.post('/interview-prep', { resume, job_description: jobDescription }),
  uploadPDF: (file) => {
    const fd = new FormData(); fd.append('file', file)
    return apiClient.post('/upload-pdf', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  searchJobs: (resume, jobDescription) =>
    apiClient.post('/search-jobs', { resume, job_description: jobDescription }),
  suggestProjects: (resume, jobDescription, matchingSkills, missingSkills, careerFields) =>
    apiClient.post('/suggest-projects', {
      resume, job_description: jobDescription,
      matching_skills: matchingSkills, missing_skills: missingSkills, career_fields: careerFields,
    }),
  evaluateAnswer: (resume, question, answer) =>
    apiClient.post('/evaluate-answer', { resume, question, answer }),
  healthCheck: () => apiClient.get('/health'),
}

export default apiClient
