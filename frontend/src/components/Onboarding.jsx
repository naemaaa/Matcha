import { useState } from 'react'

const JURUSAN_OPTIONS = [
  "Sistem Informasi",
  "Ilmu Komputer",
  "Teknik Informatika",
  "Teknik Elektro",
  "Manajemen",
  "Akuntansi",
  "Komunikasi",
  "Psikologi",
  "Hukum",
  "Teknik Industri",
  "Matematika",
  "Statistika",
  "Lainnya..."
]

const KARIR_OPTIONS = [
  "Data Analyst",
  "Data Scientist",
  "AI/ML Engineer",
  "Software Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Product Manager",
  "UI/UX Designer",
  "DevOps Engineer",
  "Cybersecurity Analyst",
  "Business Analyst",
  "Digital Marketing",
  "Lainnya..."
]

export default function Onboarding({ onComplete }) {
  const [step, setStep] = useState(1)
  const [namaUser, setNamaUser] = useState('')
  const [jurusan, setJurusan] = useState('')
  const [jurusanCustom, setJurusanCustom] = useState('')
  const [targetKarir, setTargetKarir] = useState('')
  const [targetCustom, setTargetCustom] = useState('')

  const finalJurusan = jurusan === 'Lainnya...' ? jurusanCustom : jurusan
  const finalKarir = targetKarir === 'Lainnya...' ? targetCustom : targetKarir

  const canNext =
    (step === 1 && namaUser.trim()) ||
    (step === 2 && finalJurusan.trim()) ||
    (step === 3 && finalKarir.trim())

  const handleNext = () => {
    if (!canNext) return
    if (step < 3) {
      setStep(step + 1)
    } else {
      localStorage.setItem('matcha_onboarded', 'true')
      onComplete({
        namaUser: namaUser.trim(),
        jurusan: finalJurusan.trim(),
        targetKarir: finalKarir.trim(),
      })
    }
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-emerald-900 via-green-800 to-teal-900 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8">

        {/* Logo */}
        <div className="flex items-center gap-2 mb-8">
          <span className="text-3xl">🍵</span>
          <span className="font-bold text-gray-800 text-xl">Matcha</span>
        </div>

        {/* Progress bar */}
        <div className="flex gap-2 mb-8">
          {[1, 2, 3].map(s => (
            <div
              key={s}
              className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                s <= step ? 'bg-green-500' : 'bg-gray-100'
              }`}
            />
          ))}
        </div>

        {/* Step 1 — Nama */}
        {step === 1 && (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-1">Halo! Siapa namamu? 👋</h2>
            <p className="text-gray-400 text-sm mb-6">
              Aku akan memanggilmu dengan nama ini sepanjang percakapan.
            </p>
            <input
              type="text"
              placeholder="Nama kamu..."
              value={namaUser}
              onChange={e => setNamaUser(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleNext()}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 text-gray-700"
              autoFocus
            />
          </div>
        )}

        {/* Step 2 — Jurusan */}
        {step === 2 && (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-1">Latar belakangmu apa? 🎓</h2>
            <p className="text-gray-400 text-sm mb-6">
              Ini membantu aku memahami skill yang sudah kamu miliki.
            </p>
            <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
              {JURUSAN_OPTIONS.map(j => (
                <button
                  key={j}
                  onClick={() => {
                    setJurusan(j)
                    setJurusanCustom('')
                  }}
                  className={`text-sm px-3 py-2.5 rounded-xl border text-left transition-all duration-150 ${
                    jurusan === j
                      ? 'border-green-500 bg-green-50 text-green-700 font-medium'
                      : 'border-gray-200 text-gray-600 hover:border-green-300 hover:bg-green-50'
                  }`}
                >
                  {j}
                </button>
              ))}
            </div>
            {jurusan === 'Lainnya...' && (
              <input
                type="text"
                placeholder="Tulis jurusanmu..."
                value={jurusanCustom}
                onChange={e => setJurusanCustom(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleNext()}
                className="w-full mt-3 border border-green-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 text-gray-700"
                autoFocus
              />
            )}
          </div>
        )}

        {/* Step 3 — Target Karir */}
        {step === 3 && (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-1">Mau jadi apa? 🎯</h2>
            <p className="text-gray-400 text-sm mb-6">
              Target karir yang ingin kamu capai.
            </p>
            <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
              {KARIR_OPTIONS.map(k => (
                <button
                  key={k}
                  onClick={() => {
                    setTargetKarir(k)
                    setTargetCustom('')
                  }}
                  className={`text-sm px-3 py-2.5 rounded-xl border text-left transition-all duration-150 ${
                    targetKarir === k
                      ? 'border-green-500 bg-green-50 text-green-700 font-medium'
                      : 'border-gray-200 text-gray-600 hover:border-green-300 hover:bg-green-50'
                  }`}
                >
                  {k}
                </button>
              ))}
            </div>
            {targetKarir === 'Lainnya...' && (
              <input
                type="text"
                placeholder="Tulis target karirmu..."
                value={targetCustom}
                onChange={e => setTargetCustom(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleNext()}
                className="w-full mt-3 border border-green-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 text-gray-700"
                autoFocus
              />
            )}
          </div>
        )}

        {/* CTA Button */}
        <button
          onClick={handleNext}
          disabled={!canNext}
          className="w-full mt-8 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-200 disabled:to-gray-200 disabled:text-gray-400 text-white font-medium py-3 rounded-xl transition-all duration-150 shadow-sm"
        >
          {step === 3 ? 'Mulai Sekarang 🚀' : 'Lanjut →'}
        </button>

      </div>
    </div>
  )
}