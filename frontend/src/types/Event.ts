export interface Event {
  id: string
  source: string
  domain: string
  event_type: string
  severity: number
  geometry: {
    type: 'Point'
    coordinates: [number, number]
  }
  properties: Record<string, any>
  metadata: EventMetadata
  timestamp: string
  created_at: string
}

export interface EventMetadata {
  severity_tier: 'info' | 'low' | 'moderate' | 'high' | 'critical'
  country?: string
  admin1?: string
  city?: string
  timezone?: string
  source_updated?: string
  [key: string]: any
}

export interface EventListResponse {
  events: Event[]
  total: number
  page: number
  page_size: number
}

export interface EventStatsResponse {
  period_hours: number
  domains: Array<{
    domain: string
    count: number
    avg_severity: number
    max_severity: number
  }>
  total: number
}