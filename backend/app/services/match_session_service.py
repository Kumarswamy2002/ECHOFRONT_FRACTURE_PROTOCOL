from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from backend.app.models.entities import (
    Match, MatchPlayer, MatchResult, Profile, CharacterProgress, 
    Transaction, QuestProgress, Quest
)
from backend.app.schemas.game_schemas import (
    DedicatedServerMatchStartRequest, DedicatedServerMatchEndRequest
)

class MatchSessionService:
    @staticmethod
    async def register_match_start(db: AsyncSession, req: DedicatedServerMatchStartRequest) -> dict:
        existing = await db.execute(select(Match).where(Match.server_session_id == req.server_session_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match session already registered.")

        new_match = Match(
            server_session_id=req.server_session_id,
            game_mode=req.game_mode,
            map_name=req.map_name,
            region=req.region,
            max_players=req.max_players,
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        db.add(new_match)
        await db.commit()
        await db.refresh(new_match)
        return {"status": "success", "match_id": new_match.id, "session_id": new_match.server_session_id}

    @staticmethod
    async def record_match_end(db: AsyncSession, req: DedicatedServerMatchEndRequest) -> dict:
        res = await db.execute(select(Match).where(Match.server_session_id == req.server_session_id))
        match = res.scalar_one_or_none()
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match session not found.")

        match.status = "completed"
        match.ended_at = datetime.now(timezone.utc)
        match.winning_team = req.winning_team

        # Create Match Result
        result_record = MatchResult(
            match_id=match.id,
            duration_seconds=req.duration_seconds,
            total_energy_harvested=req.total_energy_harvested,
            winning_score=1000,
            server_average_tick_rate=req.server_average_tick_rate,
            match_telemetry_json=req.match_telemetry or {}
        )
        db.add(result_record)

        # Process each player's results, XP, currencies, and operative mastery
        for p in req.players:
            # 1. Add MatchPlayer
            xp_reward = int(p.score * 1.5 + (500 if p.extracted_safely else 100))
            credits_reward = int(p.score * 0.4 + (200 if p.extracted_safely else 50))
            
            mp = MatchPlayer(
                match_id=match.id,
                profile_id=p.profile_id,
                team_id=p.team_id,
                operative_code=p.operative_code,
                score=p.score,
                eliminations=p.eliminations,
                deaths=p.deaths,
                assists=p.assists,
                damage_dealt=p.damage_dealt,
                nodes_captured=p.nodes_captured,
                nodes_sabotaged=p.nodes_sabotaged,
                extracted_safely=p.extracted_safely,
                shards_extracted=p.shards_extracted,
                xp_earned=xp_reward
            )
            db.add(mp)

            # 2. Update Profile XP and Currencies
            prof_res = await db.execute(select(Profile).where(Profile.id == p.profile_id))
            profile = prof_res.scalar_one_or_none()
            if profile:
                profile.current_xp += xp_reward
                # Handle Level Up
                while profile.current_xp >= profile.next_level_xp:
                    profile.current_xp -= profile.next_level_xp
                    profile.level += 1
                    profile.next_level_xp = int(profile.next_level_xp * 1.25)
                    profile.credits += 1000 # Level up bonus

                profile.credits += credits_reward
                profile.fracture_shards += p.shards_extracted
                profile.total_playtime_minutes += int(req.duration_seconds / 60)

                # Record transaction for rewards
                db.add(Transaction(
                    profile_id=profile.id,
                    currency_type="credits",
                    amount=credits_reward,
                    balance_after=profile.credits,
                    transaction_reason="match_completion_reward",
                    reference_id=match.id
                ))

                if p.shards_extracted > 0:
                    db.add(Transaction(
                        profile_id=profile.id,
                        currency_type="fracture_shards",
                        amount=p.shards_extracted,
                        balance_after=profile.fracture_shards,
                        transaction_reason="extraction_shards_harvested",
                        reference_id=match.id
                    ))

            # 3. Update Character Mastery
            char_res = await db.execute(select(CharacterProgress).where(
                (CharacterProgress.profile_id == p.profile_id) & 
                (CharacterProgress.operative_code_id == p.operative_code)
            ))
            char_prog = char_res.scalar_one_or_none()
            if not char_prog:
                char_prog = CharacterProgress(
                    profile_id=p.profile_id,
                    operative_code_id=p.operative_code,
                    mastery_level=1,
                    mastery_xp=xp_reward,
                    matches_played=1,
                    matches_won=1 if p.team_id == req.winning_team else 0,
                    eliminations=p.eliminations,
                    node_captures=p.nodes_captured
                )
                db.add(char_prog)
            else:
                char_prog.mastery_xp += xp_reward
                char_prog.matches_played += 1
                if p.team_id == req.winning_team:
                    char_prog.matches_won += 1
                char_prog.eliminations += p.eliminations
                char_prog.node_captures += p.nodes_captured

        await db.commit()
        return {"status": "success", "message": "Match results reconciled and awarded."}
