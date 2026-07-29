# TerraSignal Development TODO

## Phase 1: Foundation & Infrastructure
### Project Setup
- [x] Create project directory structure
- [x] Initialize Git repository
- [x] Create Docker Compose configuration
- [x] Create .env.example template
- [x] Set up ESLint/Prettier configuration

### Backend (FastAPI)
- [x] Initialize FastAPI project structure
- [x] Configure MongoDB connection (Motor/Beanie)
- [x] Set up JWT authentication system
- [x] Create API router structure
- [x] Implement WebSocket manager
- [x] Set up APScheduler for background tasks
- [x] Create base models and schemas
- [x] Add logging configuration
- [x] Health check endpoints
- [x] Authentication endpoints (register, login, refresh, me)
- [x] Events API endpoints
- [x] Compound events API endpoints
- [x] Push notifications API endpoints
- [x] Settings API endpoints

### Frontend (React + Vite + TypeScript)
- [x] Initialize Vite + React + TypeScript project
- [x] Configure TailwindCSS
- [x] Set up Zustand store structure
- [x] Configure TanStack Query
- [x] Set up Dexie (IndexedDB) for offline
- [x] Create base UI component library
- [x] Set up CesiumJS integration
- [x] Set up MapLibre GL JS integration
- [x] Configure WebSocket client
- [x] Create routing structure (React Router)
- [x] Authentication store (Zustand + persist)
- [x] Map store (Zustand + persist)
- [x] UI store (Zustand + persist)
- [x] API service with axios
- [x] WebSocket service
- [x] Type definitions
- [x] Utility functions (cn, format, etc.)

### Database (MongoDB Atlas)
- [x] Design MongoDB collections/schemas
- [x] Create indexes for geospatial queries
- [x] Set up connection pooling

---

## Phase 2: Core Data Ingestion (31 APIs)
### Environment & Climate APIs
- [x] USGS Earthquake API integration
- [x] Open-Meteo Weather API integration
- [x] OpenAQ Air Quality API integration
- [x] NASA FIRMS Fire API integration
- [x] NIFC Wildfire Perimeters integration
- [x] GDACS Disaster Alerts integration
- [x] NOAA Storm Prediction Center integration
- [x] NOAA Space Weather API integration

### Movement APIs
- [x] OpenSky Network Flight API integration
- [x] AIS Vessel Tracking integration
- [x] Transitland Public Transit integration
- [x] TomTom Traffic API integration
- [x] N2YO Satellite Tracking integration
- [x] Open Notify ISS Position integration

### Economics APIs
- [x] CoinGecko Crypto API integration
- [x] FRED Economic Data integration
- [x] Alpha Vantage Market Data integration
- [x] ExchangeRate-API Currency integration
- [x] World Bank Open Data integration
- [x] Commodity Price Feeds integration

### Humanitarian & Geopolitical APIs
- [x] GDELT GEO API integration
- [x] GDELT DOC 2.0 API integration
- [x] ReliefWeb API integration
- [x] ACLED Conflict Data integration

### Digital World APIs
- [x] Wikimedia EventStreams integration
- [x] GitHub Events API integration
- [x] Cloudflare Radar API integration
- [x] Hacker News API integration

### Geocoding
- [x] Nominatim/OpenStreetMap integration

### Data Normalization
- [x] Universal severity scoring (0-1)
- [x] Common event schema
- [x] Geospatial enrichment
- [x] Time-series storage

---

## Phase 3: Intelligence Layer
- [ ] Statistical Anomaly Detection (Z-score)
- [ ] Compound Event Correlation Engine
- [ ] Severity amplification logic
- [ ] 7-day rolling baselines
- [ ] Spatial-temporal clustering (150km, 6hr)

---

## Phase 4: Real-time Infrastructure
- [ ] WebSocket server for live updates
- [ ] CZML packet generation for Cesium
- [ ] GeoJSON streaming for MapLibre
- [ ] Client-side WebSocket reconnection
- [ ] Offline-first sync with IndexedDB

---

## Phase 5: Pulse Map (Core Globe)
- [x] CesiumJS 3D Globe component (basic)
- [ ] MapLibre 2D fallback at city zoom
- [ ] Domain layer toggles
- [ ] Event markers (earthquakes, fires, flights, ships, AQI, storms)
- [ ] Click → Event Popup with details
- [ ] 7-day mini-timeline
- [ ] Live event counters
- [ ] Camera fly-to navigation
- [ ] Zoom-level adaptive rendering

---

## Phase 6: Module Views
### Threat Board
- [ ] Compound event ranked list
- [ ] Stat cards (high-severity clusters, events/hr, active domain)
- [ ] Expandable rows with contributing signals
- [ ] News headlines integration

### City Scope
- [ ] Weather panel (Open-Meteo)
- [ ] Transit panel (Transitland)
- [ ] Air Quality panel (OpenAQ stations)
- [ ] Wikipedia Pulse panel (Wikimedia EventStreams)
- [ ] Local News panel (GDELT DOC 2.0)

### Economic Vitals
- [ ] Crypto heatmap (CoinGecko)
- [ ] Currency movement map
- [ ] Macro indicators sparklines (FRED)
- [ ] GDP vs Development scatter (World Bank)
- [ ] Commodity prices
- [ ] Remittance corridor tracker

### Digital Heartbeat
- [ ] Wikipedia edit stream
- [ ] GitHub activity
- [ ] Hacker News trends
- [ ] Cloudflare Radar internet health

### Sky & Sea
- [ ] Flight paths with trails
- [ ] Ship positions
- [ ] Transit vehicles
- [ ] ISS position
- [ ] Satellite passes

### Earth Watch
- [ ] Unified hazard map
- [ ] Environmental summary panel

### Space Window
- [ ] Solar flares / geomagnetic storms
- [ ] ISS crew count
- [ ] Space weather alerts

---

## Phase 7: UI/UX & Navigation
- [x] Desktop layout (left nav, globe, side panel, alert feed)
- [ ] Mobile layout (bottom nav, bottom sheets)
- [x] Top bar (search, voice, live counter, settings)
- [x] Module navigation
- [x] Alert feed / event timeline
- [ ] Settings panel
- [x] Dark/Light theme
- [x] Responsive design

---

## Phase 8: Advanced Features
- [ ] Voice Search (Web Speech API)
- [ ] Push Notifications (Web Push API + VAPID)
- [ ] Offline Mode (PWA + Service Worker)
- [ ] Embeddable Widget (Web Component)
- [ ] User authentication UI
- [ ] User preferences/settings

---

## Phase 9: Testing & Polish
- [ ] Unit tests (backend)
- [ ] Unit tests (frontend)
- [ ] Integration tests
- [ ] Load testing
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Documentation

---

## Phase 10: Deployment
- [ ] Docker production builds
- [ ] Docker Compose production config
- [ ] Environment configuration
- [ ] CI/CD pipeline
- [ ] Monitoring setup