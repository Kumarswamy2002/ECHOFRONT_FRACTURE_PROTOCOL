from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.schemas.game_schemas import (
    DedicatedServerMatchStartRequest, DedicatedServerMatchEndRequest
)
from backend.app.services.match_session_service import MatchSessionService

router = APIRouter(prefix="/gameserver", tags=["Dedicated Game Server"])

def verify_game_server_auth(x_server_secret: str = Header(...)):
    if x_server_secret != settings.GAME_SERVER_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized dedicated game server credentials."
        )
    return True

@router.post("/match/start")
async def match_started(
    req: DedicatedServerMatchStartRequest,
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_game_server_auth)
):
    return await MatchSessionService.register_match_start(db, req)

@router.post("/match/end")
async def match_ended(
    req: DedicatedServerMatchEndRequest,
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_game_server_auth)
):
    return await MatchSessionService.record_match_end(db, req)
