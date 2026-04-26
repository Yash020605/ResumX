import { create } from 'zustand'
import { getUser, getToken } from '../services/api'

export const useAnalysisStore = create((set, get) => ({
  // ── Auth ──────────────────────────────────────────────────────────────────
  user: getUser(),
  token: getToken(),
  setAuth: (user, token) => {
    set({ user, token })
  },
  clearAuth: () => set({ user: null, token: null }),

  // ── Inputs ────────────────────────────────────────────────────────────────
  resume: '',
  jobDescription: '',
  setResume: (resume) => set({ resume }),
  setJobDescription: (jd) => set({ jobDescription: jd }),

  // ── V2 pipeline state ─────────────────────────────────────────────────────
  pipelineResult: null,       // full state from /api/agents/run
  agentProgress: [],          // live progress list while running
  sessionId: null,

  setPipelineResult: (r) => set({ pipelineResult: r, sessionId: r?.session_id || null }),
  pushAgentProgress: (agent) =>
    set((s) => ({ agentProgress: [...s.agentProgress, agent] })),
  clearProgress: () => set({ agentProgress: [] }),

  // ── V1 compat fields (used by existing display components) ────────────────
  analysis: null,
  improvedResume: null,
  careerFields: null,
  interviewData: null,
  projectSuggestions: null,
  setAnalysis: (v) => set({ analysis: v }),
  setImprovedResume: (v) => set({ improvedResume: v }),
  setCareerFields: (v) => set({ careerFields: v }),
  setInterviewData: (v) => set({ interviewData: v }),
  setProjectSuggestions: (v) => set({ projectSuggestions: v }),

  // ── TPO ───────────────────────────────────────────────────────────────────
  tpoReport: null,
  tpoStudents: [],
  setTpoReport: (r) => set({ tpoReport: r }),
  setTpoStudents: (s) => set({ tpoStudents: s }),

  // ── UI ────────────────────────────────────────────────────────────────────
  loading: false,
  error: null,
  setLoading: (v) => set({ loading: v }),
  setError: (e) => set({ error: e }),
  clearError: () => set({ error: null }),

  reset: () => set({
    resume: '', jobDescription: '',
    pipelineResult: null, agentProgress: [], sessionId: null,
    analysis: null, improvedResume: null, careerFields: null,
    interviewData: null, projectSuggestions: null,
    loading: false, error: null,
  }),
}))
