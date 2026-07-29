import { AlertTriangle, ChevronDown, Clock, MapPin, X } from 'lucide-react'
import { useMapStore, useUIStore } from '../stores'
import { formatRelativeTime } from '../utils/format'
import { cn, getSeverityColor } from '../utils/cn'

export function ThreatBoard() {
  const { compoundEvents, events } = useMapStore()
  const { setSidebarPanel, setSidebarOpen, isMobile } = useUIStore()
  
  const activeClusters = compoundEvents.filter(e => e.status === 'active')
  const stats = {
    highSeverity: activeClusters.filter(e => e.severity >= 0.7).length,
    totalEvents: events.filter(e => 
      new Date(e.timestamp) > new Date(Date.now() - 3600000)
    ).length,
    topDomain: 'seismic',
  }
  
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto">
      <div className="mb-6">
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Threat Board
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Multi-domain compound events ranked by combined severity
        </p>
      </div>
      
      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <StatCard
          title="High-Severity Clusters"
          value={stats.highSeverity}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Events Last Hour"
          value={stats.totalEvents}
          icon={Clock}
          color="blue"
        />
        <StatCard
          title="Most Active Domain"
          value={stats.topDomain}
          icon={MapPin}
          color="purple"
        />
      </div>
      
      {/* Compound Events List */}
      <div className="space-y-3">
        {activeClusters.length === 0 ? (
          <div className="text-center py-12 text-dark-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">No active compound events</p>
            <p className="text-sm mt-1">Monitoring for multi-domain correlations...</p>
          </div>
        ) : (
          activeClusters.map((cluster) => (
            <CompoundEventCard
              key={cluster.id}
              cluster={cluster}
              onClick={() => {
                setSidebarPanel('threat')
                if (isMobile) setSidebarOpen(false)
              }}
            />
          ))
        )}
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }: { title: string; value: number | string; icon: React.ComponentType<{ className?: string }>; color: string }) {
  const colors = {
    red: 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800',
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800',
  }
  
  return (
    <div className={cn('p-4 rounded-xl border', colors[color as keyof typeof colors])}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-2xl lg:text-3xl font-bold mt-1">{value}</p>
        </div>
        <Icon className="w-10 h-10 opacity-50" />
      </div>
    </div>
  )
}

function CompoundEventCard({ cluster, onClick }: { cluster: any; onClick: () => void }) {
  const [expanded, setExpanded] = useState(false)
  
  const domains = cluster.domains.map((d: string) => 
    d.charAt(0).toUpperCase() + d.slice(1).replace(/_/g, ' ')
  )
  
  return (
    <div className="card border-l-4" style={{ borderLeftColor: getSeverityColor(cluster.severity) }}>
      <button
        onClick={onClick}
        className="w-full p-4 text-left hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <span className={cn(
                'px-2.5 py-0.5 rounded-full text-xs font-medium',
                getSeverityColor(cluster.severity),
                cluster.severity >= 0.8 && 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
                cluster.severity >= 0.6 && 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
                cluster.severity >= 0.4 && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
                cluster.severity < 0.4 && 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
              )}>
                {cluster.severity_tier.toUpperCase()}
              </span>
              <span className="text-sm font-mono text-dark-500">
                {(cluster.severity * 100).toFixed(0)}%
              </span>
              <span className="text-xs text-dark-400">
                {formatRelativeTime(cluster.detected_at)}
              </span>
            </div>
            
            <p className="font-medium text-dark-900 dark:text-dark-100 mb-1">
              {cluster.metadata.city || `${cluster.centroid.coordinates[1].toFixed(2)}, ${cluster.centroid.coordinates[0].toFixed(2)}`}
            </p>
            
            <div className="flex flex-wrap gap-1.5 mb-2">
              {domains.slice(0, 4).map((domain: string) => (
                <span key={domain} className="px-2 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
                  {domain}
                </span>
              ))}
              {cluster.domains.length > 4 && (
                <span className="px-2 py-0.5 text-xs bg-dark-100 dark:bg-dark-800 text-dark-600 dark:text-dark-400 rounded">
                  +{cluster.domains.length - 4} more
                </span>
              )}
            </div>
            
            {expanded && cluster.news_headlines.length > 0 && (
              <div className="border-t border-dark-200 dark:border-dark-800 pt-3 mt-3 space-y-1">
                <p className="text-xs font-medium text-dark-500">Recent Headlines:</p>
                {cluster.news_headlines.slice(0, 3).map((headline: string, i: number) => (
                  <p key={i} className="text-xs text-dark-600 dark:text-dark-400 line-clamp-1">
                    {headline}
                  </p>
                ))}
              </div>
            )}
          </div>
          
          <button
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
            className="p-1 text-dark-400 hover:text-dark-600 dark:hover:text-dark-300"
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            <ChevronDown className={cn('w-5 h-5 transition-transform', expanded && 'rotate-180')} />
          </button>
        </div>
      </button>
    </div>
  )
}