import React from 'react'
import { CheckCircle, AlertCircle, Zap } from 'lucide-react'

export const AnalysisResults = ({ analysis }) => {
  if (!analysis) return null

  const {
    match_percentage,
    matching_skills,
    missing_skills,
    skill_gaps,
    feedback,
    improvements,
    key_strengths,
    summary,
  } = analysis

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-blue-600'
    if (percentage >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getMatchBgColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-100'
    if (percentage >= 60) return 'bg-blue-100'
    if (percentage >= 40) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Summary */}
      {summary && (
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg p-6 text-white shadow-lg">
          <p className="text-sm font-medium opacity-90">Summary</p>
          <p className="mt-2 text-lg">{summary}</p>
        </div>
      )}

      {/* Match Percentage */}
      <div className={`rounded-lg p-6 ${getMatchBgColor(match_percentage)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700">Resume-Job Match</p>
            <p className={`text-4xl font-bold mt-2 ${getMatchColor(match_percentage)}`}>
              {match_percentage}%
            </p>
          </div>
          <div className="relative w-24 h-24">
            <svg className="transform -rotate-90" width="96" height="96">
              <circle
                cx="48"
                cy="48"
                r="44"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                className="text-gray-300"
              />
              <circle
                cx="48"
                cy="48"
                r="44"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray={`${(match_percentage / 100) * 276} 276`}
                className={getMatchColor(match_percentage)}
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center font-bold">
              {match_percentage}%
            </span>
          </div>
        </div>
      </div>

      {/* Key Strengths */}
      {key_strengths && key_strengths.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-green-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
            <CheckCircle className="text-green-600" size={24} />
            <span>Key Strengths</span>
          </h3>
          <ul className="mt-4 space-y-2">
            {key_strengths.map((strength, idx) => (
              <li key={idx} className="flex items-start space-x-3">
                <span className="text-green-600 font-bold mt-1">✓</span>
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Matching Skills */}
      {matching_skills && matching_skills.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-blue-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">
            ✅ Matching Skills ({matching_skills.length})
          </h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {matching_skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {missing_skills && missing_skills.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-orange-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">
            ⚠️ Missing Skills ({missing_skills.length})
          </h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {missing_skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Skill Gaps */}
      {skill_gaps && skill_gaps.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-yellow-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
            <AlertCircle className="text-yellow-600" size={24} />
            <span>Skill Gaps</span>
          </h3>
          <div className="mt-4 space-y-3">
            {skill_gaps.map((gap, idx) => {
              const importance = gap.importance || 'medium'
              const importanceColor =
                importance === 'high'
                  ? 'bg-red-100 border-red-300'
                  : importance === 'medium'
                    ? 'bg-yellow-100 border-yellow-300'
                    : 'bg-green-100 border-green-300'

              return (
                <div key={idx} className={`p-3 rounded border-2 ${importanceColor}`}>
                  <div className="flex justify-between items-start">
                    <span className="text-gray-800">{gap.skill}</span>
                    <span className="text-xs font-semibold px-2 py-1 bg-white rounded">
                      {importance.toUpperCase()}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Feedback */}
      {feedback && (
        <div className="bg-white rounded-lg p-6 border-2 border-primary-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">📋 Detailed Feedback</h3>
          <div className="mt-4 text-gray-700 whitespace-pre-wrap">{feedback}</div>
        </div>
      )}

      {/* Improvements */}
      {improvements && improvements.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-secondary-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
            <Zap className="text-secondary-600" size={24} />
            <span>Actionable Improvements</span>
          </h3>
          <ul className="mt-4 space-y-3">
            {improvements.map((improvement, idx) => (
              <li key={idx} className="flex items-start space-x-3">
                <span className="text-secondary-600 font-bold mt-1">→</span>
                <span className="text-gray-700">{improvement}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
