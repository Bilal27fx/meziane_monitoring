import axios from 'axios'

/**
 * RFC-008: token en mémoire (module-level) au lieu de localStorage
 * localStorage est vulnérable XSS — un script injecté peut voler le token.
 * La mémoire est inaccessible depuis l'extérieur du module.
 * Inconvénient : perdu au refresh page → géré par le refresh token en cookie httpOnly.
 */
let _accessToken: string | null = null
let _refreshToken: string | null = null

export const tokenStore = {
  setTokens(access: string, refresh: string) {
    _accessToken = access
    _refreshToken = refresh
    // Refresh token persiste dans sessionStorage (moins risqué que localStorage)
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('refresh_token', refresh)
    }
  },
  getAccessToken: () => _accessToken,
  getRefreshToken: () => {
    if (!_refreshToken && typeof window !== 'undefined') {
      _refreshToken = sessionStorage.getItem('refresh_token')
    }
    return _refreshToken
  },
  getRole: (): string | null => {
    if (!_accessToken) return null
    try {
      const payload = JSON.parse(atob(_accessToken.split('.')[1]))
      return payload.role ?? null
    } catch {
      return null
    }
  },
  clear() {
    _accessToken = null
    _refreshToken = null
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('refresh_token')
    }
  },
}

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = tokenStore.getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let _refreshing = false
let _refreshQueue: Array<(token: string) => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = tokenStore.getRefreshToken()
      if (!refreshToken) {
        tokenStore.clear()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(error)
      }
      // RFC-008: auto-refresh — si un refresh est en cours, les requêtes suivantes attendent
      if (_refreshing) {
        return new Promise((resolve) => {
          _refreshQueue.push((newToken) => {
            original.headers.Authorization = `Bearer ${newToken}`
            resolve(api(original))
          })
        })
      }
      _refreshing = true
      try {
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/auth/refresh`,
          { refresh_token: refreshToken }
        )
        tokenStore.setTokens(data.access_token, data.refresh_token)
        _refreshQueue.forEach((cb) => cb(data.access_token))
        _refreshQueue = []
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        tokenStore.clear()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        _refreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
