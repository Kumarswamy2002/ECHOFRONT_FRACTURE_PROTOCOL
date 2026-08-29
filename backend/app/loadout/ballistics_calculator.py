"""
Modular Weapon Modding & Ballistics Calculator
"""
from typing import Dict, List, Any

class WeaponBallisticsCalculator:
    @staticmethod
    def calculate_modified_stats(base_stats: Dict[str, float], attachments: List[Dict[str, float]]) -> Dict[str, float]:
        stats = dict(base_stats)
        for att in attachments:
            for stat_k, delta in att.items():
                stats[stat_k] = max(0.0, stats.get(stat_k, 0.0) + delta)
        return {k: round(v, 2) for k, v in stats.items()}
