"""
Encrypted Tactical Radio Communications Protocol
"""
import math
from typing import Dict, Any

class TacticalRadioProtocol:
    @staticmethod
    def calculate_signal_strength(sender_pos: tuple, receiver_pos: tuple, power_watts: float = 5.0) -> float:
        dist = math.dist(sender_pos, receiver_pos)
        if dist <= 1.0:
            return 1.0
        # Free-space path loss approximation
        attenuation = power_watts / (dist ** 2)
        return min(1.0, max(0.0, attenuation * 1000.0))
