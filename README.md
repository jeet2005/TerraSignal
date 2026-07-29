# TerraSignal

Real-time global event intelligence platform — a live 3D globe (CesiumJS) and 2D map (MapLibre) visualizing earthquakes, fires, flights, ships, air quality, storms, crypto markets, conflict data, Wikipedia edits, GitHub activity, satellite passes, and more.

## Features

- **Pulse Map (Core Globe)**: CesiumJS 3D globe with MapLibre 2D fallback at city zoom
- **7 Domain Modules**:
  - Threat Board — compound event correlation & ranked clusters
  - City Scope — weather, transit, air quality, local news, Wikipedia pulse
  - Economic Vitals — crypto heatmap, currency movements, macro indicators
  - Digital Heartbeat — Wikipedia edits, GitHub activity, Hacker News, internet health
  - Sky & Sea — flight paths, ship positions, transit vehicles, ISS, satellites
  - Earth Watch — unified hazard map, environmental summary
  - Space Window — solar flares, geomagnetic storms, space weather alerts
- **31+ Data Sources**: USGS, Open-Meteo, OpenAQ, NASA FIRMS, NOAA, OpenSky, AIS, CoinGecko, FRED, GDELT, Wikimedia, GitHub, Cloudflare, and more
- **Real-time**: WebSocket live updates, CZML/GeoJSON streaming
- **Offline-first**: IndexedDB caching, PWA support
- **Authentication**: JWT-based auth with refresh tokens

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Motor (MongoDB), Beanie ODM, APScheduler |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Maps | CesiumJS (3D), MapLibre GL JS (2D) |
| State | Zustand, TanStack Query |
| Offline | Dexie (IndexedDB) |
| Database | MongoDB Atlas |
| Deployment | Docker, Docker Compose |

## Project Structure

```
terrasignal/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # Beanie document models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic, data ingestion
│   │   ├── websocket/      # WebSocket manager
│   │   └── workers/        # Background jobs (APScheduler)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── stores/         # Zustand stores
│   │   ├── services/       # API, WebSocket services
│   │   ├── hooks/          # Custom hooks
│   │   └── types/          # TypeScript types
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Documentation
├── docker-compose.yml       # Local development
├── .env.example             # Environment template
└── TODO.md                  # Development roadmap
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- MongoDB Atlas account (or local MongoDB)

### With Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB URI and JWT secret
# MONGODB_URI=mongodb+srv://...
# JWT_SECRET=your-secret-key

# Start all services
docker-compose up -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env  # If exists
npm run dev
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB connection string | Yes |
| `MONGODB_DB` | Database name (default: terrasignal) | No |
| `JWT_SECRET` | Secret for JWT signing | Yes |
| `JWT_ALGORITHM` | Algorithm (default: HS256) | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 30) | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry (default: 7) | No |
| `CORS_ORIGINS` | Allowed origins (default: http://localhost:5173) | No |

## API Endpoints

- `POST /api/v1/auth/register` — Register
- `POST /api/v1/auth/login` — Login
- `POST /api/v1/auth/refresh` — Refresh token
- `GET /api/v1/auth/me` — Current user
- `GET /api/v1/events` — List events
- `GET /api/v1/events/{id}` — Get event
- `GET /api/v1/compound-events` — Compound events
- `GET /api/v1/notifications` — Push notifications
- `GET /api/v1/settings` — User settings
- `WS /api/v1/ws` — WebSocket connection

## Data Sources (Phase 2)

| Category | APIs |
|----------|------|
| Environment | USGS Earthquake, Open-Meteo, OpenAQ, NASA FIRMS, NIFC, GDACS, NOAA Storm, NOAA Space Weather |
| Movement | OpenSky Flights, AIS Vessels, Transitland, TomTom Traffic, N2YO Satellites, Open Notify ISS |
| Economics | CoinGecko, FRED, Alpha Vantage, ExchangeRate-API, World Bank, Commodities |
| Humanitarian | GDELT GEO, GDELT DOC 2.0, ReliefWeb, ACLED |
| Digital | Wikimedia EventStreams, GitHub Events, Cloudflare Radar, Hacker News |
| Geocoding | Nominatim/OpenStreetMap |

## Development

### Running Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

### Linting

```bash
# Backend
cd backend && ruff check .

# Frontend
cd frontend && npm run lint
```

## Deployment

Production deployment uses Docker Compose with production configs:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

See `docs/deployment.md` for detailed deployment guide.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License — see `LICENSE` for details.

## Roadmap

See `TODO.md` for the complete development roadmap with 10 phases covering:
- Phase 1: Foundation & Infrastructure ✓
- Phase 2: Core Data Ingestion (31 APIs) 🚧
- Phase 3: Intelligence Layer
- Phase 4: Real-time Infrastructure
- Phase 5: Pulse Map (Core Globe)
- Phase 6: Module Views (7 domains)
- Phase 7: UI/UX & Navigation
- Phase 8: Advanced Features
- Phase 9: Testing & Polish
- Phase 10: Deployment