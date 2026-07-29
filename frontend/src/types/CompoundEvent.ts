export interface CompoundEvent {
  id: string
  detected_at: string
  expires_at: string
  centroid: {
    type: 'Point'
    coordinates: [number, number]
  }
  radius_km: number
  domains: string[]
  event_ids: string[]
  severity: number
  severity_tier: 'info' | 'low' | 'moderate' | 'high' | 'critical'
  news_headlines: string[]
  status: 'active' | 'expired' | 'acknowledged'
  metadata: Record<string, any>
}

export interface CompoundEventListResponse {
  events: CompoundEvent[]
  total: number
  page: number
  page_size: number
}

export interface StatCardsResponse {
  active_high_severity_clusters: number
  total_events_last_hour: number
  most_active_domain: string
}