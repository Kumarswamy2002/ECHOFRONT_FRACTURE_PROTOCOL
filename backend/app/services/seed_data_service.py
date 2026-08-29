from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.entities import Operative, Weapon, Item, Quest, Achievement

ORIGINAL_OPERATIVES = [
    {
        "code_id": "OP_APEX",
        "display_name": "Apex (Vanguard AEX-01)",
        "role": "Vanguard",
        "lore_bio": "A cybernetically augmented frontline shock trooper specialized in kinetic suppression and room clearing.",
        "base_health": 125.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.5,
        "passive_ability": {"name": "Kinetic Shielding", "description": "Absorbs 15% shock damage from incoming explosive projectiles."},
        "tactical_ability": {"name": "Shockwave Dash", "description": "Lurches forward 10m emitting a sonic wave that disrupts enemy aim.", "cooldown": 14.0},
        "ultimate_ability": {"name": "Graviton Collapse", "description": "Fires a micro-singularity pulling all enemies within 12m to its core.", "cooldown": 110.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_BASTION",
        "display_name": "Bastion-9",
        "role": "Sentinel",
        "lore_bio": "Heavy automated defensive platform built to anchor and lock down critical Fracture Nodes.",
        "base_health": 150.0,
        "base_shield": 125.0,
        "base_sprint_speed": 6.8,
        "passive_ability": {"name": "Nanite Armor", "description": "Passively regenerates 4 shield points per second after 6s out of combat."},
        "tactical_ability": {"name": "Hardlight Barricade", "description": "Deploys a 500HP directional energy wall that absorbs incoming fire.", "cooldown": 18.0},
        "ultimate_ability": {"name": "Citadel Lockdown", "description": "Locks down the current zone with dual auto-tracking 20mm defense turrets.", "cooldown": 130.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_VAPOR",
        "display_name": "Vapor",
        "role": "Recon",
        "lore_bio": "Covert specialist equipped with multispectral optical telemetry sensors.",
        "base_health": 100.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.8,
        "passive_ability": {"name": "Thermal Footprints", "description": "Enemy sprint trails glow through walls for 8 seconds."},
        "tactical_ability": {"name": "Echo Ping", "description": "Fires a resonance sonar dart revealing all hostile silhouettes within 25m.", "cooldown": 16.0},
        "ultimate_ability": {"name": "Orbital Recon Drone", "description": "Deploys an autonomous high-altitude drone tracking all enemy movements in sector.", "cooldown": 120.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_NULL",
        "display_name": "Null",
        "role": "Disruptor",
        "lore_bio": "Cyberwarfare specialist capable of paralyzing enemy node networks and electronics.",
        "base_health": 100.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.6,
        "passive_ability": {"name": "Static Interference", "description": "Scrambles the minimap radar of enemies within a 15m radius."},
        "tactical_ability": {"name": "EMP Dart", "description": "Fires a high-voltage dart disabling deployable gadgets and halting node capture.", "cooldown": 15.0},
        "ultimate_ability": {"name": "Blackout Wave", "description": "Emits a massive EMP pulse wiping enemy HUD, crosshairs and abilities for 8s.", "cooldown": 125.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_FORGE",
        "display_name": "Forge",
        "role": "Engineer",
        "lore_bio": "Master technician with extensive knowledge of reactor thermodynamics and fracture nodes.",
        "base_health": 110.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.2,
        "passive_ability": {"name": "Overclock", "description": "Interacts with and captures Fracture Nodes 30% faster."},
        "tactical_ability": {"name": "Deployable Sentry", "description": "Constructs an automatic suppressing turret targeting nearby hostile forces.", "cooldown": 20.0},
        "ultimate_ability": {"name": "Resonance Core", "description": "Overdrives a captured Fracture Node, doubling energy output and restoring team shields.", "cooldown": 115.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_AEGIS",
        "display_name": "Aegis",
        "role": "Medic",
        "lore_bio": "Combat lifesaver utilizing biocatalytic nanite swarms to reverse mortal trauma in the field.",
        "base_health": 100.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.5,
        "passive_ability": {"name": "Field Triage", "description": "Revives downed squadmates 40% faster with bonus immediate shields."},
        "tactical_ability": {"name": "Healing Nanite Cloud", "description": "Releases an aerosol cloud restoring 25 HP/sec for all allies inside.", "cooldown": 14.0},
        "ultimate_ability": {"name": "Revival Beacon", "description": "Plants an anchoring totem preventing lethal damage for teammates in radius for 10s.", "cooldown": 140.0},
        "is_unlocked_default": True
    },
    {
        "code_id": "OP_WRAITH",
        "display_name": "Wraith",
        "role": "Hunter",
        "lore_bio": "Lethal assassin trained in high-speed cloaking strikes and silent execution.",
        "base_health": 90.0,
        "base_shield": 100.0,
        "base_sprint_speed": 8.2,
        "passive_ability": {"name": "Silent Stride", "description": "Crouched and walking movements produce zero acoustic signature."},
        "tactical_ability": {"name": "Optical Camouflage", "description": "Bends light around operative, turning 95% invisible for 6 seconds.", "cooldown": 18.0},
        "ultimate_ability": {"name": "Phase Shift", "description": "Rips through dimensional subspace to appear behind a locked target with critical strike.", "cooldown": 100.0},
        "is_unlocked_default": False
    },
    {
        "code_id": "OP_CRYO",
        "display_name": "Cryo",
        "role": "Controller",
        "lore_bio": "Cryogenic hazard controller armed with sub-zero atmospheric flash-freezing gear.",
        "base_health": 110.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.4,
        "passive_ability": {"name": "Sub-Zero Trail", "description": "Sliding creates a frosty trail that slows pursuing enemies by 25%."},
        "tactical_ability": {"name": "Cryo Grenade", "description": "Detonates in a flash-frost field that freezes node conduits and impairs movement.", "cooldown": 15.0},
        "ultimate_ability": {"name": "Absolute Zero Blizzard", "description": "Envelops a 30m zone in a lethal blizzard dealing damage over time and impairing vision.", "cooldown": 120.0},
        "is_unlocked_default": False
    },
    {
        "code_id": "OP_PHANTOM",
        "display_name": "Phantom",
        "role": "Infiltrator",
        "lore_bio": "Deception operative utilizing quantum holographic clones and temporal position anchors.",
        "base_health": 95.0,
        "base_shield": 100.0,
        "base_sprint_speed": 8.0,
        "passive_ability": {"name": "Agile Reflexes", "description": "Weapon swap and tactical reload animations are 30% faster."},
        "tactical_ability": {"name": "Holographic Decoy", "description": "Spawns a duplicate hologram sprinting in the target direction that mimics gunfire.", "cooldown": 12.0},
        "ultimate_ability": {"name": "Quantum Backtrack", "description": "Instantly teleports back to the exact coordinates occupied 5 seconds ago.", "cooldown": 90.0},
        "is_unlocked_default": False
    },
    {
        "code_id": "OP_VECTOR",
        "display_name": "Vector",
        "role": "Support",
        "lore_bio": "Tactical quartermaster supplying frontline teams with reinforced armor and combat stimulants.",
        "base_health": 115.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.3,
        "passive_ability": {"name": "Resource Scavenger", "description": "Extracts 25% more Chronal Shards and weapon ammunition from captured nodes."},
        "tactical_ability": {"name": "Supply Pod Drop", "description": "Calls in a heavy ordnance canister replenishing full armor, ammo, and tactical charges.", "cooldown": 25.0},
        "ultimate_ability": {"name": "Overdrive Surge", "description": "Injects squad with adrenaline, boosting movement speed by 35% and fire rate by 20% for 12s.", "cooldown": 105.0},
        "is_unlocked_default": False
    },
    {
        "code_id": "OP_ZEPHYR",
        "display_name": "Zephyr",
        "role": "Scout",
        "lore_bio": "Hyper-mobile parkour operative capable of defying gravitational velocity limits.",
        "base_health": 95.0,
        "base_shield": 95.0,
        "base_sprint_speed": 8.5,
        "passive_ability": {"name": "Momentum Stacker", "description": "Consecutive slide jumps increase base movement velocity by up to 20%."},
        "tactical_ability": {"name": "Grappling Cable", "description": "Fires a high-tension cable to swing across chasms and scale vertical obstacles.", "cooldown": 10.0},
        "ultimate_ability": {"name": "Hypersonic Burst", "description": "Performs 3 rapid omnidirectional kinetic blinks leaving concussive shockwaves.", "cooldown": 95.0},
        "is_unlocked_default": False
    },
    {
        "code_id": "OP_CHRONO",
        "display_name": "Chrono",
        "role": "Specialist",
        "lore_bio": "Experimental quantum chronologist able to bend local temporal flows around fracture nodes.",
        "base_health": 105.0,
        "base_shield": 100.0,
        "base_sprint_speed": 7.5,
        "passive_ability": {"name": "Temporal Anomaly", "description": "Reduces tactical and ultimate cooldowns of all adjacent squadmates by 10%."},
        "tactical_ability": {"name": "Time Stasis Field", "description": "Projects a temporal bubble that freezes incoming enemy bullets and grenades in mid-air.", "cooldown": 17.0},
        "ultimate_ability": {"name": "Chronal Rewind", "description": "Rewinds a designated Fracture Node back 15 seconds to its previous health and capture state.", "cooldown": 135.0},
        "is_unlocked_default": False
    }
]

ORIGINAL_WEAPONS = [
    {
        "weapon_code": "WEAPON_AR_VORTEX",
        "display_name": "Vortex-44 Assault Rifle",
        "weapon_class": "Assault Rifle",
        "base_damage": 24.0,
        "fire_rate_rpm": 680.0,
        "magazine_capacity": 30,
        "reload_time_seconds": 2.1,
        "effective_range_meters": 55.0,
        "recoil_profile": {"vertical": 1.2, "horizontal": 0.4, "first_shot_multiplier": 1.5}
    },
    {
        "weapon_code": "WEAPON_SMG_STORM",
        "display_name": "Stormburst Submachine Gun",
        "weapon_class": "SMG",
        "base_damage": 17.0,
        "fire_rate_rpm": 920.0,
        "magazine_capacity": 36,
        "reload_time_seconds": 1.6,
        "effective_range_meters": 28.0,
        "recoil_profile": {"vertical": 0.8, "horizontal": 0.7, "first_shot_multiplier": 1.1}
    },
    {
        "weapon_code": "WEAPON_DMR_SPECTRE",
        "display_name": "Spectre-7 Marksman Rifle",
        "weapon_class": "DMR",
        "base_damage": 52.0,
        "fire_rate_rpm": 240.0,
        "magazine_capacity": 15,
        "reload_time_seconds": 2.4,
        "effective_range_meters": 110.0,
        "recoil_profile": {"vertical": 2.8, "horizontal": 0.2, "first_shot_multiplier": 2.0}
    },
    {
        "weapon_code": "WEAPON_SHOTGUN_TITAN",
        "display_name": "Titan-8 Breaching Shotgun",
        "weapon_class": "Shotgun",
        "base_damage": 96.0,
        "fire_rate_rpm": 90.0,
        "magazine_capacity": 8,
        "reload_time_seconds": 3.0,
        "effective_range_meters": 14.0,
        "recoil_profile": {"vertical": 4.5, "horizontal": 1.1, "first_shot_multiplier": 1.0}
    },
    {
        "weapon_code": "WEAPON_PISTOL_ION",
        "display_name": "Ion Pulse Sidearm",
        "weapon_class": "Pistol",
        "base_damage": 32.0,
        "fire_rate_rpm": 400.0,
        "magazine_capacity": 16,
        "reload_time_seconds": 1.2,
        "effective_range_meters": 35.0,
        "recoil_profile": {"vertical": 1.0, "horizontal": 0.3, "first_shot_multiplier": 1.2}
    }
]

ORIGINAL_COSMETICS = [
    {
        "item_code": "SKIN_APEX_CYBERPUNK",
        "name": "Apex: Neon Ronin",
        "description": "High-gloss chrome armor with glowing magenta cyber-chassis accents.",
        "item_type": "skin",
        "rarity": "Legendary",
        "price_credits": 12000,
        "price_shards": 1000,
        "asset_reference": "/Game/Cosmetics/Apex/Skins/SK_Apex_NeonRonin"
    },
    {
        "item_code": "SKIN_BASTION_WARHAMMER",
        "name": "Bastion-9: Obsidian Dreadnought",
        "description": "Heavy matte carbon-fiber armor plating with burning orange thermal vents.",
        "item_type": "skin",
        "rarity": "Epic",
        "price_credits": 8000,
        "price_shards": 600,
        "asset_reference": "/Game/Cosmetics/Bastion/Skins/SK_Bastion_Obsidian"
    },
    {
        "item_code": "WRAP_VORTEX_DRAGON",
        "name": "Vortex-44: Quantum Shimmer",
        "description": "Prismatic animated weapon finish that ripples with chronal energy.",
        "item_type": "weapon_wrap",
        "rarity": "Rare",
        "price_credits": 3500,
        "price_shards": 300,
        "asset_reference": "/Game/Cosmetics/Weapons/Wraps/MAT_QuantumShimmer"
    }
]

ORIGINAL_QUESTS = [
    {
        "title": "Fracture Controller",
        "description": "Capture 5 Fracture Nodes across competitive matches.",
        "quest_category": "daily",
        "target_metric": "nodes_captured",
        "target_count": 5,
        "reward_xp": 1000,
        "reward_credits": 500,
        "reward_shards": 0
    },
    {
        "title": "Subspace Extraction",
        "description": "Successfully extract from a destabilizing fracture zone with at least 50 Chronal Shards.",
        "quest_category": "daily",
        "target_metric": "shards_extracted",
        "target_count": 50,
        "reward_xp": 1500,
        "reward_credits": 750,
        "reward_shards": 25
    },
    {
        "title": "Tactical Superiority",
        "description": "Eliminate 15 enemy operatives in Fracture or Extraction mode.",
        "quest_category": "weekly",
        "target_metric": "eliminations",
        "target_count": 15,
        "reward_xp": 4000,
        "reward_credits": 2000,
        "reward_shards": 50
    }
]

ORIGINAL_ACHIEVEMENTS = [
    {
        "code": "ACH_FIRST_FRACTURE",
        "title": "First Resonance",
        "description": "Successfully capture your very first Fracture Node.",
        "achievement_points": 10,
        "badge_icon": "/Game/UI/Badges/badge_first_fracture.png"
    },
    {
        "code": "ACH_CLEAN_EXTRACTION",
        "title": "Clean Exit",
        "description": "Extract from a tier-5 destabilized match without taking fatal damage.",
        "achievement_points": 25,
        "badge_icon": "/Game/UI/Badges/badge_clean_extraction.png"
    },
    {
        "code": "ACH_APEX_CHAMPION",
        "title": "Master of the Fracture",
        "description": "Win 50 ranked matches with 10 or more eliminations.",
        "achievement_points": 100,
        "badge_icon": "/Game/UI/Badges/badge_master_fracture.png"
    }
]

async def seed_master_game_data(db: AsyncSession):
    # 1. Seed Operatives
    for op_data in ORIGINAL_OPERATIVES:
        res = await db.execute(select(Operative).where(Operative.code_id == op_data["code_id"]))
        if not res.scalar_one_or_none():
            db.add(Operative(**op_data))

    # 2. Seed Weapons
    for wpn_data in ORIGINAL_WEAPONS:
        res = await db.execute(select(Weapon).where(Weapon.weapon_code == wpn_data["weapon_code"]))
        if not res.scalar_one_or_none():
            db.add(Weapon(**wpn_data))

    # 3. Seed Cosmetics & Store Items
    for item_data in ORIGINAL_COSMETICS:
        res = await db.execute(select(Item).where(Item.item_code == item_data["item_code"]))
        if not res.scalar_one_or_none():
            db.add(Item(**item_data))

    # 4. Seed Quests
    for q_data in ORIGINAL_QUESTS:
        res = await db.execute(select(Quest).where(Quest.title == q_data["title"]))
        if not res.scalar_one_or_none():
            db.add(Quest(**q_data))

    # 5. Seed Achievements
    for ach_data in ORIGINAL_ACHIEVEMENTS:
        res = await db.execute(select(Achievement).where(Achievement.code == ach_data["code"]))
        if not res.scalar_one_or_none():
            db.add(Achievement(**ach_data))

    await db.commit()
