import { useAuthStore } from '../stores/authStore'
import type { Event, CompoundEvent, EventFilters, User, AuthTokens, ApiResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private async getHeaders(): Promise<HeadersInit> {
    const { accessToken } = useAuthStore.getState()
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }
    return headers
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = await this.getHeaders()
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        useAuthStore.getState().clearAuth()
        window.location.href = '/login'
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `Request failed: ${response.status}`)
    }
    
    if (response.status === 204) {
      return undefined as T
    }
    
    return response.json()
  }
  
  // Auth
  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Login failed')
    }
    
    return response.json()
  }
  
  async register(email: string, password: string, fullName?: string): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
  }
  
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return this.request<AuthTokens>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  }
  
  async getMe(): Promise<User> {
    return this.request<User>('/auth/me')
  }
  
  async updateMe(data: Partial<User>): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }
  
  // Events
  async getEvents(filters?: EventFilters): Promise<ApiResponse<Event[]>> {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, String(v)))
          } else {
            params.append(key, String(value))
          }
        }
      })
    }
    return this.request<ApiResponse<Event[]>>(`/events?${params.toString()}`)
  }
  
  async getLatestEvents(limit = 100, domain?: string): Promise<Event[]> {
    const params = new URLSearchParams({ limit: String(limit) })
    if (domain) params.append('domain', domain)
    return this.request<Event[]>(`/events/latest?${params.toString()}`)
  }
  
  async getEvent(eventId: string): Promise<Event> {
    return this.request<Event>(`/events/${eventId}`)
  }
  
  async getDomains(): Promise<string[]> {
    return this.request<string[]>('/events/domains')
  }
  
  async getEventTypes(domain?: string): Promise<string[]> {
    const params = domain ? `?domain=${domain}` : ''
    return this.request<string[]>(`/events/types${params}`)
  }
  
  async getEventStats(hours = 24): Promise<any> {
    return this.request<any>(`/events/stats?hours=${hours}`)
  }
  
  // Compound Events
  async getCompoundEvents(params?: {
    status?: string
    severity_min?: number
    page?: number
    page_size?: number
  }): Promise<ApiResponse<CompoundEvent[]>> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value))
        }
      })
    }
    return this.request<ApiResponse<CompoundEvent[]>>(`/compound?${searchParams.toString()}`)
  }
  
  async getCompoundEvent(eventId: string): Promise<CompoundEvent> {
    return this.request<CompoundEvent>(`/compound/${eventId}`)
  }
  
  async getCompoundStats(): Promise<any> {
    return this.request<any>('/compound/stats')
  }
  
  // City Scope
  async getCityScope(citySlug: string): Promise<any> {
    return this.request<any>(`/city-scope/${citySlug}`)
  }
  
  // Push Notifications
  async subscribePush(subscription: PushSubscription): Promise<void> {
    return this.request<void>('/push/subscribe', {
      method: 'POST',
      body: JSON.stringify(subscription.toJSON()),
    })
  }
  
  async unsubscribePush(endpoint: string): Promise<void> {
    return this.request<void>(`/push/unsubscribe/${encodeURIComponent(endpoint)}`, {
      method: 'DELETE',
    })
  }
  
  // WebSocket URL
  getWebSocketUrl(): string {
    const wsBase = API_BASE.replace('http', 'ws').replace('/api/v1', '')
    return `${wsBase}/ws`
  }
}

export const api = new ApiClient()