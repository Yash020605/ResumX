import React from 'react'

export const JobDescriptionInput = ({ jobDescription, onJobDescriptionChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          💼 Job Description
        </label>
        <textarea
          value={jobDescription}
          onChange={(e) => onJobDescriptionChange(e.target.value)}
          placeholder="Paste the job description here... (minimum 30 characters)"
          className="w-full h-64 p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 bg-white shadow-sm transition"
        />
        <p className="text-xs text-gray-500 mt-2">
          {jobDescription.length} characters • Minimum 30 required
        </p>
      </div>
    </div>
  )
}
