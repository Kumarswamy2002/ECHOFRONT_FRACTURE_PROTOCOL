from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from backend.app.models.entities import Profile, Account, User, CharacterProgress, MatchPlayer, QuestProgress, Quest
from backend.app.schemas.game_schemas import ProfileResponse, ProfileUpdateRequest

class PlayerService:
    @staticmethod
    async def get_player_profile(db: AsyncSession, user_id: str) -> ProfileResponse:
        acc_res = await db.execute(select(Account).where(Account.user_id == user_id))
        account = acc_res.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

        prof_res = await db.execute(select(Profile).where(Profile.account_id == account.id))
        profile = prof_res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()

        return ProfileResponse(
            id=profile.id,
            username=user.username if user else "",
            display_name=account.display_name,
            avatar_url=account.avatar_url,
            banner_url=account.banner_url,
            level=profile.level,
            current_xp=profile.current_xp,
            next_level_xp=profile.next_level_xp,
            credits=profile.credits,
            fracture_shards=profile.fracture_shards,
            event_tokens=profile.event_tokens,
            rank_tier=profile.rank_tier,
            rank_points=profile.rank_points,
            total_playtime_minutes=profile.total_playtime_minutes
        )

    @staticmethod
    async def update_player_profile(db: AsyncSession, user_id: str, req: ProfileUpdateRequest) -> ProfileResponse:
        acc_res = await db.execute(select(Account).where(Account.user_id == user_id))
        account = acc_res.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

        if req.display_name is not None:
            account.display_name = req.display_name
        if req.avatar_url is not None:
            account.avatar_url = req.avatar_url
        if req.banner_url is not None:
            account.banner_url = req.banner_url

        await db.commit()
        return await PlayerService.get_player_profile(db, user_id)

    @staticmethod
    async def get_player_statistics(db: AsyncSession, profile_id: str) -> dict:
        mp_res = await db.execute(select(MatchPlayer).where(MatchPlayer.profile_id == profile_id))
        match_records = mp_res.scalars().all()

        total_matches = len(match_records)
        total_kills = sum(m.eliminations for m in match_records)
        total_deaths = sum(m.deaths for m in match_records)
        total_captures = sum(m.nodes_captured for m in match_records)
        total_extractions = sum(1 for m in match_records if m.extracted_safely)
        total_damage = sum(m.damage_dealt for m in match_records)

        kd_ratio = round(total_kills / max(1, total_deaths), 2)

        return {
            "total_matches": total_matches,
            "eliminations": total_kills,
            "deaths": total_deaths,
            "kd_ratio": kd_ratio,
            "nodes_captured": total_captures,
            "successful_extractions": total_extractions,
            "total_damage_dealt": total_damage
        }
