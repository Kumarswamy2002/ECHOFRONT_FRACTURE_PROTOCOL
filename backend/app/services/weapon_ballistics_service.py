import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class BallisticVector3:
    x: float
    y: float
    z: float

    def distance_to(self, other: 'BallisticVector3') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

@dataclass
class WeaponBallisticProfile:
    weapon_code: str
    muzzle_velocity_mps: float      # Initial bullet speed (m/s)
    bullet_mass_grams: float
    drag_coefficient: float
    gravity_scale: float
    max_range_meters: float
    base_damage: float
    headshot_multiplier: float
    leg_multiplier: float
    armor_penetration_factor: float # 0.0 to 1.0
    falloff_start_meters: float
    falloff_end_meters: float
    min_damage_falloff: float
    recoil_pitch_curve: List[float]
    recoil_yaw_curve: List[float]

@dataclass
class TrajectoryPoint:
    position: BallisticVector3
    velocity: BallisticVector3
    time_seconds: float
    energy_joules: float

class BallisticsSimulationEngine:
    GRAVITY = 9.80665
    AIR_DENSITY = 1.225

    def __init__(self):
        self.profiles: Dict[str, WeaponBallisticProfile] = {
            "WEAPON_AR_VORTEX": WeaponBallisticProfile(
                weapon_code="WEAPON_AR_VORTEX",
                muzzle_velocity_mps=880.0,
                bullet_mass_grams=4.0,
                drag_coefficient=0.295,
                gravity_scale=1.0,
                max_range_meters=600.0,
                base_damage=28.0,
                headshot_multiplier=1.75,
                leg_multiplier=0.85,
                armor_penetration_factor=0.65,
                falloff_start_meters=45.0,
                falloff_end_meters=180.0,
                min_damage_falloff=16.0,
                recoil_pitch_curve=[0.8, 1.2, 1.6, 2.1, 2.4, 2.6, 2.8, 3.0],
                recoil_yaw_curve=[-0.2, 0.4, -0.3, 0.5, 0.6, -0.4, 0.2, 0.0]
            ),
            "WEAPON_DMR_SPECTRE": WeaponBallisticProfile(
                weapon_code="WEAPON_DMR_SPECTRE",
                muzzle_velocity_mps=960.0,
                bullet_mass_grams=9.5,
                drag_coefficient=0.220,
                gravity_scale=0.8,
                max_range_meters=1200.0,
                base_damage=62.0,
                headshot_multiplier=2.1,
                leg_multiplier=0.9,
                armor_penetration_factor=0.85,
                falloff_start_meters=90.0,
                falloff_end_meters=350.0,
                min_damage_falloff=45.0,
                recoil_pitch_curve=[2.5, 3.2, 3.8],
                recoil_yaw_curve=[0.1, -0.2, 0.1]
            ),
            "WEAPON_SMG_STORM": WeaponBallisticProfile(
                weapon_code="WEAPON_SMG_STORM",
                muzzle_velocity_mps=420.0,
                bullet_mass_grams=7.5,
                drag_coefficient=0.360,
                gravity_scale=1.2,
                max_range_meters=300.0,
                base_damage=19.0,
                headshot_multiplier=1.5,
                leg_multiplier=0.8,
                armor_penetration_factor=0.45,
                falloff_start_meters=20.0,
                falloff_end_meters=75.0,
                min_damage_falloff=10.0,
                recoil_pitch_curve=[0.5, 0.9, 1.2, 1.5, 1.8, 2.0],
                recoil_yaw_curve=[-0.4, 0.5, -0.6, 0.7, -0.5, 0.4]
            )
        }

    def simulate_trajectory(
        self,
        weapon_code: str,
        origin: BallisticVector3,
        direction: BallisticVector3,
        wind_vector: BallisticVector3 = BallisticVector3(0, 0, 0),
        dt_seconds: float = 0.005,
        max_simulation_steps: int = 400
    ) -> List[TrajectoryPoint]:
        profile = self.profiles.get(weapon_code)
        if not profile:
            raise ValueError(f"Unknown weapon code: {weapon_code}")

        # Normalize direction
        length = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
        if length == 0:
            return []
        
        dir_norm = BallisticVector3(direction.x / length, direction.y / length, direction.z / length)

        pos = BallisticVector3(origin.x, origin.y, origin.z)
        vel = BallisticVector3(
            dir_norm.x * profile.muzzle_velocity_mps,
            dir_norm.y * profile.muzzle_velocity_mps,
            dir_norm.z * profile.muzzle_velocity_mps
        )

        mass_kg = profile.bullet_mass_grams / 1000.0
        trajectory = []
        time_elapsed = 0.0

        for step in range(max_simulation_steps):
            speed = math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
            if speed < 10.0 or pos.distance_to(origin) > profile.max_range_meters:
                break

            energy = 0.5 * mass_kg * (speed ** 2)
            trajectory.append(TrajectoryPoint(
                position=BallisticVector3(pos.x, pos.y, pos.z),
                velocity=BallisticVector3(vel.x, vel.y, vel.z),
                time_seconds=time_elapsed,
                energy_joules=energy
            ))

            # Drag force calculation
            cross_section = math.pi * ((0.00762 / 2) ** 2)
            drag_magnitude = 0.5 * self.AIR_DENSITY * (speed ** 2) * profile.drag_coefficient * cross_section
            drag_accel = drag_magnitude / mass_kg

            drag_ax = -drag_accel * (vel.x / speed) + (wind_vector.x * 0.1)
            drag_ay = -drag_accel * (vel.y / speed) - (self.GRAVITY * profile.gravity_scale)
            drag_az = -drag_accel * (vel.z / speed) + (wind_vector.z * 0.1)

            vel.x += drag_ax * dt_seconds
            vel.y += drag_ay * dt_seconds
            vel.z += drag_az * dt_seconds

            pos.x += vel.x * dt_seconds
            pos.y += vel.y * dt_seconds
            pos.z += vel.z * dt_seconds

            time_elapsed += dt_seconds

        return trajectory

    def calculate_hit_damage(
        self,
        weapon_code: str,
        distance_meters: float,
        hit_location: str, # "head", "torso", "legs"
        target_shield: float,
        target_health: float
    ) -> Tuple[float, float, float]:
        profile = self.profiles.get(weapon_code)
        if not profile:
            return 0.0, target_shield, target_health

        # Falloff calculation
        if distance_meters <= profile.falloff_start_meters:
            damage = profile.base_damage
        elif distance_meters >= profile.falloff_end_meters:
            damage = profile.min_damage_falloff
        else:
            t = (distance_meters - profile.falloff_start_meters) / (profile.falloff_end_meters - profile.falloff_start_meters)
            damage = profile.base_damage - t * (profile.base_damage - profile.min_damage_falloff)

        # Hit Location Multiplier
        if hit_location == "head":
            damage *= profile.headshot_multiplier
        elif hit_location == "legs":
            damage *= profile.leg_multiplier

        # Shield & Armor Penetration
        if target_shield > 0:
            shield_damage = damage * (1.0 - profile.armor_penetration_factor)
            penetration_damage = damage * profile.armor_penetration_factor

            actual_shield_lost = min(target_shield, shield_damage)
            remaining_shield = target_shield - actual_shield_lost
            remaining_health = max(0.0, target_health - penetration_damage)

            if actual_shield_lost >= target_shield:
                bleedover = shield_damage - target_shield
                remaining_health = max(0.0, remaining_health - bleedover)

            return damage, remaining_shield, remaining_health
        else:
            remaining_health = max(0.0, target_health - damage)
            return damage, 0.0, remaining_health
