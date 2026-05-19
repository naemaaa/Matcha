import { User, Clock, DollarSign, Target, TrendingUp, Calendar } from 'lucide-react'

// Parse skill gaps dari teks mentah LLM jadi array item
function parseSkillGaps(text) {
  if (!text) return []

  // Stop parsing setelah ketemu section resource/rekomendasi
  const stopKeywords = ['RESOURCE', 'REKOMENDASI', 'LEARNING PATH', 'PENJELASAN', 'SUMBER']
  let cleanText = text
  for (const kw of stopKeywords) {
    const idx = text.toUpperCase().indexOf(kw)
    if (idx !== -1) {
      cleanText = text.slice(0, idx)
      break
    }
  }

  const lines = cleanText.split('\n')
  const skills = []
  const excludeWords = ['dicoding', 'revou', 'coursera', 'youtube', 'sanbercode', 'udemy', 'skillacademy', 'buildwithangga', 'minggu', 'bulan', 'jam']

  for (const line of lines) {
    const match = line.match(/^\d+\.\s+(.+)$/) || line.match(/^[-•]\s+(.+)$/)
    if (match) {
      const raw = match[1].trim()
      const name = raw.split(':')[0].split('(')[0].split('—')[0].replace(/\*\*/g, '').trim()
      const isExcluded = excludeWords.some(w => name.toLowerCase().includes(w))
      if (name.length > 0 && name.length < 60 && !isExcluded) {
        skills.push(name)
      }
    }
  }
  return skills.slice(0, 6)
}

// Warna progress bar per index
const GAP_COLORS = [
  { bar: 'bg-red-400',    bg: 'bg-red-50',    text: 'text-red-600',    label: 'Kritis' },
  { bar: 'bg-orange-400', bg: 'bg-orange-50',  text: 'text-orange-600', label: 'Tinggi' },
  { bar: 'bg-amber-400',  bg: 'bg-amber-50',   text: 'text-amber-600',  label: 'Sedang' },
  { bar: 'bg-yellow-400', bg: 'bg-yellow-50',  text: 'text-yellow-600', label: 'Sedang' },
  { bar: 'bg-lime-400',   bg: 'bg-lime-50',    text: 'text-lime-600',   label: 'Rendah' },
  { bar: 'bg-green-400',  bg: 'bg-green-50',   text: 'text-green-600',  label: 'Rendah' },
]

// Progress value per index (makin tinggi = makin butuh dipelajari)
const GAP_PROGRESS = [92, 78, 65, 52, 40, 28]

export default function ProfilePanel({ agentState }) {
  const profile = agentState?.user_profile
  const skillGapsRaw = agentState?.skill_gaps
  const parsedSkills = parseSkillGaps(skillGapsRaw)

  return (
    <div className="w-72 bg-white border-l border-gray-100 h-screen flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto p-5 space-y-6">

        {/* ── Profil Karir ── */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Profil Karir
          </p>

          {!profile || (!profile.current_role && !profile.target_role) ? (
            <div className="bg-gray-50 rounded-2xl p-5 text-center">
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <User size={18} className="text-gray-300" />
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">
                Profil akan terisi otomatis seiring percakapan
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {profile.current_role && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                  <div className="w-7 h-7 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
                    <User size={12} className="text-gray-500" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-gray-400">Posisi Saat Ini</p>
                    <p className="text-sm font-medium text-gray-700 truncate">{profile.current_role}</p>
                  </div>
                </div>
              )}

              {profile.target_role && (
                <div className="flex items-center gap-3 bg-green-50 rounded-xl p-3">
                  <div className="w-7 h-7 bg-green-200 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Target size={12} className="text-green-600" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-gray-400">Target Karir</p>
                    <p className="text-sm font-semibold text-green-700 truncate">{profile.target_role}</p>
                  </div>
                </div>
              )}

              {profile.hours_per_week && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                  <div className="w-7 h-7 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock size={12} className="text-blue-500" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Waktu/Minggu</p>
                    <p className="text-sm font-medium text-gray-700">{profile.hours_per_week} jam</p>
                  </div>
                </div>
              )}

              {profile.budget_idr && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                  <div className="w-7 h-7 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <DollarSign size={12} className="text-purple-500" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Budget</p>
                    <p className="text-sm font-medium text-gray-700">
                      Rp {Number(profile.budget_idr).toLocaleString('id-ID')}
                    </p>
                  </div>
                </div>
              )}

              {profile.timeline_months && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                  <div className="w-7 h-7 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Calendar size={12} className="text-amber-500" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Target Waktu</p>
                    <p className="text-sm font-medium text-gray-700">{profile.timeline_months} bulan</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Skill Gap Cards ── */}
        {parsedSkills.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Skill Gap
              </p>
              <div className="flex items-center gap-1">
                <TrendingUp size={10} className="text-gray-400" />
                <span className="text-xs text-gray-400">{parsedSkills.length} skill</span>
              </div>
            </div>

            <div className="space-y-2">
              {parsedSkills.map((skill, i) => {
                const color = GAP_COLORS[i] || GAP_COLORS[GAP_COLORS.length - 1]
                const progress = GAP_PROGRESS[i] || 20
                return (
                  <div key={i} className={`${color.bg} rounded-xl p-3`}>
                    <div className="flex items-center justify-between mb-1.5">
                      <p className="text-xs font-medium text-gray-700 truncate flex-1 mr-2">{skill}</p>
                      <span className={`text-xs font-semibold ${color.text} flex-shrink-0`}>
                        {color.label}
                      </span>
                    </div>
                    <div className="w-full bg-white bg-opacity-60 rounded-full h-1.5">
                      <div
                        className={`${color.bar} h-1.5 rounded-full transition-all duration-500`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Fallback skill gap teks kalau parse gagal */}
        {skillGapsRaw && parsedSkills.length === 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Skill Gap
            </p>
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">
                {skillGapsRaw.slice(0, 300)}...
              </p>
            </div>
          </div>
        )}

        {/* ── Drift Warning ── */}
        {agentState?.drift_detected && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
            <p className="text-xs text-amber-700 font-semibold">⚡ Perubahan tujuan terdeteksi</p>
            <p className="text-xs text-amber-600 mt-1 leading-relaxed">
              Profil sedang diperbarui secara otomatis sesuai arah baru kamu.
            </p>
          </div>
        )}

      </div>
    </div>
  )
}