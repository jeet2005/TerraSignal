import { Bell, X, ChevronDown, ChevronUp } from 'lucide-react'
import { useUIStore } from '../stores/uiStore'
import { useMapStore } from '../stores/mapStore'
import { formatRelativeTime } from '../utils/format'
import { cn } from '../utils/cn'

export function AlertFeed() {
  const { bottomSheetOpen, bottomSheetContent, setBottomSheetOpen, setBottomSheetContent } = useUIStore()
  const { compoundEvents, events } = useMapStore()
  const [expanded, setExpanded] = useState(false)
  
  const recentEvents = [...events]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 50)
  
  const activeCompounds = compoundEvents
    .filter(e => e.status === 'active')
    .sort((a, b) => b.severity - a.severity)
    .slice(0, 10)
  
  const items = [
    ...activeCompounds.map(e => ({
      id: e.id,
      type: 'compound' as const,
      title: `${e.domains.length} domains affected`,
      location: e.metadata.city || `${e.centroid.coordinates[1].toFixed(2)}, ${e.centroid.coordinates[0].toFixed(2)}`,
      severity: e.severity,
      timestamp: e.detected_at,
      domains: e.domains,
    })),
    ...recentEvents.slice(0, 20).map(e => ({
      id: e.id,
      type: 'event' as const,
      title: e.event_type.replace(/_/g, ' '),
      location: e.metadata.city || e.properties.place || 'Unknown',
      severity: e.severity,
      timestamp: e.timestamp,
      domain: e.domain,
    })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  
  if (items.length === 0) return null
  
  return (
    <div className="h-20 lg:h-24 border-t border-dark-200 dark:border-dark-800 bg-white/80 dark:bg-dark-950/80 backdrop-blur-sm overflow-hidden">
      <div className="flex items-center justify-between h-8 px-3 bg-dark-50 dark:bg-dark-900 border-b border-dark-200 dark:border-dark-800">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-dark-500" />
          <span className="text-xs font-medium text-dark-700 dark:text-dark-300">Live Alert Feed</span>
          <span className="px-1.5 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
            {items.length}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 rounded hover:bg-dark-200 dark:hover:bg-dark-800"
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          <button
            onClick={() => {
              setBottomSheetContent('alerts')
              setBottomSheetOpen(true)
            }}
            className="p-1 rounded hover:bg-dark-200 dark:hover:bg-dark-800"
            aria-label="Open full feed"
          >
            <ChevronUp size={14} className="rotate-90" />
          </button>
        </div>
      </div>
      
      <div className={cn('flex-1 overflow-x-auto transition-all duration-300', expanded ? 'h-[calc(100%-2rem)]' : 'h-[calc(100%-2rem)]')}>
        <div className="flex gap-2 p-2 h-full items-start" role="list" aria-label="Recent alerts">
          {items.slice(0, expanded ? 30 : 8).map((item, index) => (
            <button
              key={item.id}
              onClick={() => {
                if (item.type === 'compound') {
                  // Fly to compound event
                } else {
                  // Fly to event
                }
              }}
              className={cn(
                'flex-shrink-0 w-56 lg:w-60 p-2 rounded-lg border transition-all duration-200',
                'hover:bg-dark-100 dark:hover:bg-dark-800',
                index === 0 ? 'border-primary-300 dark:border-primary-700' : 'border-dark-200 dark:border-dark-700'
              )}
              role="listitem"
            >
              <div className="flex items-start justify-between gap-1">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-dark-900 dark:text-dark-100 truncate">
                    {item.title}
                  </p>
                  <p className="text-xs text-dark-500 dark:text-dark-400 truncate mt-0.5">
                    {item.location}
                  </p>
                  <p className="text-[10px] text-dark-400 mt-1">
                    {formatRelativeTime(item.timestamp)}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <div
                    className={cn(
                      'w-2 h-2 rounded-full',
                      getSeverityColor(item.severity)
                    )}
                  />
                  {item.type === 'compound' && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
                      Compound
                    </span>
                  )}
                  {item.type === 'event' && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-dark-100 dark:bg-dark-800 text-dark-600 dark:text-dark-400 rounded">
                      {item.domain}
                    </span>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function getSeverityColor(severity: number) {
  if (severity >= 0.8) return 'bg-red-500'
  if (severity >= 0.6) return 'bg-orange-500'
  if (severity >= 0.4) return 'bg-yellow-500'
  if (severity >= 0.2) return 'bg-blue-500'
  return 'bg-gray-500'
}