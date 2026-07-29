import { useEffect, useRef, useState } from 'react'
import { Viewer, Entity, Cartesian3, Color, ScreenSpaceEventHandler, ScreenSpaceEventType, JulianDate, SampledPositionProperty, CallbackProperty, Math as CesiumMath, defined } from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import { useMapStore, useUIStore } from '../stores'
import { api } from '../services/api'
import { ws } from '../services/websocket'
import { cn } from '../utils/cn'
import { EventPopup } from '../components/EventPopup'

const DOMAIN_COLORS: Record<string, string> = {
  seismic: '#ef4444',
  fire: '#f97316',
  air_quality: '#3b82f6',
  weather: '#06b6d4',
  disaster: '#8b5cf6',
  aviation: '#ec4899',
  maritime: '#14b8a6',
  transit: '#84cc16',
  space: '#64748b',
  crypto: '#f59e0b',
  fx: '#10b981',
  macro: '#6366f1',
  commodities: '#f97316',
  remittances: '#ec4899',
  worldbank: '#0ea5e9',
  wikipedia: '#8b5cf6',
  github: '#6366f1',
  hackernews: '#f59e0b',
  cloudflare: '#06b6d4',
  solar: '#fbbf24',
  iss: '#ef4444',
  satellites: '#64748b',
}

export function PulseMap() {
  const viewerRef = useRef<HTMLDivElement>(null)
  const viewer = useRef<Viewer | null>(null)
  const handlerRef = useRef<ScreenSpaceEventHandler | null>(null)
  const entityMap = useRef<Map<string, Entity>>(new Map())
  const [initialized, setInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { events, compoundEvents, visibleDomains, selectedEvent, selectEvent, cameraPosition, setCameraPosition } = useMapStore()
  const { isMobile } = useUIStore()
  
  // Initialize Cesium viewer
  useEffect(() => {
    if (!viewerRef.current || initialized) return
    
    try {
      const v = new Viewer(viewerRef.current, {
        terrainProvider: Viewer.CesiumTerrainProvider.fromUrl('https://assets.cesium.com/terrain', {
          requestVertexNormals: true,
        }),
        imageryProvider: Viewer.CesiumIonImageryProvider.fromAssetId(3), // Bing Maps
        scene3DOnly: true,
        requestRenderMode: true,
        maximumRenderTimeChange: Infinity,
        shadows: true,
        timeline: false,
        animation: false,
        fullscreenButton: false,
        vrButton: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        infoBox: false,
        selectionIndicator: false,
        navigation: false,
      })
      
      v.scene.globe.enableLighting = true
      v.scene.skyAtmosphere.show = true
      v.scene.skyBox.show = false
      v.camera.setView({
        destination: Cartesian3.fromDegrees(0, 20, 30000000),
      })
      
      viewer.current = v
      handlerRef.current = new ScreenSpaceEventHandler(v.canvas)
      
      // Click handler for entities
      handlerRef.current.setInputAction((movement) => {
        const picked = v.scene.pick(movement.position)
        if (defined(picked) && picked.id && picked.id.eventId) {
          selectEvent(picked.id.eventId)
        } else {
          selectEvent(null)
        }
      }, ScreenSpaceEventType.LEFT_CLICK)
      
      // Camera change handler
      v.camera.changed.addEventListener(() => {
        const carto = v.camera.positionCartographic
        if (carto) {
          setCameraPosition({
            lat: CesiumMath.toDegrees(carto.latitude),
            lon: CesiumMath.toDegrees(carto.longitude),
            zoom: v.camera.positionCartographic.height,
          })
        }
      })
      
      setInitialized(true)
      loadInitialEvents()
      setupWebSocket()
    } catch (e) {
      console.error('Cesium init error:', e)
      setError('Failed to initialize 3D globe')
    }
    
    return () => {
      handlerRef.current?.destroy()
      viewer.current?.destroy()
      viewer.current = null
      initialized = false
    }
  }, [initialized])
  
  const loadInitialEvents = async () => {
    try {
      const data = await api.getEvents({ limit: 500 })
      useMapStore.getState().setEvents(data.events)
    } catch (e) {
      console.error('Failed to load events:', e)
    }
  }
  
  const setupWebSocket = () => {
    ws.connect().catch(console.error)
    ws.subscribeToEvents()
    ws.startHeartbeat()
    
    return () => {
      ws.disconnect()
    }
  }
  
  // Update entities when events change
  useEffect(() => {
    if (!viewer.current || !initialized) return
    
    // Add new entities
    events.forEach(event => {
      if (!entityMap.current.has(event.id)) {
        createEntity(event)
      }
    })
    
    // Remove entities no longer in events
    const currentIds = new Set(events.map(e => e.id))
    entityMap.current.forEach((entity, id) => {
      if (!currentIds.has(id)) {
        viewer.current?.entities.remove(entity)
        entityMap.current.delete(id)
      }
    })
  }, [events, initialized])
  
  // Update compound events
  useEffect(() => {
    if (!viewer.current || !initialized) return
    
    compoundEvents.forEach(event => {
      if (!entityMap.current.has(`compound-${event.id}`)) {
        createCompoundEntity(event)
      }
    })
  }, [compoundEvents, initialized])
  
  const createEntity = (event: any) => {
    if (!viewer.current) return
    
    const color = DOMAIN_COLORS[event.domain] || '#888'
    const severity = event.severity || 0.5
    const size = Math.max(8, Math.min(40, 8 + severity * 32))
    
    const entity = viewer.current.entities.add({
      eventId: event.id,
      position: Cartesian3.fromDegrees(
        event.geometry.coordinates[0],
        event.geometry.coordinates[1],
        event.properties.altitude || 0
      ),
      point: {
        pixelSize: size,
        color: Color.fromCssColorString(color).withAlpha(0.8),
        outlineColor: Color.WHITE,
        outlineWidth: 2,
        heightReference: 0,
      },
      label: {
        text: event.event_type.replace(/_/g, ' '),
        font: '12px Inter',
        style: 0,
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        pixelOffset: { x: 0, y: -size - 8 },
        showBackground: true,
        backgroundColor: Color.fromCssColorString(color).withAlpha(0.8),
        backgroundPadding: { x: 6, y: 4 },
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      properties: { ...event },
    })
    
    entityMap.current.set(event.id, entity)
  }
  
  const createCompoundEntity = (event: any) => {
    if (!viewer.current) return
    
    const severity = event.severity || 0.7
    const size = Math.max(20, Math.min(60, 20 + severity * 40))
    
    const entity = viewer.current.entities.add({
      eventId: `compound-${event.id}`,
      position: Cartesian3.fromDegrees(
        event.centroid.coordinates[0],
        event.centroid.coordinates[1],
        100000
      ),
      ellipse: {
        semiMajorAxis: event.radius_km * 1000,
        semiMinorAxis: event.radius_km * 1000,
        material: Color.fromCssColorString(DOMAIN_COLORS.seismic).withAlpha(0.15),
        outline: true,
        outlineColor: Color.fromCssColorString(DOMAIN_COLORS.seismic).withAlpha(0.5),
        outlineWidth: 2,
      },
      point: {
        pixelSize: size,
        color: Color.fromCssColorString(DOMAIN_COLORS.seismic).withAlpha(0.9),
        outlineColor: Color.WHITE,
        outlineWidth: 3,
        heightReference: 0,
      },
      label: {
        text: `⚠ ${event.severity_tier.toUpperCase()} • ${event.domains.length} domains`,
        font: '14px Inter',
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        pixelOffset: { x: 0, y: -size - 12 },
        showBackground: true,
        backgroundColor: Color.fromCssColorString(DOMAIN_COLORS.seismic).withAlpha(0.9),
        backgroundPadding: { x: 8, y: 6 },
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      properties: { ...event, isCompound: true },
    })
    
    entityMap.current.set(`compound-${event.id}`, entity)
  }
  
  // Fly to location
  const flyTo = (lon: number, lat: number, zoom = 500000) => {
    if (!viewer.current) return
    viewer.current.camera.flyTo({
      destination: Cartesian3.fromDegrees(lon, lat, zoom),
      duration: 1.5,
    })
  }
  
  // Handle selected event
  useEffect(() => {
    if (selectedEvent && viewer.current) {
      const coords = selectedEvent.geometry?.coordinates || 
        selectedEvent.centroid?.coordinates
      if (coords) {
        flyTo(coords[0], coords[1])
      }
    }
  }, [selectedEvent])
  
  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-dark-50 dark:bg-dark-950">
        <div className="text-center p-8">
          <div className="w-16 h-16 mx-auto mb-4 text-red-500">⚠</div>
          <h2 className="text-xl font-semibold text-dark-900 dark:text-dark-100 mb-2">
            Globe Unavailable
          </h2>
          <p className="text-dark-600 dark:text-dark-400">
            {error}. WebGL may not be supported in this browser.
          </p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="relative h-full w-full">
      <div 
        ref={viewerRef} 
        className="absolute inset-0" 
        id="cesium-container"
      />
      
      {/* Domain Legend */}
      <div className="absolute bottom-20 left-4 lg:bottom-24 lg:left-6 z-20 glass-strong rounded-xl p-3 max-w-xs">
        <h4 className="font-medium text-dark-900 dark:text-dark-100 mb-2">Active Layers</h4>
        <div className="space-y-1.5 max-h-60 overflow-y-auto">
          {domainLayers.map((layer) => {
            const isVisible = visibleDomains.has(layer.domain)
            return (
              <label 
                key={layer.id}
                className="flex items-center gap-2 cursor-pointer text-sm"
              >
                <input
                  type="checkbox"
                  checked={isVisible}
                  onChange={() => useMapStore.getState().toggleDomain(layer.domain)}
                  className="w-4 h-4 text-primary-600 border-dark-300 rounded"
                />
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: layer.color, opacity: isVisible ? 1 : 0.3 }}
                />
                <span className={cn(
                  'truncate',
                  isVisible ? 'text-dark-900 dark:text-dark-100' : 'text-dark-500'
                )}>
                  {layer.label}
                </span>
              </label>
            )
          })}
        </div>
      </div>
      
      {/* Live Counter */}
      <div className="absolute top-16 right-4 z-20 glass-strong rounded-xl px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm font-medium text-dark-900 dark:text-dark-100">
            {events.length + compoundEvents.length} live events
          </span>
        </div>
      </div>
      
      {/* Event Popup */}
      <EventPopup 
        event={selectedEvent}
        onClose={() => selectEvent(null)}
      />
    </div>
  )
}

// Import domain layers from sidebar
import { domainLayers } from '../components/Sidebar'