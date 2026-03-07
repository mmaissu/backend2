import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'

const API_BASE = '/api'

async function parseErrorDetail(res: Response): Promise<string> {
  if (res.status === 0) return 'Cannot reach server. Start backend: docker compose up -d'
  if (res.status === 502) return 'Backend not responding. Run: docker compose up -d'
  if (res.status >= 500) return 'Server error. Check backend logs: docker compose logs backend'
  const err = await res.json().catch(() => ({}))
  const d = (err as { detail?: string | { msg: string }[] }).detail
  if (typeof d === 'string') return d
  if (Array.isArray(d) && d.length) return d.map((x: { msg?: string }) => x.msg || '').filter(Boolean).join('. ') || 'Request failed'
  return ''
}

export type User = { id: string; email: string; full_name: string | null; role: string; is_active: boolean }

type AuthContextType = {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)

  const refreshUser = useCallback(async () => {
    const t = localStorage.getItem('token')
    if (!t) {
      setUser(null)
      return
    }
    try {
      const res = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${t}` } })
      if (res.ok) setUser(await res.json())
      else setUser(null)
    } catch {
      setUser(null)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const msg = await parseErrorDetail(res)
      throw new Error(msg || 'Login failed')
    }
    const data = await res.json()
    setToken(data.access_token)
    localStorage.setItem('token', data.access_token)
    await refreshUser()
  }, [refreshUser])

  const register = useCallback(async (email: string, password: string, fullName?: string) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName ?? null }),
    })
    if (!res.ok) {
      const msg = await parseErrorDetail(res)
      throw new Error(msg || 'Registration failed')
    }
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }, [])

  useEffect(() => {
    if (token) refreshUser()
    else setUser(null)
  }, [token, refreshUser])

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function apiFetch(path: string, init?: RequestInit) {
  const token = localStorage.getItem('token')
  return fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })
}
