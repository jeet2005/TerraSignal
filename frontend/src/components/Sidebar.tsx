import { NavLink, useLocation } from 'react-router-dom'
import { useUIStore } from '../stores/uiStore'
import { useMapStore } from '../stores/mapStore'
import {
  Globe,
  AlertTriangle,
  Plane,
  Mountain,
  TrendingUp,
  Activity,
  Satellite,
  MapPin,
  Settings,
  ChevronRight,
  Zap,
  Flame,
  Cloud,
  Wind,
  Waves,
  Radio,
  Ship,
  TrendingUp as TrendingUpIcon,
  Cpu,
  Wifi,
  Sun as SunIcon,
  Layers,
  Eye,
  EyeOff,
} from 'lucide-react'
import { cn } from '../utils/cn'

const navItems = [
  { path: '/', icon: Globe, label: 'Pulse Map', description: 'Live global events' },
  { path: '/threat-board', icon: AlertTriangle, label: 'Threat Board', description: 'Compound events' },
  { path: '/sky-sea', icon: Plane, label: 'Sky & Sea', description: 'Movement tracking' },
  { path: '/earth-watch', icon: Mountain, label: 'Earth Watch', description: 'Hazard monitoring' },
  { path: '/economic-vitals', icon: TrendingUpIcon, label: 'Economic Vitals', description: 'Markets & finance' },
  { path: '/digital-heartbeat', icon: Activity, label: 'Digital Heartbeat', description: 'Internet health' },
  { path: '/space-window', icon: Satellite, label: 'Space Window', description: 'Space weather' },
]

const domainLayers = [
  { id: 'seismic', label: 'Earthquakes', icon: Zap, color: '#ef4444', domain: 'seismic' },
  { id: 'fire', label: 'Wildfires', icon: Flame, color: '#f97316', domain: 'fire' },
  { id: 'air_quality', label: 'Air Quality', icon: Cloud, color: '#3b82f6', domain: 'air_quality' },
  { id: 'weather', label: 'Weather', icon: Wind, color: '#06b6d4', domain: 'weather' },
  { id: 'disaster', label: 'Disasters', icon: Waves, color: '#8b5cf6', domain: 'disaster' },
  { id: 'aviation', label: 'Flights', icon: Radio, color: '#ec4899', domain: 'aviation' },
  { id: 'maritime', label: 'Ships', icon: Ship, color: '#14b8a6', domain: 'maritime' },
  { id: 'transit', label: 'Transit', icon: TrendingUpIcon, color: '#84cc16', domain: 'transit' },
  { id: 'space', label: 'Satellites', icon: Satellite, color: '#64748b', domain: 'space' },
]

export function Sidebar() {
  const location = useLocation()
  const { setSidebarPanel, setBottomSheetContent, setBottomSheetOpen, isMobile, sidebarOpen } = useUIStore()
  const { visibleDomains, toggleDomain } = useMapStore()
  
  return (
    <aside className={cn(
      'fixed inset-y-0 left-0 z-30 w-72 bg-white dark:bg-dark-950 border-r border-dark-200 dark:border-dark-800 transition-transform duration-300 lg:relative flex flex-col',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
    )}>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto" aria-label="Module navigation">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
            (item.path !== '/' && location.pathname.startsWith(item.path))
          const Icon = item.icon
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => isMobile && useUIStore.getState().setSidebarOpen(false)}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
                'text-sm font-medium',
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 hover:text-dark-900 dark:hover:text-dark-100'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
              <span className="truncate">{item.label}</span>
              {isActive && <ChevronRight className="w-4 h-4 flex-shrink-0 ml-auto" />}
            </NavLink>
          )
        })}
      </nav>
      
      <div className="p-3 border-t border-dark-200 dark:border-dark-800 space-y-3">
        <button
          onClick={() => {
            setSidebarPanel('threat')
            if (isMobile) useUIStore.getState().setSidebarOpen(false)
          }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
        >
          <MapPin className="w-5 h-5" />
          <span>City Scope</span>
        </button>
        
        <button
          onClick={() => {
            setBottomSheetContent('alerts')
            setBottomSheetOpen(true)
          }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
        >
          <Bell className="w-5 h-5" />
          <span>Alert Feed</span>
        </button>
        
        <button
          onClick={() => {
            setBottomSheetContent('timeline')
            setBottomSheetOpen(true)
          }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
        >
          <Clock className="w-5 h-5" />
          <span>Timeline</span>
        </button>
        
        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </NavLink>
      </div>
      
      <div className="p-3 border-t border-dark-200 dark:border-dark-800">
        <h3 className="px-2 text-xs font-semibold text-dark-500 dark:text-dark-500 uppercase tracking-wider mb-2">
          Map Layers
        </h3>
        <div className="space-y-1">
          {domainLayers.map((layer) => {
            const isVisible = visibleDomains.has(layer.domain)
            const Icon = layer.icon
            
            return (
              <label 
                key={layer.id}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={isVisible}
                  onChange={() => toggleDomain(layer.domain)}
                  className="w-4 h-4 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
                />
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: layer.color, opacity: isVisible ? 1 : 0.3 }}
                />
                <Icon className="w-4 h-4 text-dark-500 dark:text-dark-400 flex-shrink-0" />
                <span className="text-sm text-dark-700 dark:text-dark-300 truncate">{layer.label}</span>
              </label>
            )
          })}
        </div>
      </div>
      
      <div className="mt-auto p-3 border-t border-dark-200 dark:border-dark-800">
        <p className="text-xs text-dark-500 dark:text-dark-400 text-center">
          TerraSignal v0.1.0
        </p>
      </div>
    </aside>
  )
}