import math
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

@dataclass
class VoiceParticipant:
    profile_id: str
    session_id: str
    channel_id: str
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    orientation_yaw: float = 0.0
    is_muted: bool = False
    is_deafened: bool = False

class SpatialVoiceSignalingServer:
    MAX_AUDIBLE_DISTANCE_METERS = 40.0
    ROLLOFF_FACTOR = 1.5

    def __init__(self):
        self.channels: Dict[str, Set[str]] = {} # channel_id -> Set[session_id]
        self.participants: Dict[str, VoiceParticipant] = {} # session_id -> VoiceParticipant

    def register_participant(self, profile_id: str, session_id: str, channel_id: str) -> VoiceParticipant:
        if channel_id not in self.channels:
            self.channels[channel_id] = set()

        participant = VoiceParticipant(
            profile_id=profile_id,
            session_id=session_id,
            channel_id=channel_id
        )
        self.participants[session_id] = participant
        self.channels[channel_id].add(session_id)
        return participant

    def unregister_participant(self, session_id: str):
        if session_id in self.participants:
            part = self.participants.pop(session_id)
            if part.channel_id in self.channels:
                self.channels[part.channel_id].discard(session_id)
                if not self.channels[part.channel_id]:
                    del self.channels[part.channel_id]

    def update_participant_transform(
        self,
        session_id: str,
        x: float, y: float, z: float,
        yaw: float
    ):
        part = self.participants.get(session_id)
        if part:
            part.pos_x = x
            part.pos_y = y
            part.pos_z = z
            part.orientation_yaw = yaw

    def calculate_spatial_audio_gains(self, listener_session_id: str) -> Dict[str, Dict[str, float]]:
        listener = self.participants.get(listener_session_id)
        if not listener or listener.is_deafened:
            return {}

        channel_sessions = self.channels.get(listener.channel_id, set())
        gain_matrix = {}

        for speaker_id in channel_sessions:
            if speaker_id == listener_session_id:
                continue

            speaker = self.participants.get(speaker_id)
            if not speaker or speaker.is_muted:
                continue

            # Calculate 3D distance
            dx = speaker.pos_x - listener.pos_x
            dy = speaker.pos_y - listener.pos_y
            dz = speaker.pos_z - listener.pos_z
            dist = math.sqrt(dx**2 + dy**2 + dz**2)

            if dist > self.MAX_AUDIBLE_DISTANCE_METERS:
                gain_matrix[speaker_id] = {"gain_left": 0.0, "gain_right": 0.0, "occlusion": 1.0}
                continue

            # Distance Attenuation
            attenuation = 1.0 - (dist / self.MAX_AUDIBLE_DISTANCE_METERS) ** self.ROLLOFF_FACTOR
            attenuation = max(0.0, min(1.0, attenuation))

            # Pan Angle calculation relative to listener yaw
            angle_to_speaker = math.atan2(dx, dz)
            relative_angle = angle_to_speaker - listener.orientation_yaw
            pan = math.sin(relative_angle) # -1.0 (left) to 1.0 (right)

            gain_left = attenuation * max(0.0, min(1.0, 0.5 * (1.0 - pan)))
            gain_right = attenuation * max(0.0, min(1.0, 0.5 * (1.0 + pan)))

            gain_matrix[speaker_id] = {
                "gain_left": round(gain_left, 3),
                "gain_right": round(gain_right, 3),
                "distance": round(dist, 2)
            }

        return gain_matrix
