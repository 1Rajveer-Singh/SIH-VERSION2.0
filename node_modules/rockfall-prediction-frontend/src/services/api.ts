import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      localStorage.removeItem('currentUser')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API methods
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    username: string
    full_name: string
    role: string
    is_active: boolean
    created_at: string
  }
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post('/api/auth/login', credentials)
    return response.data
  },
  
  logout: async (): Promise<void> => {
    await api.post('/api/auth/logout')
  },
  
  getCurrentUser: async (): Promise<LoginResponse['user']> => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
  
  testConnection: async (): Promise<boolean> => {
    try {
      console.log('=== Testing backend connection ===')
      console.log('API_BASE_URL:', API_BASE_URL)
      console.log('Making request to:', API_BASE_URL + '/health')
      
      const response = await api.get('/health', { timeout: 5000 })
      console.log('✅ Connection test successful:', response.data)
      return true
    } catch (error: any) {
      console.error('❌ Connection test failed:')
      console.error('Error message:', error.message)
      console.error('Error code:', error.code)
      console.error('Response status:', error.response?.status)
      console.error('Response data:', error.response?.data)
      console.error('Full error:', error)
      return false
    }
  }
}

// Auth utilities
export const authUtils = {
  setToken: (token: string) => {
    localStorage.setItem('authToken', token)
  },
  
  getToken: (): string | null => {
    return localStorage.getItem('authToken')
  },
  
  removeToken: () => {
    localStorage.removeItem('authToken')
  },
  
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('authToken')
  },
  
  setUser: (user: LoginResponse['user']) => {
    localStorage.setItem('currentUser', JSON.stringify(user))
  },
  
  getUser: (): LoginResponse['user'] | null => {
    const userData = localStorage.getItem('currentUser')
    return userData ? JSON.parse(userData) : null
  },
  
  removeUser: () => {
    localStorage.removeItem('currentUser')
  },
  
  clearAuth: () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('currentUser')
  }
}

export default api