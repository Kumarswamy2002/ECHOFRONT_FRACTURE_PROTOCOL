from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ---------------------------------------------------------
# Auth & User Schemas
# ---------------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    profile_id: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------
# Player & Profile Schemas
# ---------------------------------------------------------
class ProfileResponse(BaseModel):
    id: str
    username: str
    display_name: str
    avatar_url: str
    banner_url: str
    level: int
    current_xp: int
    next_level_xp: int
    credits: int
    fracture_shards: int
    event_tokens: int
    rank_tier: str
    rank_points: int
    total_playtime_minutes: int

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None


# ---------------------------------------------------------
# Operatives & Abilities Schemas
# ---------------------------------------------------------
class AbilitySchema(BaseModel):
    name: str
    description: str
    cooldown_seconds: float
    energy_cost: float
    damage_profile: Optional[Dict[str, Any]] = None

class OperativeResponse(BaseModel):
    id: str
    code_id: str
    display_name: str
    role: str
    lore_bio: Optional[str] = None
    base_health: float
    base_shield: float
    base_sprint_speed: float
    passive_ability: Dict[str, Any]
    tactical_ability: Dict[str, Any]
    ultimate_ability: Dict[str, Any]
    is_unlocked: bool = True


# ---------------------------------------------------------
# Inventory & Loadout Schemas
# ---------------------------------------------------------
class InventoryItemResponse(BaseModel):
    inventory_id: str
    item_id: str
    item_code: str
    name: str
    item_type: str
    rarity: str
    quantity: int
    asset_reference: str
    acquired_at: datetime

class LoadoutResponse(BaseModel):
    id: str
    operative_code: str
    loadout_name: str
    primary_weapon_code: str
    secondary_weapon_code: str
    tactical_gadget: str
    cosmetic_skin_item_id: Optional[str] = None
    is_active: bool

class LoadoutUpdateRequest(BaseModel):
    operative_code: str
    loadout_name: Optional[str] = None
    primary_weapon_code: Optional[str] = None
    secondary_weapon_code: Optional[str] = None
    tactical_gadget: Optional[str] = None
    cosmetic_skin_item_id: Optional[str] = None


# ---------------------------------------------------------
# Matchmaking & Game Session Schemas
# ---------------------------------------------------------
class MatchmakingQueueRequest(BaseModel):
    game_mode: str = "Fracture" # Fracture, Extraction, Territory, Survival
    region: str = "us-east"
    operative_code: str

class MatchmakingQueueResponse(BaseModel):
    status: str # queued, matched, ready
    ticket_id: str
    estimated_wait_seconds: int
    queue_position: int

class DedicatedServerMatchStartRequest(BaseModel):
    server_session_id: str
    game_mode: str
    map_name: str
    region: str
    max_players: int

class MatchPlayerResultInput(BaseModel):
    profile_id: str
    team_id: int
    operative_code: str
    score: int
    eliminations: int
    deaths: int
    assists: int
    damage_dealt: float
    nodes_captured: int
    nodes_sabotaged: int
    extracted_safely: bool
    shards_extracted: int

class DedicatedServerMatchEndRequest(BaseModel):
    server_session_id: str
    duration_seconds: int
    winning_team: int
    total_energy_harvested: float
    server_average_tick_rate: float
    players: List[MatchPlayerResultInput]
    match_telemetry: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# Economy & Store Schemas
# ---------------------------------------------------------
class StoreItemResponse(BaseModel):
    id: str
    item_code: str
    name: str
    description: Optional[str] = None
    item_type: str
    rarity: str
    price_credits: int
    price_shards: int
    asset_reference: str

class PurchaseItemRequest(BaseModel):
    item_id: str
    currency_type: str = "credits" # credits or fracture_shards
    idempotency_key: str

class TransactionResponse(BaseModel):
    id: str
    currency_type: str
    amount: int
    balance_after: int
    transaction_reason: str
    created_at: datetime


# ---------------------------------------------------------
# Party & Social Schemas
# ---------------------------------------------------------
class PartyCreateResponse(BaseModel):
    party_id: str
    party_code: str
    leader_profile_id: str
    max_size: int

class PartyInviteRequest(BaseModel):
    target_profile_id: str

class FriendRequest(BaseModel):
    target_username: str


# ---------------------------------------------------------
# Anti-Cheat & Moderation Schemas
# ---------------------------------------------------------
class PlayerReportRequest(BaseModel):
    target_profile_id: str
    match_id: Optional[str] = None
    reason: str # cheating, toxicity, griefing, exploiting
    details: Optional[str] = None

class AdminPenaltyRequest(BaseModel):
    target_profile_id: str
    penalty_type: str # warning, temporary_ban, permanent_ban
    reason: str
    duration_hours: Optional[int] = 24
