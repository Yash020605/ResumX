import React, { useState } from 'react'
import { BookOpen, Users, Mic } from 'lucide-react'
import { VoiceMockInterview } from './VoiceMockInterview'

export const InterviewPrepDisplay = ({ interviewData, resume }) => {
  const [showMockInterview, setShowMockInterview] = useState(false)
  if (!interviewData) return null

  const {
    probable_questions,
    focus_areas,
    expected_answers,
    follow_up_questions,
    common_mistakes,
    strengths_to_highlight,
    prep_resources,
  } = interviewData

  if (showMockInterview) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => setShowMockInterview(false)}
          className="text-indigo-600 hover:text-indigo-800 font-medium mb-4 flex items-center gap-1"
        >
          &larr; Back to Interview Prep Guide
        </button>
        <VoiceMockInterview questions={probable_questions} resume={resume} />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Action Button for Mock Interview */}
      {probable_questions && probable_questions.length > 0 && (
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 text-white shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
              <Mic size={24} /> Practice with Voice AI
            </h3>
            <p className="opacity-90">Simulate a real interview environment with our interactive speech agent.</p>
          </div>
          <button
            onClick={() => setShowMockInterview(true)}
            className="bg-white text-indigo-600 hover:bg-gray-50 px-6 py-3 rounded-full font-bold shadow-md transition transform hover:scale-105 whitespace-nowrap"
          >
            Start Mock Interview
          </button>
        </div>
      )}

      {/* Strengths to Highlight */}
      {strengths_to_highlight && strengths_to_highlight.length > 0 && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg p-6 shadow-lg">
          <h3 className="text-lg font-semibold mb-4">💪 Key Strengths to Emphasize</h3>
          <ul className="space-y-2">
            {strengths_to_highlight.map((strength, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="font-bold">✓</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Focus Areas */}
      {focus_areas && focus_areas.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-blue-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <BookOpen className="text-blue-600" size={24} />
            Key Areas to Prepare
          </h3>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            {focus_areas.map((area, idx) => (
              <div key={idx} className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                <p className="text-gray-800 font-medium">{area}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Probable Questions */}
      {probable_questions && probable_questions.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-primary-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            🎤 Probable Interview Questions ({probable_questions.length})
          </h3>
          <div className="space-y-4">
            {probable_questions.map((question, idx) => (
              <div
                key={idx}
                className="border-l-4 border-primary-500 bg-primary-50 p-4 rounded"
              >
                <p className="font-semibold text-gray-800 text-sm">Q{idx + 1}: {question}</p>
                {expected_answers && expected_answers[question] && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm text-primary-600 font-medium hover:text-primary-700">
                      View suggested answer →
                    </summary>
                    <p className="mt-2 text-gray-700 text-sm">{expected_answers[question]}</p>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Follow-up Questions */}
      {follow_up_questions && follow_up_questions.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-yellow-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            🔄 Common Follow-up Questions
          </h3>
          <ul className="space-y-2">
            {follow_up_questions.map((question, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="text-yellow-600 font-bold">→</span>
                <span className="text-gray-700">{question}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Common Mistakes */}
      {common_mistakes && common_mistakes.length > 0 && (
        <div className="bg-red-50 rounded-lg p-6 border-2 border-red-200 shadow-sm">
          <h3 className="text-lg font-semibold text-red-800 mb-4">⚠️ Mistakes to Avoid</h3>
          <ul className="space-y-2">
            {common_mistakes.map((mistake, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="text-red-600 font-bold">✗</span>
                <span className="text-gray-700">{mistake}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Prep Resources */}
      {prep_resources && prep_resources.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-purple-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Users className="text-purple-600" size={24} />
            Topics to Study
          </h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {prep_resources.map((resource, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
              >
                {resource}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
