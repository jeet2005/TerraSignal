import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Loader2, CheckCircle, Save, User, Shield, Key, 
  Globe, MapPin, Flame, Cloud, Plane, Ship, Zap, 
  Layers, AlertTriangle, Satellite, Mail, Lock
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useUIStore } from '../stores/uiStore'
import { cn } from '../utils/cn'

export function Settings() {
  const navigate = useNavigate()
  const { user, logout, updateUser } = useAuthStore()
  const { theme, setTheme } = useUIStore()
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  
  const [form, setForm] = useState({
    alertThreshold: user?.alert_threshold || 0.7,
    defaultLayers: user?.default_layers || ['earthquakes', 'fires', 'aqi', 'flights', 'ships'],
    units: user?.units || 'metric',
    offlineMode: user?.offline_mode || false,
    mapStyle: user?.map_style || 'satellite',
    autoRefresh: user?.auto_refresh !== false,
    refreshInterval: user?.refresh_interval || 30000,
    voiceEnabled: user?.voice_enabled || false,
    language: user?.language || 'en',
  })
  
  const handleChange = (field: string, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setSaved(false)
  }
  
  const handleSave = async () => {
    setSaving(true)
    try {
      await updateUser(form)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }
  
  useEffect(() => {
    if (user) {
      setForm({
        alertThreshold: user.alert_threshold || 0.7,
        defaultLayers: user.default_layers || ['earthquakes', 'fires', 'aqi', 'flights', 'ships'],
        units: user.units || 'metric',
        offlineMode: user.offline_mode || false,
        mapStyle: user.map_style || 'satellite',
        autoRefresh: user.auto_refresh !== false,
        refreshInterval: user.refresh_interval || 30000,
        voiceEnabled: user.voice_enabled || false,
        language: user.language || 'en',
      })
    }
  }, [user])
  
  const layerOptions = [
    { id: 'earthquakes', label: 'Earthquakes', icon: Globe, color: '#ef4444' },
    { id: 'fires', label: 'Wildfires', icon: Flame, color: '#f97316' },
    { id: 'aqi', label: 'Air Quality', icon: Cloud, color: '#3b82f6' },
    { id: 'flights', label: 'Flights', icon: Plane, color: '#ec4899' },
    { id: 'ships', label: 'Ships', icon: Ship, color: '#06b6d4' },
    { id: 'storms', label: 'Storms', icon: Zap, color: '#f59e0b' },
    { id: 'disasters', label: 'Disasters', icon: AlertTriangle, color: '#8b5cf6' },
    { id: 'transit', label: 'Transit', icon: MapPin, color: '#84cc16' },
    { id: 'satellites', label: 'Satellites', icon: Satellite, color: '#64748b' },
  ]
  
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto space-y-8">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Settings
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Customize your TerraSignal experience
        </p>
      </div>
      
      <div className="card space-y-6 p-4 lg:p-6">
        {/* Map Layers */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-dark-900 dark:text-dark-100">Default Map Layers</h2>
          </div>
          
          <p className="text-sm text-dark-500 mb-4">
            Choose which layers are visible when you open the map
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {layerOptions.map(layer => {
              const Icon = layer.icon
              const checked = form.defaultLayers.includes(layer.id)
              return (
                <label key={layer.id} className="flex items-center gap-2 p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50 cursor-pointer transition-colors">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => handleChange(
                      'defaultLayers',
                      e.target.checked 
                        ? [...form.defaultLayers, layer.id] 
                        : form.defaultLayers.filter((l: string) => l !== layer.id)
                    )}
                    className="w-4 h-4 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
                  />
                  <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: layer.color, opacity: checked ? 1 : 0.3 }} />
                  <Icon className="w-4 h-4 text-dark-500 dark:text-dark-400 flex-shrink-0" />
                  <span className="text-sm text-dark-700 dark:text-dark-300">{layer.label}</span>
                </label>
              )
            })}
          </div>
        </section>
        
        <hr className="border-dark-200 dark:border-dark-800" />
        
        {/* General Settings */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-dark-900 dark:text-dark-100">General</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                Alert Threshold
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.alertThreshold}
                  onChange={(e) => handleChange('alertThreshold', parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-dark-200 dark:bg-dark-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                />
                <span className="text-sm font-mono text-dark-900 dark:text-dark-100 min-w-[3rem]">
                  {(form.alertThreshold * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-dark-500 mt-1">Only notify for events above this severity</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                  Units
                </label>
                <select
                  value={form.units}
                  onChange={(e) => handleChange('units', e.target.value)}
                  className="input"
                >
                  <option value="metric">Metric (°C, km, m/s)</option>
                  <option value="imperial">Imperial (°F, mi, mph)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                  Map Style
                </label>
                <select
                  value={form.mapStyle}
                  onChange={(e) => handleChange('mapStyle', e.target.value)}
                  className="input"
                >
                  <option value="satellite">Satellite</option>
                  <option value="streets">Streets</option>
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                  Auto Refresh
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.autoRefresh}
                    onChange={(e) => handleChange('autoRefresh', e.target.checked)}
                    className="w-4 h-4 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-dark-700 dark:text-dark-300">Enabled</span>
                </label>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                  Refresh Interval
                </label>
                <select
                  value={form.refreshInterval}
                  onChange={(e) => handleChange('refreshInterval', parseInt(e.target.value))}
                  className="input"
                >
                  <option value="15000">15 seconds</option>
                  <option value="30000">30 seconds</option>
                  <option value="60000">1 minute</option>
                  <option value="300000">5 minutes</option>
                  <option value="600000">10 minutes</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="offlineMode"
                checked={form.offlineMode}
                onChange={(e) => handleChange('offlineMode', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="offlineMode" className="text-sm text-dark-700 dark:text-dark-300 cursor-pointer">
                Offline Mode (cache last known state)
              </label>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="voiceEnabled"
                checked={form.voiceEnabled}
                onChange={(e) => handleChange('voiceEnabled', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-dark-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="voiceEnabled" className="text-sm text-dark-700 dark:text-dark-300 cursor-pointer">
                Voice Search
              </label>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
                Language
              </label>
              <select
                value={form.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="input w-auto"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="zh">Chinese</option>
                <option value="ja">Japanese</option>
              </select>
            </div>
          </div>
        </section>
        
        <hr className="border-dark-200 dark:border-dark-800" />
        
        {/* Appearance */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Sun className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-dark-900 dark:text-dark-100">Appearance</h2>
          </div>
          
          <div className="flex gap-2">
            {(['light', 'dark', 'system'] as const).map(t => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                className={cn(
                  'flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  theme === t
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-100 dark:bg-dark-800 text-dark-700 dark:text-dark-300 hover:bg-dark-200 dark:hover:bg-dark-700'
                )}
              >
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </section>
        
        <hr className="border-dark-200 dark:border-dark-800" />
        
        {/* Account */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-dark-900 dark:text-dark-100">Account</h2>
          </div>
          
          <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-50 dark:bg-dark-900">
            <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                {user?.full_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
              </span>
            </div>
            <div className="flex-1">
              <p className="font-medium text-dark-900 dark:text-dark-100">{user?.full_name || 'User'}</p>
              <p className="text-sm text-dark-500">{user?.email}</p>
            </div>
          </div>
          
          <button
            onClick={() => { logout(); navigate('/login'); }}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors mt-4"
          >
            <Key className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </section>
        
        {/* Save Button */}
        <div className="flex justify-end pt-4 border-t border-dark-200 dark:border-dark-800">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary px-6"
          >
            {saving ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </span>
            ) : saved ? (
              <span className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Saved
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Save className="w-4 h-4" />
                Save Changes
              </span>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}