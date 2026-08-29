"""
Deterministic Match Replay Recorder & Frame Indexer
"""
from typing import List, Dict, Any

class MatchReplayRecorder:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.frames: List[Dict[str, Any]] = []
        self.key_events: List[Dict[str, Any]] = []

    def record_frame(self, tick: int, frame_data: Dict[str, Any]):
        self.frames.append({"tick": tick, "data": frame_data})

    def record_key_event(self, tick: int, event_name: str, details: Dict[str, Any]):
        self.key_events.append({"tick": tick, "event": event_name, "details": details})

    def export_summary(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "total_frames": len(self.frames),
            "key_events_count": len(self.key_events),
            "key_events": self.key_events
        }
