"""
TerraRisk Workshop - Bivariate Maps API
"""

import os
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import LAYERS_CONFIG, BIVARIATE_DIR, MAPS_DIR

router = APIRouter()


class BivariateRequest(BaseModel):
    layer1Id: str
    layer2Id: str


def get_bivariate_cache_key(layer1_id: str, layer2_id: str) -> str:
    """Generate cache key for bivariate map"""
    # Sort to make order-independent
    sorted_ids = sorted([layer1_id, layer2_id])
    return hashlib.md5(f"{sorted_ids[0]}_{sorted_ids[1]}".encode()).hexdigest()[:12]


def find_existing_bivariate(layer1_id: str, layer2_id: str) -> str | None:
    """Check if a pre-generated bivariate map exists"""
    # Map layer IDs to keywords in existing files
    layer_keywords = {
        "governance_general": "Governance",
        "governance_climatic": "Governance",
        "vulnerability": "Vulnerability",
        "biodiversity": "Biodiversity",
        "fire_risk": "Fire",
        "flooding": "Flooding",
        "hydric_stress": "Hydric",
        "dengue": "Dengue",
        "diarrhea": "Diarrhea",
        "cv_mortality": "Mortality",
        "resp_hosp": "Hospitalization",
        "poverty": "Poverty",
        "rural": "Rural",
        "leishmaniasis": "Leishmaniasis",
        "natural_habitat": "Habitat",
        "pollination": "Pollination",
    }

    kw1 = layer_keywords.get(layer1_id, "")
    kw2 = layer_keywords.get(layer2_id, "")

    # Check for existing bivariate maps
    bivariate_files = [
        "bivariate_Governance_vs_Vulnerability_EN.png",
        "bivariate_ClimateRisk_vs_Vulnerability_EN.png",
    ]

    for filename in bivariate_files:
        filepath = MAPS_DIR / filename
        if filepath.exists():
            # Check if keywords match
            if (kw1 in filename and kw2 in filename) or (kw2 in filename and kw1 in filename):
                return f"/maps/{filename}"

    return None


@router.post("")
async def generate_bivariate(request: BivariateRequest):
    """Generate or retrieve a bivariate map"""
    # Validate layers
    layer1 = next((l for l in LAYERS_CONFIG if l["id"] == request.layer1Id), None)
    layer2 = next((l for l in LAYERS_CONFIG if l["id"] == request.layer2Id), None)

    if not layer1 or not layer2:
        raise HTTPException(status_code=404, detail="Capa no encontrada")

    if request.layer1Id == request.layer2Id:
        raise HTTPException(status_code=400, detail="Selecciona dos capas diferentes")

    # Check for pre-generated bivariate
    existing = find_existing_bivariate(request.layer1Id, request.layer2Id)
    if existing:
        return {"imageUrl": existing}

    # Check cache
    cache_key = get_bivariate_cache_key(request.layer1Id, request.layer2Id)
    cache_path = BIVARIATE_DIR / f"{cache_key}.png"

    if cache_path.exists():
        return {"imageUrl": f"/maps/bivariate/{cache_key}.png"}

    # For now, if no pre-generated map exists, return an error
    # In a full implementation, we would generate the bivariate map on-demand
    raise HTTPException(
        status_code=501,
        detail="Mapa bivariado no disponible. Esta combinacion sera generada proximamente."
    )


@router.get("/available")
async def get_available_bivariates():
    """List available pre-generated bivariate maps"""
    available = []

    if MAPS_DIR.exists():
        for f in MAPS_DIR.glob("bivariate_*.png"):
            available.append({
                "filename": f.name,
                "url": f"/maps/{f.name}"
            })

    return available
