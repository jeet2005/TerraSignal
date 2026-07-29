import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Mic, Bell, Settings, Menu, X, Sun, Moon, Globe, User, LogOut } from 'lucide-react'
import { useAuthStore, useUIStore } from '../stores'
import { cn } from '../utils/cn'

export function Header() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuthStore()
  const { theme, setTheme, voiceEnabled, setVoiceEnabled, liveCount, sidebarOpen, setSidebarOpen } = useUIStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showVoiceHint, setShowVoiceHint] = useState(false)
  const voiceRef = useRef<SpeechRecognition | null>(null)
  const userMenuRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])
  
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      voiceRef.current = new SpeechRecognition()
      voiceRef.current.continuous = false
      voiceRef.current.interimResults = true
      voiceRef.current.lang = 'en-US'
      
      voiceRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(r => r[0].transcript)
          .join('')
        setSearchQuery(transcript)
        if (event.results[0].isFinal) {
          handleSearch(transcript)
        }
      }
      
      voiceRef.current.onend = () => {
        setVoiceEnabled(false)
        setShowVoiceHint(false)
      }
      
      voiceRef.current.onerror = () => {
        setVoiceEnabled(false)
        setShowVoiceHint(false)
      }
    }
  }, [])
  
  const handleSearch = (query?: string) => {
    const q = query || searchQuery
    if (!q.trim()) return
    
    const lower = q.toLowerCase()
    if (lower.includes('earthquake') || lower.includes('quake')) {
      navigate('/?filter=earthquakes')
    } else if (lower.includes('fire') || lower.includes('wildfire')) {
      navigate('/?filter=fires')
    } else if (lower.includes('flight') || lower.includes('plane')) {
      navigate('/?filter=flights')
    } else if (lower.includes('ship') || lower.includes('vessel')) {
      navigate('/?filter=ships')
    } else if (lower.includes('weather') || lower.includes('storm')) {
      navigate('/?filter=weather')
    } else if (lower.includes('air quality') || lower.includes('pollution') || lower.includes('aqi')) {
      navigate('/?filter=aqi')
    } else {
      navigate(`/search?q=${encodeURIComponent(q)}`)
    }
    setSearchQuery('')
  }
  
  const handleVoiceToggle = () => {
    if (!voiceRef.current) return
    
    if (voiceEnabled) {
      voiceRef.current.stop()
      setVoiceEnabled(false)
    } else {
      setShowVoiceHint(true)
      voiceRef.current.start()
      setVoiceEnabled(true)
    }
  }
  
  const toggleTheme = () => {
    const themes: ('light' | 'dark' | 'system')[] = ['light', 'dark', 'system']
    const currentIndex = themes.indexOf(theme)
    const nextTheme = themes[(currentIndex + 1) % themes.length]
    setTheme(nextTheme)
  }
  
  return (
    <header className="h-14 border-b border-dark-200 dark:border-dark-800 bg-white/80 dark:bg-dark-950/80 backdrop-blur-sm flex items-center justify-between px-4 sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800"
          aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        
        <div className="flex items-center gap-2">
          <Globe className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          <span className="font-bold text-lg text-dark-900 dark:text-dark-100">TerraSignal</span>
        </div>
      </div>
      
      <div className="flex-1 max-w-xl mx-4 hidden md:block">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search location, event, or say 'earthquakes in Japan'..."
            className="w-full pl-10 pr-10 py-2 text-sm bg-dark-100 dark:bg-dark-800 border border-dark-200 dark:border-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            aria-label="Search"
          />
          <button
            onClick={handleVoiceToggle}
            className={cn(
              'absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-colors',
              voiceEnabled
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 animate-pulse'
                : 'text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-800'
            )}
            aria-label={voiceEnabled ? 'Stop listening' : 'Voice search'}
            aria-pressed={voiceEnabled}
          >
            <Mic size={16} />
          </button>
        </div>
        
        {showVoiceHint && voiceEnabled && (
          <div className="absolute top-full left-0 right-0 mt-2 p-3 bg-dark-900 dark:bg-dark-100 rounded-lg shadow-lg text-sm text-dark-100 dark:text-dark-900 animate-in">
            Listening... Try saying "earthquakes in Japan" or "wildfires in California"
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-1 ml-4">
        <div className="hidden sm:flex items-center gap-1 px-3 py-1.5 bg-dark-100 dark:bg-dark-800 rounded-lg text-xs font-medium text-dark-600 dark:text-dark-400">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span>{liveCount.toLocaleString()} events/min</span>
        </div>
        
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800 text-dark-600 dark:text-dark-400"
          aria-label={`Current theme: ${theme}. Click to change.`}
        >
          {theme === 'light' && <Sun size={18} />}
          {theme === 'dark' && <Moon size={18} />}
          {theme === 'system' && <Globe size={18} />}
        </button>
        
        <button
          className="p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800 text-dark-600 dark:text-dark-400"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>
        
        {isAuthenticated && user && (
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-800"
            >
              <div className="w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                  {user.full_name?.[0] || user.email[0].toUpperCase()}
                </span>
              </div>
              <span className="hidden sm:block text-sm font-medium text-dark-700 dark:text-dark-300">
                {user.full_name || user.email.split('@')[0]}
              </span>
            </button>
            
            {showUserMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-dark-900 border border-dark-200 dark:border-dark-800 rounded-lg shadow-lg py-1 animate-in">
                <div className="px-4 py-2 border-b border-dark-200 dark:border-dark-800">
                  <p className="text-sm font-medium text-dark-900 dark:text-dark-100">{user.full_name || user.email}</p>
                  <p className="text-xs text-dark-500">{user.email}</p>
                </div>
                <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-dark-700 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-800">
                  <User size={16} />
                  Profile
                </button>
                <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-dark-700 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-800">
                  <Settings size={16} />
                  Settings
                </button>
                <hr className="my-1 border-dark-200 dark:border-dark-800" />
                <button
                  onClick={() => { logout(); setShowUserMenu(false); }}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <LogOut size={16} />
                  Sign out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  )
}