import React from 'react'
import { AlertCircle, Loader } from 'lucide-react'

export const LoadingSpinner = ({ message = 'Processing your resume...' }) => {
  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-12">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 rounded-full"></div>
        <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary-500 rounded-full animate-spin border-t-transparent"></div>
      </div>
      <p className="text-gray-600 font-medium">{message}</p>
      <p className="text-sm text-gray-500">Using Claude AI for deep analysis...</p>
    </div>
  )
}

export const ErrorMessage = ({ error, onDismiss }) => {
  return (
    <div className="flex items-start gap-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
      <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={24} />
      <div className="flex-1">
        <h3 className="font-semibold text-red-800">Error</h3>
        <p className="text-red-700 text-sm mt-1">{error}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-600 hover:text-red-800 font-semibold"
        >
          ✕
        </button>
      )}
    </div>
  )
}

export const SuccessMessage = ({ message }) => {
  return (
    <div className="flex items-start gap-4 p-4 bg-green-50 border-l-4 border-green-500 rounded-lg">
      <div className="text-green-600 flex-shrink-0 mt-0.5 text-2xl">✓</div>
      <div>
        <p className="text-green-700 font-medium">{message}</p>
      </div>
    </div>
  )
}
