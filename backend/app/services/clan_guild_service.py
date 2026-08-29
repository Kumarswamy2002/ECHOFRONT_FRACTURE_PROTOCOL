import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class GuildRole(Enum):
    RECRUIT = "recruit"
    OPERATIVE = "operative"
    OFFICER = "officer"
    CO_COMMANDER = "co_commander"
    COMMANDER = "commander"

@dataclass
class GuildMember:
    profile_id: str
    username: str
    role: GuildRole
    joined_at: float
    contribution_points: int = 0
    weekly_shards_harvested: int = 0
    last_active: float = field(default_factory=time.time)

@dataclass
class GuildTerritoryControl:
    sector_id: str
    node_name: str
    captured_at: float
    tax_rate_percent: float = 5.0
    total_energy_siphoned: float = 0.0

class GuildManagementService:
    MAX_MEMBERS_BASE = 30
    MAX_MEMBERS_MAX_LEVEL = 100

    def __init__(self, guild_id: str, name: str, tag: str, founder_profile_id: str, founder_username: str):
        self.guild_id = guild_id
        self.name = name
        self.tag = tag.upper()
        self.level = 1
        self.experience = 0
        self.vault_credits = 0
        self.vault_shards = 0
        self.territories: List[GuildTerritoryControl] = []
        self.members: Dict[str, GuildMember] = {
            founder_profile_id: GuildMember(
                profile_id=founder_profile_id,
                username=founder_username,
                role=GuildRole.COMMANDER,
                joined_at=time.time()
            )
        }
        self.join_policy = "invite_only" # "open", "application", "invite_only"
        self.min_level_req = 10

    def add_member(self, profile_id: str, username: str) -> bool:
        max_allowed = self.MAX_MEMBERS_BASE + (self.level * 5)
        if len(self.members) >= max_allowed:
            return False
        if profile_id in self.members:
            return False

        self.members[profile_id] = GuildMember(
            profile_id=profile_id,
            username=username,
            role=GuildRole.RECRUIT,
            joined_at=time.time()
        )
        return True

    def remove_member(self, actor_id: str, target_id: str) -> bool:
        actor = self.members.get(actor_id)
        target = self.members.get(target_id)
        if not actor or not target:
            return False

        # Permission check
        if actor.role in [GuildRole.COMMANDER, GuildRole.CO_COMMANDER]:
            if target.role != GuildRole.COMMANDER:
                del self.members[target_id]
                return True
        elif actor_id == target_id:
            if actor.role != GuildRole.COMMANDER or len(self.members) == 1:
                del self.members[target_id]
                return True
        return False

    def promote_member(self, actor_id: str, target_id: str) -> bool:
        actor = self.members.get(actor_id)
        target = self.members.get(target_id)
        if not actor or not target or actor.role != GuildRole.COMMANDER:
            return False

        role_progression = [GuildRole.RECRUIT, GuildRole.OPERATIVE, GuildRole.OFFICER, GuildRole.CO_COMMANDER]
        if target.role in role_progression:
            idx = role_progression.index(target.role)
            if idx + 1 < len(role_progression):
                target.role = role_progression[idx + 1]
                return True
        return False

    def record_node_harvest_tax(self, sector_id: str, energy_harvested: float, shards_extracted: int):
        tax_shards = int(shards_extracted * 0.05)
        tax_credits = int(energy_harvested * 0.20)
        self.vault_shards += tax_shards
        self.vault_credits += tax_credits
        self.experience += int(energy_harvested * 0.5)

        # Level up guild
        xp_needed = self.level * 10000
        while self.experience >= xp_needed:
            self.experience -= xp_needed
            self.level += 1
            xp_needed = self.level * 10000
