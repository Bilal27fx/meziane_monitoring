'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import api, { tokenStore } from '@/lib/api/client'
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

      // RFC-008: tokens en mémoire + sessionStorage (pas localStorage — vulnérable XSS)
      tokenStore.setTokens(response.data.access_token, response.data.refresh_token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 429) {
        setError('Trop de tentatives. Réessayez dans 5 minutes.')
      } else if (status === 401) {
        setError('Identifiants invalides. Vérifiez votre email et mot de passe.')
      } else {
        setError('Erreur de connexion. Réessayez dans un instant.')
      }
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    // RFC-008: révoque le refresh token côté serveur avant de vider la mémoire
    const refreshToken = tokenStore.getRefreshToken()
    if (refreshToken) {
      try {
        await api.post('/api/auth/logout', { refresh_token: refreshToken })
      } catch {
        // On logout même si la révocation échoue
      }
    }
    tokenStore.clear()
    router.push('/login')
  }

  const isAuthenticated = () => {
    return !!tokenStore.getAccessToken() || !!tokenStore.getRefreshToken()
  }

  return { login, logout, loading, error, isAuthenticated }
}
