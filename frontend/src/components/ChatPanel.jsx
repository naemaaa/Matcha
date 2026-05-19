import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(SKILL GAP|LEARNING PATH|RESOURCE|PENJELASAN|CV STRENGTH|CV GAP|REKOMENDASI KONKRET|TEMPLATE BULLET POINT|PROFILE STRENGTH|PROFILE GAP|HEADLINE & SUMMARY)\*\*/g,
  '<div class="inline-block bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-lg mt-3 mb-1">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/#{3}\s?(.*?)(\n|$)/g, '<h3 class="font-bold text-sm mt-3 mb-1 text-gray-800">$1</h3>')
    .replace(/#{2}\s?(.*?)(\n|$)/g, '<h2 class="font-bold text-base mt-4 mb-1 text-gray-800">$1</h2>')
    .replace(/#{1}\s?(.*?)(\n|$)/g, '<h1 class="font-bold text-lg mt-4 mb-2 text-gray-800">$1</h1>')
    .replace(/^\d+\.\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
    .replace(/^[-•]\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
    .replace(/\n\n/g, '<div class="my-2"></div>')
    .replace(/^\*\s(.+)$/gm, '<div class="flex gap-2 my-1"><span class="text-green-600 font-semibold flex-shrink-0">•</span><span>$1</span></div>')
}

export default function ChatPanel({ chatHistory, isLoading, onSendMessage }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory, isLoading])

  const handleSend = () => {
    if (!input.trim() || isLoading) return
    onSendMessage(input)
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px'
  }

  return (
    <div className="flex flex-col h-screen bg-[#F7F8FA]">

      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-6 py-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center shadow-sm">
            <span className="text-white text-sm font-bold">M</span>
          </div>
          <div>
            <p className="font-semibold text-gray-800 text-sm">Matcha Career Assistant</p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
              <p className="text-xs text-gray-400">Aktif</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {chatHistory.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center select-none">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center shadow-lg">
              <span className="text-3xl">🍵</span>
            </div>
            <div>
              <p className="text-gray-800 font-semibold text-lg">Selamat datang di Matcha!</p>
              <p className="text-gray-400 text-sm mt-1 max-w-xs leading-relaxed">
                Asisten karir adaptif — ceritakan tujuan karirmu dan aku akan bantu merancang jalannya.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {[
                "Aku mau jadi Data Analyst 📊",
                "Bantu review CV aku 📄",
                "Aku ingin pindah karir ke AI Engineer 🤖",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setInput(suggestion)
                    textareaRef.current?.focus()
                }}
                  className="text-xs bg-white border border-gray-200 hover:border-green-400 hover:bg-green-50 text-gray-600 hover:text-green-700 px-3 py-2 rounded-xl transition-all duration-150 shadow-sm"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {chatHistory.map((msg, i) => (
          <div
            key={i}
            className={`flex items-end gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {/* Avatar assistant */}
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center flex-shrink-0 mb-0.5 shadow-sm">
                <span className="text-white text-xs font-bold">M</span>
              </div>
            )}

            {/* Bubble */}
            <div
              className={`
                max-w-[72%] px-4 py-3 text-sm leading-relaxed shadow-sm
                ${msg.role === 'user'
                  ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-2xl rounded-br-sm'
                  : 'bg-white text-gray-700 rounded-2xl rounded-bl-sm border border-gray-100'
                }
              `}
              dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
            />

            {/* Avatar user */}
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mb-0.5">
                <span className="text-gray-500 text-xs font-bold">U</span>
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex items-end gap-2.5 justify-start">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center flex-shrink-0 shadow-sm">
              <span className="text-white text-xs font-bold">M</span>
            </div>
            <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
              <div className="flex gap-1 items-center h-4">
                <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* Skill Gap Analysis Card */}
        {agentState?.skill_gaps && (
          <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm mt-4">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={16} className="text-green-600" />
              <h3 className="font-semibold text-gray-800 text-sm">Analisis Gap Ilmu</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {['Prototyping (Advanced)', 'APIs & Microservices', 'User Research', 'UX Metrics & Analytics'].map((skill, i) => (
                <div key={i} className="bg-gray-50 rounded-lg p-2.5 text-xs">
                  <p className="text-gray-600 font-medium">{skill}</p>
                  <div className="mt-1.5 bg-white rounded-full h-1.5 overflow-hidden">
                    <div className="bg-orange-400 h-full" style={{ width: `${65 - i * 10}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Learning Path Card */}
        {agentState?.learning_path && (
          <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm mt-4">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen size={16} className="text-blue-600" />
              <h3 className="font-semibold text-gray-800 text-sm">Peta Jalan Belajar Terpersonalisasi</h3>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex gap-3 items-start">
                <span className="bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded text-xs flex-shrink-0">Minggu 1</span>
                <div>
                  <p className="font-medium text-gray-800">Advanced Interaction Design</p>
                  <p className="text-gray-500 text-xs mt-0.5">Figma prototyping, micro-interactions</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <span className="bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded text-xs flex-shrink-0">Minggu 2</span>
                <div>
                  <p className="font-medium text-gray-800">Modern Design Systems</p>
                  <p className="text-gray-500 text-xs mt-0.5">Creating scalable component libraries</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <span className="bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded text-xs flex-shrink-0">Minggu 3</span>
                <div>
                  <p className="font-medium text-gray-800">User Research Ethics</p>
                  <p className="text-gray-500 text-xs mt-0.5">Interview frameworks, data analysis</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />

      {/* Input */}
      <div className="bg-white border-t border-gray-100 px-5 py-4 flex-shrink-0">
        <div className="flex items-end gap-3 bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3 focus-within:border-green-400 focus-within:bg-white transition-all duration-150">
          <textarea
            ref={textareaRef}
            className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 resize-none focus:outline-none min-h-[20px] max-h-32 leading-relaxed"
            rows={1}
            placeholder="Ceritakan situasimu atau tujuan karirmu..."
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="
              w-8 h-8 flex items-center justify-center rounded-xl flex-shrink-0
              bg-gradient-to-br from-green-500 to-emerald-600
              hover:from-green-600 hover:to-emerald-700
              disabled:from-gray-200 disabled:to-gray-200
              text-white disabled:text-gray-400
              transition-all duration-150 shadow-sm
            "
          >
            <Send size={14} />
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          Enter untuk kirim · Shift+Enter untuk baris baru
        </p>
      </div>

    </div>
  )
}