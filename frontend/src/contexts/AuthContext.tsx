import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { api } from '../services/api'

interface User {
  id: string
  username: string
  email: string
  role: string
  full_name?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: { user: User; token: string } }
  | { type: 'CLEAR_USER' }

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('authToken'),
  isLoading: true,
  isAuthenticated: false,
}

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_USER':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      }
    case 'CLEAR_USER':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      }
    default:
      return state
  }
}

interface AuthContextType {
  state: AuthState
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/api/auth/login', { email, password })
      const { access_token, user } = response.data
      
      localStorage.setItem('authToken', access_token)
      dispatch({ type: 'SET_USER', payload: { user, token: access_token } })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('authToken')
    dispatch({ type: 'CLEAR_USER' })
  }

  const checkAuth = async () => {
    const token = localStorage.getItem('authToken')
    if (!token) {
      dispatch({ type: 'SET_LOADING', payload: false })
      return
    }

    try {
      const response = await api.get('/api/auth/me')
      dispatch({ 
        type: 'SET_USER', 
        payload: { user: response.data, token } 
      })
    } catch (error) {
      localStorage.removeItem('authToken')
      dispatch({ type: 'CLEAR_USER' })
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <AuthContext.Provider value={{ state, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}