import uuid
import time
from typing import Dict, List, Optional
from backend.app.schemas.game_schemas import MatchmakingQueueRequest, MatchmakingQueueResponse

# In-Memory Queue Manager (with Redis fall-through)
class MatchmakingService:
    # Queue structure: { region: [ { ticket_id, profile_id, operative_code, game_mode, queued_at } ] }
    _queues: Dict[str, List[dict]] = {
        "us-east": [],
        "us-west": [],
        "eu-central": [],
        "asia-east": []
    }
    
    _active_tickets: Dict[str, dict] = {}

    @classmethod
    async def join_queue(cls, profile_id: str, req: MatchmakingQueueRequest) -> MatchmakingQueueResponse:
        region = req.region if req.region in cls._queues else "us-east"
        ticket_id = f"TICKET_{uuid.uuid4().hex[:12].upper()}"

        queue_entry = {
            "ticket_id": ticket_id,
            "profile_id": profile_id,
            "operative_code": req.operative_code,
            "game_mode": req.game_mode,
            "region": region,
            "queued_at": time.time(),
            "status": "queued"
        }

        cls._queues[region].append(queue_entry)
        cls._active_tickets[ticket_id] = queue_entry

        position = len(cls._queues[region])
        est_wait = max(5, position * 3)

        return MatchmakingQueueResponse(
            status="queued",
            ticket_id=ticket_id,
            estimated_wait_seconds=est_wait,
            queue_position=position
        )

    @classmethod
    async def leave_queue(cls, ticket_id: str) -> bool:
        if ticket_id in cls._active_tickets:
            entry = cls._active_tickets.pop(ticket_id)
            region = entry["region"]
            cls._queues[region] = [e for e in cls._queues[region] if e["ticket_id"] != ticket_id]
            return True
        return False

    @classmethod
    async def get_ticket_status(cls, ticket_id: str) -> dict:
        ticket = cls._active_tickets.get(ticket_id)
        if not ticket:
            return {"status": "not_found"}
        return ticket
