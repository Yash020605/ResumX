import { create } from 'zustand'

export const useAnalysisStore = create((set) => ({
  // State
  resume: '',
  jobDescription: '',
  analysis: null,
  improvedResume: null,
  careerFields: null,
  interviewData: null,
  loading: false,
  error: null,
  currentStep: 1,

  // Actions
  setResume: (resume) => set({ resume }),
  setJobDescription: (jobDescription) => set({ jobDescription }),
  setAnalysis: (analysis) => set({ analysis }),
  setImprovedResume: (improvedResume) => set({ improvedResume }),
  setCareerFields: (careerFields) => set({ careerFields }),
  setInterviewData: (interviewData) => set({ interviewData }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setCurrentStep: (step) => set({ currentStep: step }),

  // Reset
  reset: () =>
    set({
      resume: '',
      jobDescription: '',
      analysis: null,
      improvedResume: null,
      careerFields: null,
      interviewData: null,
      loading: false,
      error: null,
      currentStep: 1,
    }),

  // Clear error
  clearError: () => set({ error: null }),
}))
