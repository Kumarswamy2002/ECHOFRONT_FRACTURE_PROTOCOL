from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import Dict, List
from backend.app.models.entities import Season, BattlePass, BattlePassProgress, Profile, Transaction, Inventory, Item

class BattlePassService:
    @staticmethod
    async def get_active_battle_pass(db: AsyncSession, profile_id: str) -> dict:
        # Get active season
        s_res = await db.execute(select(Season).where(Season.is_active == True))
        season = s_res.scalar_one_or_none()
        
        if not season:
            season_info = {"season_number": 1, "title": "Fracture Genesis", "tier_count": 50}
        else:
            season_info = {"season_number": season.season_number, "title": season.title, "tier_count": season.max_battle_pass_tier}

        # Get or create progress
        bp_res = await db.execute(select(BattlePassProgress).where(BattlePassProgress.profile_id == profile_id))
        progress = bp_res.scalar_one_or_none()

        if not progress:
            progress = BattlePassProgress(
                profile_id=profile_id,
                battle_pass_id="BP_SEASON_01",
                current_tier=1,
                tier_xp=0,
                is_premium=False
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)

        return {
            "season": season_info,
            "current_tier": progress.current_tier,
            "tier_xp": progress.tier_xp,
            "xp_required_per_tier": 1000,
            "is_premium": progress.is_premium
        }

    @staticmethod
    async def upgrade_to_premium(db: AsyncSession, profile_id: str) -> dict:
        prof_res = await db.execute(select(Profile).where(Profile.id == profile_id))
        profile = prof_res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

        cost_shards = 1000
        if profile.fracture_shards < cost_shards:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient Chronal Shards.")

        bp_res = await db.execute(select(BattlePassProgress).where(BattlePassProgress.profile_id == profile_id))
        progress = bp_res.scalar_one_or_none()
        if progress and progress.is_premium:
            return {"status": "info", "message": "Battle Pass already premium."}

        profile.fracture_shards -= cost_shards
        
        # Ledger Transaction
        tx = Transaction(
            profile_id=profile.id,
            currency_type="fracture_shards",
            amount=-cost_shards,
            balance_after=profile.fracture_shards,
            transaction_reason="battle_pass_premium_upgrade"
        )
        db.add(tx)

        if not progress:
            progress = BattlePassProgress(
                profile_id=profile_id,
                battle_pass_id="BP_SEASON_01",
                current_tier=1,
                tier_xp=0,
                is_premium=True
            )
            db.add(progress)
        else:
            progress.is_premium = True

        await db.commit()
        return {
            "status": "success",
            "message": "Upgraded to Season 1 Premium Battle Pass!",
            "remaining_shards": profile.fracture_shards
        }
