"""
TerraRisk Workshop - Groups API
"""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database import (
    create_group,
    get_group,
    list_groups,
    update_group_credits,
    record_purchase,
)
from core.config import LAYERS_CONFIG

router = APIRouter()


class CreateGroupRequest(BaseModel):
    name: str
    professionalArea: str | None = None
    environmentalExperience: str | None = None
    numParticipants: int | None = None


class PurchaseLayerRequest(BaseModel):
    layerId: str


@router.post("")
async def create_new_group(request: CreateGroupRequest):
    """Create a new group"""
    if not request.name or len(request.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Nombre debe tener al menos 2 caracteres")

    group_id = str(uuid.uuid4())[:8]
    group = create_group(
        group_id,
        request.name.strip(),
        professional_area=request.professionalArea,
        environmental_experience=request.environmentalExperience,
        num_participants=request.numParticipants,
    )

    return group


@router.get("")
async def get_all_groups():
    """List all groups"""
    return list_groups()


@router.get("/{group_id}")
async def get_group_by_id(group_id: str):
    """Get group by ID"""
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group


@router.post("/{group_id}/purchase")
async def purchase_layer(group_id: str, request: PurchaseLayerRequest):
    """Purchase a layer for a group"""
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    # Find layer
    layer = next((l for l in LAYERS_CONFIG if l["id"] == request.layerId), None)
    if not layer:
        raise HTTPException(status_code=404, detail="Capa no encontrada")

    # Check if already purchased
    if request.layerId in group["purchasedLayers"]:
        raise HTTPException(status_code=400, detail="Capa ya comprada")

    # Check if free
    if layer.get("isFree"):
        raise HTTPException(status_code=400, detail="Esta capa es gratuita")

    # Check credits
    cost = layer.get("cost", 1)
    if group["credits"] < cost:
        raise HTTPException(status_code=400, detail="Creditos insuficientes")

    # Update group
    new_credits = group["credits"] - cost
    new_purchased = group["purchasedLayers"] + [request.layerId]

    updated_group = update_group_credits(group_id, new_credits, new_purchased)

    # Record purchase
    record_purchase(group_id, request.layerId, cost)

    return updated_group
