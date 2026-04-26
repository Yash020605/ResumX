import React, { useState } from 'react'
import { Code, Lightbulb, Target, Clock, Star, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'

export const ProjectSuggestionsDisplay = ({ projectData }) => {
  const [expandedProjects, setExpandedProjects] = useState(new Set())

  if (!projectData) return null

  const { projects, context } = projectData

  const toggleProject = (projectId) => {
    const newExpanded = new Set(expandedProjects)
    if (newExpanded.has(projectId)) {
      newExpanded.delete(projectId)
    } else {
      newExpanded.add(projectId)
    }
    setExpandedProjects(newExpanded)
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'advanced':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getPortfolioValueColor = (value) => {
    switch (value) {
      case 'high':
        return 'text-green-600'
      case 'medium':
        return 'text-yellow-600'
      case 'low':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Context Summary */}
      {context && (
        <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg p-6 shadow-lg">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Target size={24} />
            Project Recommendations Based On Your Profile
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            {context.skill_gaps && context.skill_gaps.length > 0 && (
              <div>
                <p className="font-medium mb-2">Skills to Develop:</p>
                <div className="flex flex-wrap gap-1">
                  {context.skill_gaps.slice(0, 3).map((skill, idx) => (
                    <span key={idx} className="px-2 py-1 bg-white/20 rounded text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {context.career_alignment && context.career_alignment.length > 0 && (
              <div>
                <p className="font-medium mb-2">Career Focus:</p>
                <div className="flex flex-wrap gap-1">
                  {context.career_alignment.slice(0, 2).map((field, idx) => (
                    <span key={idx} className="px-2 py-1 bg-white/20 rounded text-xs">
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {context.focus_areas && context.focus_areas.length > 0 && (
              <div>
                <p className="font-medium mb-2">Focus Areas:</p>
                <div className="flex flex-wrap gap-1">
                  {context.focus_areas.slice(0, 2).map((area, idx) => (
                    <span key={idx} className="px-2 py-1 bg-white/20 rounded text-xs">
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Project Cards */}
      <div className="grid gap-6">
        {projects && projects.length > 0 ? (
          projects.map((project, idx) => (
            <div
              key={project.project_id || idx}
              className="bg-white rounded-lg border-2 border-gray-200 shadow-sm hover:shadow-md transition-shadow"
            >
              {/* Project Header */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-800">{project.title}</h3>
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {project.category}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3">{project.description}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <div className="flex items-center gap-1">
                      <Star className={getPortfolioValueColor(project.portfolio_value)} size={16} />
                      <span className={`text-sm font-medium ${getPortfolioValueColor(project.portfolio_value)}`}>
                        {project.portfolio_value} value
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded border ${getDifficultyColor(project.difficulty)}`}>
                      {project.difficulty}
                    </span>
                  </div>
                </div>

                {/* Quick Info */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                  <div className="flex items-center gap-1">
                    <Clock size={16} />
                    <span>{project.estimated_duration}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Target size={16} />
                    <span>Match: {Math.round((project.relevance_score || 0.5) * 100)}%</span>
                  </div>
                </div>

                {/* Why Recommended */}
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <p className="text-sm text-gray-700">
                    <strong>Why recommended:</strong> {project.why_recommended}
                  </p>
                </div>

                {/* Toggle Button */}
                <button
                  onClick={() => toggleProject(project.project_id || idx)}
                  className="mt-4 flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  {expandedProjects.has(project.project_id || idx) ? (
                    <>
                      <ChevronUp size={16} />
                      Show Less Details
                    </>
                  ) : (
                    <>
                      <ChevronDown size={16} />
                      Show More Details
                    </>
                  )}
                </button>
              </div>

              {/* Expanded Details */}
              {expandedProjects.has(project.project_id || idx) && (
                <div className="p-6 space-y-6">
                  {/* Tech Stack */}
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <Code size={18} />
                      Technology Stack
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {project.tech_stack && project.tech_stack.map((tech, techIdx) => (
                        <span
                          key={techIdx}
                          className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Skills Developed */}
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <Lightbulb size={18} />
                      Skills You'll Develop
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {project.skills_developed && project.skills_developed.map((skill, skillIdx) => (
                        <span
                          key={skillIdx}
                          className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Skill Gaps Addressed */}
                  {project.skill_gap_addressed && project.skill_gap_addressed.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3">🎯 Skill Gaps This Project Addresses</h4>
                      <div className="flex flex-wrap gap-2">
                        {project.skill_gap_addressed.map((skill, skillIdx) => (
                          <span
                            key={skillIdx}
                            className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Career Benefits */}
                  <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                    <h4 className="font-semibold text-gray-800 mb-2">💼 Career Benefits</h4>
                    <p className="text-sm text-gray-700">{project.career_benefits}</p>
                  </div>

                  {/* Learning Outcomes */}
                  {project.learning_outcomes && project.learning_outcomes.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3">📚 What You'll Learn</h4>
                      <ul className="space-y-2">
                        {project.learning_outcomes.map((outcome, outcomeIdx) => (
                          <li key={outcomeIdx} className="flex items-start gap-3">
                            <span className="text-green-600 font-bold mt-1">✓</span>
                            <span className="text-gray-700 text-sm">{outcome}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Next Steps */}
                  {project.next_steps && project.next_steps.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3">🚀 Getting Started</h4>
                      <ol className="space-y-2">
                        {project.next_steps.map((step, stepIdx) => (
                          <li key={stepIdx} className="flex items-start gap-3">
                            <span className="bg-primary-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold mt-0.5">
                              {stepIdx + 1}
                            </span>
                            <span className="text-gray-700 text-sm">{step}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-4 border-t border-gray-100">
                    <button className="flex-1 bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium transition">
                      Start This Project
                    </button>
                    <button className="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition flex items-center gap-2">
                      <ExternalLink size={16} />
                      Resources
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No project suggestions available</p>
            <p className="text-gray-400 text-sm mt-2">
              Try running the resume analysis first to get personalized project recommendations
            </p>
          </div>
        )}
      </div>

      {/* Summary */}
      {projects && projects.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <h3 className="font-semibold text-gray-800 mb-3">📊 Project Portfolio Strategy</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="font-medium text-gray-700">Recommended Projects:</p>
              <p className="text-2xl font-bold text-primary-600">{projects.length}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Difficulty Mix:</p>
              <div className="flex gap-1 mt-1">
                {['beginner', 'intermediate', 'advanced'].map(level => {
                  const count = projects.filter(p => p.difficulty === level).length
                  return count > 0 && (
                    <span key={level} className={`px-2 py-1 rounded text-xs ${getDifficultyColor(level)}`}>
                      {count} {level}
                    </span>
                  )
                })}
              </div>
            </div>
            <div>
              <p className="font-medium text-gray-700">Portfolio Impact:</p>
              <div className="flex gap-1 mt-1">
                {['high', 'medium', 'low'].map(value => {
                  const count = projects.filter(p => p.portfolio_value === value).length
                  return count > 0 && (
                    <span key={value} className={`px-2 py-1 rounded text-xs ${getPortfolioValueColor(value)} bg-gray-100`}>
                      {count} {value}
                    </span>
                  )
                })}
              </div>
            </div>
          </div>
          <p className="text-gray-600 text-sm mt-4">
            💡 <strong>Tip:</strong> Start with 1-2 projects that address your biggest skill gaps, then gradually work on more advanced projects to build a comprehensive portfolio.
          </p>
        </div>
      )}
    </div>
  )
}