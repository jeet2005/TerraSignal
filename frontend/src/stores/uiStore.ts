import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  sidebarOpen: boolean
  sidebarPanel: 'threat' | 'city' | 'event' | null
  bottomSheetOpen: boolean
  bottomSheetContent: 'alerts' | 'timeline' | null
  theme: 'light' | 'dark' | 'system'
  isMobile: boolean
  liveCount: number
  lastUpdate: number
  notificationsEnabled: boolean
  voiceEnabled: boolean
  searchQuery: string
  voiceListening: boolean
  
  setSidebarOpen: (open: boolean) => void
  setSidebarPanel: (panel: UIState['sidebarPanel']) => void
  toggleSidebar: () => void
  setBottomSheetOpen: (open: boolean) => void
  setBottomSheetContent: (content: UIState['bottomSheetContent']) => void
  setTheme: (theme: UIState['theme']) => void
  setIsMobile: (mobile: boolean) => void
  setLiveCount: (count: number) => void
  setLastUpdate: (timestamp: number) => void
  setNotificationsEnabled: (enabled: boolean) => void
  setVoiceEnabled: (enabled: boolean) => void
  setSearchQuery: (query: string) => void
  setVoiceListening: (listening: boolean) => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      sidebarPanel: null,
      bottomSheetOpen: false,
      bottomSheetContent: null,
      theme: 'system',
      isMobile: false,
      liveCount: 0,
      lastUpdate: Date.now(),
      notificationsEnabled: false,
      voiceEnabled: false,
      searchQuery: '',
      voiceListening: false,
      
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      setSidebarPanel: (sidebarPanel) => set({ sidebarPanel }),
      toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
      setBottomSheetOpen: (bottomSheetOpen) => set({ bottomSheetOpen }),
      setBottomSheetContent: (bottomSheetContent) => set({ bottomSheetContent }),
      setTheme: (theme) => {
        set({ theme })
        if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      },
      setIsMobile: (isMobile) => set({ isMobile }),
      setLiveCount: (liveCount) => set({ liveCount, lastUpdate: Date.now() }),
      setLastUpdate: (lastUpdate) => set({ lastUpdate }),
      setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
      setVoiceEnabled: (voiceEnabled) => set({ voiceEnabled }),
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      setVoiceListening: (voiceListening) => set({ voiceListening }),
    }),
    {
      name: 'terrasignal-ui',
      partialize: (state) => ({
        theme: state.theme,
        notificationsEnabled: state.notificationsEnabled,
        voiceEnabled: state.voiceEnabled,
      }),
    }
  )
)