import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, 
    Text, JSON, UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# ---------------------------------------------------------
# 1. Identity & Accounts
# ---------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="player", nullable=False) # player, moderator, admin, game_server
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    account = relationship("Account", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    country_code = Column(String(3), default="US")
    language = Column(String(10), default="en")
    avatar_url = Column(String(512), default="default_avatar.png")
    banner_url = Column(String(512), default="default_banner.png")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="account")
    profile = relationship("Profile", back_populates="account", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_xp = Column(Integer, default=0, nullable=False)
    next_level_xp = Column(Integer, default=1000, nullable=False)
    total_playtime_minutes = Column(Integer, default=0, nullable=False)
    
    # Currencies (Double-Entry verified)
    credits = Column(Integer, default=5000, nullable=False)        # Free gameplay currency
    fracture_shards = Column(Integer, default=200, nullable=False) # Premium currency
    event_tokens = Column(Integer, default=0, nullable=False)      # Temporal seasonal tokens
    
    # Competitive Rank
    rank_tier = Column(String(30), default="Cadet I", nullable=False)
    rank_points = Column(Integer, default=1000, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    account = relationship("Account", back_populates="profile")
    character_progress = relationship("CharacterProgress", back_populates="profile", cascade="all, delete-orphan")
    inventories = relationship("Inventory", back_populates="profile", cascade="all, delete-orphan")
    loadouts = relationship("Loadout", back_populates="profile", cascade="all, delete-orphan")
    quest_progress = relationship("QuestProgress", back_populates="profile", cascade="all, delete-orphan")
    achievements = relationship("ProfileAchievement", back_populates="profile", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="profile", cascade="all, delete-orphan")


# ---------------------------------------------------------
# 2. Operatives, Abilities & Weapons
# ---------------------------------------------------------
class Operative(Base):
    __tablename__ = "operatives"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "OP_APEX"
    display_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False) # Vanguard, Sentinel, Recon, etc.
    lore_bio = Column(Text, nullable=True)
    base_health = Column(Float, default=100.0, nullable=False)
    base_shield = Column(Float, default=100.0, nullable=False)
    base_sprint_speed = Column(Float, default=7.5, nullable=False) # m/s
    passive_ability = Column(JSON, nullable=False)
    tactical_ability = Column(JSON, nullable=False)
    ultimate_ability = Column(JSON, nullable=False)
    is_unlocked_default = Column(Boolean, default=False, nullable=False)


class CharacterProgress(Base):
    __tablename__ = "character_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    operative_code_id = Column(String(50), nullable=False)
    mastery_level = Column(Integer, default=1, nullable=False)
    mastery_xp = Column(Integer, default=0, nullable=False)
    matches_played = Column(Integer, default=0, nullable=False)
    matches_won = Column(Integer, default=0, nullable=False)
    eliminations = Column(Integer, default=0, nullable=False)
    node_captures = Column(Integer, default=0, nullable=False)

    profile = relationship("Profile", back_populates="character_progress")
    __table_args__ = (UniqueConstraint("profile_id", "operative_code_id", name="uq_profile_operative"),)


class Weapon(Base):
    __tablename__ = "weapons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    weapon_code = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    weapon_class = Column(String(50), nullable=False) # Assault Rifle, DMR, Shotgun, SMG, Sniper, Heavy
    base_damage = Column(Float, nullable=False)
    fire_rate_rpm = Column(Float, nullable=False)
    magazine_capacity = Column(Integer, nullable=False)
    reload_time_seconds = Column(Float, nullable=False)
    effective_range_meters = Column(Float, nullable=False)
    recoil_profile = Column(JSON, nullable=True)


# ---------------------------------------------------------
# 3. Inventory, Items, Cosmetics & Loadouts
# ---------------------------------------------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String(50), nullable=False) # skin, weapon_wrap, banner, emote, charm, finisher
    rarity = Column(String(30), default="Common", nullable=False) # Common, Rare, Epic, Legendary, Mythic
    price_credits = Column(Integer, default=0, nullable=False)
    price_shards = Column(Integer, default=0, nullable=False)
    asset_reference = Column(String(512), nullable=False)
    is_available_in_store = Column(Boolean, default=True, nullable=False)


class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    acquired_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="inventories")
    item = relationship("Item")
    __table_args__ = (UniqueConstraint("profile_id", "item_id", name="uq_profile_item"),)


class Loadout(Base):
    __tablename__ = "loadouts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    operative_code = Column(String(50), nullable=False)
    loadout_name = Column(String(50), default="Custom Loadout", nullable=False)
    primary_weapon_code = Column(String(50), default="WEAPON_AR_VORTEX", nullable=False)
    secondary_weapon_code = Column(String(50), default="WEAPON_PISTOL_ION", nullable=False)
    tactical_gadget = Column(String(50), default="GADGET_FRAG_GRENADE", nullable=False)
    cosmetic_skin_item_id = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    profile = relationship("Profile", back_populates="loadouts")


# ---------------------------------------------------------
# 4. Matches, Sessions & Results
# ---------------------------------------------------------
class Match(Base):
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    server_session_id = Column(String(100), unique=True, index=True, nullable=False)
    game_mode = Column(String(50), default="Fracture", nullable=False)
    map_name = Column(String(100), default="Reactor_Chamber_07", nullable=False)
    region = Column(String(20), default="us-east", nullable=False)
    status = Column(String(30), default="in_progress", nullable=False) # pending, in_progress, completed, aborted
    max_players = Column(Integer, default=24, nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    winning_team = Column(Integer, nullable=True)
    replay_file_url = Column(String(512), nullable=True)

    players = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")
    result = relationship("MatchResult", back_populates="match", uselist=False, cascade="all, delete-orphan")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_id = Column(String(36), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, default=1, nullable=False)
    operative_code = Column(String(50), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    eliminations = Column(Integer, default=0, nullable=False)
    deaths = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    damage_dealt = Column(Float, default=0.0, nullable=False)
    nodes_captured = Column(Integer, default=0, nullable=False)
    nodes_sabotaged = Column(Integer, default=0, nullable=False)
    extracted_safely = Column(Boolean, default=False, nullable=False)
    shards_extracted = Column(Integer, default=0, nullable=False)
    xp_earned = Column(Integer, default=0, nullable=False)

    match = relationship("Match", back_populates="players")
    profile = relationship("Profile")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_id = Column(String(36), ForeignKey("matches.id", ondelete="CASCADE"), unique=True, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    total_energy_harvested = Column(Float, default=0.0, nullable=False)
    winning_score = Column(Integer, default=0, nullable=False)
    server_average_tick_rate = Column(Float, default=60.0, nullable=False)
    match_telemetry_json = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="result")


# ---------------------------------------------------------
# 5. Social, Parties & Friends
# ---------------------------------------------------------
class Friend(Base):
    __tablename__ = "friends"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sender_profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    receiver_profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending", nullable=False) # pending, accepted, blocked
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (UniqueConstraint("sender_profile_id", "receiver_profile_id", name="uq_friend_pair"),)


class Party(Base):
    __tablename__ = "parties"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    leader_profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    party_code = Column(String(8), unique=True, index=True, nullable=False)
    max_size = Column(Integer, default=4, nullable=False)
    is_open = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


# ---------------------------------------------------------
# 6. Economy, Transactions & Monetization
# ---------------------------------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    currency_type = Column(String(20), nullable=False) # credits, fracture_shards, event_tokens
    amount = Column(Integer, nullable=False) # Positive (gain), Negative (spend)
    balance_after = Column(Integer, nullable=False)
    transaction_reason = Column(String(100), nullable=False) # match_reward, battle_pass, cosmetic_purchase
    reference_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="transactions")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    currency_type = Column(String(20), nullable=False)
    price_paid = Column(Integer, nullable=False)
    idempotency_key = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


# ---------------------------------------------------------
# 7. Quests, Achievements & Battle Pass
# ---------------------------------------------------------
class Quest(Base):
    __tablename__ = "quests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    quest_category = Column(String(30), default="daily", nullable=False) # daily, weekly, seasonal
    target_metric = Column(String(50), nullable=False) # node_captures, eliminations, extraction_shards
    target_count = Column(Integer, default=1, nullable=False)
    reward_xp = Column(Integer, default=500, nullable=False)
    reward_credits = Column(Integer, default=250, nullable=False)
    reward_shards = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class QuestProgress(Base):
    __tablename__ = "quest_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    quest_id = Column(String(36), ForeignKey("quests.id", ondelete="CASCADE"), nullable=False)
    current_count = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    reward_claimed = Column(Boolean, default=False, nullable=False)

    profile = relationship("Profile", back_populates="quest_progress")
    quest = relationship("Quest")
    __table_args__ = (UniqueConstraint("profile_id", "quest_id", name="uq_profile_quest"),)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String(255), default="badge_default.png")
    achievement_points = Column(Integer, default=10, nullable=False)


class ProfileAchievement(Base):
    __tablename__ = "profile_achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(String(36), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="achievements")
    achievement = relationship("Achievement")
    __table_args__ = (UniqueConstraint("profile_id", "achievement_id", name="uq_profile_achievement"),)


class Season(Base):
    __tablename__ = "seasons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    season_number = Column(Integer, unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    start_time = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_battle_pass_tier = Column(Integer, default=50, nullable=False)


class BattlePass(Base):
    __tablename__ = "battle_passes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    season_id = Column(String(36), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    price_shards = Column(Integer, default=1000, nullable=False)
    tier_count = Column(Integer, default=50, nullable=False)


class BattlePassProgress(Base):
    __tablename__ = "battle_pass_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    battle_pass_id = Column(String(50), default="BP_SEASON_01", nullable=False)
    current_tier = Column(Integer, default=1, nullable=False)
    tier_xp = Column(Integer, default=0, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (UniqueConstraint("profile_id", "battle_pass_id", name="uq_profile_battlepass"),)



# ---------------------------------------------------------
# 8. Moderation, Reports & Audit
# ---------------------------------------------------------
class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reporter_profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    target_profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    match_id = Column(String(36), nullable=True)
    reason = Column(String(50), nullable=False) # cheating, toxicity, griefing, exploiting
    details = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False) # pending, reviewing, resolved, dismissed
    risk_score = Column(Float, default=0.5, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Penalty(Base):
    __tablename__ = "penalties"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    penalty_type = Column(String(30), nullable=False) # warning, chat_mute, temporary_ban, permanent_ban
    reason = Column(String(255), nullable=False)
    issued_by = Column(String(100), default="System_AntiCheat", nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=False)
    actor_role = Column(String(30), nullable=False)
    action = Column(String(100), nullable=False)
    target_entity = Column(String(100), nullable=False)
    details_json = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
