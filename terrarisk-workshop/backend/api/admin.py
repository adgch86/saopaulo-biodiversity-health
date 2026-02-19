"""
TerraRisk Workshop - Admin API (Protected)
"""

import os
from fastapi import APIRouter, HTTPException, Header

from core.database import (
    get_purchase_stats,
    reset_group_credits,
    delete_group,
    get_group,
)

router = APIRouter()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
if not ADMIN_API_KEY:
    raise RuntimeError("ADMIN_API_KEY environment variable is required")


async def verify_admin(x_api_key: str = Header(default=None)):
    """Verify admin API key"""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/stats")
async def get_admin_stats(x_api_key: str = Header(default=None)):
    """Get admin statistics"""
    await verify_admin(x_api_key)
    return get_purchase_stats()


@router.post("/reset/{group_id}")
async def reset_group_credits_endpoint(
    group_id: str,
    x_api_key: str = Header(default=None),
):
    """Reset a group's credits to initial value"""
    await verify_admin(x_api_key)
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    updated = reset_group_credits(group_id)
    return updated


@router.delete("/groups/{group_id}")
async def delete_group_endpoint(
    group_id: str,
    x_api_key: str = Header(default=None),
):
    """Delete a group"""
    await verify_admin(x_api_key)
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    success = delete_group(group_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar grupo")

    return {"status": "deleted", "groupId": group_id}
