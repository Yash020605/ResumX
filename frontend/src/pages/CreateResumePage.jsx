import React, { useState } from 'react'
import { useAnalysisStore } from '../store/analysisStore'
import { ChatBot } from '../components/ChatBot'
import ResumeTemplate from '../components/ResumeTemplate'
import axios from 'axios'

// ── 12 questions covering every resume section ────────────────────────────────
const QUESTIONS = [
  {
    key:         'name',
    label:       'Full Name',
    icon:        '👤',
    placeholder: 'e.g. Yash Limbhore',
    tip:         'Use your full legal name as it appears on official documents.',
    rows:        1,
  },
  {
    key:         'contact',
    label:       'Contact Details',
    icon:        '📬',
    placeholder: 'Email: yash@example.com\nPhone: +91 XXXXX XXXXX\nLinkedIn: linkedin.com/in/yash\nGitHub: github.com/yash',
    tip:         'Include LinkedIn and GitHub — recruiters check them before calling.',
    rows:        4,
  },
  {
    key:         'summary',
    label:       'Professional Summary',
    icon:        '✍️',
    placeholder: 'e.g. Final-year B.Tech CS student with hands-on experience building AI agents and full-stack web apps. Passionate about LLMs and autonomous systems.',
    tip:         '2-3 sentences. Mention your domain, key strength, and career goal. This is the first thing recruiters read.',
    rows:        3,
  },
  {
    key:         'education',
    label:       'Education',
    icon:        '🎓',
    placeholder: 'B.Tech Computer Science — ADYPU, Pune (2021–2025) — CGPA: 8.2/10\n12th — XYZ School (2021) — 88%',
    tip:         'List most recent first. Include degree, institution, year, and CGPA/percentage.',
    rows:        3,
  },
  {
    key:         'skills',
    label:       'Technical Skills',
    icon:        '⚙️',
    placeholder: 'Languages: Python, JavaScript, SQL\nFrameworks: FastAPI, React, LangChain, LangGraph\nTools: Docker, Git, Postman, VS Code\nDatabases: PostgreSQL, MongoDB, FAISS\nCloud: AWS basics, Vercel',
    tip:         'Group by category. Only list skills you can confidently discuss in an interview.',
    rows:        5,
  },
  {
    key:         'experience',
    label:       'Work Experience / Internships',
    icon:        '💼',
    placeholder: 'AI Engineer Intern — TechCorp, Pune (Jun–Aug 2024)\n• Built a multi-agent RAG pipeline using LangGraph, reducing query time by 40%\n• Integrated Groq API for real-time LLM inference\n• Deployed FastAPI backend on AWS EC2\n\nNo experience? Write "Fresher" and focus on projects.',
    tip:         'Use bullet points starting with action verbs. Add numbers/impact wherever possible.',
    rows:        6,
  },
  {
    key:         'projects',
    label:       'Projects',
    icon:        '🚀',
    placeholder: 'ResumX — AI Career Platform (Python, LangGraph, React, Groq)\n• 5-agent pipeline: analyzer, career, improvement, project, interview\n• 26-key Groq pool with auto-rotation and Gemini fallback\n• GitHub: github.com/yash/resumx\n\nStudent Portal — Flask + React + MySQL\n• Role-based auth, REST API, deployed on Heroku',
    tip:         'Include tech stack, what it does, and a measurable outcome or GitHub link.',
    rows:        7,
  },
  {
    key:         'achievements',
    label:       'Achievements & Awards',
    icon:        '🏆',
    placeholder: '• 1st place — Smart India Hackathon 2024 (AI track)\n• Top 10 — Google Solution Challenge 2024\n• Published paper: "Autonomous AI Agents for Resume Analysis" — IEEE 2024\n• 5-star Python on HackerRank',
    tip:         'Hackathons, competitions, publications, rankings — these stand out to recruiters.',
    rows:        4,
  },
  {
    key:         'certifications',
    label:       'Certifications & Courses',
    icon:        '📜',
    placeholder: '• AWS Cloud Practitioner (2024)\n• Deep Learning Specialization — Coursera (Andrew Ng)\n• LangChain for LLM Application Development — DeepLearning.AI\n• Google Data Analytics Certificate',
    tip:         'Include the issuing body and year. Online certs from Coursera/Google/AWS count.',
    rows:        4,
  },
  {
    key:         'softskills',
    label:       'Soft Skills & Languages',
    icon:        '🤝',
    placeholder: 'Soft Skills: Problem-solving, Team leadership, Communication, Adaptability\nLanguages: English (Fluent), Hindi (Native), Marathi (Conversational)',
    tip:         'Keep soft skills concise. Language proficiency is important for global roles.',
    rows:        3,
  },
  {
    key:         'extracurricular',
    label:       'Extra-Curricular & Volunteering',
    icon:        '🌟',
    placeholder: '• Technical Head — GDSC ADYPU (2023–24): organized 5 workshops, 200+ attendees\n• Mentor — Code for Good NGO: taught Python to 30 underprivileged students\n• Core member — Robotics Club',
    tip:         'Leadership roles and community work show initiative beyond academics.',
    rows:        4,
  },
  {
    key:         'goal',
    label:       'Target Role & Career Goal',
    icon:        '🎯',
    placeholder: 'Target Role: Agentic AI Engineer / Backend Developer\nTarget Companies: Google, Microsoft, Razorpay, Zepto, any AI-first startup\nGoal: Build production-grade AI systems that solve real-world problems at scale.',
    tip:         'Be specific. This shapes how the AI tailors your entire resume.',
    rows:        3,
  },
]

// ── AI-powered resume builder ─────────────────────────────────────────────────
async function buildResumeWithAI(answers) {
  const sections = QUESTIONS.map(q => `### ${q.label}\n${answers[q.key] || 'Not provided'}`).join('\n\n')
  try {
    const res = await axios.post('/api/chat', {
      messages: [
        {
          role: 'system',
          content: `You are a professional resume writer. Generate a clean, ATS-optimized resume in plain text format.
Use this structure:
[NAME]
[CONTACT]

PROFESSIONAL SUMMARY
[2-3 sentences]

EDUCATION
[entries]

TECHNICAL SKILLS
[grouped by category]

WORK EXPERIENCE
[entries with bullet points]

PROJECTS
[entries with bullet points]

ACHIEVEMENTS & AWARDS
[bullet points]

CERTIFICATIONS
[list]

SOFT SKILLS & LANGUAGES
[brief]

EXTRA-CURRICULAR
[brief]

CAREER OBJECTIVE
[1-2 sentences]

Rules: Plain text only. No markdown. Use bullet points with •. Keep it professional and concise.`,
        },
        {
          role: 'user',
          content: `Build a professional resume from this information:\n\n${sections}`,
        },
      ],
    })
    return res.data.reply || buildResumeFallback(answers)
  } catch {
    return buildResumeFallback(answers)
  }
}

function buildResumeFallback(a) {
  return `${a.name || 'Your Name'}
${a.contact || ''}

PROFESSIONAL SUMMARY
${a.summary || ''}

EDUCATION
${a.education || ''}

TECHNICAL SKILLS
${a.skills || ''}

WORK EXPERIENCE
${a.experience || 'Fresher – focused on projects and academics.'}

PROJECTS
${a.projects || ''}

ACHIEVEMENTS & AWARDS
${a.achievements || ''}

CERTIFICATIONS
${a.certifications || ''}

SOFT SKILLS & LANGUAGES
${a.softskills || ''}

EXTRA-CURRICULAR
${a.extracurricular || ''}

CAREER OBJECTIVE
${a.goal || ''}`.trim()
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function CreateResumePage({ onDone, onBack }) {
  const [step, setStep]         = useState(0)
  const [answers, setAnswers]   = useState({})
  const [current, setCurrent]   = useState('')
  const [building, setBuilding] = useState(false)
  const [builtResume, setBuiltResume] = useState(null)
  const store                   = useAnalysisStore()

  const q      = QUESTIONS[step]
  const isLast = step === QUESTIONS.length - 1
  const pct    = Math.round((step / QUESTIONS.length) * 100)

  const goNext = async () => {
    const updated = { ...answers, [q.key]: current }
    setAnswers(updated)
    setCurrent('')

    if (isLast) {
      setBuilding(true)
      const resume = await buildResumeWithAI(updated)
      store.setResume(resume)
      setBuilding(false)
      setBuiltResume(resume)   // show template instead of going straight to analyze
    } else {
      setStep(s => s + 1)
    }
  }

  const goBack = () => {
    setStep(s => s - 1)
    setCurrent(answers[QUESTIONS[step - 1].key] || '')
  }

  const skip = () => {
    setAnswers(a => ({ ...a, [q.key]: '' }))
    setCurrent('')
    setStep(s => s + 1)
  }

  const chatContext = `User is building their resume on step ${step + 1}/${QUESTIONS.length}: "${q.label}". Give specific advice for this section.`

  // Show the MNC resume template after building
  if (builtResume) return (
    <ResumeTemplate
      resumeText={builtResume}
      onBack={() => onDone(builtResume)}
    />
  )

  if (building) return (    <div className="min-h-screen bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700 flex items-center justify-center">
      <div className="text-center text-white">
        <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-6" />
        <p className="text-2xl font-black mb-2">Building your resume…</p>
        <p className="text-violet-200 text-sm">AI is crafting a professional resume from your answers</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700 flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-xl">

        {/* Top bar */}
        <div className="flex items-center justify-between px-7 pt-6 pb-0">
          <button onClick={onBack} className="text-gray-400 hover:text-gray-600 text-sm transition">← Back</button>
          <span className="text-xs text-gray-400 font-semibold">{step + 1} / {QUESTIONS.length}</span>
        </div>

        {/* Progress */}
        <div className="px-7 pt-4 pb-0">
          <div className="w-full bg-gray-100 rounded-full h-1.5">
            <div className="bg-gradient-to-r from-violet-500 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${pct}%` }} />
          </div>
          {/* Step dots */}
          <div className="flex justify-between mt-2 px-0.5">
            {QUESTIONS.map((_, i) => (
              <div key={i} className={`w-1.5 h-1.5 rounded-full transition-all duration-300
                ${i < step ? 'bg-violet-500' : i === step ? 'bg-indigo-500 scale-150' : 'bg-gray-200'}`} />
            ))}
          </div>
        </div>

        {/* Logo */}
        <div className="text-center pt-5 pb-2">
          <span className="text-xl font-black bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent">
            ResumX Creator
          </span>
        </div>

        {/* Question */}
        <div className="px-7 pb-6 pt-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">{q.icon}</span>
            <label className="text-base font-black text-gray-800">{q.label}</label>
          </div>

          <p className="text-xs text-violet-600 bg-violet-50 rounded-xl px-3 py-2 mb-3 border border-violet-100 leading-relaxed">
            💡 {q.tip}
          </p>

          <textarea
            autoFocus
            rows={q.rows || 2}
            value={current}
            onChange={e => setCurrent(e.target.value)}
            placeholder={q.placeholder}
            onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) goNext() }}
            className="w-full border-2 border-gray-200 focus:border-violet-400 rounded-xl px-4 py-3
              text-sm text-gray-700 resize-none focus:outline-none transition leading-relaxed"
          />
          <p className="text-[10px] text-gray-300 mt-1">Ctrl+Enter to continue</p>

          {/* Buttons */}
          <div className="flex gap-3 mt-4">
            {step > 0 && (
              <button onClick={goBack}
                className="flex-1 py-3 border-2 border-gray-200 text-gray-600 font-semibold rounded-xl hover:bg-gray-50 text-sm transition">
                ← Back
              </button>
            )}
            <button onClick={goNext}
              className="flex-1 py-3 bg-gradient-to-r from-violet-600 to-indigo-500 text-white font-bold rounded-xl hover:opacity-90 text-sm shadow transition">
              {isLast ? '✨ Build My Resume with AI' : 'Next →'}
            </button>
          </div>

          {!isLast && (
            <button onClick={skip} className="w-full mt-2 text-xs text-gray-400 hover:text-gray-600 transition">
              Skip this step
            </button>
          )}
        </div>
      </div>

      <ChatBot context={chatContext} />
    </div>
  )
}
