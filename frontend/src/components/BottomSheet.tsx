import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { cn } from '../utils/cn'

interface BottomSheetProps {
  isOpen: boolean
  onClose: () => void
  content: 'alerts' | 'timeline'
}

export function BottomSheet({ isOpen, onClose, content }: BottomSheetProps) {
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 lg:hidden">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      
      <div className={cn(
        'relative bg-white dark:bg-dark-950 rounded-t-2xl shadow-xl max-h-[70vh] flex flex-col',
        'animate-slide-up'
      )}>
        <div className="flex items-center justify-between p-4 border-b border-dark-200 dark:border-dark-800">
          <div className="w-10 h-1 bg-dark-300 dark:bg-dark-600 rounded-full mx-auto" />
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          {content === 'alerts' && <AlertFeedContent />}
          {content === 'timeline' && <TimelineContent />}
        </div>
      </div>
    </div>
  )
}

function AlertFeedContent() {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-dark-900 dark:text-dark-100">Recent Alerts</h3>
      <div className="space-y-2">
        {[
          { type: 'compound', severity: 'high', location: 'Tokyo, Japan', time: '5m ago', domains: ['seismic', 'air_quality'] },
          { type: 'event', severity: 'moderate', location: 'California, USA', time: '12m ago', event: 'Wildfire' },
          { type: 'event', severity: 'low', location: 'Atlantic Ocean', time: '23m ago', event: 'M 4.2 Earthquake' },
          { type: 'compound', severity: 'critical', location: 'Jakarta, Indonesia', time: '45m ago', domains: ['flood', 'humanitarian'] },
        ].map((alert, i) => (
          <div key={i} className="flex items-start gap-3 p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
            <div className={cn(
              'w-2 h-2 rounded-full mt-2 flex-shrink-0',
              alert.severity === 'critical' && 'bg-red-500',
              alert.severity === 'high' && 'bg-orange-500',
              alert.severity === 'moderate' && 'bg-yellow-500',
              alert.severity === 'low' && 'bg-blue-500'
            )} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-dark-900 dark:text-dark-100">
                  {alert.type === 'compound' ? 'Compound Event' : alert.event}
                </span>
                <span className="text-xs text-dark-500">{alert.time}</span>
              </div>
              <p className="text-sm text-dark-600 dark:text-dark-400">{alert.location}</p>
              {alert.domains && (
                <div className="flex gap-1 mt-1">
                  {alert.domains.map((d: string) => (
                    <span key={d} className="text-xs px-1.5 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded">
                      {d}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TimelineContent() {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-dark-900 dark:text-dark-100">Event Timeline</h3>
      <div className="space-y-4">
        {[
          { time: '14:32', type: 'earthquake', severity: 'moderate', location: 'Fiji Islands', detail: 'M 5.1' },
          { time: '14:28', type: 'fire', severity: 'high', location: 'British Columbia', detail: '1,200 ha' },
          { time: '14:15', type: 'storm', severity: 'moderate', location: 'Gulf of Mexico', detail: 'Tropical Storm' },
          { time: '14:03', type: 'earthquake', severity: 'low', location: 'Offshore Chile', detail: 'M 3.8' },
        ].map((event, i) => (
          <div key={i} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className={cn(
                'w-2 h-2 rounded-full',
                event.severity === 'high' && 'bg-red-500',
                event.severity === 'moderate' && 'bg-yellow-500',
                event.severity === 'low' && 'bg-blue-500'
              )} />
              <div className="w-0.5 h-12 bg-dark-200 dark:bg-dark-700" />
            </div>
            <div className="flex-1 pt-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-dark-900 dark:text-dark-100 capitalize">{event.type}</span>
                <span className="text-xs text-dark-500">{event.time}</span>
              </div>
              <p className="text-sm text-dark-600 dark:text-dark-400">{event.location}</p>
              <p className="text-xs text-dark-500">{event.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}