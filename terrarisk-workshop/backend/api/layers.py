"""
TerraRisk Workshop - Layers API
"""

from fastapi import APIRouter, HTTPException

from core.config import LAYERS_CONFIG, MAPS_DIR

router = APIRouter()


@router.get("")
async def get_all_layers():
    """Get all available layers"""
    layers = []

    for layer_config in LAYERS_CONFIG:
        layer = {
            "id": layer_config["id"],
            "name": layer_config["name"],
            "category": layer_config["category"],
            "description": layer_config["description"],
            "cost": layer_config["cost"],
            "variable": layer_config["variable"],
            "imageUrl": f"/maps/{layer_config['imageFile']}",
            "colorScale": layer_config["colorScale"],
            "isFree": layer_config.get("isFree", False),
            "popularity": 0,  # Could be computed from purchases
        }
        layers.append(layer)

    return layers


@router.get("/{layer_id}")
async def get_layer_by_id(layer_id: str):
    """Get a specific layer by ID"""
    layer_config = next((l for l in LAYERS_CONFIG if l["id"] == layer_id), None)

    if not layer_config:
        raise HTTPException(status_code=404, detail="Capa no encontrada")

    return {
        "id": layer_config["id"],
        "name": layer_config["name"],
        "category": layer_config["category"],
        "description": layer_config["description"],
        "cost": layer_config["cost"],
        "variable": layer_config["variable"],
        "imageUrl": f"/maps/{layer_config['imageFile']}",
        "colorScale": layer_config["colorScale"],
        "isFree": layer_config.get("isFree", False),
        "popularity": 0,
    }
