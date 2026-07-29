import { useEffect, useState } from 'react'
import { X, Clock, MapPin, AlertCircle, ExternalLink } from 'lucide-react'
import { useUIStore } from '../stores/uiStore'
import { cn, getSeverityColor, formatRelativeTime } from '../utils/cn'
import type { Event, CompoundEvent } from '../types'

interface EventPopupProps {
  event: Event | CompoundEvent | null
  onClose: () => void
}

export function EventPopup({ event, onClose }: EventPopupProps) {
  const [expanded, setExpanded] = useState(false)
  const { isMobile } = useUIStore()
  
  if (!event) return null
  
  const isCompound = 'domains' in event
  const severity = event.severity
  const tier = isCompound ? event.severity_tier : getSeverityTier(severity)
  
  const title = isCompound 
    ? `${event.domains.length}-Domain Compound Event`
    : event.event_type.replace(/_/g, ' ')
  
  const location = isCompound
    ? event.metadata?.city || `${event.centroid.coordinates[1].toFixed(2)}, ${event.centroid.coordinates[0].toFixed(2)}`
    : event.metadata?.city || event.properties?.place || 'Unknown location'
  
  const domains = isCompound ? event.domains : [event.domain]
  
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [onClose])
  
  return (
    <div className={cn(
      'fixed bottom-24 left-4 right-4 lg:left-auto lg:right-4 lg:w-96 z-40 animate-in',
      isMobile ? 'bottom-20 left-2 right-2 lg:w-full' : ''
    )}>
      <div className="glass-strong rounded-xl shadow-xl border border-dark-200 dark:border-dark-800 overflow-hidden">
        {/* Header */}
        <div className={cn(
          'flex items-start justify-between p-4 border-b border-dark-200 dark:border-dark-800',
          `border-l-4 ${getSeverityColor(severity).replace('bg-', 'border-').replace('text-', 'border-')}`
        )}>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className={cn(
                'px-2 py-0.5 rounded-full text-xs font-medium',
                getSeverityColor(severity)
              )}>
                {tier.toUpperCase()}
              </span>
              <span className="text-xs font-mono text-dark-500">
                {(severity * 100).toFixed(0)}%
              </span>
              {isCompound && (
                <span className="px-2 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
                  COMPOUND
                </span>
              )}
            </div>
            <h3 className="font-semibold text-dark-900 dark:text-dark-100 truncate">
              {title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-dark-100 dark:hover:bg-dark-800 text-dark-400 hover:text-dark-600 dark:hover:text-dark-300"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-4 space-y-3 max-h-[50vh] overflow-y-auto">
          {/* Location & Time */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-dark-400" />
              <span className="text-dark-600 dark:text-dark-400 truncate">{location}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-dark-400" />
              <span className="text-dark-600 dark:text-dark-400">
                {formatRelativeTime(isCompound ? event.detected_at : event.timestamp)}
              </span>
            </div>
          </div>
          
          {/* Domains */}
          <div>
            <p className="text-xs font-medium text-dark-500 mb-1">DOMAINS</p>
            <div className="flex flex-wrap gap-1.5">
              {domains.map((domain: string) => (
                <span key={domain} className="px-2 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
                  {domain.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
          
          {/* Event-specific details */}
          {isCompound ? (
            <CompoundDetails event={event} />
          ) : (
            <EventDetails event={event} />
          )}
          
          {/* News headlines */}
          {isCompound && event.news_headlines?.length > 0 && (
            <div className="border-t border-dark-200 dark:border-dark-800 pt-3">
              <p className="text-xs font-medium text-dark-500 mb-2">RECENT HEADLINES</p>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {event.news_headlines.slice(0, 5).map((headline: string, i: number) => (
                  <p key={i} className="text-xs text-dark-600 dark:text-dark-400 line-clamp-2">
                    {headline}
                  </p>
                ))}
              </div>
            </div>
          )}
          
          {/* Actions */}
          <div className="flex gap-2 pt-2 border-t border-dark-200 dark:border-dark-800">
            <button className="flex-1 btn-secondary text-sm">
              <MapPin className="w-4 h-4 mr-1" />
              Fly To
            </button>
            <button className="flex-1 btn-primary text-sm">
              <ExternalLink className="w-4 h-4 mr-1" />
              Details
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function EventDetails({ event }: { event: Event }) {
  const props = event.properties || {}
  
  return (
    <div className="space-y-2">
      {props.magnitude && (
        <DetailRow label="Magnitude" value={`${props.magnitude} ${props.magType || ''}`} />
      )}
      {props.depth && (
        <DetailRow label="Depth" value={`${props.depth} km`} />
      )}
      {props.alert && (
        <DetailRow label="Alert Level" value={props.alert.toUpperCase()} />
      )}
      {props.tsunami !== undefined && (
        <DetailRow label="Tsunami" value={props.tsunami ? 'Yes' : 'No'} />
      )}
    </div>
  )
}

function CompoundDetails({ event }: { event: CompoundEvent }) {
  return (
    <div className="space-y-2">
      <DetailRow label="Contributing Events" value={event.event_ids.length.toString()} />
      <DetailRow label="Radius" value={`${event.radius_km} km`} />
      {event.metadata?.estimated_population && (
        <DetailRow label="Est. Population" value={formatNumber(event.metadata.estimated_population)} />
      )}
      <DetailRow label="Expires" value={formatRelativeTime(event.expires_at)} />
    </div>
  )
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-dark-500">{label}</span>
      <span className="font-medium text-dark-900 dark:text-dark-100">{value}</span>
    </div>
  )
}