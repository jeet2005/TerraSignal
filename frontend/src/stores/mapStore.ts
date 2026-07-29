import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { Event, CompoundEvent, Domain } from '../types'

interface MapState {
  events: Event[]
  compoundEvents: CompoundEvent[]
  visibleDomains: Set<Domain>
  selectedEvent: Event | null
  selectedCompoundEvent: CompoundEvent | null
  cameraPosition: { lat: number; lon: number; zoom: number }
  isLoading: boolean
  error: string | null
  
  // Actions
  setEvents: (events: Event[]) => void
  addEvents: (events: Event[]) => void
  removeEvent: (id: string) => void
  clearEvents: () => void
  setCompoundEvents: (events: CompoundEvent[]) => void
  addCompoundEvent: (event: CompoundEvent) => void
  removeCompoundEvent: (id: string) => void
  setVisibleDomains: (domains: Domain[]) => void
  toggleDomain: (domain: Domain) => void
  selectEvent: (event: Event | null) => void
  selectCompoundEvent: (event: CompoundEvent | null) => void
  setCameraPosition: (pos: { lat: number; lon: number; zoom: number }) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

const DEFAULT_DOMAINS: Domain[] = [
  'seismic', 'fire', 'air_quality', 'weather', 'disaster',
  'aviation', 'maritime', 'transit', 'space',
  'crypto', 'fx', 'macro', 'commodities', 'remittances', 'worldbank',
  'wikipedia', 'github', 'hackernews', 'cloudflare',
  'solar', 'iss', 'satellites'
]

export const useMapStore = create<MapState>()(
  devtools(
    (set, get) => ({
      events: [],
      compoundEvents: [],
      visibleDomains: new Set(DEFAULT_DOMAINS),
      selectedEvent: null,
      selectedCompoundEvent: null,
      cameraPosition: { lat: 0, lon: 0, zoom: 1.5 },
      isLoading: false,
      error: null,
      
      setEvents: (events) => set({ events }),
      
      addEvents: (newEvents) => set(state => {
        const existingIds = new Set(state.events.map(e => e.id))
        const unique = newEvents.filter(e => !existingIds.has(e.id))
        return { events: [...state.events, ...unique] }
      }),
      
      removeEvent: (id) => set(state => ({
        events: state.events.filter(e => e.id !== id)
      })),
      
      clearEvents: () => set({ events: [] }),
      
      setCompoundEvents: (compoundEvents) => set({ compoundEvents }),
      
      addCompoundEvent: (event) => set(state => {
        const existing = state.compoundEvents.findIndex(e => e.id === event.id)
        if (existing >= 0) {
          const newEvents = [...state.compoundEvents]
          newEvents[existing] = event
          return { compoundEvents: newEvents }
        }
        return { compoundEvents: [event, ...state.compoundEvents] }
      }),
      
      removeCompoundEvent: (id) => set(state => ({
        compoundEvents: state.compoundEvents.filter(e => e.id !== id)
      })),
      
      setVisibleDomains: (domains) => set({ visibleDomains: new Set(domains) }),
      
      toggleDomain: (domain) => set(state => {
        const newSet = new Set(state.visibleDomains)
        if (newSet.has(domain)) newSet.delete(domain)
        else newSet.add(domain)
        return { visibleDomains: newSet }
      }),
      
      selectEvent: (event) => set({ selectedEvent: event }),
      
      selectCompoundEvent: (event) => set({ selectedCompoundEvent: event }),
      
      setCameraPosition: (pos) => set({ cameraPosition: pos }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error }),
    }),
    { name: 'map-store' }
  )
)