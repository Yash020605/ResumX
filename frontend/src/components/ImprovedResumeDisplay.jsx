import React from 'react'
import { Copy, Download } from 'lucide-react'

export const ImprovedResumeDisplay = ({ resume, onDownload }) => {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(resume)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const element = document.createElement('a')
    const file = new Blob([resume], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = 'improved-resume.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-gray-800">✨ Your Improved Resume</h3>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition"
          >
            <Copy size={18} />
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition"
          >
            <Download size={18} />
            Download
          </button>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-6 border-2 border-gray-200">
        <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
          {resume}
        </pre>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> This resume has been optimized to match the job description
          while maintaining authenticity. Review the content to ensure all information is accurate
          before submitting.
        </p>
      </div>
    </div>
  )
}
