import React, { useState, useEffect } from 'react'
import { Briefcase, MapPin, Clock, DollarSign, ExternalLink, Loader } from 'lucide-react'
import { analysisAPI } from '../services/api'

export const JobListings = ({ resume = '' }) => {
  const [jobs, setJobs] = useState([])
  const [keywords, setKeywords] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchJobs = async () => {
    if (!resume.trim()) {
      setError('Please provide your resume first')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await analysisAPI.searchJobs(resume)
      console.log('Job search response:', response.data)
      
      if (response.data.success) {
        setJobs(response.data.jobs || [])
        setKeywords(response.data.keywords || {})
      } else {
        setError(response.data.error || 'Failed to fetch jobs')
        setJobs([])
      }
    } catch (err) {
      console.error('Job search error:', err)
      setError('Failed to search for jobs. Please try again.')
      setJobs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (resume && resume.length > 50) {
      fetchJobs()
    }
  }, [resume])

  const getMatchColor = (score) => {
    if (score >= 0.8) return 'from-green-400 to-green-600'
    if (score >= 0.6) return 'from-yellow-400 to-yellow-600'
    return 'from-orange-400 to-orange-600'
  }

  const getMatchText = (score) => {
    if (score >= 0.8) return '🔥 Excellent Match'
    if (score >= 0.6) return '👍 Good Match'
    return '✓ Potential Fit'
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
          <Briefcase className="text-blue-500" size={28} />
          Recommended Job Opportunities
        </h2>
        <p className="text-gray-600">
          Personalized job listings based on your resume and experience
        </p>
      </div>

      {/* Keywords Display */}
      {keywords && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg mb-6 border-2 border-blue-200">
          <h3 className="font-semibold text-gray-800 mb-3">📋 Your Profile Keywords</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Target Roles:</p>
              <div className="flex flex-wrap gap-2">
                {keywords.job_titles?.slice(0, 3).map((title, idx) => (
                  <span key={idx} className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                    {title}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Key Skills:</p>
              <div className="flex flex-wrap gap-2">
                {keywords.skills?.slice(0, 3).map((skill, idx) => (
                  <span key={idx} className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-300 text-red-800 p-4 rounded-lg mb-6">
          <p className="font-semibold">⚠️ {error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin text-blue-500 mr-3" size={24} />
          <p className="text-gray-600 font-semibold">Finding the best opportunities for you...</p>
        </div>
      )}

      {/* Jobs Grid */}
      {!loading && jobs.length > 0 && (
        <div className="grid grid-cols-1 gap-4">
          {jobs.map((job, idx) => (
            <div
              key={job.id || idx}
              className="bg-gradient-to-r from-white to-gray-50 border-2 border-gray-200 rounded-lg p-6 hover:shadow-lg transition transform hover:-translate-y-1"
            >
              {/* Match Badge */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-800 mb-1">{job.title}</h3>
                  <p className="text-gray-600 font-semibold">{job.company}</p>
                </div>
                <div className={`bg-gradient-to-br ${getMatchColor(job.match_score)} text-white px-4 py-2 rounded-lg text-center whitespace-nowrap ml-4`}>
                  <p className="text-sm font-bold">{getMatchText(job.match_score)}</p>
                  <p className="text-xs">{Math.round(job.match_score * 100)}% match</p>
                </div>
              </div>

              {/* Job Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="flex items-center gap-2 text-gray-700">
                  <MapPin size={16} className="text-blue-500" />
                  <span className="text-sm">{job.location}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <Clock size={16} className="text-green-500" />
                  <span className="text-sm">{job.type}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <DollarSign size={16} className="text-yellow-500" />
                  <span className="text-sm">{job.salary}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <Clock size={16} className="text-purple-500" />
                  <span className="text-sm">{job.posted_date}</span>
                </div>
              </div>

              {/* Description */}
              {job.description && (
                <div className="mb-4">
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {job.description}
                    {job.description.length >= 500 && '...'}
                  </p>
                </div>
              )}

              {/* Apply Button */}
              {job.apply_url && (
                <a
                  href={job.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition transform hover:scale-105 active:scale-95"
                >
                  Apply Now
                  <ExternalLink size={18} />
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && jobs.length === 0 && !error && (
        <div className="text-center py-12">
          <Briefcase size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-600 font-semibold">No jobs found yet</p>
          <p className="text-gray-500 text-sm">Upload your resume and run analysis to see matching opportunities</p>
        </div>
      )}

      {/* Results Counter */}
      {jobs.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Showing <span className="font-bold text-gray-800">{jobs.length}</span> matching job opportunities
          </p>
        </div>
      )}
    </div>
  )
}
