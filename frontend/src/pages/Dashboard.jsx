import { useState, useRef, useEffect } from 'react'
import { Send, Bell, Settings, User, FileText, CheckCircle2, Search, ChevronRight, Plus } from 'lucide-react'
import { useMatcha } from '../hooks/useMatcha'
import Onboarding from '../components/Onboarding'

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(SKILL GAP|LEARNING PATH|RESOURCE|PENJELASAN|CV STRENGTH|CV GAP|REKOMENDASI KONKRET|TEMPLATE BULLET POINT|PROFILE STRENGTH|PROFILE GAP|HEADLINE & SUMMARY)\*\*/g,
      '<span class="inline-block bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-lg mr-1">$1</span>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\*\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
    .replace(/^\d+\.\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
    .replace(/^[-•]\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
    .replace(/\n\n/g, '<div class="my-2"></div>')
    .replace(/\n/g, '<br/>')
}

function parseSkillGaps(text) {
  if (!text) return []
  const stopKeywords = ['RESOURCE', 'REKOMENDASI', 'LEARNING PATH', 'PENJELASAN', 'SUMBER']
  let cleanText = text
  for (const kw of stopKeywords) {
    const idx = text.toUpperCase().indexOf(kw)
    if (idx !== -1) { cleanText = text.slice(0, idx); break }
  }
  const excludeWords = ['dicoding', 'revou', 'coursera', 'youtube', 'sanbercode', 'udemy', 'minggu', 'bulan', 'jam']
  const skills = []
  for (const line of cleanText.split('\n')) {
    const match = line.match(/^\d+\.\s+(.+)$/) || line.match(/^[-•]\s+(.+)$/)
    if (match) {
      const name = match[1].split(':')[0].split('(')[0].split('—')[0].replace(/\*\*/g, '').trim()
      const excluded = excludeWords.some(w => name.toLowerCase().includes(w))
      if (name.length > 0 && name.length < 60 && !excluded) skills.push(name)
    }
  }
  return skills.slice(0, 4)
}

function parseLearningPath(text) {
  if (!text) return []
  const lpMatch = text.match(/LEARNING PATH[\s\S]*?(?=RESOURCE|PENJELASAN|$)/i)
  if (!lpMatch) return []
  const lines = lpMatch[0].split('\n').filter(l => l.match(/minggu/i))
  return lines.slice(0, 4).map((line, i) => {
    const clean = line.replace(/^\*?\s*/, '').replace(/\*\*/g, '').trim()
    const colonIdx = clean.indexOf(':')
    const week = colonIdx > -1 ? clean.slice(0, colonIdx).trim() : `Minggu ${i + 1}`
    const topic = colonIdx > -1 ? clean.slice(colonIdx + 1).trim() : clean
    return { week, topic }
  })
}

const GAP_COLORS = [
  { bar: 'bg-red-400',    bg: 'bg-red-50',    text: 'text-red-500',    label: 'Kritis',  pct: 88 },
  { bar: 'bg-orange-400', bg: 'bg-orange-50',  text: 'text-orange-500', label: 'Tinggi',  pct: 72 },
  { bar: 'bg-amber-400',  bg: 'bg-amber-50',   text: 'text-amber-500',  label: 'Sedang',  pct: 55 },
  { bar: 'bg-green-400',  bg: 'bg-green-50',   text: 'text-green-600',  label: 'Rendah',  pct: 35 },
]

export default function Dashboard() {
  const { chatHistory, agentState, isLoading, sendChat, uploadDocument, reviewDocumentFull, analyzeJobDescription } = useMatcha()
  const [showOnboarding, setShowOnboarding] = useState(!localStorage.getItem('matcha_onboarded'))
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [input, setInput] = useState('')
  const [jobDesc, setJobDesc] = useState('')
  const [cvUploaded, setCvUploaded] = useState(false)
  const [linkedinUploaded, setLinkedinUploaded] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory, isLoading])

  const profile = agentState?.user_profile
  const skillGaps = parseSkillGaps(agentState?.skill_gaps)
  const learningPath = parseLearningPath(agentState?.skill_gaps)

  const handleSend = () => {
    if (!input.trim() || isLoading) return
    sendChat(input); setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const handleFileUpload = async (e, fileType) => {
    const file = e.target.files[0]; if (!file) return
    await uploadDocument(file, fileType)
    if (fileType === 'cv') setCvUploaded(true)
    else setLinkedinUploaded(true)
  }

  return (
    <div className="min-h-screen bg-[#F7F8FA] flex flex-col">
      {showOnboarding && (
        <Onboarding onComplete={({ namaUser, jurusan, targetKarir }) => {
          setShowOnboarding(false)
          sendChat(`Halo! Namaku ${namaUser}. Latar belakang pendidikan/pekerjaan saya saat ini: ${jurusan}. Target karir yang ingin saya capai: ${targetKarir}.`)
        }} />
      )}

      {/* NAVBAR */}
      <nav className="bg-white border-b border-gray-100 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center">
              <span className="text-sm">🍵</span>
            </div>
            <span className="font-bold text-gray-800">Matcha</span>
          </div>
          <div className="flex gap-1">
            {['Dashboard', 'Career Path', 'Resources'].map(nav => (
              <button key={nav} onClick={() => setActiveNav(nav)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${activeNav === nav ? 'bg-gray-100 text-gray-800' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}`}>
                {nav}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition">
            <Bell size={16} className="text-gray-500" />
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition">
            <Settings size={16} className="text-gray-500" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center">
            <User size={14} className="text-white" />
          </div>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden">

        {/* SIDEBAR */}
        <aside className="w-52 bg-white border-r border-gray-100 flex flex-col overflow-y-auto flex-shrink-0">
          <div className="p-4 space-y-5 flex-1">

            {/* Dokumen */}
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Dokumen</p>
              <label className="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-gray-50 cursor-pointer transition group">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${cvUploaded ? 'bg-green-100' : 'bg-gray-100'}`}>
                  {cvUploaded ? <CheckCircle2 size={14} className="text-green-600" /> : <FileText size={14} className="text-gray-500" />}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-gray-700">CV Utama</p>
                  <p className={`text-xs ${cvUploaded ? 'text-green-500' : 'text-gray-400'}`}>{cvUploaded ? 'Terupload ✓' : 'Upload PDF/DOCX'}</p>
                </div>
                <input type="file" accept=".pdf,.docx" className="hidden" onChange={e => handleFileUpload(e, 'cv')} />
              </label>

              <label className="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-gray-50 cursor-pointer transition group">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${linkedinUploaded ? 'bg-blue-100' : 'bg-gray-100'}`}>
                  {linkedinUploaded ? <CheckCircle2 size={14} className="text-blue-500" /> : <span className="text-xs font-bold text-gray-500">in</span>}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-gray-700">LinkedIn Profile</p>
                  <p className={`text-xs ${linkedinUploaded ? 'text-blue-500' : 'text-gray-400'}`}>{linkedinUploaded ? 'Terupload ✓' : 'Upload PDF'}</p>
                </div>
                <input type="file" accept=".pdf" className="hidden" onChange={e => handleFileUpload(e, 'linkedin')} />
              </label>

              <label className="mt-2 flex flex-col items-center gap-1 border-2 border-dashed border-gray-200 hover:border-green-300 rounded-xl p-3 cursor-pointer transition group">
                <div className="w-7 h-7 rounded-lg bg-gray-100 group-hover:bg-green-50 flex items-center justify-center transition">
                  <Plus size={13} className="text-gray-400 group-hover:text-green-500" />
                </div>
                <p className="text-xs text-gray-400 text-center">Drag file ke sini</p>
                <p className="text-xs text-green-600 font-medium">Browse</p>
                <input type="file" accept=".pdf,.docx" className="hidden" onChange={e => handleFileUpload(e, 'cv')} />
              </label>
            </div>

            {/* Status Review */}
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Status Review</p>
              <div className="space-y-1">
                <button onClick={() => reviewDocumentFull('cv')}
                  className="w-full flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-gray-50 transition text-left">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${cvUploaded ? 'bg-green-100' : 'bg-gray-100'}`}>
                    <FileText size={13} className={cvUploaded ? 'text-green-600' : 'text-gray-400'} />
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-700">Review CV</p>
                    <p className={`text-xs ${cvUploaded ? 'text-green-500' : 'text-gray-400'}`}>{cvUploaded ? 'Klik untuk review' : 'Belum dianalisis'}</p>
                  </div>
                </button>
                <button onClick={() => reviewDocumentFull('linkedin')}
                  className="w-full flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-gray-50 transition text-left">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${linkedinUploaded ? 'bg-blue-100' : 'bg-gray-100'}`}>
                    <span className={`text-xs font-bold ${linkedinUploaded ? 'text-blue-500' : 'text-gray-400'}`}>in</span>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-700">Review LinkedIn</p>
                    <p className={`text-xs ${linkedinUploaded ? 'text-blue-500' : 'text-gray-400'}`}>{linkedinUploaded ? 'Klik untuk review' : 'Belum dihubungkan'}</p>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-gray-100">
            <button onClick={() => { localStorage.removeItem('matcha_onboarded'); window.location.reload() }}
              className="text-xs text-gray-400 hover:text-red-400 transition">
              Reset & Mulai Ulang
            </button>
          </div>
        </aside>

        {/* MAIN */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-4">

            {/* Hero Banner */}
            <div className="relative rounded-2xl overflow-hidden bg-gradient-to-r from-emerald-900 via-green-800 to-teal-800 p-6">
              <div className="absolute inset-0 opacity-20" style={{
                backgroundImage: 'url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&auto=format&fit=crop")',
                backgroundSize: 'cover', backgroundPosition: 'center'
              }} />
              <div className="relative">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-4 h-4 rounded-full border border-white/50 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                  </div>
                  <p className="text-white/70 text-xs">Asisten Karir Adaptif — Temukan Jalur Karir Idealmu</p>
                </div>
                <h1 className="text-white text-xl font-bold">
                  {profile?.current_role ? `Halo, ${profile.current_role}! 👋` : 'Selamat Datang di Matcha'}
                </h1>
                {profile?.target_role && <p className="text-white/60 text-xs mt-0.5">Target: {profile.target_role}</p>}
              </div>
            </div>

            {/* Grid utama */}
            <div className="grid grid-cols-3 gap-4">

              {/* Chat */}
              <div className="col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm flex flex-col" style={{ height: '400px' }}>
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">M</span>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-800">Matcha Career Assistant</p>
                      <div className="flex items-center gap-1">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                        <p className="text-xs text-gray-400">Aktif</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-lg">Chat</button>
                    <button className="px-3 py-1 text-xs font-medium text-gray-400 hover:bg-gray-50 rounded-lg transition">Arsip</button>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
                  {chatHistory.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
                      <span className="text-3xl">🍵</span>
                      <p className="text-gray-400 text-xs">Ceritakan situasimu atau tujuan karirmu</p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        {['Aku mau jadi Data Analyst 📊', 'Review CV aku 📄', 'Aku ingin jadi AI Engineer 🤖'].map(s => (
                          <button key={s} onClick={() => { setInput(s); textareaRef.current?.focus() }}
                            className="text-xs bg-gray-50 border border-gray-200 hover:border-green-300 hover:bg-green-50 text-gray-600 px-3 py-1.5 rounded-lg transition">
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {chatHistory.map((msg, i) => (
                    <div key={i} className={`flex items-end gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      {msg.role === 'assistant' && (
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-xs font-bold">M</span>
                        </div>
                      )}
                      <div className={`max-w-xs px-3 py-2 text-xs leading-relaxed rounded-2xl shadow-sm ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-br-sm'
                          : 'bg-gray-50 text-gray-700 rounded-bl-sm border border-gray-100'
                      }`} dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }} />
                      {msg.role === 'user' && (
                        <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                          <User size={10} className="text-gray-500" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex items-end gap-2">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-xs font-bold">M</span>
                      </div>
                      <div className="bg-gray-50 border border-gray-100 px-3 py-2 rounded-2xl rounded-bl-sm">
                        <div className="flex gap-1">
                          {[0,150,300].map(d => (
                            <div key={d} className="w-1.5 h-1.5 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={bottomRef} />
                </div>

                <div className="px-3 py-3 border-t border-gray-100 flex-shrink-0">
                  <div className="flex items-center gap-2 bg-gray-50 rounded-xl px-3 py-2 border border-gray-200 focus-within:border-green-400 transition">
                    <textarea ref={textareaRef} rows={1}
                      className="flex-1 bg-transparent text-xs text-gray-700 placeholder-gray-400 resize-none focus:outline-none"
                      placeholder="Ceritakan situasimu atau tujuan karirmu..."
                      value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKeyDown} />
                    <button onClick={handleSend} disabled={!input.trim() || isLoading}
                      className="w-7 h-7 flex items-center justify-center rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 disabled:from-gray-200 disabled:to-gray-200 text-white disabled:text-gray-400 transition flex-shrink-0">
                      <Send size={12} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Panel kanan */}
              <div className="space-y-3">
                {/* Profil */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Profil Karir</p>
                  {!profile?.target_role ? (
                    <p className="text-xs text-gray-400 text-center py-2 leading-relaxed">Profil akan terisi seiring percakapan</p>
                  ) : (
                    <div className="space-y-1.5">
                      {profile.current_role && (
                        <div className="flex items-center gap-2 bg-gray-50 rounded-xl p-2.5">
                          <User size={11} className="text-gray-400 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-gray-400">Posisi Saat Ini</p>
                            <p className="text-xs font-semibold text-gray-700">{profile.current_role}</p>
                          </div>
                        </div>
                      )}
                      {profile.target_role && (
                        <div className="flex items-center gap-2 bg-green-50 rounded-xl p-2.5">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0" />
                          <div>
                            <p className="text-xs text-gray-400">Target Karir</p>
                            <p className="text-xs font-semibold text-green-700">{profile.target_role}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Cek Lowongan */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Cek Lowongan</p>
                  <textarea
                    className="w-full text-xs border border-gray-100 bg-gray-50 rounded-xl p-2.5 resize-none focus:outline-none focus:ring-1 focus:ring-green-300 text-gray-700 placeholder-gray-300"
                    rows={4} placeholder="Copy-paste job description here..."
                    value={jobDesc} onChange={e => setJobDesc(e.target.value)} />
                  <button onClick={async () => { await analyzeJobDescription(jobDesc); setJobDesc('') }}
                    disabled={!jobDesc.trim()}
                    className="w-full mt-2 flex items-center justify-center gap-1.5 bg-gradient-to-r from-green-500 to-emerald-600 disabled:from-gray-200 disabled:to-gray-200 disabled:text-gray-400 text-white text-xs font-semibold py-2 rounded-xl transition">
                    <Search size={11} /> Analisis Ulang
                  </button>
                </div>

                {/* Keahlian */}
                {skillGaps.length > 0 && (
                  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Keahlian Saat Ini</p>
                    <div className="flex flex-wrap gap-1.5">
                      {skillGaps.slice(0, 3).map((s, i) => (
                        <span key={i} className="text-xs bg-green-50 text-green-700 border border-green-100 px-2.5 py-1 rounded-lg font-medium">{s.split(' ').slice(0,2).join(' ')}</span>
                      ))}
                      <button className="text-xs bg-gray-100 text-gray-500 hover:bg-green-50 hover:text-green-600 px-2.5 py-1 rounded-lg flex items-center gap-1 transition">
                        <Plus size={10} /> Tambah
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Analisis Gap */}
              {skillGaps.length > 0 && (
                <div className="col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-semibold text-gray-800">Analisis Gap Ilmu</p>
                    <span className="text-xs text-gray-400">Berdasarkan CV & Job Desc</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {skillGaps.map((skill, i) => {
                      const c = GAP_COLORS[i] || GAP_COLORS[GAP_COLORS.length - 1]
                      return (
                        <div key={i} className={`${c.bg} rounded-xl p-3`}>
                          <div className="flex justify-between items-center mb-1.5">
                            <p className="text-xs font-semibold text-gray-700 truncate flex-1 mr-2">{skill}</p>
                            <span className={`text-xs font-bold ${c.text} flex-shrink-0`}>{c.pct}% Match</span>
                          </div>
                          <div className="w-full bg-white bg-opacity-60 rounded-full h-1.5">
                            <div className={`${c.bar} h-1.5 rounded-full`} style={{ width: `${c.pct}%` }} />
                          </div>
                          <p className="text-xs text-gray-500 mt-1.5">
                            {c.label === 'Kritis' ? 'Perlu diprioritaskan' : c.label === 'Tinggi' ? 'Perlu ditingkatkan' : 'Dalam perkembangan'}
                          </p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Learning Path Table */}
              {learningPath.length > 0 && (
                <div className="col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-semibold text-gray-800">Peta Jalan Belajar Terpersonalisasi</p>
                    <button className="text-xs text-green-600 font-medium flex items-center gap-1">
                      Detail Penuh <ChevronRight size={12} />
                    </button>
                  </div>
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left text-xs font-semibold text-gray-400 pb-2 w-28">Minggu</th>
                        <th className="text-left text-xs font-semibold text-gray-400 pb-2">Topik Utama</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {learningPath.map((row, i) => (
                        <tr key={i} className="hover:bg-gray-50 transition">
                          <td className="py-2.5 text-xs text-gray-500 font-medium">{row.week}</td>
                          <td className="py-2.5 text-xs text-gray-700">{row.topic}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

            </div>
          </div>
        </main>
      </div>
    </div>
  )
}