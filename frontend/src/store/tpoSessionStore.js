import { create } from 'zustand'
import { tpoSessionAPI } from '../services/api'

export const useTpoSessionStore = create((set, get) => ({
  // ── State ──────────────────────────────────────────────────────────────────
  activeSession: null,    // { id, session_code, status, started_at }
  dashboardData: null,    // latest GET /dashboard response
  summaryData: null,      // latest GET /summary response
  sessionList: [],        // paginated list of sessions
  sessionListMeta: { total: 0, page: 1, per_page: 20, pages: 1 },
  joinedSession: null,    // student's joined session info
  loading: false,
  error: null,

  // ── Actions ────────────────────────────────────────────────────────────────

  createSession: async () => {
    set({ loading: true, error: null })
    try {
      const res = await tpoSessionAPI.createSession()
      set({ activeSession: res.data, loading: false })
      return res.data
    } catch (err) {
      set({ error: err.message, loading: false })
      throw err
    }
  },

  endSession: async (sessionId) => {
    set({ loading: true, error: null })
    try {
      const res = await tpoSessionAPI.endSession(sessionId)
      set((s) => ({
        activeSession: s.activeSession
          ? { ...s.activeSession, status: 'ended', ended_at: res.data.ended_at }
          : null,
        loading: false,
      }))
      return res.data
    } catch (err) {
      set({ error: err.message, loading: false })
      throw err
    }
  },

  fetchDashboard: async (sessionId) => {
    // No loading spinner for polling — silent update
    try {
      const res = await tpoSessionAPI.getDashboard(sessionId)
      set({ dashboardData: res.data })
      return res.data
    } catch (err) {
      set({ error: err.message })
    }
  },

  fetchSummary: async (sessionId) => {
    set({ loading: true, error: null })
    try {
      const res = await tpoSessionAPI.getSummary(sessionId)
      set({ summaryData: res.data, loading: false })
      return res.data
    } catch (err) {
      set({ error: err.message, loading: false })
      throw err
    }
  },

  listSessions: async (params = {}) => {
    set({ loading: true, error: null })
    try {
      const res = await tpoSessionAPI.listSessions(params)
      set({
        sessionList: res.data.sessions || [],
        sessionListMeta: {
          total: res.data.total,
          page: res.data.page,
          per_page: res.data.per_page,
          pages: res.data.pages,
        },
        loading: false,
      })
      return res.data
    } catch (err) {
      set({ error: err.message, loading: false })
      throw err
    }
  },

  joinSession: async (sessionCode) => {
    set({ loading: true, error: null })
    try {
      const res = await tpoSessionAPI.joinSession(sessionCode)
      set({ joinedSession: res.data, loading: false })
      return res.data
    } catch (err) {
      set({ error: err.message, loading: false })
      throw err
    }
  },

  clearSession: () => set({
    activeSession: null,
    dashboardData: null,
    summaryData: null,
    joinedSession: null,
    error: null,
  }),

  clearError: () => set({ error: null }),
}))
