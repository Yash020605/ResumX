import React, { useState } from 'react'
import { ExternalLink, Search } from 'lucide-react'

export const JobSearchSection = ({ jobTitle = '', resume = '' }) => {
  const [searchQuery, setSearchQuery] = useState(jobTitle)

  const jobPlatforms = [
    {
      name: 'LinkedIn',
      icon: '💼',
      url: (query) => `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(query)}`,
      color: 'from-blue-600 to-blue-700',
    },
    {
      name: 'Naukri',
      icon: '🇮🇳',
      url: (query) => `https://www.naukri.com/jobs-${query.replace(/\s+/g, '-')}`,
      color: 'from-blue-500 to-blue-600',
    },
    {
      name: 'Indeed',
      icon: '📋',
      url: (query) => `https://www.indeed.com/jobs?q=${encodeURIComponent(query)}`,
      color: 'from-purple-600 to-purple-700',
    },
    {
      name: 'Glassdoor',
      icon: '🏢',
      url: (query) => `https://www.glassdoor.com/Jobs/jobs.htm?keyword=${encodeURIComponent(query)}`,
      color: 'from-green-600 to-green-700',
    },
    {
      name: 'AngelList',
      icon: '🚀',
      url: (query) => `https://angel.co/jobs?keywords=${encodeURIComponent(query)}`,
      color: 'from-black to-gray-800',
    },
    {
      name: 'FlexJobs',
      icon: '⏰',
      url: (query) => `https://www.flexjobs.com/search?search=${encodeURIComponent(query)}`,
      color: 'from-orange-600 to-orange-700',
    },
    {
      name: 'RemoteOK',
      icon: '🌍',
      url: (query) => `https://remoteok.com/remote-${query.replace(/\s+/g, '-')}-jobs`,
      color: 'from-red-600 to-red-700',
    },
    {
      name: 'GitHub Jobs',
      icon: '👨‍💻',
      url: (query) => `https://github.com/search?q=${encodeURIComponent(query)}&type=code`,
      color: 'from-gray-800 to-gray-900',
    },
  ]

  const handleSearch = (platform) => {
    const query = searchQuery.trim() || jobTitle || 'Software Engineer'
    const searchUrl = platform.url(query)
    console.log('Opening URL:', searchUrl)
    const newWindow = window.open(searchUrl, '_blank', 'noopener,noreferrer')
    if (!newWindow) {
      alert('Please allow pop-ups to search on ' + platform.name)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
          <Search className="text-primary-500" />
          Job Search Opportunities
        </h2>
        <p className="text-gray-600">
          Search for job opportunities across multiple platforms instantly
        </p>
      </div>

      {/* Search Input */}
      <div className="mb-6 flex gap-3">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Enter job title or keyword (e.g., 'Software Engineer', 'Data Scientist')"
          className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 transition"
        />
        <button
          onClick={() => handleSearch(jobPlatforms[0])}
          className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-3 rounded-lg font-semibold transition transform hover:scale-105"
        >
          Quick Search
        </button>
      </div>

      {/* Platform Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {jobPlatforms.map((platform) => (
          <button
            key={platform.name}
            onClick={() => handleSearch(platform)}
            className={`bg-gradient-to-br ${platform.color} text-white p-6 rounded-lg shadow-md hover:shadow-lg transition transform hover:scale-105 active:scale-95 group`}
          >
            <div className="text-3xl mb-2">{platform.icon}</div>
            <h3 className="font-semibold text-lg mb-1">{platform.name}</h3>
            <div className="flex items-center gap-1 text-sm opacity-90 group-hover:opacity-100">
              <span>Search Now</span>
              <ExternalLink size={14} />
            </div>
          </button>
        ))}
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-gray-700">
          💡 <strong>Pro Tip:</strong> Customize your search query above to find roles that match your
          skills and experience level. Each platform offers unique job listings and filtering options.
        </p>
      </div>

      {/* Popular Searches */}
      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3">Quick searches:</p>
        <div className="flex flex-wrap gap-2">
          {['Software Engineer', 'Data Scientist', 'Product Manager', 'DevOps Engineer', 'Full Stack Developer'].map((query) => (
            <button
              key={query}
              onClick={() => {
                setSearchQuery(query)
                handleSearch(jobPlatforms[0])
              }}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm rounded-full transition"
            >
              {query}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
