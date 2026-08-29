from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_profile
from backend.app.models.entities import Profile
from backend.app.schemas.game_schemas import InventoryItemResponse, LoadoutResponse, LoadoutUpdateRequest
from backend.app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory & Loadouts"])

@router.get("", response_model=List[InventoryItemResponse])
async def get_inventory(
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await InventoryService.get_player_inventory(db, profile.id)

@router.get("/loadouts", response_model=List[LoadoutResponse])
async def get_loadouts(
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await InventoryService.get_player_loadouts(db, profile.id)

@router.post("/loadout", response_model=LoadoutResponse)
async def update_loadout(
    req: LoadoutUpdateRequest,
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await InventoryService.update_or_create_loadout(db, profile.id, req)
