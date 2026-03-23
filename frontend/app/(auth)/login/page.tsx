'use client'

import { useState, useCallback } from 'react'
import { useAuth } from '@/lib/hooks/useAuth'

export default function LoginPage() {
  const { login, loading, error } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      await login({ username: email, password })
    },
    [email, password, login]
  )

  const inputClass =
    'w-full h-9 text-sm bg-[#0d0d0d] border border-[#262626] rounded px-3 text-white placeholder-[#525252] focus:outline-none focus:border-[#404040] transition-colors'

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-start justify-center pt-40">
      <div className="w-full max-w-sm mx-4 bg-[#111111] border border-[#262626] rounded-lg p-8">
        <div className="mb-8 text-center">
          <h1 className="text-sm font-semibold text-white tracking-widest uppercase">
            Meziane Monitoring
          </h1>
          <p className="text-xs text-[#525252] mt-1">Portfolio immobilier</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-[10px] text-[#737373] uppercase tracking-wide block mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.fr"
              className={inputClass}
              required
              autoComplete="email"
            />
          </div>

          <div>
            <label className="text-[10px] text-[#737373] uppercase tracking-wide block mb-1">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className={inputClass}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="text-xs text-[#ef4444] bg-[#ef4444]/10 border border-[#ef4444]/20 rounded px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full h-9 bg-white text-black text-sm font-medium rounded hover:bg-[#e5e5e5] disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-2"
          >
            {loading ? 'Connexion…' : 'Se connecter →'}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-[#262626] text-center">
          <p className="text-[9px] text-[#404040]">
            Pour tester : admin@meziane.fr / admin123
          </p>
        </div>
      </div>
    </div>
  )
}
