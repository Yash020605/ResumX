import React, { useState, useEffect, useRef } from 'react'
import { Mic, Play, Square, ChevronRight, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'
import { analysisAPI } from '../services/api'
import { LoadingSpinner } from './Common'

export const VoiceMockInterview = ({ questions = [], resume = '' }) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [evaluation, setEvaluation] = useState(null)
  const [error, setError] = useState('')
  const [hasStarted, setHasStarted] = useState(false)

  const recognitionRef = useRef(null)
  const synthRef = useRef(window.speechSynthesis)

  useEffect(() => {
    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true

      recognitionRef.current.onresult = (event) => {
        let currentTranscript = ''
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript
        }
        setTranscript(currentTranscript)
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error', event.error)
        // Only set error if it's not a normal stop
        if (event.error !== 'no-speech') {
          setError(`Microphone error: ${event.error}`)
          setIsListening(false)
        }
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    } else {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
    }

    return () => {
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop()
      }
      synthRef.current.cancel()
    }
  }, [])

  const startInterview = () => {
    setHasStarted(true)
    readQuestion(questions[0])
  }

  const readQuestion = (text) => {
    synthRef.current.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9 // slightly slower for better comprehension
    synthRef.current.speak(utterance)
  }

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
    } else {
      setError('')
      try {
        recognitionRef.current?.start()
        setIsListening(true)
      } catch (err) {
        // Handle case where it's already started
        console.error(err)
      }
    }
  }

  const submitAnswer = async () => {
    if (!transcript.trim()) {
      setError('Please provide an answer before submitting.')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
    }

    setIsEvaluating(true)
    setError('')
    synthRef.current.cancel()

    try {
      const response = await analysisAPI.evaluateAnswer(
        resume,
        questions[currentIndex],
        transcript
      )
      
      if (response.data.success) {
        setEvaluation(response.data.evaluation)
        
        // Optionally read out a brief feedback statement
        const fbUtterance = new SpeechSynthesisUtterance(`You scored ${response.data.evaluation.score} out of 10. Check the screen for detailed feedback.`)
        synthRef.current.speak(fbUtterance)
      } else {
        setError('Failed to evaluate answer.')
      }
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.error || 'Error evaluating answer.')
    } finally {
      setIsEvaluating(false)
    }
  }

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      const nextIdx = currentIndex + 1
      setCurrentIndex(nextIdx)
      setTranscript('')
      setEvaluation(null)
      setError('')
      readQuestion(questions[nextIdx])
    }
  }

  const restartInterview = () => {
    setCurrentIndex(0)
    setTranscript('')
    setEvaluation(null)
    setError('')
    setHasStarted(false)
    synthRef.current.cancel()
  }

  if (!questions || questions.length === 0) {
    return <div className="text-gray-500">No questions available for mock interview.</div>
  }

  if (!hasStarted) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center border-t-4 border-indigo-500">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex justify-center items-center gap-2">
          <Mic className="text-indigo-500" size={32} />
          Voice AI Mock Interview
        </h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Practice your interview skills with our AI. It will ask you {questions.length} questions based on your profile and the job description, listen to your answers, and provide instant evaluations.
        </p>
        <button
          onClick={startInterview}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition transform hover:scale-105 flex items-center gap-2 mx-auto"
        >
          <Play size={20} />
          Start Mock Interview
        </button>
      </div>
    )
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-100">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-100">
        <h3 className="text-xl font-bold text-gray-800">
          Question {currentIndex + 1} of {questions.length}
        </h3>
        <button 
          onClick={restartInterview}
          className="text-gray-500 hover:text-indigo-600 flex items-center gap-1 text-sm font-medium transition"
        >
          <RefreshCw size={16} /> Restart
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded-lg mb-4 flex items-center gap-2">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Question Section */}
      <div className="bg-indigo-50 p-6 rounded-xl mb-6 shadow-sm">
        <p className="text-lg font-semibold text-indigo-900 mb-3 flex items-start gap-3">
          <span className="bg-indigo-200 text-indigo-800 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-0.5">
            Q
          </span>
          {currentQuestion}
        </p>
        <button
          onClick={() => readQuestion(currentQuestion)}
          className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center gap-1 ml-11"
        >
          <Play size={14} /> Replay Audio
        </button>
      </div>

      {/* Answer Section */}
      <div className="mb-6">
        <div className="flex justify-between items-end mb-2">
          <label className="font-semibold text-gray-700">Your Answer:</label>
          <button
            onClick={toggleListening}
            disabled={isEvaluating || !!evaluation}
            className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium transition ${
              isListening 
                ? 'bg-red-100 text-red-700 hover:bg-red-200 animate-pulse' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            } ${(isEvaluating || !!evaluation) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isListening ? (
              <><Square size={16} className="fill-current" /> Stop Listening</>
            ) : (
              <><Mic size={16} /> {transcript ? 'Resume Answering' : 'Start Answering'}</>
            )}
          </button>
        </div>
        
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          disabled={isEvaluating || !!evaluation}
          placeholder="Click 'Start Answering' to speak, or type your answer here..."
          className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none transition"
        />
      </div>

      {/* Controls */}
      {!evaluation && (
        <div className="flex justify-end">
          <button
            onClick={submitAnswer}
            disabled={isEvaluating || !transcript.trim() || isListening}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 transition flex items-center gap-2"
          >
            {isEvaluating ? (
              <><LoadingSpinner message="Evaluating..." /> Evaluating...</>
            ) : (
              <><CheckCircle size={18} /> Submit Answer</>
            )}
          </button>
        </div>
      )}

      {/* Evaluation Results */}
      {evaluation && (
        <div className="mt-8 bg-gray-50 rounded-xl p-6 border border-gray-200 animate-fade-in shadow-inner">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-xl font-bold text-gray-800">Feedback</h4>
            <div className={`px-4 py-2 rounded-full font-bold text-lg ${
              evaluation.score >= 8 ? 'bg-green-100 text-green-700' : 
              evaluation.score >= 5 ? 'bg-yellow-100 text-yellow-700' : 
              'bg-red-100 text-red-700'
            }`}>
              Score: {evaluation.score}/10
            </div>
          </div>

          <p className="text-gray-700 mb-6 italic">{evaluation.feedback}</p>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {evaluation.strengths && evaluation.strengths.length > 0 && (
              <div className="bg-white p-4 rounded-lg border border-green-200 shadow-sm">
                <h5 className="font-semibold text-green-700 mb-2 flex items-center gap-2">
                  <CheckCircle size={16} /> Strengths
                </h5>
                <ul className="space-y-1">
                  {evaluation.strengths.map((s, i) => (
                    <li key={i} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-green-500">•</span> {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {evaluation.areas_for_improvement && evaluation.areas_for_improvement.length > 0 && (
              <div className="bg-white p-4 rounded-lg border border-orange-200 shadow-sm">
                <h5 className="font-semibold text-orange-700 mb-2 flex items-center gap-2">
                  <AlertCircle size={16} /> Areas to Improve
                </h5>
                <ul className="space-y-1">
                  {evaluation.areas_for_improvement.map((a, i) => (
                    <li key={i} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-orange-500">•</span> {a}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {evaluation.ideal_answer_concept && (
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-6 shadow-sm">
              <h5 className="font-semibold text-blue-800 mb-2">💡 Ideal Answer Concept</h5>
              <p className="text-sm text-gray-700">{evaluation.ideal_answer_concept}</p>
            </div>
          )}

          <div className="flex justify-end pt-4 border-t border-gray-200">
            {currentIndex < questions.length - 1 ? (
              <button
                onClick={nextQuestion}
                className="bg-gray-800 hover:bg-gray-900 text-white px-6 py-2 rounded-lg font-semibold transition flex items-center gap-2"
              >
                Next Question <ChevronRight size={18} />
              </button>
            ) : (
              <div className="text-green-600 font-bold flex items-center gap-2">
                <CheckCircle size={24} /> Interview Complete!
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
