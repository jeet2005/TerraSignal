export interface WeatherResponse {
  current: {
    temperature_2m: number
    relative_humidity_2m: number
    apparent_temperature: number
    weather_code: number
    wind_speed_10m: number
    wind_direction_10m: number
  }
  hourly: {
    time: string[]
    temperature_2m: number[]
    precipitation_probability: number[]
    weather_code: number[]
  }
  daily: {
    time: string[]
    weather_code: number[]
    temperature_2m_max: number[]
    temperature_2m_min: number[]
    precipitation_probability_max: number[]
  }
}

export interface WeatherCode {
  code: number
  description: string
  icon: string
}

export const WEATHER_CODES: Record<number, WeatherCode> = {
  0: { code: 0, description: 'Clear sky', icon: 'sun' },
  1: { code: 1, description: 'Mainly clear', icon: 'sun' },
  2: { code: 2, description: 'Partly cloudy', icon: 'cloud' },
  3: { code: 3, description: 'Overcast', icon: 'cloud' },
  45: { code: 45, description: 'Fog', icon: 'cloud' },
  48: { code: 48, description: 'Depositing rime fog', icon: 'cloud' },
  51: { code: 51, description: 'Light drizzle', icon: 'cloud-rain' },
  53: { code: 53, description: 'Moderate drizzle', icon: 'cloud-rain' },
  55: { code: 55, description: 'Dense drizzle', icon: 'cloud-rain' },
  56: { code: 56, description: 'Light freezing drizzle', icon: 'cloud-rain' },
  57: { code: 57, description: 'Dense freezing drizzle', icon: 'cloud-rain' },
  61: { code: 61, description: 'Slight rain', icon: 'cloud-rain' },
  63: { code: 63, description: 'Moderate rain', icon: 'cloud-rain' },
  65: { code: 65, description: 'Heavy rain', icon: 'cloud-rain' },
  66: { code: 66, description: 'Light freezing rain', icon: 'cloud-rain' },
  67: { code: 67, description: 'Heavy freezing rain', icon: 'cloud-rain' },
  71: { code: 71, description: 'Slight snow fall', icon: 'cloud' },
  73: { code: 73, description: 'Moderate snow fall', icon: 'cloud' },
  75: { code: 75, description: 'Heavy snow fall', icon: 'cloud' },
  77: { code: 77, description: 'Snow grains', icon: 'cloud' },
  80: { code: 80, description: 'Slight rain showers', icon: 'cloud-rain' },
  81: { code: 81, description: 'Moderate rain showers', icon: 'cloud-rain' },
  82: { code: 82, description: 'Violent rain showers', icon: 'cloud-rain' },
  85: { code: 85, description: 'Slight snow showers', icon: 'cloud' },
  86: { code: 86, description: 'Heavy snow showers', icon: 'cloud' },
  95: { code: 95, description: 'Thunderstorm', icon: 'alert-triangle' },
  96: { code: 96, description: 'Thunderstorm with slight hail', icon: 'alert-triangle' },
  99: { code: 99, description: 'Thunderstorm with heavy hail', icon: 'alert-triangle' },
}