import React from 'react'
import { FileText, Upload } from 'lucide-react'

export const ResumeInput = ({ resume, onResumeChange, onFileUpload }) => {
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileUpload(file)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          📄 Your Resume
        </label>
        <textarea
          value={resume}
          onChange={(e) => onResumeChange(e.target.value)}
          placeholder="Paste your resume text here... (minimum 50 characters)"
          className="w-full h-64 p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 bg-white shadow-sm transition"
        />
        <p className="text-xs text-gray-500 mt-2">
          {resume.length} characters • Minimum 50 required
        </p>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t-2 border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">or upload PDF</span>
        </div>
      </div>

      <label className="block">
        <div className="border-2 border-dashed border-primary-500 rounded-lg p-6 cursor-pointer hover:bg-primary-50 transition">
          <div className="flex items-center justify-center space-x-2">
            <Upload size={20} className="text-primary-500" />
            <span className="text-primary-500 font-medium">Click to upload PDF resume</span>
          </div>
          <p className="text-xs text-gray-500 text-center mt-2">or drag and drop</p>
        </div>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>
    </div>
  )
}
