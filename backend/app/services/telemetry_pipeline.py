import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class TelemetryEvent:
    event_id: str
    event_type: str # "player_death", "node_capture", "weapon_fired", "ability_used", "extraction"
    session_id: str
    match_id: str
    timestamp_utc: float
    profile_id: str
    operative_code: str
    position_x: float
    position_y: float
    position_z: float
    payload: Dict

class TelemetryAggregationPipeline:
    def __init__(self):
        self.buffer: List[TelemetryEvent] = []
        self.max_buffer_size = 50000

    def push_event(self, event: TelemetryEvent):
        self.buffer.append(event)
        if len(self.buffer) > self.max_buffer_size:
            self.flush_to_storage()

    def flush_to_storage(self) -> int:
        count = len(self.buffer)
        self.buffer.clear()
        return count

    def generate_match_kill_heatmap(self, match_id: str, grid_resolution: int = 32) -> List[List[int]]:
        grid = [[0 for _ in range(grid_resolution)] for _ in range(grid_resolution)]
        arena_min = -80.0
        arena_max = 80.0
        span = arena_max - arena_min

        match_deaths = [e for e in self.buffer if e.match_id == match_id and e.event_type == "player_death"]
        for death in match_deaths:
            gx = int(((death.position_x - arena_min) / span) * grid_resolution)
            gz = int(((death.position_z - arena_min) / span) * grid_resolution)
            gx = max(0, min(grid_resolution - 1, gx))
            gz = max(0, min(grid_resolution - 1, gz))
            grid[gz][gx] += 1

        return grid

    def compute_weapon_meta_statistics(self) -> Dict[str, Dict[str, float]]:
        stats: Dict[str, Dict] = {}
        for ev in self.buffer:
            if ev.event_type == "weapon_fired":
                wpn = ev.payload.get("weapon_code", "UNKNOWN")
                if wpn not in stats:
                    stats[wpn] = {"shots": 0, "hits": 0, "kills": 0, "headshots": 0}
                stats[wpn]["shots"] += 1
                if ev.payload.get("hit", False):
                    stats[wpn]["hits"] += 1
                if ev.payload.get("headshot", False):
                    stats[wpn]["headshots"] += 1
            elif ev.event_type == "player_death":
                wpn = ev.payload.get("killer_weapon", "UNKNOWN")
                if wpn in stats:
                    stats[wpn]["kills"] += 1

        metrics = {}
        for wpn, data in stats.items():
            shots = max(1, data["shots"])
            hits = data["hits"]
            metrics[wpn] = {
                "accuracy_rate": round(hits / shots, 4),
                "headshot_ratio": round(data["headshots"] / max(1, hits), 4),
                "total_kills": data["kills"],
                "total_shots": shots
            }
        return metrics
