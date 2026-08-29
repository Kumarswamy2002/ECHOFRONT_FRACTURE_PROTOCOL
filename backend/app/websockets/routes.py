import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.websockets.manager import ws_manager
from backend.app.core.security import decode_token

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/events")
async def websocket_event_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Authentication failed.")
        return

    profile_id = payload.get("sub")
    await ws_manager.connect(profile_id, websocket)
    
    # Send initial connection acknowledgment
    await ws_manager.send_personal_event(profile_id, "player.connected", {
        "user_id": profile_id,
        "server_time": "2026-08-29T14:26:47Z",
        "status": "online"
    })

    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                action = msg.get("action")
                
                if action == "join_match_channel":
                    match_id = msg.get("match_id")
                    if match_id:
                        ws_manager.join_match_room(match_id, websocket)
                        await ws_manager.send_personal_event(profile_id, "room.joined", {"match_id": match_id})
                
                elif action == "ping":
                    await websocket.send_text(json.dumps({"event": "pong", "timestamp": "2026-08-29T14:26:47Z"}))

            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(profile_id, websocket)
