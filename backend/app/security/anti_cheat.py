"""
Anti-Cheat Movement & Telemetry Anomaly Detector
"""
import math
from typing import Dict, Any

class AntiCheatAnalyzer:
    MAX_ALLOWABLE_SPEED_MPS = 15.0  # Max sprint/slide speed

    @classmethod
    def evaluate_movement_tick(cls, start_pos: tuple, end_pos: tuple, delta_time_sec: float) -> Dict[str, Any]:
        dt = max(0.001, delta_time_sec)
        dist = math.dist(start_pos, end_pos)
        speed = dist / dt
        is_suspicious = speed > cls.MAX_ALLOWABLE_SPEED_MPS
        return {
            "speed_mps": round(speed, 2),
            "is_suspicious": is_suspicious,
            "violation_type": "SPEED_HACK" if is_suspicious else "NONE"
        }
