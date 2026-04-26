import React from 'react'
import { Briefcase, TrendingUp, Award } from 'lucide-react'

export const CareerFieldsDisplay = ({ careerData }) => {
  if (!careerData) return null

  const {
    career_fields,
    job_titles,
    industries,
    growth_opportunities,
    recommended_skills,
    certifications,
    summary,
  } = careerData

  return (
    <div className="space-y-6 animate-fade-in">
      {summary && (
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg p-6 shadow-lg">
          <p className="font-medium mb-2">Career Potential Summary</p>
          <p className="text-lg">{summary}</p>
        </div>
      )}

      {/* Career Fields */}
      {career_fields && career_fields.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-primary-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Briefcase className="text-primary-500" />
            Career Fields ({career_fields.length})
          </h3>
          <div className="mt-4 space-y-3">
            {career_fields.map((field, idx) => (
              <div
                key={idx}
                className="p-4 bg-primary-50 border-l-4 border-primary-500 rounded"
              >
                <p className="font-semibold text-gray-800">
                  {typeof field === 'string' ? field : field.field}
                </p>
                {typeof field === 'object' && field.explanation && (
                  <p className="text-sm text-gray-600 mt-1">{field.explanation}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Job Titles */}
      {job_titles && job_titles.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-blue-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">💼 Job Titles to Search</h3>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
            {job_titles.map((title, idx) => (
              <div key={idx} className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg text-sm">
                {title}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Industries */}
      {industries && industries.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-green-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">🏭 High-Value Industries</h3>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
            {industries.map((industry, idx) => (
              <div key={idx} className="px-4 py-2 bg-green-100 text-green-800 rounded-lg text-sm">
                {industry}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Growth Opportunities */}
      {growth_opportunities && growth_opportunities.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-yellow-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <TrendingUp className="text-yellow-600" />
            Growth Opportunities
          </h3>
          <ul className="mt-4 space-y-2">
            {growth_opportunities.map((opportunity, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="text-yellow-600 font-bold">→</span>
                <span className="text-gray-700">{opportunity}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Skills */}
      {recommended_skills && recommended_skills.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-purple-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800">🎯 Skills to Develop</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {recommended_skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Certifications */}
      {certifications && certifications.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-orange-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Award className="text-orange-600" />
            Recommended Certifications
          </h3>
          <ul className="mt-4 space-y-2">
            {certifications.map((cert, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="text-orange-600 font-bold">✓</span>
                <span className="text-gray-700">{cert}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
