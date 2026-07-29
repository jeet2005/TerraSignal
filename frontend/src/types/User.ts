export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  alert_threshold: number
  default_layers: string[]
  units: 'metric' | 'imperial'
  offline_mode: boolean
  map_style: string
  auto_refresh: boolean
  refresh_interval: number
  voice_enabled: boolean
  language: string
  created_at: string
  updated_at: string
  last_login?: string
}