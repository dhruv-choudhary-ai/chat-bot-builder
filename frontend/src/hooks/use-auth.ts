import { useState, useEffect } from 'react'
import { tokenManager, authAPI, userAPI } from '@/lib/api'

interface UseAuthReturn {
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  user: any | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export function useAuth(type: 'user' | 'admin' = 'user'): UseAuthReturn {
  const [token, setToken] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const storedToken = tokenManager.getToken()
        if (storedToken && tokenManager.isAuthenticated()) {
          setToken(storedToken)
          setIsAuthenticated(true)
          
          // Try to get user info
          try {
            if (type === 'admin') {
              const userInfo = await authAPI.getCurrentAdmin()
              setUser(userInfo)
            } else {
              const userInfo = await userAPI.getCurrentUser()
              setUser(userInfo)
            }
          } catch (error) {
            console.error('Failed to get user info:', error)
            // Token might be invalid, clear it
            tokenManager.removeToken()
            setToken(null)
            setIsAuthenticated(false)
            setUser(null)
          }
        } else {
          setToken(null)
          setIsAuthenticated(false)
          setUser(null)
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        setToken(null)
        setIsAuthenticated(false)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [type])

  const login = async (email: string, password: string) => {
    try {
      let response
      if (type === 'admin') {
        response = await authAPI.login(email, password)
      } else {
        response = await userAPI.login(email, password)
      }

      tokenManager.setToken(response.access_token)
      setToken(response.access_token)
      setIsAuthenticated(true)

      // Get user info after login
      try {
        if (type === 'admin') {
          const userInfo = await authAPI.getCurrentAdmin()
          setUser(userInfo)
        } else {
          const userInfo = await userAPI.getCurrentUser()
          setUser(userInfo)
        }
      } catch (error) {
        console.error('Failed to get user info after login:', error)
      }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    tokenManager.removeToken()
    setToken(null)
    setIsAuthenticated(false)
    setUser(null)
    
    // Redirect to login page
    if (type === 'admin') {
      window.location.href = '/admin/login'
    } else {
      window.location.href = '/login'
    }
  }

  return {
    token,
    isAuthenticated,
    loading,
    user,
    login,
    logout,
  }
}