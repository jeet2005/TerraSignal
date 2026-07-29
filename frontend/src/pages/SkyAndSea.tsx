import { Plane, Ship, Satellite, MapPin } from 'lucide-react'
import { useMapStore } from '../stores/mapStore'
import { cn } from '../utils/cn'

const movementLayers = [
  { id: 'aviation', label: 'Flights', icon: Plane, color: '#ec4899', count: 8432 },
  { id: 'maritime', label: 'Ships', icon: Ship, color: '#06b6d4', count: 2847 },
  { id: 'transit', label: 'Transit', icon: MapPin, color: '#84cc16', count: 15623 },
  { id: 'satellites', label: 'Satellites', icon: Satellite, color: '#64748b', count: 5842 },
]

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ComponentType<{ className?: string }>; color: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-dark-500">{label}</p>
          <p className="text-2xl font-bold text-dark-900 dark:text-dark-100">{value.toLocaleString()}</p>
        </div>
        <div className="p-3 rounded-xl" style={{ backgroundColor: `${color}10` }}>
          <Icon className="w-6 h-6" style={{ color }} />
        </div>
      </div>
    </div>
  )
}

function LayerToggle({ layer, isVisible, onToggle }: { layer: typeof movementLayers[0]; isVisible: boolean; onToggle: () => void }) {
  const Icon = layer.icon
  return (
    <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50 cursor-pointer transition-colors">
      <input
        type="checkbox"
        checked={isVisible}
        onChange={onToggle}
        className="w-5 h-5 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
      />
      <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${layer.color}15` }}>
        <Icon className="w-4 h-4" style={{ color: layer.color }} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-dark-900 dark:text-dark-100">{layer.label}</p>
        <p className="text-sm text-dark-500">{layer.count.toLocaleString()} active</p>
      </div>
      <div className="text-right">
        <div className={cn(
          'w-2 h-2 rounded-full mx-auto mb-1',
          isVisible ? `bg-[${layer.color}]` : 'bg-dark-300 dark:bg-dark-600'
        )} />
        <span className="text-xs text-dark-500">{isVisible ? 'Visible' : 'Hidden'}</span>
      </div>
    </label>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card p-4">
      <h3 className="font-semibold text-dark-900 dark:text-dark-100 mb-3">{title}</h3>
      {children}
    </div>
  )
}

function InfoCard({ title, stats, color }: { title: string; stats: { label: string; value: string }[]; color: string }) {
  return (
    <div className="card p-4 border-l-4" style={{ borderLeftColor: color }}>
      <h4 className="font-medium text-dark-900 dark:text-dark-100 mb-3">{title}</h4>
      <div className="grid grid-cols-2 gap-3">
        {stats.map((stat, i) => (
          <div key={i} className="p-2 bg-dark-50 dark:bg-dark-900 rounded-lg">
            <p className="text-xs text-dark-500">{stat.label}</p>
            <p className="font-bold text-dark-900 dark:text-dark-100">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export function SkyAndSea() {
  const { visibleDomains, toggleDomain, events } = useMapStore()
  
  const aviationEvents = events.filter(e => e.domain === 'aviation')
  const maritimeEvents = events.filter(e => e.domain === 'maritime')
  const transitEvents = events.filter(e => e.domain === 'transit')
  const satelliteEvents = events.filter(e => e.domain === 'satellites')
  
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto space-y-6">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Sky & Sea
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Everything in motion — flights, ships, transit, and orbital traffic
        </p>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Active Flights" value={aviationEvents.length} icon={Plane} color="#ec4899" />
        <StatCard label="Tracked Vessels" value={maritimeEvents.length} icon={Ship} color="#06b6d4" />
        <StatCard label="Transit Vehicles" value={transitEvents.length} icon={MapPin} color="#84cc16" />
        <StatCard label="Satellites" value={satelliteEvents.length} icon={Satellite} color="#64748b" />
      </div>
      
      <div className="space-y-4">
        <Section title="Map Layers">
          <div className="space-y-2">
            {movementLayers.map((layer) => (
              <LayerToggle
                key={layer.id}
                layer={layer}
                isVisible={visibleDomains.has(layer.id)}
                onToggle={() => toggleDomain(layer.id)}
              />
            ))}
          </div>
        </Section>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <InfoCard title="Aviation" color="#ec4899" stats={[
            { label: 'Commercial', value: '6,234' },
            { label: 'Cargo', value: '1,456' },
            { label: 'General Aviation', value: '523' },
            { label: 'Military', value: '219' },
          ]} />
          
          <InfoCard title="Maritime" color="#06b6d4" stats={[
            { label: 'Cargo Ships', value: '1,234' },
            { label: 'Tankers', value: '456' },
            { label: 'Passenger', value: '89' },
            { label: 'Fishing', value: '1,068' },
          ]} />
          
          <InfoCard title="Transit" color="#84cc16" stats={[
            { label: 'Buses', value: '8,234' },
            { label: 'Trains', value: '4,567' },
            { label: 'Trams', value: '2,345' },
            { label: 'Ferries', value: '477' },
          ]} />
          
          <InfoCard title="Orbital" color="#64748b" stats={[
            { label: 'Active', value: '3,241' },
            { label: 'Debris', value: '2,601' },
            { label: 'ISS', value: '1' },
            { label: 'Visible Tonight', value: '12' },
          ]} />
        </div>
      </div>
    </div>
  )
}