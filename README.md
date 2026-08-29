# ECHOFRONT: FRACTURE PROTOCOL

[![Architecture: Authoritative Dedicated Server](https://img.shields.io/badge/Networking-Authoritative%2060Hz%20UDP-cyan.svg)](#)
[![Backend: FastAPI Async](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy-blue.svg)](#)
[![Database: PostgreSQL + Redis](https://img.shields.io/badge/Database-PostgreSQL%2016%20%2B%20Redis%207.2-purple.svg)](#)
[![Engine: Unreal Engine 5](https://img.shields.io/badge/Game%20Engine-Unreal%20Engine%205%20C%2B%2B-black.svg)](#)
[![IP Status: 100% Original Proprietary](https://img.shields.io/badge/Intellectual%20Property-Original%20Registered-green.svg)](#)

---

## 1. Project Overview & Product Vision

**ECHOFRONT: Fracture Protocol** is a high-stakes tactical multiplayer action game designed around dynamic territory control, spatial fracture node harmonics, and tactical extraction. 

Set in the **Fracture Horizon (Year 2148)**, teams of **Resonance Anchors** deploy into unstable fracture sectors to capture energy nodes, overload map conduits, and extract valuable **Chronal Shards** before the battlefield destabilizes.

---

## 2. Core Architecture & System Boundaries

```
echofront/
├── backend/                    # Python 3.12 / FastAPI Async Enterprise Backend
│   ├── app/
│   │   ├── api/v1/             # REST Endpoints (Auth, Player, Loadout, Store, Matchmaking, Admin)
│   │   ├── core/               # Security, JWT, Argon2id, Config, Async Database
│   │   ├── models/             # 28 SQLAlchemy Relational Models (PostgreSQL Core)
│   │   ├── schemas/            # Pydantic v2 Request/Response Data Validation
│   │   ├── services/           # Double-Entry Ledger, Matchmaking, Match Session Reconciler
│   │   └── websockets/         # Real-time WebSocket Event Broker
│   ├── tests/                  # Pytest Unit & Async Integration Test Suite
│   └── main.py                 # Application Lifespan & Startup Entrypoint
├── game-server/                # Authoritative C++ Dedicated Simulation Server
│   ├── include/
│   │   ├── fracture/           # 5-Stage Fracture Node State Machine
│   │   ├── combat/             # Lag Compensation Buffer (Historical Hitbox Rewind)
│   │   └── anticheat/          # Spatial Speedhack & Fire-Rate Sanity Validators
│   └── src/
│       └── ServerMain.cpp      # 60Hz Tick Simulation Loop Runner
├── admin-portal/               # Modern Glassmorphic Admin Telemetry Dashboard (HTML/CSS/JS)
│   ├── index.html              # Live Overview, Operative Matrix, Node Monitor, Player Ban Queue
│   ├── css/style.css           # Premium Cyber-Tactical Dark Styling & Glassmorphism
│   └── js/app.js               # Dynamic Dashboard State & Roster Renderer
├── infrastructure/             # Docker Compose & Container Orchestration Manifests
│   ├── docker-compose.yml      # Multi-container PostgreSQL, Redis, Backend & Admin
│   └── Dockerfile.backend      # Production Container Spec
└── docs/
    └── legal/
        └── ASSET_IP_REGISTRY.json # Formal IP and Commercial Ownership Declarations
```

---

## 3. Quick Start & Execution Guide

### Option A: Run via Docker Compose (Recommended)

```bash
cd infrastructure
docker-compose up --build
```
- **Backend API & OpenAPI Docs**: `http://localhost:8000/docs`
- **Admin Fleet & Moderation Portal**: `http://localhost:3000`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

### Option B: Run Locally with Python

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Start the Backend API
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option C: Run Dedicated Simulation Server (C++)

```bash
cd game-server
g++ -std=c++17 -I.. src/ServerMain.cpp -o EchofrontServer.exe
./EchofrontServer.exe
```

---

## 4. 12 Original Operatives Roster

1. **Vanguard: Apex (AEX-01)** — *Kinetic Shielding* / *Shockwave Dash* / *Graviton Collapse*
2. **Sentinel: Bastion-9** — *Nanite Armor* / *Hardlight Barricade* / *Citadel Lockdown*
3. **Recon: Vapor** — *Thermal Footprints* / *Echo Ping* / *Orbital Recon Drone*
4. **Disruptor: Null** — *Static Interference* / *EMP Dart* / *Blackout Wave*
5. **Engineer: Forge** — *Overclock* / *Deployable Sentry* / *Resonance Core*
6. **Medic: Aegis** — *Field Triage* / *Healing Nanite Cloud* / *Revival Beacon*
7. **Hunter: Wraith** — *Silent Stride* / *Optical Camouflage* / *Phase Shift*
8. **Controller: Cryo** — *Sub-Zero Trail* / *Cryo Grenade* / *Absolute Zero Blizzard*
9. **Infiltrator: Phantom** — *Agile Reflexes* / *Holographic Decoy* / *Quantum Backtrack*
10. **Support: Vector** — *Resource Scavenger* / *Supply Pod Drop* / *Overdrive Surge*
11. **Scout: Zephyr** — *Momentum Stacker* / *Grappling Cable* / *Hypersonic Burst*
12. **Specialist: Chrono** — *Temporal Anomaly* / *Time Stasis Field* / *Chronal Rewind*

---

## 5. Intellectual Property & Ownership Notice

All concepts, characters, weapon designs, narrative lore, network protocols, and source code are registered under the project ownership baseline (`docs/legal/ASSET_IP_REGISTRY.json`). All commercial and derivative rights remain exclusively owned by the project author.
