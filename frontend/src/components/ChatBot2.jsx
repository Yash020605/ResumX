import React, { useState, useRef, useEffect } from 'react'
import { Send, X, Minimize2, Maximize2, Award, Zap } from 'lucide-react'
import axios from 'axios'

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hey there! 👋 I'm your personal career sidekick! I'm here to help you crush your resume, ace interviews, and land your dream job. Ready to level up? 🚀",
      sender: 'bot',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [points, setPoints] = useState(0)
  const [streak, setStreak] = useState(0)
  const [level, setLevel] = useState(1)
  const [badges, setBadges] = useState([])
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Gamification logic
  const addPoints = (amount = 10) => {
    const newPoints = points + amount
    setPoints(newPoints)
    
    // Level up every 100 points
    if (newPoints % 100 === 0) {
      setLevel(Math.floor(newPoints / 100) + 1)
      addBadge('levelup')
    }
  }

  const addBadge = (type) => {
    const badgeList = {
      first_chat: { name: '🎯 First Step', description: 'Had your first chat' },
      curious: { name: '🤔 Curious Mind', description: 'Asked 5 questions' },
      interview_pro: { name: '🎤 Interview Ready', description: 'Asked interview tips' },
      resume_master: { name: '📄 Resume Master', description: 'Asked about resume improvements' },
      levelup: { name: '⬆️ Level Up', description: 'Reached a new level' },
      streak_5: { name: '🔥 On Fire', description: 'Maintained 5-message streak' },
    }
    
    if (badgeList[type] && !badges.find(b => b.type === type)) {
      setBadges([...badges, { type, ...badgeList[type] }])
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    const userInput = input
    setInput('')
    setLoading(true)

    // Add points for sending message
    addPoints(5)
    
    // Track streak
    setStreak(streak + 1)
    if (streak >= 5) {
      addBadge('streak_5')
    }

    // Check for badges based on questions
    if (userInput.toLowerCase().includes('interview')) {
      addBadge('interview_pro')
    }
    if (userInput.toLowerCase().includes('resume')) {
      addBadge('resume_master')
    }
    if (messages.length >= 5) {
      addBadge('curious')
    }
    if (messages.length === 1) {
      addBadge('first_chat')
    }

    try {
      const response = await axios.post(
        '/api/chat',
        {
          messages: [
            ...messages.map((msg) => ({
              role: msg.sender === 'user' ? 'user' : 'assistant',
              content: msg.text,
            })),
            { role: 'user', content: userInput },
          ],
        }
      )

      const botMessage = {
        id: messages.length + 2,
        text: response.data.reply,
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
      addPoints(15) // Bonus points for getting a response
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        id: messages.length + 2,
        text: 'Oops! I hit a snag. 😅 Let me catch my breath and try again in a moment!',
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full shadow-lg hover:shadow-xl transition transform hover:scale-110 flex items-center justify-center z-50 text-2xl relative"
        title="Chat with AI Career Coach"
      >
        🤖
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold animate-pulse">
          {level}
        </span>
      </button>
    )
  }

  return (
    <div
      className={`fixed bottom-6 right-6 w-96 bg-gradient-to-b from-purple-50 to-pink-50 rounded-lg shadow-2xl z-50 flex flex-col transition-all border-2 border-purple-200 ${
        isMinimized ? 'h-20' : 'h-[680px]'
      }`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div>
          <h3 className="font-bold text-lg flex items-center gap-2">
            🤖 AI Career Coach
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">Level {level}</span>
          </h3>
          <p className="text-xs text-purple-100">Your AI Career Coach 🎯</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="hover:bg-white/20 p-1 rounded transition"
          >
            {isMinimized ? <Maximize2 size={18} /> : <Minimize2 size={18} />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-white/20 p-1 rounded transition"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Stats Bar */}
          <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-3 flex justify-around border-b-2 border-purple-200">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 font-bold text-purple-700">
                <Zap size={16} />
                {points}
              </div>
              <p className="text-xs text-gray-600">Points</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 font-bold text-red-600">
                <span className="text-lg">🔥</span>
                {streak}
              </div>
              <p className="text-xs text-gray-600">Streak</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 font-bold text-yellow-600">
                <Award size={16} />
                {badges.length}
              </div>
              <p className="text-xs text-gray-600">Badges</p>
            </div>
          </div>

          {/* Badges Display */}
          {badges.length > 0 && (
            <div className="bg-purple-50 p-2 border-b border-purple-200 overflow-x-auto">
              <div className="flex gap-2">
                {badges.map((badge) => (
                  <div
                    key={badge.type}
                    className="flex-shrink-0 text-center p-2 bg-white rounded-lg border-2 border-yellow-400 shadow-sm hover:shadow-md transition cursor-help"
                    title={badge.description}
                  >
                    <div className="text-xl">{badge.name.split(' ')[0]}</div>
                    <p className="text-xs text-gray-600 whitespace-nowrap">{badge.name.split(' ')[1]}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div
                  className={`max-w-xs p-3 rounded-lg ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-br-none'
                      : 'bg-white text-gray-800 border-2 border-purple-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border-2 border-purple-200 text-gray-800 p-3 rounded-lg rounded-bl-none shadow-sm">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t-2 border-purple-200 p-4 bg-white rounded-b-lg flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything... +5 points! 🎁"
              className="flex-1 border-2 border-purple-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 transition"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 text-white p-2 rounded-lg transition transform hover:scale-105 active:scale-95"
            >
              <Send size={20} />
            </button>
          </div>
        </>
      )}
    </div>
  )
}
