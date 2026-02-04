# TerraRisk Workshop Platform

Interactive web platform for the SEMIL-USP Workshop to explore the Governance-Biodiversity-Climate-Health nexus in 645 municipalities of São Paulo, Brazil.

## Features

- **16+ thematic layers** as overlays
- **Gamified credit system** (10 credits/group)
- **Bivariate maps** when combining 2 variables (4 quadrants)
- **Municipality info panel** with detailed data on click
- **Admin panel** for workshop management

## Quick Start (Development)

### Prerequisites

- Node.js 20+
- Python 3.11+
- pip

### 1. Start Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

### 3. Access

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Admin: http://localhost:3000/admin

## Production Deployment

### With Docker Compose

```bash
docker-compose up -d
```

### Manual Deployment

1. Build frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Start backend:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Configure nginx with provided `nginx.conf`

## Project Structure

```
terrarisk-workshop/
├── frontend/           # Next.js 14 + TypeScript
│   ├── src/
│   │   ├── app/        # Pages (/, /workshop, /admin)
│   │   ├── components/ # React components
│   │   └── lib/        # Store, API, types
│   └── public/
│       └── geojson/    # Simplified SP municipalities
│
├── backend/            # FastAPI + Python
│   ├── api/            # Endpoints
│   ├── core/           # Config, database
│   └── data/
│       ├── maps/       # PNG layers
│       └── municipios.csv
│
├── docker-compose.yml
└── nginx.conf
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/groups` | GET/POST | List/create groups |
| `/api/groups/{id}` | GET | Get group details |
| `/api/groups/{id}/purchase` | POST | Purchase a layer |
| `/api/layers` | GET | List all layers |
| `/api/municipalities` | GET | List municipalities |
| `/api/municipalities/{code}` | GET | Municipality details |
| `/api/bivariate` | POST | Generate bivariate map |
| `/api/admin/stats` | GET | Admin statistics |
| `/api/admin/reset/{id}` | POST | Reset group credits |

## Configuration

### Free Layers (no credits needed)

- Gobernanza General
- Indice de Vulnerabilidad

### Credit Costs

All other layers cost 1 credit each.

## Workshop Flow

1. Groups access the landing page
2. Create or join a group (starts with 10 credits)
3. Explore free layers
4. Purchase additional layers strategically
5. Combine 2 layers to generate bivariate maps
6. Click municipalities to see detailed data

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, react-leaflet, Zustand
- **Backend**: FastAPI, Python, SQLite, pandas
- **Deployment**: Docker, nginx

## License

Developed for SEMIL-USP Workshop 2026.
