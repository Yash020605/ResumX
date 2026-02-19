import axios from 'axios'

// API instance with default config
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)

    // Provide user-friendly error messages
    let errorMessage = 'An unexpected error occurred. Please try again.'

    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      if (status === 400) {
        errorMessage = data?.error || 'Invalid request. Please check your input.'
      } else if (status === 500) {
        errorMessage = 'Server error. Please try again later.'
      } else if (status >= 500) {
        errorMessage = 'Service temporarily unavailable. Please try again later.'
      } else {
        errorMessage = data?.error || errorMessage
      }
    } else if (error.request) {
      errorMessage = 'Network error. Please check your connection and try again.'
    }

    // Create a new error with user-friendly message
    const friendlyError = new Error(errorMessage)
    friendlyError.originalError = error
    return Promise.reject(friendlyError)
  }
)

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

export const analysisAPI = {
  // Analyze resume against job description
  analyzeResume: (resume, jobDescription) =>
    apiClient.post('/analyze', {
      resume,
      job_description: jobDescription,
    }),

  // Generate improved resume
  improveResume: (resume, jobDescription, improvements) =>
    apiClient.post('/improve-resume', {
      resume,
      job_description: jobDescription,
      improvements,
    }),

  // Get career field suggestions
  getCareerFields: (resume) =>
    apiClient.post('/career-fields', { resume }),

  // Get interview preparation guide
  getInterviewPrep: (resume, jobDescription) =>
    apiClient.post('/interview-prep', {
      resume,
      job_description: jobDescription,
    }),

  // Upload PDF file
  uploadPDF: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // Search for matching jobs
  searchJobs: (resume) =>
    apiClient.post('/search-jobs', { resume }),

  // Health check
  healthCheck: () => apiClient.get('/health'),
}

export default apiClient
