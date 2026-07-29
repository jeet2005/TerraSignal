import { Globe, Plane, Ship, Satellite, Zap, MapPin, ChevronDown, Flame, Cloud, Wind, Waves, Radio, Ship as ShipIcon, TrendingUp, Cpu, Wifi, Sun } from 'lucide-react'
import { useMapStore } from '../stores'
import { cn, getSeverityColor } from '../utils/cn'

const domainLayers = [
  { id: 'seismic', label: 'Earthquakes', icon: Zap, color: '#ef4444', domain: 'seismic' },
  { id: 'fire', label: 'Wildfires', icon: Flame, color: '#f97316', domain: 'fire' },
  { id: 'air_quality', label: 'Air Quality', icon: Cloud, color: '#3b82f6', domain: 'air_quality' },
  { id: 'weather', label: 'Weather', icon: Wind, color: '#06b6d4', domain: 'weather' },
  { id: 'disaster', label: 'Disasters', icon: Waves, color: '#8b5cf6', domain: 'disaster' },
  { id: 'aviation', label: 'Flights', icon: Radio, color: '#ec4899', domain: 'aviation' },
  { id: 'maritime', label: 'Ships', icon: ShipIcon, color: '#14b8a6', domain: 'maritime' },
  { id: 'transit', label: 'Transit', icon: TrendingUp, color: '#84cc16', domain: 'transit' },
  { id: 'space', label: 'Satellites', icon: Satellite, color: '#64748b', domain: 'space' },
]

function Section({ title, icon: Icon, children }: { title: string; icon: React.ComponentType<{ className?: string }>; children: React.ReactNode }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-5 h-5 text-primary-600" />
        <h3 className="font-semibold text-dark-900 dark:text-dark-100">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function EventRow({ event, onClick }: { event: any; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full p-3 rounded-lg border border-dark-200 dark:border-dark-800 hover:bg-dark-50 dark:hover:bg-dark-800/50 text-left transition-colors"
    >
      <div className="flex items-center gap-3">
        <div 
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: getSeverityColor(event.severity).replace('bg-', '').replace(' text-red-800', '').replace(' dark:bg-red-900/30 dark:text-red-300', '') }}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-dark-900 dark:text-dark-100 truncate">
              {event.event_type.replace(/_/g, ' ')}
            </span>
            <span className="px-1.5 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
              {event.domain}
            </span>
          </div>
          <p className="text-sm text-dark-500 truncate">
            {event.metadata?.city || event.properties?.place || 'Unknown location'}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-dark-400">
            {(event.severity * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-dark-500">
            {new Date(event.timestamp).toLocaleTimeString()}
          </p>
        </div>
      </div>
    </button>
  )
}

export function EarthWatch() {
  const { events, visibleDomains, toggleDomain } = useMapStore()
  
  const domains = [
    { id: 'seismic', label: 'Earthquakes', icon: Zap, color: '#ef4444', domain: 'seismic', count: events.filter(e => e.domain === 'seismic').length },
    { id: 'fire', label: 'Wildfires', icon: Flame, color: '#f97316', domain: 'fire', count: events.filter(e => e.domain === 'fire').length },
    { id: 'air_quality', label: 'Air Quality', icon: Cloud, color: '#3b82f6', domain: 'air_quality', count: events.filter(e => e.domain === 'air_quality').length },
    { id: 'weather', label: 'Severe Weather', icon: Wind, color: '#06b6d4', domain: 'weather', count: events.filter(e => e.domain === 'weather').length },
    { id: 'disaster', label: 'Disasters', icon: Waves, color: '#8b5cf6', domain: 'disaster', count: events.filter(e => e.domain === 'disaster').length },
  ]
  
  const hazardEvents = events.filter(e => 
    ['seismic', 'fire', 'weather', 'disaster', 'air_quality'].includes(e.domain)
  ).slice(0, 20)
  
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto">
      <div className="mb-6">
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Earth Watch
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Unified environmental hazard monitoring
        </p>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
        {domains.map(domain => {
          const Icon = domain.icon
          const isVisible = visibleDomains.has(domain.id)
          return (
            <button
              key={domain.id}
              onClick={() => toggleDomain(domain.id)}
              className={cn(
                'p-4 rounded-xl border transition-all',
                isVisible
                  ? `bg-gradient-to-br from-[${domain.color}] to-[${domain.color}] text-white border-transparent shadow-lg`
                  : 'bg-white dark:bg-dark-950 border-dark-200 dark:border-dark-800 hover:border-primary-300 dark:hover:border-primary-700'
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className={cn('w-5 h-5', isVisible ? '' : 'text-dark-400')} style={isVisible ? {} : { color: domain.color }} />
                <span className={cn('text-xs font-medium', isVisible ? 'opacity-90' : 'text-dark-500')}>
                  {domain.count}
                </span>
              </div>
              <span className={cn('text-sm font-medium', isVisible ? '' : 'text-dark-600 dark:text-dark-400')}>
                {domain.label}
              </span>
            </button>
          )
        })}
      </div>
      
      <div className="space-y-2">
        {hazardEvents.length === 0 ? (
          <div className="text-center py-12 text-dark-500">
            <div className="w-12 h-12 mx-auto mb-4 opacity-50 animate-pulse">🌍</div>
            <p className="text-lg font-medium">No environmental hazards detected</p>
            <p className="text-sm mt-1">Monitoring global seismic, fire, weather, and air quality data</p>
          </div>
        ) : (
          hazardEvents.map(event => (
            <EventRow key={event.id} event={event} onClick={() => selectEvent(event)} />
          ))
        )}
      </div>
    </div>
  )
}