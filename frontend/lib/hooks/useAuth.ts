'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api/client'
import type { AuthTokens, LoginCredentials } from '@/lib/types'

export function useAuth() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (credentials: LoginCredentials) => {
    setLoading(true)
    setError(null)
    try {
      const formData = new URLSearchParams()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await api.post<AuthTokens>('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      localStorage.setItem('access_token', response.data.access_token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 401) {
        setError('Identifiants invalides. Vérifiez votre email et mot de passe.')
      } else {
        setError('Erreur de connexion. Réessayez dans un instant.')
      }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    router.push('/login')
  }

  const isAuthenticated = () => {
    if (typeof window === 'undefined') return false
    return !!localStorage.getItem('access_token')
  }

  return { login, logout, loading, error, isAuthenticated }
}
