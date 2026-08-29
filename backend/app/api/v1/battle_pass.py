from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_profile
from backend.app.models.entities import Profile
from backend.app.services.battle_pass_service import BattlePassService

router = APIRouter(prefix="/battlepass", tags=["Battle Pass"])

@router.get("/progress")
async def get_battle_pass_progress(
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await BattlePassService.get_active_battle_pass(db, profile.id)

@router.post("/upgrade")
async def upgrade_battle_pass(
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await BattlePassService.upgrade_to_premium(db, profile.id)
