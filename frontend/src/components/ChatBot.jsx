import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const SUGGESTIONS = [
  'How do I improve my resume?',
  'What skills should I learn next?',
  'How to prepare for interviews?',
  'What salary should I expect?',
]

const INIT_MSG = {
  id: 0,
  role: 'bot',
  text: "Hi! I'm your ResumX career coach. Ask me anything about your resume, interviews, or career path. 🚀",
}

export const ChatBot = ({ context = '' }) => {
  const [open, setOpen]       = useState(false)
  const [msgs, setMsgs]       = useState([INIT_MSG])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef             = useRef(null)
  const inputRef              = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, open])

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100)
  }, [open])

  const send = async (text) => {
    const q = (text || input).trim()
    if (!q) return
    setInput('')
    setMsgs((m) => [...m, { id: Date.now(), role: 'user', text: q }])
    setLoading(true)
    try {
      const history = msgs.map((m) => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }))
      if (context) history.unshift({ role: 'system', content: `Context: ${context}` })
      history.push({ role: 'user', content: q })
      const res = await axios.post('/api/chat', { messages: history })
      setMsgs((m) => [...m, { id: Date.now() + 1, role: 'bot', text: res.data.reply }])
    } catch {
      setMsgs((m) => [...m, { id: Date.now() + 1, role: 'bot', text: "Sorry, I couldn't connect. Please try again." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* FAB */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-br from-violet-600 to-indigo-500
            text-white rounded-full shadow-xl hover:shadow-2xl hover:scale-110 transition-all duration-200
            flex items-center justify-center text-2xl"
          title="Career Coach"
        >
          💬
        </button>
      )}

      {/* Chat window */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-[360px] flex flex-col rounded-2xl shadow-2xl
          border border-gray-200 bg-white overflow-hidden"
          style={{ height: '520px' }}>

          {/* Header */}
          <div className="bg-gradient-to-r from-violet-600 to-indigo-500 px-4 py-3 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-base">🤖</div>
              <div>
                <p className="text-white font-bold text-sm leading-none">ResumX Coach</p>
                <p className="text-violet-200 text-[10px]">Always here to help</p>
              </div>
            </div>
            <button onClick={() => setOpen(false)}
              className="text-white/70 hover:text-white transition text-xl leading-none">×</button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-gray-50">
            {msgs.map((m) => (
              <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.role === 'bot' && (
                  <div className="w-6 h-6 rounded-full bg-violet-100 flex items-center justify-center text-xs mr-2 flex-shrink-0 mt-0.5">🤖</div>
                )}
                <div className={`max-w-[75%] px-3 py-2 rounded-2xl text-sm leading-relaxed
                  ${m.role === 'user'
                    ? 'bg-gradient-to-br from-violet-600 to-indigo-500 text-white rounded-br-sm'
                    : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-bl-sm'}`}>
                  {m.text}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="w-6 h-6 rounded-full bg-violet-100 flex items-center justify-center text-xs mr-2 flex-shrink-0">🤖</div>
                <div className="bg-white border border-gray-100 shadow-sm px-4 py-3 rounded-2xl rounded-bl-sm">
                  <div className="flex gap-1.5 items-center">
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick suggestions — only show when just the init message */}
          {msgs.length === 1 && (
            <div className="px-3 py-2 flex gap-2 flex-wrap border-t border-gray-100 bg-white flex-shrink-0">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)}
                  className="text-[11px] px-2.5 py-1 bg-violet-50 text-violet-700 rounded-full
                    border border-violet-200 hover:bg-violet-100 transition font-medium">
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="px-3 py-3 border-t border-gray-100 bg-white flex gap-2 flex-shrink-0">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask anything…"
              disabled={loading}
              className="flex-1 text-sm px-3 py-2 rounded-xl border border-gray-200
                focus:outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-200
                bg-gray-50 transition disabled:opacity-50"
            />
            <button
              onClick={() => send()}
              disabled={loading || !input.trim()}
              className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-500
                text-white flex items-center justify-center hover:opacity-90
                disabled:opacity-40 transition flex-shrink-0">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  )
}
