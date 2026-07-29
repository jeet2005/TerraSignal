export interface AQIStation {
  id: string
  name: string
  lat: number
  lon: number
  pm25?: number
  pm10?: number
  no2?: number
  o3?: number
  aqi?: number
  updated: string
}