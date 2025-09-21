import api from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  role?: string
}

export interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login', credentials)
    const { access_token, token_type, user } = response.data
    
    // Store token
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    return response.data
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post('/api/auth/register', data)
    const { access_token, token_type, user } = response.data
    
    // Store token
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  async getProfile(): Promise<User> {
    const response = await api.get('/api/auth/profile')
    return response.data
  },

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  getToken(): string | null {
    return localStorage.getItem('token')
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  }
}

export default authService