import { useState, useEffect } from 'react'
import { config } from '../theme'

const PASS_HASH = 'a1b2c3' // simple obfuscation, not real security
const STORAGE_KEY = 'vibedeck-auth'
const EXPIRE_DAYS = 7

function hashCode(str) {
  // Simple hash — this is front-end only, not cryptographic
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0
  }
  return h.toString(36)
}

const EXPECTED_HASH = hashCode(config.password || 'slide-kit')

function isAuthenticated() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return false
    const { hash, ts } = JSON.parse(raw)
    if (hash !== EXPECTED_HASH) return false
    if (Date.now() - ts > EXPIRE_DAYS * 86400000) return false
    return true
  } catch {
    return false
  }
}

export default function PasswordGate({ children }) {
  const [authed, setAuthed] = useState(isAuthenticated)
  const [input, setInput] = useState('')
  const [error, setError] = useState(false)
  const [shaking, setShaking] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (hashCode(input.trim()) === EXPECTED_HASH) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ hash: EXPECTED_HASH, ts: Date.now() }))
      setAuthed(true)
    } else {
      setError(true)
      setShaking(true)
      setTimeout(() => setShaking(false), 500)
    }
  }

  if (authed) return children

  return (
    <div className="fixed inset-0 bg-neutral-950 flex items-center justify-center overflow-hidden">
      {/* Ambient gradient orbs */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-blue-600/8 rounded-full blur-[120px]" />
      <div className="absolute bottom-1/4 -right-32 w-80 h-80 bg-blue-400/6 rounded-full blur-[100px]" />

      {/* Dot grid background */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: 'radial-gradient(circle, #fff 0.5px, transparent 0.5px)',
          backgroundSize: '32px 32px',
        }}
      />

      <form
        onSubmit={handleSubmit}
        className={`relative flex flex-col items-center gap-5 ${shaking ? 'animate-shake' : ''}`}
      >
        <div className="flex flex-col items-center gap-3 mb-4">
          <img src={config.logo || '/logo.svg'} alt="logo" className="h-6 opacity-70" onError={(e) => e.target.style.display = 'none'} />
          <div className="flex items-center gap-2 mt-1">
            <div className="w-6 h-[1px] bg-white/15" />
            <span className="text-white/30 text-[10px] font-mono tracking-[0.25em] uppercase">Internal Access</span>
            <div className="w-6 h-[1px] bg-white/15" />
          </div>
        </div>

        <input
          type="password"
          value={input}
          onChange={(e) => { setInput(e.target.value); setError(false) }}
          placeholder="输入访问密码"
          autoFocus
          className={`w-72 px-4 py-3 rounded-xl bg-white/[0.06] border text-white text-sm placeholder-white/25 outline-none transition-all backdrop-blur-sm ${
            error ? 'border-red-500/50 bg-red-500/[0.04]' : 'border-white/[0.08] focus:border-blue-500/40 focus:bg-white/[0.08]'
          }`}
        />

        {error && <span className="text-red-400/90 text-xs font-medium">密码错误</span>}

        <button
          type="submit"
          className="w-72 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-medium transition-all shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30"
        >
          进入
        </button>

        <span className="text-white/15 text-[10px] mt-6 font-mono tracking-wider">有效期 {EXPIRE_DAYS} 天</span>
      </form>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20%, 60% { transform: translateX(-8px); }
          40%, 80% { transform: translateX(8px); }
        }
        .animate-shake { animation: shake 0.4s ease-in-out; }
      `}</style>
    </div>
  )
}
