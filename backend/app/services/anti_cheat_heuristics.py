import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class AimSample:
    pitch: float
    yaw: float
    timestamp: float

@dataclass
class PlayerCombatIntegrityState:
    profile_id: str
    aim_samples: List[AimSample] = field(default_factory=list)
    recent_damage_timestamps: List[float] = field(default_factory=list)
    angular_velocity_history: List[float] = field(default_factory=list)
    consecutive_snaps: int = 0
    risk_score: float = 0.0
    is_flagged: bool = False

class AntiCheatHeuristicsEngine:
    MAX_NATURAL_ANGULAR_VELOCITY_DEG_S = 1800.0  # Max human flick speed (deg/s)
    SNAP_CONVERGENCE_TIME_THRESHOLD_S = 0.035     # Impossible 1-tick snap lock
    MAX_AIM_SAMPLES = 60

    def __init__(self):
        self.player_states: Dict[str, PlayerCombatIntegrityState] = {}

    def analyze_aim_movement(
        self,
        profile_id: str,
        current_pitch: float,
        current_yaw: float,
        timestamp: float,
        target_locked: bool
    ) -> Tuple[bool, float]:
        if profile_id not in self.player_states:
            self.player_states[profile_id] = PlayerCombatIntegrityState(profile_id=profile_id)

        state = self.player_states[profile_id]
        new_sample = AimSample(pitch=current_pitch, yaw=current_yaw, timestamp=timestamp)

        if not state.aim_samples:
            state.aim_samples.append(new_sample)
            return False, 0.0

        last_sample = state.aim_samples[-1]
        dt = timestamp - last_sample.timestamp
        if dt <= 0.001:
            return False, state.risk_score

        # Angular delta calculation
        dpitch = abs(current_pitch - last_sample.pitch)
        dyaw = abs(current_yaw - last_sample.yaw)
        if dyaw > 180.0:
            dyaw = 360.0 - dyaw

        total_angular_delta = math.sqrt(dpitch**2 + dyaw**2)
        angular_velocity = total_angular_delta / dt
        state.angular_velocity_history.append(angular_velocity)
        if len(state.angular_velocity_history) > 100:
            state.angular_velocity_history.pop(0)

        # Detect unnatural snap-to-target
        if angular_velocity > self.MAX_NATURAL_ANGULAR_VELOCITY_DEG_S and dt < self.SNAP_CONVERGENCE_TIME_THRESHOLD_S and target_locked:
            state.consecutive_snaps += 1
            state.risk_score = min(1.0, state.risk_score + 0.25)
        else:
            if state.consecutive_snaps > 0:
                state.consecutive_snaps -= 1

        state.aim_samples.append(new_sample)
        if len(state.aim_samples) > self.MAX_AIM_SAMPLES:
            state.aim_samples.pop(0)

        if state.risk_score >= 0.85:
            state.is_flagged = True
            return True, state.risk_score

        return False, state.risk_score

    def verify_time_to_kill_anomaly(
        self,
        weapon_theoretical_min_ttk: float,
        actual_recorded_ttk: float
    ) -> bool:
        # If player eliminated target faster than weapon cyclic rate allows
        if actual_recorded_ttk < (weapon_theoretical_min_ttk * 0.75):
            return True
        return False
