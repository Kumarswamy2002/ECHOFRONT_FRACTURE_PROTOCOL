from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.api.deps import get_current_profile
from backend.app.models.entities import Profile
from backend.app.schemas.game_schemas import MatchmakingQueueRequest, MatchmakingQueueResponse
from backend.app.services.matchmaking_service import MatchmakingService

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/join", response_model=MatchmakingQueueResponse)
async def join_matchmaking_queue(
    req: MatchmakingQueueRequest,
    profile: Profile = Depends(get_current_profile)
):
    return await MatchmakingService.join_queue(profile.id, req)

@router.delete("/leave/{ticket_id}")
async def leave_matchmaking_queue(ticket_id: str):
    success = await MatchmakingService.leave_queue(ticket_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue ticket not found.")
    return {"status": "success", "message": "Left matchmaking queue."}

@router.get("/status/{ticket_id}")
async def check_ticket_status(ticket_id: str):
    status_data = await MatchmakingService.get_ticket_status(ticket_id)
    if status_data.get("status") == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue ticket not found.")
    return status_data
