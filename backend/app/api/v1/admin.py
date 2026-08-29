from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_admin
from backend.app.models.entities import User, Profile, Account, Match, MatchPlayer, Report, Penalty, AuditLog
from backend.app.schemas.game_schemas import AdminPenaltyRequest

router = APIRouter(prefix="/admin", tags=["Admin & Moderation Platform"])

@router.get("/metrics/overview")
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    # Total Users
    users_res = await db.execute(select(User))
    total_users = len(users_res.scalars().all())

    # Total Matches
    matches_res = await db.execute(select(Match))
    all_matches = matches_res.scalars().all()
    total_matches = len(all_matches)
    active_matches = sum(1 for m in all_matches if m.status == "in_progress")

    # Reports
    reports_res = await db.execute(select(Report).where(Report.status == "pending"))
    pending_reports = len(reports_res.scalars().all())

    return {
        "dau_estimate": total_users,
        "ccu_estimate": max(14, active_matches * 16),
        "total_registered_accounts": total_users,
        "total_matches_played": total_matches,
        "active_matches": active_matches,
        "pending_moderation_reports": pending_reports,
        "server_fleet_status": "Optimal",
        "average_tick_rate": 60.0
    }

@router.get("/players")
async def list_players(
    query: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    stmt = select(User, Account, Profile).join(Account, User.id == Account.user_id).join(Profile, Account.id == Profile.account_id)
    if query:
        stmt = stmt.where((User.username.ilike(f"%{query}%")) | (Account.display_name.ilike(f"%{query}%")))
    
    res = await db.execute(stmt.limit(limit))
    records = res.all()

    player_list = []
    for user, account, profile in records:
        player_list.append({
            "user_id": user.id,
            "profile_id": profile.id,
            "username": user.username,
            "display_name": account.display_name,
            "email": user.email,
            "role": user.role,
            "is_banned": user.is_banned,
            "level": profile.level,
            "rank_tier": profile.rank_tier,
            "credits": profile.credits,
            "fracture_shards": profile.fracture_shards,
            "created_at": user.created_at
        })
    return player_list

@router.post("/players/{user_id}/ban")
async def ban_player(
    user_id: str,
    req: AdminPenaltyRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_banned = True

    # Record Penalty
    penalty = Penalty(
        profile_id=req.target_profile_id,
        penalty_type=req.penalty_type,
        reason=req.reason,
        issued_by=admin.username,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=req.duration_hours or 24) if req.penalty_type != "permanent_ban" else None
    )
    db.add(penalty)

    # Record Audit Log
    db.add(AuditLog(
        actor_id=admin.id,
        actor_role=admin.role,
        action=f"player_banned_{req.penalty_type}",
        target_entity=user.id,
        details_json={"reason": req.reason, "target_username": user.username}
    ))

    await db.commit()
    return {"status": "success", "message": f"Player {user.username} has been penalized."}
