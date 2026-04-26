import React, { useState } from 'react'
import { useAnalysisStore } from '../store/analysisStore'
import { analysisAPI } from '../services/api'
import { ResumeInput } from '../components/ResumeInput'
import { JobDescriptionInput } from '../components/JobDescriptionInput'
import { AnalysisResults } from '../components/AnalysisResults'
import { ImprovedResumeDisplay } from '../components/ImprovedResumeDisplay'
import { CareerFieldsDisplay } from '../components/CareerFieldsDisplay'
import { InterviewPrepDisplay } from '../components/InterviewPrepDisplay'
import { LoadingSpinner, ErrorMessage, SuccessMessage } from '../components/Common'
import { ChatBot } from '../components/ChatBot'
import { JobListings } from '../components/JobListings'

export const HomePage = () => {
  const store = useAnalysisStore()
  const [activeTab, setActiveTab] = useState('analysis')

  const handleAnalyze = async () => {
    if (!store.resume.trim() || !store.jobDescription.trim()) {
      store.setError('Please provide both resume and job description')
      return
    }

    store.setLoading(true)
    store.clearError()

    try {
      const response = await analysisAPI.analyzeResume(store.resume, store.jobDescription)
      store.setAnalysis(response.data.analysis)
      setActiveTab('analysis')
    } catch (err) {
      store.setError(err.response?.data?.error || 'Failed to analyze resume. Please try again.')
    } finally {
      store.setLoading(false)
    }
  }

  const handleImproveResume = async () => {
    if (!store.analysis?.improvements) {
      store.setError('Please run analysis first')
      return
    }

    store.setLoading(true)
    store.clearError()

    try {
      const response = await analysisAPI.improveResume(
        store.resume,
        store.jobDescription,
        store.analysis.improvements
      )
      store.setImprovedResume(response.data.improved_resume)
      setActiveTab('improved')
    } catch (err) {
      store.setError(err.response?.data?.error || 'Failed to improve resume. Please try again.')
    } finally {
      store.setLoading(false)
    }
  }

  const handleGetCareerFields = async () => {
    store.setLoading(true)
    store.clearError()

    try {
      console.log('Fetching career fields...')
      const response = await analysisAPI.getCareerFields(store.resume)
      console.log('Career fields response:', response.data)
      store.setCareerFields(response.data.career_data)
      setActiveTab('career')
    } catch (err) {
      console.error('Career fields error:', err)
      store.setError(
        err.response?.data?.error || 'Failed to get career suggestions. Please try again.'
      )
    } finally {
      store.setLoading(false)
    }
  }

  const handleGetInterviewPrep = async () => {
    if (!store.resume.trim() || !store.jobDescription.trim()) {
      store.setError('Please provide both resume and job description')
      return
    }

    store.setLoading(true)
    store.clearError()

    try {
      console.log('Fetching interview prep...')
      const response = await analysisAPI.getInterviewPrep(store.resume, store.jobDescription)
      console.log('Interview prep response:', response.data)
      store.setInterviewData(response.data.interview_data)
      setActiveTab('interview')
    } catch (err) {
      console.error('Interview prep error:', err)
      store.setError(
        err.response?.data?.error || 'Failed to generate interview prep. Please try again.'
      )
    } finally {
      store.setLoading(false)
    }
  }

  const handleFileUpload = async (file) => {
    try {
      const response = await analysisAPI.uploadPDF(file)
      store.setResume(response.data.text)
    } catch (err) {
      store.setError(err.response?.data?.error || 'Failed to upload PDF. Please try again.')
    }
  }

  const tabs = [
    { id: 'analysis', label: '📊 Analysis', icon: '📊' },
    { id: 'improved', label: '✨ Improved Resume', icon: '✨' },
    { id: 'career', label: '💼 Career Fields', icon: '💼' },
    { id: 'interview', label: '🎤 Interview Prep', icon: '🎤' },
  ]

  return (
    <div className="min-h-screen bg-gradient-page pb-12">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold">📄 AI Resume Analyzer</h1>
          <p className="text-primary-100 mt-1">Optimize your resume using advanced AI analysis</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {store.error && (
          <div className="mb-6">
            <ErrorMessage error={store.error} onDismiss={() => store.clearError()} />
          </div>
        )}

        {/* Input Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <ResumeInput
              resume={store.resume}
              onResumeChange={(text) => store.setResume(text)}
              onFileUpload={handleFileUpload}
            />
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <JobDescriptionInput
              jobDescription={store.jobDescription}
              onJobDescriptionChange={(text) => store.setJobDescription(text)}
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <button
            onClick={handleAnalyze}
            disabled={store.loading}
            className="w-full px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 disabled:opacity-50 text-white font-semibold rounded-lg shadow-md transition transform hover:scale-105 active:scale-95"
          >
            {store.loading ? '🔄 Analyzing...' : '📊 Analyze Resume'}
          </button>

          <button
            onClick={handleGetCareerFields}
            disabled={store.loading || !store.resume.trim()}
            className="w-full px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-semibold rounded-lg shadow-md transition transform hover:scale-105 active:scale-95"
          >
            💼 Career Fields
          </button>

          <button
            onClick={handleGetInterviewPrep}
            disabled={store.loading || !store.resume.trim() || !store.jobDescription.trim()}
            className="w-full px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white font-semibold rounded-lg shadow-md transition transform hover:scale-105 active:scale-95"
          >
            🎤 Interview Prep
          </button>

          <button
            onClick={handleImproveResume}
            disabled={store.loading || !store.analysis}
            className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white font-semibold rounded-lg shadow-md transition transform hover:scale-105 active:scale-95"
          >
            ✨ Improve Resume
          </button>
        </div>

        {/* Results Section */}
        {store.loading ? (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            {/* Tabs */}
            <div className="flex flex-wrap gap-2 mb-6 bg-white rounded-lg p-4 shadow-md">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  disabled={
                    (tab.id === 'analysis' && !store.analysis) ||
                    (tab.id === 'improved' && !store.improvedResume) ||
                    (tab.id === 'career' && !store.careerFields) ||
                    (tab.id === 'interview' && !store.interviewData)
                  }
                  className={`px-4 py-2 font-semibold rounded-lg transition ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              {activeTab === 'analysis' && store.analysis && (
                <AnalysisResults analysis={store.analysis} />
              )}

              {activeTab === 'improved' && store.improvedResume && (
                <ImprovedResumeDisplay resume={store.improvedResume} />
              )}

              {activeTab === 'career' && store.careerFields && (
                <CareerFieldsDisplay careerData={store.careerFields} />
              )}

              {activeTab === 'interview' && store.interviewData && (
                <InterviewPrepDisplay interviewData={store.interviewData} />
              )}

              {!store.analysis &&
                !store.improvedResume &&
                !store.careerFields &&
                !store.interviewData && (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">
                      👆 Provide your resume and job description, then click "Analyze Resume" to get started
                    </p>
                  </div>
                )}
            </div>
          </>
        )}

        {/* Job Search Section */}
        <JobListings resume={store.resume} />

        {/* ChatBot */}
        <ChatBot />
      </main>
    </div>
  )
}

export default HomePage
