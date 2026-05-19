import { useState } from 'react'
import { FileText, Search, RotateCcw, CheckCircle2 } from 'lucide-react'

export default function Sidebar({ agentState, onUpload, onAnalyzeJob }) {
  const [jobDesc, setJobDesc] = useState('')
  const [cvUploaded, setCvUploaded] = useState(false)
  const [linkedinUploaded, setLinkedinUploaded] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleFileUpload = async (e, fileType) => {
    const file = e.target.files[0]
    if (!file) return
    await onUpload(file, fileType)
    if (fileType === 'cv') setCvUploaded(true)
    else setLinkedinUploaded(true)
  }

  const handleAnalyze = async () => {
    if (!jobDesc.trim()) return
    setIsAnalyzing(true)
    await onAnalyzeJob(jobDesc)
    setIsAnalyzing(false)
    setJobDesc('')
  }

  return (
    <div className="w-64 bg-white border-r border-gray-100 h-screen flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto p-5 space-y-6">

        {/* Logo */}
        <div className="flex items-center gap-2.5 py-1">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center shadow-sm">
            <span className="text-base">🍵</span>
          </div>
          <span className="font-bold text-gray-800 text-base">Matcha</span>
        </div>

        {/* Dokumen */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Dokumen
          </p>

          {/* CV Upload */}
          <label className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 cursor-pointer transition-all duration-150 group">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-150 ${
              cvUploaded ? 'bg-green-100' : 'bg-gray-100 group-hover:bg-gray-200'
            }`}>
              {cvUploaded
                ? <CheckCircle2 size={16} className="text-green-600" />
                : <FileText size={16} className="text-gray-500" />
              }
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-700">CV Utama</p>
              <p className={`text-xs truncate ${cvUploaded ? 'text-green-500' : 'text-gray-400'}`}>
                {cvUploaded ? 'Terupload ✓' : 'Upload PDF / DOCX'}
              </p>
            </div>
            <input
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={(e) => handleFileUpload(e, 'cv')}
            />
          </label>

          {/* LinkedIn Upload */}
          <label className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 cursor-pointer transition-all duration-150 group">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-150 ${
              linkedinUploaded ? 'bg-blue-100' : 'bg-gray-100 group-hover:bg-gray-200'
            }`}>
              {linkedinUploaded
                ? <CheckCircle2 size={16} className="text-blue-500" />
                : <span className="text-xs font-bold text-gray-500">in</span>
              }
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-700">LinkedIn Profile</p>
              <p className={`text-xs truncate ${linkedinUploaded ? 'text-blue-500' : 'text-gray-400'}`}>
                {linkedinUploaded ? 'Terupload ✓' : 'Upload PDF'}
              </p>
            </div>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => handleFileUpload(e, 'linkedin')}
            />
          </label>
        </div>

        {/* Cek Lowongan */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Cek Lowongan
          </p>
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
            <textarea
              className="w-full text-xs bg-transparent border-none resize-none focus:outline-none text-gray-700 placeholder-gray-300 leading-relaxed"
              rows={5}
              placeholder="Copy-paste job description dari Glints, LinkedIn, JobStreet..."
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={!jobDesc.trim() || isAnalyzing}
            className="w-full mt-2 flex items-center justify-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-200 disabled:to-gray-200 disabled:text-gray-400 text-white text-xs font-semibold py-2.5 rounded-xl transition-all duration-150 shadow-sm"
          >
            <Search size={12} />
            {isAnalyzing ? 'Menganalisis...' : 'Analisis Lowongan'}
          </button>
        </div>

        {/* Target Aktif */}
        {agentState?.user_profile?.target_role && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Target Aktif
            </p>
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-100 rounded-xl p-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0"></div>
                <p className="text-sm font-semibold text-green-700 truncate">
                  {agentState.user_profile.target_role}
                </p>
              </div>
              {agentState.user_profile.current_role && (
                <p className="text-xs text-gray-400 mt-1 truncate">
                  dari {agentState.user_profile.current_role}
                </p>
              )}
            </div>
          </div>
        )}

      </div>

      {/* Footer */}
      <div className="p-5 border-t border-gray-100">
        <button
          onClick={() => {
            localStorage.removeItem('matcha_onboarded')
            window.location.reload()
          }}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-red-400 transition-all duration-150"
        >
          <RotateCcw size={11} />
          Reset & Mulai Ulang
        </button>
      </div>
    </div>
  )
}