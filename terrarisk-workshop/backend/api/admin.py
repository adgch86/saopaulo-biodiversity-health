"""
TerraRisk Workshop - Admin API
"""

from fastapi import APIRouter, HTTPException

from core.database import (
    get_purchase_stats,
    reset_group_credits,
    delete_group,
    get_group,
)

router = APIRouter()


@router.get("/stats")
async def get_admin_stats():
    """Get admin statistics"""
    return get_purchase_stats()


@router.post("/reset/{group_id}")
async def reset_group_credits_endpoint(group_id: str):
    """Reset a group's credits to initial value"""
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    updated = reset_group_credits(group_id)
    return updated


@router.delete("/groups/{group_id}")
async def delete_group_endpoint(group_id: str):
    """Delete a group"""
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    success = delete_group(group_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar grupo")

    return {"status": "deleted", "groupId": group_id}
