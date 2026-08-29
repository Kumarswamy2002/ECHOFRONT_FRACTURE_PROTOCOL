from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_profile
from backend.app.models.entities import Profile
from backend.app.schemas.game_schemas import StoreItemResponse, PurchaseItemRequest
from backend.app.services.economy_service import EconomyService

router = APIRouter(prefix="/store", tags=["Store & Economy"])

@router.get("/catalog", response_model=List[StoreItemResponse])
async def get_store_catalog(db: AsyncSession = Depends(get_db)):
    return await EconomyService.get_store_catalog(db)

@router.post("/purchase")
async def purchase_item(
    req: PurchaseItemRequest,
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await EconomyService.process_purchase(db, profile.id, req)
