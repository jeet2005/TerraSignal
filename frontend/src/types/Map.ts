export type Domain = 
  | 'seismic' 
  | 'fire' 
  | 'air_quality' 
  | 'weather' 
  | 'disaster'
  | 'aviation' 
  | 'maritime' 
  | 'transit' 
  | 'space'
  | 'crypto' 
  | 'fx' 
  | 'macro' 
  | 'commodities' 
  | 'remittances' 
  | 'worldbank'
  | 'wikipedia' 
  | 'github' 
  | 'hackernews' 
  | 'cloudflare'
  | 'solar' 
  | 'iss' 
  | 'satellites'
  | 'anomaly'

export interface MapViewport {
  lat: number
  lon: number
  zoom: number
}

export interface MapFilters {
  severityMin: number
  severityMax: number
  domains: Domain[]
  timeRangeHours: number
}