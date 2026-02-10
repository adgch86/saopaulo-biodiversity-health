"""
TerraRisk Workshop - FastAPI Backend
Main application entry point
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import time
from collections import defaultdict

from api.groups import router as groups_router
from api.layers import router as layers_router
from api.municipalities import router as municipalities_router
from api.bivariate import router as bivariate_router
from api.admin import router as admin_router
from api.workshop_flow import router as workshop_router
from core.database import init_db

app = FastAPI(
    title="TerraRisk Workshop API",
    description="API for the TerraRisk Workshop - SEMIL-USP 2026",
    version="1.0.0",
    docs_url=None,   # Disable Swagger docs in production
    redoc_url=None,   # Disable ReDoc in production
)

# --- CORS: Only allow our frontend ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://terrarisk.arlexperalta.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# --- Rate Limiting ---
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 60   # max requests
RATE_LIMIT_WINDOW = 60     # per 60 seconds
SCRAPING_THRESHOLD = 20    # burst requests in 5 seconds = likely scraping


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limit by IP to prevent scraping"""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Clean old entries
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW
    ]

    # Check for scraping pattern (burst)
    recent = [t for t in _rate_limit_store[client_ip] if now - t < 5]
    if len(recent) >= SCRAPING_THRESHOLD:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Automated access detected."}
        )

    # Check rate limit
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."}
        )

    _rate_limit_store[client_ip].append(now)
    response = await call_next(request)
    return response

# Static files for maps
maps_dir = os.path.join(os.path.dirname(__file__), "data", "maps")
if os.path.exists(maps_dir):
    app.mount("/maps", StaticFiles(directory=maps_dir), name="maps")

# Include routers
app.include_router(groups_router, prefix="/api/groups", tags=["groups"])
app.include_router(layers_router, prefix="/api/layers", tags=["layers"])
app.include_router(municipalities_router, prefix="/api/municipalities", tags=["municipalities"])
app.include_router(bivariate_router, prefix="/api/bivariate", tags=["bivariate"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(workshop_router, prefix="/api/workshop", tags=["workshop"])


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
