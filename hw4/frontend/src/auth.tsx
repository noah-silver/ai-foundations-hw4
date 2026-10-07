import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export interface User {
  id: number
  name: string
  email: string
  first_name: string | null
  last_name: string | null
}

interface AuthValue {
  user: User | null
  loading: boolean
  signup: (data: SignupData) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export interface SignupData {
  first_name: string
  last_name: string
  email: string
  password: string
}

const TOKEN_KEY = 'cc_token'
const AuthContext = createContext<AuthValue | null>(null)

/** The saved session token, or null. Used by non-React callers like the chat client. */
export const authToken = () => localStorage.getItem(TOKEN_KEY)

async function authFetch<T>(url: string, body: object): Promise<{ token: string; user: User }> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Something went wrong. Please try again.')
  return data as T & { token: string; user: User }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // On load, restore the session if a saved token is still valid.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    fetch('/api/me', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setUser(data.user))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false))
  }, [])

  function persist(token: string, u: User) {
    localStorage.setItem(TOKEN_KEY, token)
    setUser(u)
  }

  const value: AuthValue = {
    user,
    loading,
    async signup(data) {
      const res = await authFetch('/api/signup', data)
      persist(res.token, res.user)
    },
    async login(email, password) {
      const res = await authFetch('/api/login', { email, password })
      persist(res.token, res.user)
    },
    async logout() {
      const token = localStorage.getItem(TOKEN_KEY)
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
      if (token) {
        await fetch('/api/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => {})
      }
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
