from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, get_current_profile
from backend.app.models.entities import User, Profile, Operative, CharacterProgress
from backend.app.schemas.game_schemas import ProfileResponse, ProfileUpdateRequest, OperativeResponse
from backend.app.services.player_service import PlayerService

router = APIRouter(prefix="/player", tags=["Player"])

@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlayerService.get_player_profile(db, current_user.id)

@router.patch("", response_model=ProfileResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlayerService.update_player_profile(db, current_user.id, req)

@router.get("/stats")
async def get_stats(
    profile: Profile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db)
):
    return await PlayerService.get_player_statistics(db, profile.id)

@router.get("/operatives", response_model=List[OperativeResponse])
async def list_operatives(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Operative))
    ops = res.scalars().all()
    return [
        OperativeResponse(
            id=op.id,
            code_id=op.code_id,
            display_name=op.display_name,
            role=op.role,
            lore_bio=op.lore_bio,
            base_health=op.base_health,
            base_shield=op.base_shield,
            base_sprint_speed=op.base_sprint_speed,
            passive_ability=op.passive_ability,
            tactical_ability=op.tactical_ability,
            ultimate_ability=op.ultimate_ability,
            is_unlocked=op.is_unlocked_default
        )
        for op in ops
    ]
