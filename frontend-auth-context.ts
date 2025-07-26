import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../services/api'

export interface User {
  id: number
  username: string
  email: string
  role: 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
  manager_id?: number
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (username: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('authToken')
    const storedRole = localStorage.getItem('userRole')
    
    if (storedToken && storedRole) {
      setToken(storedToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      // Fetch current user info
      fetchCurrentUser(storedToken)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      })
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch current user:', error)
      // Clear invalid token
      localStorage.removeItem('authToken')
      localStorage.removeItem('userRole')
      setToken(null)
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string) => {
    try {
      setLoading(true)
      const response = await api.post('/auth/login', { username })
      const { access_token, role } = response.data
      
      setToken(access_token)
      localStorage.setItem('authToken', access_token)
      localStorage.setItem('userRole', role)
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Fetch user details
      await fetchCurrentUser(access_token)
    } catch (error: any) {
      setLoading(false)
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('authToken')
    localStorage.removeItem('userRole')
    delete api.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}