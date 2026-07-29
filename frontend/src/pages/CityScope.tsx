export function CityScope() {
  const [activeTab, setActiveTab] = useState<'weather' | 'transit' | 'aqi' | 'wiki' | 'news'>('weather')
  
  const city = {
    name: 'Tokyo',
    country: 'Japan',
    lat: 35.6762,
    lon: 139.6503,
    weather: {
      current: { temperature: 22, apparent_temperature: 23, humidity: 65, wind_speed: 12, wind_direction: 180, weather_code: 1 },
      hourly: { time: ['14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00'], temperature_2m: [22, 22, 21, 20, 19, 18, 17, 17, 16, 16, 15, 15], weather_code: [1, 1, 2, 2, 3, 51, 51, 53, 53, 51, 2, 1], precipitation_probability: [10, 5, 5, 10, 20, 30, 40, 35, 25, 15, 10, 5] },
      daily: { time: ['Today', 'Tomorrow', 'Mon', 'Tue', 'Wed'], weather_code: [1, 2, 3, 51, 1], temperature_2m_max: [24, 22, 20, 19, 23], temperature_2m_min: [16, 17, 18, 15, 17], precipitation_probability_max: [10, 20, 40, 60, 15] }
    },
    transit: [
      { id: 'T001', route: 'JR Yamanote Line', lat: 35.6895, lon: 139.6917, bearing: 45, speed: 65, updated: new Date().toISOString() },
      { id: 'T002', route: 'Tokyo Metro Ginza', lat: 35.6722, lon: 139.7614, bearing: 120, speed: 45, updated: new Date().toISOString() },
      { id: 'T003', route: 'Toei Asakusa Line', lat: 35.6631, lon: 139.7345, bearing: 280, speed: 55, updated: new Date().toISOString() },
    ],
    aqi: [
      { id: 'aq1', name: 'Shibuya Station', pm25: 12, pm10: 18, no2: 25, o3: 45, aqi: 35, updated: new Date().toISOString() },
      { id: 'aq2', name: 'Shinjuku West', pm25: 18, pm10: 28, no2: 35, o3: 38, aqi: 52, updated: new Date().toISOString() },
      { id: 'aq3', name: 'Imperial Palace', pm25: 8, pm10: 14, no2: 18, o3: 52, aqi: 28, updated: new Date().toISOString() },
    ],
    wiki: [
      { title: 'Tokyo', user: 'JapanBot', time: '2 min ago', comment: 'Updated population figure', diff_url: '#' },
      { title: '2024 Noto earthquake', user: 'EarthquakeBot', time: '5 min ago', comment: 'Added casualty updates', diff_url: '#' },
      { title: 'Tokyo Metro', user: 'TransitFan', time: '12 min ago', comment: 'New station opening', diff_url: '#' },
    ],
    news: [
      { title: 'Tokyo prepares for typhoon season', url: '#', source: 'NHK', published: '2 hours ago', tension_score: 0.3, location: 'Tokyo' },
      { title: 'New disaster prevention measures', url: '#', source: 'Japan Times', published: '5 hours ago', tension_score: 0.2, location: 'Tokyo' },
    ],
  }
  
  const tabs = [
    { id: 'weather', label: 'Weather', icon: Sun },
    { id: 'transit', label: 'Transit', icon: Train },
    { id: 'aqi', label: 'Air Quality', icon: Activity },
    { id: 'wiki', label: 'Wikipedia', icon: Globe },
    { id: 'news', label: 'News', icon: Newspaper },
  ] as const
  
  const w = city.weather
  const c = w.current
  const h = w.hourly
  const d = w.daily
  
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-dark-200 dark:border-dark-800 bg-white dark:bg-dark-950 sticky top-0 z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-dark-900 dark:text-dark-100">{city.name}</h1>
              <p className="text-sm text-dark-500">{city.country} • {city.lat.toFixed(2)}, {city.lon.toFixed(2)}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-1 overflow-x-auto pb-2">
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                  activeTab === tab.id
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                    : 'text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800'
                )}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'weather' && (
          <>
            <div className="grid grid-cols-4 gap-3">
              <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
                <p className="text-xs text-dark-500">Temperature</p>
                <div className="flex items-center gap-2 mt-1">
                  <WeatherIcon code={c.weather_code} className="w-8 h-8" />
                  <span className="font-bold text-dark-900 dark:text-dark-100">{c.temperature}°C</span>
                </div>
              </div>
              <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
                <p className="text-xs text-dark-500">Feels Like</p>
                <div className="flex items-center gap-2 mt-1">
                  <Sun className="w-6 h-6 text-orange-500" />
                  <span className="font-bold text-dark-900 dark:text-dark-100">{c.apparent_temperature}°C</span>
                </div>
              </div>
              <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
                <p className="text-xs text-dark-500">Humidity</p>
                <div className="flex items-center gap-2 mt-1">
                  <Droplet className="w-6 h-6 text-blue-500" />
                  <span className="font-bold text-dark-900 dark:text-dark-100">{c.humidity}%</span>
                </div>
              </div>
              <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
                <p className="text-xs text-dark-500">Wind</p>
                <div className="flex items-center gap-2 mt-1">
                  <Wind className="w-6 h-6 text-gray-500" />
                  <span className="font-bold text-dark-900 dark:text-dark-100">{c.wind_speed} km/h</span>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold text-dark-900 dark:text-dark-100">Hourly Forecast</h3>
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {h.time.slice(0, 12).map((time, i) => (
                    <div key={i} className="flex-shrink-0 w-20 p-2 rounded-lg bg-dark-50 dark:bg-dark-900 text-center">
                      <p className="text-xs text-dark-500">{time}</p>
                      <WeatherIcon code={h.weather_code[i]} className="w-8 h-8 mx-auto my-1" />
                      <p className="font-semibold text-dark-900 dark:text-dark-100">{h.temperature_2m[i]}°C</p>
                      <p className="text-[10px] text-blue-600">{h.precipitation_probability[i]}% rain</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold text-dark-900 dark:text-dark-100">5-Day Forecast</h3>
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {d.time.map((day, i) => (
                    <div key={i} className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg text-center">
                      <p className="text-sm font-medium text-dark-900 dark:text-dark-100">{day}</p>
                      <WeatherIcon code={d.weather_code[i]} className="w-10 h-10 mx-auto my-1" />
                      <p className="font-semibold text-dark-900 dark:text-dark-100">{d.temperature_2m_max[i]}° / {d.temperature_2m_min[i]}°</p>
                      <p className="text-[10px] text-blue-600">{d.precipitation_probability_max[i]}% rain</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Sun className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold text-dark-900 dark:text-dark-100">Details</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Sunrise</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">05:42</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Sunset</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">18:23</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">UV Index</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">5 (Moderate)</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Pressure</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">1013 hPa</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Visibility</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">10 km</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Cloud Cover</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">25%</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-200 dark:border-dark-800">
                    <span className="text-dark-600 dark:text-dark-400">Wind Direction</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">{c.wind_direction}°</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-dark-600 dark:text-dark-400">Last Updated</span>
                    <span className="font-medium text-dark-900 dark:text-dark-100">{formatRelativeTime(new Date().toISOString())}</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default CityScope