import React from 'react'

// ── Shared resume parser ──────────────────────────────────────────────────────
export function parseResume(text) {
  const lines = (text || '').split('\n').map(l => l.trim()).filter(Boolean)

  const get = (header) => {
    const idx = lines.findIndex(l => l.toUpperCase().includes(header.toUpperCase()))
    if (idx === -1) return []
    const next = lines.findIndex((l, i) => i > idx && /^[A-Z\s]{4,}$/.test(l))
    return lines.slice(idx + 1, next === -1 ? undefined : next)
  }

  const name    = lines[0] || ''
  const contact = lines.slice(1, 4).filter(l =>
    l.includes('@') || l.includes('+') || l.includes('linkedin') ||
    l.includes('github') || l.includes('http')
  )
  const summary =
    get('PROFESSIONAL SUMMARY').join(' ') ||
    get('SUMMARY').join(' ') ||
    get('OBJECTIVE').join(' ')

  const parseTimeline = (sectionLines) => {
    const entries = []
    let cur = null
    sectionLines.forEach(l => {
      if (l.startsWith('•') || l.startsWith('-') || l.startsWith('·')) {
        if (cur) cur.bullets.push(l.replace(/^[•\-·]\s*/, ''))
      } else if (
        /\d{4}/.test(l) ||
        /intern|engineer|developer|manager|analyst|lead|head|officer/i.test(l)
      ) {
        if (cur) entries.push(cur)
        cur = { dates: '', location: '', role: l, company: '', bullets: [] }
      } else if (cur && !cur.company && l.length < 60) {
        cur.company = l
      } else if (cur) {
        cur.bullets.push(l)
      } else {
        cur = { dates: '', location: '', role: l, company: '', bullets: [] }
      }
    })
    if (cur) entries.push(cur)
    return entries
  }

  const expLines  = get('WORK EXPERIENCE').length  ? get('WORK EXPERIENCE')  :
                    get('PROFESSIONAL EXPERIENCE').length ? get('PROFESSIONAL EXPERIENCE') :
                    get('EXPERIENCE')
  const projLines = get('PROJECTS')
  const eduLines  = get('EDUCATION')
  const skillsRaw = (get('TECHNICAL SKILLS').length ? get('TECHNICAL SKILLS') : get('SKILLS')).join(' ')
  const skills    = skillsRaw
    .split(/[,|•\n]/)
    .map(s => s.replace(/^[A-Za-z\s]+:/, '').trim())
    .filter(s => s.length > 1 && s.length < 35)
  const achLines  = get('ACHIEVEMENTS').length ? get('ACHIEVEMENTS') :
                    get('KEY ACHIEVEMENTS').length ? get('KEY ACHIEVEMENTS') : get('AWARDS')
  const certLines = get('CERTIFICATIONS').length ? get('CERTIFICATIONS') : get('CERTIFICATIONS & COURSES')
  const extraLines = get('EXTRA-CURRICULAR').length ? get('EXTRA-CURRICULAR') :
                     get('EXTRACURRICULAR').length ? get('EXTRACURRICULAR') : get('VOLUNTEERING')

  return {
    name, contact, summary,
    experience:     parseTimeline(expLines),
    projects:       parseTimeline(projLines),
    education:      parseTimeline(eduLines),
    skills,
    achievements:   achLines.map(l => l.replace(/^[•\-·]\s*/, '')).filter(Boolean),
    certifications: certLines.map(l => l.replace(/^[•\-·]\s*/, '')).filter(Boolean),
    extra:          extraLines.map(l => l.replace(/^[•\-·]\s*/, '')).filter(Boolean),
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 1 — TemplateTeal  (existing teal timeline style)
// ═══════════════════════════════════════════════════════════════════════════════
const TEAL = '#1a6b8a'

function TealSection({ title, children }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{
        fontSize: 13, fontWeight: 800, letterSpacing: 1.5,
        textTransform: 'uppercase', color: '#1a1a2e',
        borderBottom: `2px solid ${TEAL}`, paddingBottom: 3, marginBottom: 10,
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function TealTimelineRow({ dates, location, role, company, bullets = [] }) {
  return (
    <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
      <div style={{ minWidth: 90, maxWidth: 90, fontSize: 10.5, color: '#555', lineHeight: 1.5 }}>
        <div style={{ fontWeight: 600 }}>{dates}</div>
        <div>{location}</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 3 }}>
        <div style={{ width: 7, height: 7, borderRadius: '50%', background: TEAL, flexShrink: 0 }} />
        {bullets.length > 0 && <div style={{ width: 1, flex: 1, background: '#ddd', marginTop: 3 }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#1a1a2e' }}>{role}</div>
        {company && <div style={{ fontSize: 12, fontWeight: 600, color: TEAL, marginBottom: 4 }}>{company}</div>}
        {bullets.map((b, i) => (
          <div key={i} style={{ fontSize: 11, color: '#333', lineHeight: 1.55, display: 'flex', gap: 6, marginBottom: 2 }}>
            <span style={{ color: TEAL, flexShrink: 0 }}>·</span>
            <span>{b}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function TemplateTeal({ resumeText }) {
  const data = parseResume(resumeText)
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '36px 44px', fontSize: 11, color: '#1a1a2e', lineHeight: 1.5, background: '#fff' }}>
      {/* Header */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 30, fontWeight: 900, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 2 }}>
          {data.name || 'YOUR NAME'}
        </div>
        {data.summary && (
          <div style={{ color: TEAL, fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
            {data.summary.split('.')[0]}
          </div>
        )}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 20px', fontSize: 10.5, color: '#555' }}>
          {data.contact.map((c, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ color: TEAL }}>{c.includes('@') ? '✉' : c.includes('+') ? '📞' : '🔗'}</span>
              {c}
            </span>
          ))}
        </div>
      </div>

      {data.summary && (
        <TealSection title="Summary">
          <p style={{ fontSize: 11, color: '#333', lineHeight: 1.65 }}>{data.summary}</p>
        </TealSection>
      )}

      {data.achievements.length > 0 && (
        <TealSection title="Key Achievements">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
            {data.achievements.slice(0, 6).map((a, i) => (
              <div key={i} style={{ borderLeft: `3px solid ${TEAL}`, paddingLeft: 8 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: TEAL, marginBottom: 2 }}>{a.split('—')[0]}</div>
                <div style={{ fontSize: 10.5, color: '#555' }}>{a.split('—')[1] || ''}</div>
              </div>
            ))}
          </div>
        </TealSection>
      )}

      {data.experience.length > 0 && (
        <TealSection title="Professional Experience">
          {data.experience.map((e, i) => <TealTimelineRow key={i} {...e} />)}
        </TealSection>
      )}

      {data.projects.length > 0 && (
        <TealSection title="Projects">
          {data.projects.map((p, i) => <TealTimelineRow key={i} {...p} />)}
        </TealSection>
      )}

      {data.education.length > 0 && (
        <TealSection title="Education">
          {data.education.map((e, i) => <TealTimelineRow key={i} {...e} />)}
        </TealSection>
      )}

      {data.skills.length > 0 && (
        <TealSection title="Technical Skills">
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {data.skills.map((s, i) => (
              <span key={i} style={{
                border: '1px solid #bbb', borderRadius: 3, padding: '2px 8px',
                fontSize: 10.5, color: '#333', marginRight: 5, marginBottom: 5,
                display: 'inline-block', background: '#fafafa',
              }}>{s}</span>
            ))}
          </div>
        </TealSection>
      )}

      {data.certifications.length > 0 && (
        <TealSection title="Certifications">
          {data.certifications.map((c, i) => (
            <div key={i} style={{ fontSize: 11, color: '#333', marginBottom: 3, display: 'flex', gap: 6 }}>
              <span style={{ color: TEAL }}>·</span>{c}
            </div>
          ))}
        </TealSection>
      )}

      {data.extra.length > 0 && (
        <TealSection title="Extra-Curricular & Volunteering">
          {data.extra.map((e, i) => (
            <div key={i} style={{ fontSize: 11, color: '#333', marginBottom: 3, display: 'flex', gap: 6 }}>
              <span style={{ color: TEAL }}>·</span>{e}
            </div>
          ))}
        </TealSection>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 2 — TemplateClassic  (Google / McKinsey — clean black & white serif)
// ═══════════════════════════════════════════════════════════════════════════════
function ClassicSection({ title, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        fontSize: 11, fontWeight: 700, letterSpacing: 1.2,
        textTransform: 'uppercase', color: '#000',
        borderBottom: '1.5px solid #000', paddingBottom: 2, marginBottom: 8,
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function ClassicEntry({ role, company, bullets = [] }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: '#000' }}>{role}</div>
      {company && <div style={{ fontSize: 11, color: '#333', marginBottom: 3, fontStyle: 'italic' }}>{company}</div>}
      {bullets.map((b, i) => (
        <div key={i} style={{ fontSize: 11, color: '#222', lineHeight: 1.55, display: 'flex', gap: 8, marginBottom: 2 }}>
          <span style={{ flexShrink: 0 }}>•</span>
          <span>{b}</span>
        </div>
      ))}
    </div>
  )
}

export function TemplateClassic({ resumeText }) {
  const data = parseResume(resumeText)
  return (
    <div style={{
      fontFamily: 'Georgia, "Times New Roman", serif',
      padding: '40px 48px', fontSize: 11, color: '#000',
      lineHeight: 1.55, background: '#fff',
    }}>
      {/* Header */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 22, fontWeight: 700, color: '#000', marginBottom: 4 }}>
          {data.name || 'YOUR NAME'}
        </div>
        <hr style={{ border: 'none', borderTop: '1px solid #000', margin: '4px 0 6px' }} />
        <div style={{ fontSize: 10.5, color: '#333', display: 'flex', flexWrap: 'wrap', gap: '0 18px' }}>
          {data.contact.map((c, i) => <span key={i}>{c}</span>)}
        </div>
      </div>

      {data.summary && (
        <ClassicSection title="Professional Summary">
          <p style={{ fontSize: 11, color: '#222', lineHeight: 1.65 }}>{data.summary}</p>
        </ClassicSection>
      )}

      {data.experience.length > 0 && (
        <ClassicSection title="Work Experience">
          {data.experience.map((e, i) => <ClassicEntry key={i} {...e} />)}
        </ClassicSection>
      )}

      {data.projects.length > 0 && (
        <ClassicSection title="Projects">
          {data.projects.map((p, i) => <ClassicEntry key={i} {...p} />)}
        </ClassicSection>
      )}

      {data.education.length > 0 && (
        <ClassicSection title="Education">
          {data.education.map((e, i) => <ClassicEntry key={i} {...e} />)}
        </ClassicSection>
      )}

      {data.skills.length > 0 && (
        <ClassicSection title="Technical Skills">
          <p style={{ fontSize: 11, color: '#222', lineHeight: 1.7 }}>
            {data.skills.join(', ')}
          </p>
        </ClassicSection>
      )}

      {data.achievements.length > 0 && (
        <ClassicSection title="Achievements">
          {data.achievements.map((a, i) => (
            <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8 }}>
              <span>•</span><span>{a}</span>
            </div>
          ))}
        </ClassicSection>
      )}

      {data.certifications.length > 0 && (
        <ClassicSection title="Certifications">
          {data.certifications.map((c, i) => (
            <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8 }}>
              <span>•</span><span>{c}</span>
            </div>
          ))}
        </ClassicSection>
      )}

      {data.extra.length > 0 && (
        <ClassicSection title="Extra-Curricular">
          {data.extra.map((e, i) => (
            <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8 }}>
              <span>•</span><span>{e}</span>
            </div>
          ))}
        </ClassicSection>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 3 — TemplateModern  (Microsoft / Amazon — two-column navy sidebar)
// ═══════════════════════════════════════════════════════════════════════════════
const NAVY  = '#1e293b'
const SKY   = '#38bdf8'

function SidebarSection({ title, children }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{
        fontSize: 9, fontWeight: 700, letterSpacing: 1.5,
        textTransform: 'uppercase', color: '#fff',
        borderBottom: `2px solid ${SKY}`, paddingBottom: 3, marginBottom: 8,
        fontVariant: 'small-caps',
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function MainSection({ title, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        fontSize: 12, fontWeight: 700, color: NAVY,
        borderLeft: `3px solid ${SKY}`, paddingLeft: 8, marginBottom: 8,
        textTransform: 'uppercase', letterSpacing: 0.8,
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function ModernEntry({ role, company, bullets = [] }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: NAVY }}>{role}</div>
      {company && <div style={{ fontSize: 11, color: SKY, marginBottom: 3, fontWeight: 600 }}>{company}</div>}
      {bullets.map((b, i) => (
        <div key={i} style={{ fontSize: 10.5, color: '#334155', lineHeight: 1.55, display: 'flex', gap: 6, marginBottom: 2 }}>
          <span style={{ color: SKY, flexShrink: 0 }}>▸</span>
          <span>{b}</span>
        </div>
      ))}
    </div>
  )
}

export function TemplateModern({ resumeText }) {
  const data = parseResume(resumeText)
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', fontSize: 11, color: '#1a1a2e', lineHeight: 1.5, background: '#fff', display: 'flex', minHeight: 900 }}>
      {/* Sidebar */}
      <div style={{ width: '30%', background: NAVY, color: '#fff', padding: '36px 20px', flexShrink: 0 }}>
        {/* Name */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 20, fontWeight: 900, color: '#fff', letterSpacing: 0.5, lineHeight: 1.2, marginBottom: 6 }}>
            {data.name || 'YOUR NAME'}
          </div>
          {data.summary && (
            <div style={{ fontSize: 10, color: '#94a3b8', lineHeight: 1.5 }}>
              {data.summary.split('.')[0]}
            </div>
          )}
        </div>

        {/* Contact */}
        {data.contact.length > 0 && (
          <SidebarSection title="Contact">
            {data.contact.map((c, i) => (
              <div key={i} style={{ fontSize: 10, color: '#cbd5e1', marginBottom: 4, wordBreak: 'break-all' }}>{c}</div>
            ))}
          </SidebarSection>
        )}

        {/* Skills */}
        {data.skills.length > 0 && (
          <SidebarSection title="Skills">
            {data.skills.map((s, i) => (
              <div key={i} style={{
                fontSize: 10, color: '#e2e8f0', marginBottom: 4,
                borderLeft: `2px solid ${SKY}`, paddingLeft: 6,
              }}>{s}</div>
            ))}
          </SidebarSection>
        )}

        {/* Certifications */}
        {data.certifications.length > 0 && (
          <SidebarSection title="Certifications">
            {data.certifications.map((c, i) => (
              <div key={i} style={{ fontSize: 10, color: '#cbd5e1', marginBottom: 4 }}>· {c}</div>
            ))}
          </SidebarSection>
        )}

        {/* Achievements */}
        {data.achievements.length > 0 && (
          <SidebarSection title="Achievements">
            {data.achievements.map((a, i) => (
              <div key={i} style={{ fontSize: 10, color: '#cbd5e1', marginBottom: 4 }}>· {a}</div>
            ))}
          </SidebarSection>
        )}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, padding: '36px 32px', background: '#fff' }}>
        {data.summary && (
          <MainSection title="Summary">
            <p style={{ fontSize: 11, color: '#334155', lineHeight: 1.65 }}>{data.summary}</p>
          </MainSection>
        )}

        {data.experience.length > 0 && (
          <MainSection title="Experience">
            {data.experience.map((e, i) => <ModernEntry key={i} {...e} />)}
          </MainSection>
        )}

        {data.projects.length > 0 && (
          <MainSection title="Projects">
            {data.projects.map((p, i) => <ModernEntry key={i} {...p} />)}
          </MainSection>
        )}

        {data.education.length > 0 && (
          <MainSection title="Education">
            {data.education.map((e, i) => <ModernEntry key={i} {...e} />)}
          </MainSection>
        )}

        {data.extra.length > 0 && (
          <MainSection title="Extra-Curricular">
            {data.extra.map((e, i) => (
              <div key={i} style={{ fontSize: 11, color: '#334155', marginBottom: 3, display: 'flex', gap: 6 }}>
                <span style={{ color: SKY }}>▸</span><span>{e}</span>
              </div>
            ))}
          </MainSection>
        )}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 4 — TemplateMinimal  (Apple / Stripe / startup — ultra-minimal)
// ═══════════════════════════════════════════════════════════════════════════════
const INDIGO = '#6366f1'

function MinimalSection({ title, children }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{
        fontSize: 10, fontWeight: 700, letterSpacing: 3,
        textTransform: 'uppercase', color: INDIGO, marginBottom: 12,
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function MinimalEntry({ role, company, bullets = [] }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#111', marginBottom: 1 }}>{role}</div>
      {company && <div style={{ fontSize: 11, color: '#6b7280', marginBottom: 5 }}>{company}</div>}
      {bullets.map((b, i) => (
        <div key={i} style={{ fontSize: 11, color: '#374151', lineHeight: 1.65, display: 'flex', gap: 8, marginBottom: 3 }}>
          <span style={{ color: INDIGO, flexShrink: 0 }}>—</span>
          <span>{b}</span>
        </div>
      ))}
    </div>
  )
}

export function TemplateMinimal({ resumeText }) {
  const data = parseResume(resumeText)
  return (
    <div style={{
      fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
      padding: '48px 56px', fontSize: 11, color: '#111',
      lineHeight: 1.6, background: '#fff',
    }}>
      {/* Header */}
      <div style={{ marginBottom: 36 }}>
        <div style={{ fontSize: 28, fontWeight: 300, color: '#111', letterSpacing: -0.5, marginBottom: 8 }}>
          {(data.name || 'your name').toLowerCase()}
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 20px', fontSize: 10.5, color: '#6b7280' }}>
          {data.contact.map((c, i) => <span key={i}>{c}</span>)}
        </div>
      </div>

      {data.summary && (
        <MinimalSection title="About">
          <p style={{ fontSize: 12, color: '#374151', lineHeight: 1.75, fontWeight: 300 }}>{data.summary}</p>
        </MinimalSection>
      )}

      {data.experience.length > 0 && (
        <MinimalSection title="Experience">
          {data.experience.map((e, i) => <MinimalEntry key={i} {...e} />)}
        </MinimalSection>
      )}

      {data.projects.length > 0 && (
        <MinimalSection title="Projects">
          {data.projects.map((p, i) => <MinimalEntry key={i} {...p} />)}
        </MinimalSection>
      )}

      {data.education.length > 0 && (
        <MinimalSection title="Education">
          {data.education.map((e, i) => <MinimalEntry key={i} {...e} />)}
        </MinimalSection>
      )}

      {data.skills.length > 0 && (
        <MinimalSection title="Skills">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {data.skills.map((s, i) => (
              <span key={i} style={{
                border: `1px solid ${INDIGO}`, borderRadius: 20,
                padding: '3px 12px', fontSize: 10.5, color: INDIGO,
                display: 'inline-block',
              }}>{s}</span>
            ))}
          </div>
        </MinimalSection>
      )}

      {data.achievements.length > 0 && (
        <MinimalSection title="Achievements">
          {data.achievements.map((a, i) => (
            <div key={i} style={{ fontSize: 11, color: '#374151', marginBottom: 5, display: 'flex', gap: 8 }}>
              <span style={{ color: INDIGO }}>—</span><span>{a}</span>
            </div>
          ))}
        </MinimalSection>
      )}

      {data.certifications.length > 0 && (
        <MinimalSection title="Certifications">
          {data.certifications.map((c, i) => (
            <div key={i} style={{ fontSize: 11, color: '#374151', marginBottom: 5, display: 'flex', gap: 8 }}>
              <span style={{ color: INDIGO }}>—</span><span>{c}</span>
            </div>
          ))}
        </MinimalSection>
      )}

      {data.extra.length > 0 && (
        <MinimalSection title="Extra-Curricular">
          {data.extra.map((e, i) => (
            <div key={i} style={{ fontSize: 11, color: '#374151', marginBottom: 5, display: 'flex', gap: 8 }}>
              <span style={{ color: INDIGO }}>—</span><span>{e}</span>
            </div>
          ))}
        </MinimalSection>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE 5 — TemplateProfessional  (Deloitte / TCS / Infosys — corporate)
// ═══════════════════════════════════════════════════════════════════════════════
const CORP_NAVY = '#1e3a5f'

function CorpSection({ title, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        background: CORP_NAVY, color: '#fff',
        fontSize: 11, fontWeight: 700, letterSpacing: 1,
        textTransform: 'uppercase', padding: '4px 10px', marginBottom: 8,
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function CorpEntry({ role, company, bullets = [] }) {
  return (
    <div style={{ marginBottom: 10, paddingLeft: 4 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: CORP_NAVY }}>{role}</div>
      {company && <div style={{ fontSize: 11, color: '#555', fontStyle: 'italic', marginBottom: 3 }}>{company}</div>}
      {bullets.map((b, i) => (
        <div key={i} style={{ fontSize: 11, color: '#222', lineHeight: 1.55, display: 'flex', gap: 8, marginBottom: 2 }}>
          <span style={{ color: CORP_NAVY, flexShrink: 0 }}>•</span>
          <span>{b}</span>
        </div>
      ))}
    </div>
  )
}

export function TemplateProfessional({ resumeText }) {
  const data = parseResume(resumeText)
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', fontSize: 11, color: '#1a1a2e', lineHeight: 1.5, background: '#fff' }}>
      {/* Header banner */}
      <div style={{
        background: CORP_NAVY, color: '#fff',
        padding: '24px 36px', marginBottom: 0,
      }}>
        <div style={{ fontSize: 26, fontWeight: 900, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 6 }}>
          {data.name || 'YOUR NAME'}
        </div>
        {data.summary && (
          <div style={{ fontSize: 11, color: '#93c5fd', marginBottom: 6 }}>
            {data.summary.split('.')[0]}
          </div>
        )}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 20px', fontSize: 10.5, color: '#bfdbfe' }}>
          {data.contact.map((c, i) => <span key={i}>{c}</span>)}
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: '20px 36px' }}>
        {data.summary && (
          <CorpSection title="Professional Summary">
            <p style={{ fontSize: 11, color: '#222', lineHeight: 1.65, paddingLeft: 4 }}>{data.summary}</p>
          </CorpSection>
        )}

        {data.experience.length > 0 && (
          <CorpSection title="Work Experience">
            {data.experience.map((e, i) => <CorpEntry key={i} {...e} />)}
          </CorpSection>
        )}

        {data.projects.length > 0 && (
          <CorpSection title="Projects">
            {data.projects.map((p, i) => <CorpEntry key={i} {...p} />)}
          </CorpSection>
        )}

        {data.education.length > 0 && (
          <CorpSection title="Education">
            {data.education.map((e, i) => <CorpEntry key={i} {...e} />)}
          </CorpSection>
        )}

        {data.skills.length > 0 && (
          <CorpSection title="Technical Skills">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6, paddingLeft: 4 }}>
              {data.skills.map((s, i) => (
                <div key={i} style={{
                  border: `1px solid ${CORP_NAVY}`, padding: '4px 8px',
                  fontSize: 10.5, color: CORP_NAVY, textAlign: 'center',
                  background: '#f0f4f8',
                }}>{s}</div>
              ))}
            </div>
          </CorpSection>
        )}

        {data.achievements.length > 0 && (
          <CorpSection title="Achievements & Awards">
            {data.achievements.map((a, i) => (
              <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8, paddingLeft: 4 }}>
                <span style={{ color: CORP_NAVY }}>•</span><span>{a}</span>
              </div>
            ))}
          </CorpSection>
        )}

        {data.certifications.length > 0 && (
          <CorpSection title="Certifications">
            {data.certifications.map((c, i) => (
              <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8, paddingLeft: 4 }}>
                <span style={{ color: CORP_NAVY }}>•</span><span>{c}</span>
              </div>
            ))}
          </CorpSection>
        )}

        {data.extra.length > 0 && (
          <CorpSection title="Extra-Curricular & Volunteering">
            {data.extra.map((e, i) => (
              <div key={i} style={{ fontSize: 11, color: '#222', marginBottom: 3, display: 'flex', gap: 8, paddingLeft: 4 }}>
                <span style={{ color: CORP_NAVY }}>•</span><span>{e}</span>
              </div>
            ))}
          </CorpSection>
        )}
      </div>
    </div>
  )
}
