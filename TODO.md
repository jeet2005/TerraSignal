# TerraSignal Development TODO

## Phase 1: Foundation & Infrastructure
### Project Setup
- [x] Create project directory structure
- [x] Initialize Git repository
- [x] Create Docker Compose configuration
- [x] Create .env.example template
- [x] Set up ESLint/Prettier configuration (frontend)

### Backend (FastAPI + MongoDB + Beanie)
- [x] Initialize FastAPI project structure
- [x] Configure MongoDB connection (motor + Beanie)
- [x] Set up JWT authentication system
- [x] Create API router structure
- [x] Set up APScheduler for background tasks
- [x] Create base models and schemas
- [x] Add logging configuration (structlog)
- [x] Health check endpoints
- [x] Authentication endpoints (register, login, refresh, me)
- [x] Events API endpoints
- [x] Compound events API endpoints
- [x] Push notifications API endpoints
- [x] Settings API endpoints

### Database Models (MongoDB + Beanie)
- [x] Base model (UUIDMixin, TimestampMixin)
- [x] Event models (all 77 event types across 6 domains)
- [x] Domain models (Environment, Movement, Space Weather, Economics, Humanitarian, Digital)
- [x] Compound Event model with correlation engine support
- [x] Anomaly Detection model
- [x] User/Auth models
- [x] Health check / monitoring models
- [x] GeoJSON/Geometry support (MongoDB geospatial indexes)
- [ ] Create Alembic migrations

### Frontend (React + Vite + TypeScript)
- [ ] Initialize Vite + React + TypeScript project
- [ ] Configure Tailwind CSS
- [ ] Set up Zustand store structure
- [ ] Configure TanStack Query
- [ ] Set up Dexie (IndexedDB) for offline
- [ ] Create base UI component library
- [ ] Set up CesiumJS integration (3D globe)
- [ ] Set up MapLibre GL JS integration (2D fallback)
- [ ] Configure WebSocket client
- [ ] Create routing structure (React Router)
- [ ] Authentication store (Zustand + persist)
- [ ] Map store (Zustand + persist)
- [ ] UI store (Zustand + persist)
- [ ] API service with axios
- [ ] WebSocket service
- [ ] Type definitions
- [ ] Utility functions

---

## Phase 2: Core Data Ingestion (31 APIs)

### Environment & Climate APIs
- [ ] USGS Earthquake API integration
- [ ] Open-Meteo Weather API integration
- [ ] OpenAQ Air Quality API integration
- [ ] NASA FIRMS Fire API integration
- [ ] NIFC Wildfire Perimeters integration
- [ ] GDACS Disaster Alerts integration
- [ ] NOAA Storm Prediction Center integration
- [ ] NOAA Space Weather API integration

### Movement APIs
- [x] OpenSky Network Flight API integration
- [ ] AIS Vessel Tracking integration
- [ ] Transitland Public Transit integration
- [x] TomTom Traffic API integration
- [ ] N2YO Satellite Tracking integration
- [ ] Open Notify ISS Position integration

### Economics APIs
- [x] CoinGecko Crypto API integration
- [x] FRED Economic Data integration
- [x] Alpha Vantage Market Data integration
- [ ] ExchangeRate-API Currency integration
- [ ] World Bank Open Data integration
- [ ] Commodity Price Feeds integration

### Humanitarian & Geopolitical APIs
- [ ] GDELT GEO API integration
- [ ] GDELT DOC 2.0 API integration
- [ ] ReliefWeb API integration
- [ ] ACLED Conflict Data integration

### Digital World APIs
- [ ] Wikimedia EventStreams integration
- [ ] GitHub Events API integration
- [ ] Cloudflare Radar API integration
- [ ] Hacker News API integration

### Geocoding
- [ ] Nominatim/OpenStreetMap integration

### Data Normalization Pipeline
- [ ] Universal severity scoring (0-1)
- [ ] Common event schema transformation
- [ ] Geospatial enrichment (reverse geocoding)
- [ ] Time-series storage optimization
- [ ] Deduplication logic
- [ ] Data validation & quality checks

---

## Phase 3: Intelligence Layer
- [ ] Statistical Anomaly Detection (Z-score, 7-day rolling baseline)
- [ ] Compound Event Correlation Engine
  - [ ] Spatial-temporal clustering (150km, 6hr window)
  - [ ] Multi-domain detection (min 2 domains)
  - [ ] Severity amplification logic (2 domains: 1.3x, 3: 1.7x, 4+: 2.2x)
- [ ] 7-day rolling baselines per metric
- [ ] Alert threshold management
- [ ] Background worker orchestration

---

## Phase 4: Real-time Infrastructure
- [ ] WebSocket server for live updates
- [ ] CZML packet generation for Cesium
- [ ] GeoJSON streaming for MapLibre
- [ ] Client-side WebSocket reconnection logic
- [ ] Offline-first sync with IndexedDB
- [ ] Message broadcasting (Redis pub/sub)

---

## Phase 5: Pulse Map (Core Globe)
- [ ] CesiumJS 3D Globe component
- [ ] MapLibre 2D fallback at city zoom (level 8+)
- [ ] Domain layer toggles (6 domains)
- [ ] Event markers:
  - [ ] Earthquakes (pulsing circles, magnitude-sized)
  - [ ] Wildfires (flame icons, age-fade)
  - [ ] Flights (moving trails)
  - [ ] Ships (dots, shipping lanes)
  - [ ] Air Quality (heatmap over cities)
  - [ ] Storm/Wildfire polygons
- [ ] Click → Event Popup with details
- [ ] 7-day mini-timeline in popup
- [ ] Live event counters per layer
- [ ] Camera fly-to navigation
- [ ] Zoom-level adaptive rendering
- [ ] Voice search integration

---

## Phase 6: Module Views
### Threat Board
- [ ] Compound event ranked list (live reordering)
- [ ] Stat cards (high-severity clusters, events/hr, active domain)
- [ ] Expandable rows with contributing signals
- [ ] News headlines integration (GDELT)

### City Scope
- [ ] Weather panel (current + 12hr forecast)
- [ ] Transit panel (live vehicle positions)
- [ ] Air Quality panel (station breakdown, WHO thresholds)
- [ ] Wikipedia Pulse panel (live edit count)
- [ ] Local News panel (GDELT geocoded)

### Economic Vitals
- [ ] Crypto heatmap (top 50, 24h change)
- [ ] Currency movement world map
- [ ] Macro indicators sparklines (6 FRED series)
- [ ] GDP vs Development scatter (World Bank)
- [ ] Commodity prices (30-day trend)
- [ ] Remittance corridor tracker

### Digital Heartbeat
- [ ] Wikipedia edit stream (human, non-bot)
- [ ] GitHub activity (global open-source)
- [ ] Hacker News trending
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
- [ ] Desktop layout (left nav, globe, side panel, alert feed)
- [ ] Mobile layout (bottom nav, bottom sheets)
- [ ] Top bar (search, voice, live counter, settings)
- [ ] Module navigation
- [ ] Alert feed / event timeline
- [ ] Settings panel (alert threshold, layers, units, offline toggle)
- [ ] Dark/Light theme
- [ ] Responsive design
- [ ] PWA manifest + service worker

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
- [ ] Monitoring setup (Prometheus + Grafana)

---

**Current Status: Phase 1 Backend Foundation - COMPLETE | Phase 2 Ingestion - IN PROGRESS**
- Completed: Project structure, Docker Compose, config, MongoDB/Beanie models, auth, all API endpoints
- Completed ingestion: OpenSky (flights), CoinGecko (crypto)
- Next: Remaining 29 API ingestors, Alembic → MongoDB indexes, frontend initialization