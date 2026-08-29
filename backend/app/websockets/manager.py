import json
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        # Active connections per profile_id: { profile_id: [WebSocket, ...] }
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Match lobby subscribers: { match_id: [WebSocket, ...] }
        self.match_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, profile_id: str, websocket: WebSocket):
        await websocket.accept()
        if profile_id not in self.active_connections:
            self.active_connections[profile_id] = set()
        self.active_connections[profile_id].add(websocket)

    def disconnect(self, profile_id: str, websocket: WebSocket):
        if profile_id in self.active_connections:
            self.active_connections[profile_id].discard(websocket)
            if not self.active_connections[profile_id]:
                del self.active_connections[profile_id]

        for match_id, room in list(self.match_rooms.items()):
            room.discard(websocket)
            if not room:
                del self.match_rooms[match_id]

    async def send_personal_event(self, profile_id: str, event_type: str, payload: dict):
        message = json.dumps({"event": event_type, "data": payload, "version": "1.0"})
        if profile_id in self.active_connections:
            for ws in list(self.active_connections[profile_id]):
                try:
                    await ws.send_text(message)
                except Exception:
                    self.active_connections[profile_id].discard(ws)

    async def broadcast_to_match(self, match_id: str, event_type: str, payload: dict):
        message = json.dumps({"event": event_type, "data": payload, "version": "1.0"})
        if match_id in self.match_rooms:
            for ws in list(self.match_rooms[match_id]):
                try:
                    await ws.send_text(message)
                except Exception:
                    self.match_rooms[match_id].discard(ws)

    def join_match_room(self, match_id: str, websocket: WebSocket):
        if match_id not in self.match_rooms:
            self.match_rooms[match_id] = set()
        self.match_rooms[match_id].add(websocket)

ws_manager = ConnectionManager()
