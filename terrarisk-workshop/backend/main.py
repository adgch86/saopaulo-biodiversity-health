"""
TerraRisk Workshop - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.groups import router as groups_router
from api.layers import router as layers_router
from api.municipalities import router as municipalities_router
from api.bivariate import router as bivariate_router
from api.admin import router as admin_router
from core.database import init_db

app = FastAPI(
    title="TerraRisk Workshop API",
    description="API for the TerraRisk Workshop - SEMIL-USP 2026",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
