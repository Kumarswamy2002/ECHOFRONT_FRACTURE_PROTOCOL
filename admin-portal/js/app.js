// ECHOFRONT: FRACTURE PROTOCOL - Real-time Admin Telemetry & Operations Console

const OPERATIVES_DATA = [
    {
        code: "OP_APEX",
        name: "Apex (AEX-01)",
        role: "Vanguard",
        bio: "Cybernetic frontline breacher specialized in kinetic suppression and room clearing.",
        passive: "Kinetic Shielding (15% shock reduction)",
        tactical: "Shockwave Dash (14s CD)",
        ultimate: "Graviton Collapse (110s CD)"
    },
    {
        code: "OP_BASTION",
        name: "Bastion-9",
        role: "Sentinel",
        bio: "Heavy defensive anchor equipped to fortify and lock down critical Fracture Nodes.",
        passive: "Nanite Armor (+4 shield/s)",
        tactical: "Hardlight Barricade (18s CD)",
        ultimate: "Citadel Lockdown (130s CD)"
    },
    {
        code: "OP_VAPOR",
        name: "Vapor",
        role: "Recon",
        bio: "Covert scout equipped with multispectral optical telemetry sensors.",
        passive: "Thermal Footprints (8s glow)",
        tactical: "Echo Ping (16s CD)",
        ultimate: "Orbital Recon Drone (120s CD)"
    },
    {
        code: "OP_NULL",
        name: "Null",
        role: "Disruptor",
        bio: "Cyberwarfare specialist capable of paralyzing enemy node networks and electronics.",
        passive: "Static Interference (15m scramble)",
        tactical: "EMP Dart (15s CD)",
        ultimate: "Blackout Wave (125s CD)"
    },
    {
        code: "OP_FORGE",
        name: "Forge",
        role: "Engineer",
        bio: "Master technician with extensive knowledge of reactor thermodynamics and fracture nodes.",
        passive: "Overclock (+30% capture speed)",
        tactical: "Deployable Sentry (20s CD)",
        ultimate: "Resonance Core (115s CD)"
    },
    {
        code: "OP_AEGIS",
        name: "Aegis",
        role: "Medic",
        bio: "Combat lifesaver utilizing biocatalytic nanite swarms to reverse mortal trauma in the field.",
        passive: "Field Triage (+40% revive speed)",
        tactical: "Healing Nanite Cloud (14s CD)",
        ultimate: "Revival Beacon (140s CD)"
    },
    {
        code: "OP_WRAITH",
        name: "Wraith",
        role: "Hunter",
        bio: "Lethal assassin trained in high-speed cloaking strikes and silent execution.",
        passive: "Silent Stride (0 acoustic footprint)",
        tactical: "Optical Camouflage (18s CD)",
        ultimate: "Phase Shift (100s CD)"
    },
    {
        code: "OP_CRYO",
        name: "Cryo",
        role: "Controller",
        bio: "Cryogenic hazard controller armed with sub-zero atmospheric flash-freezing gear.",
        passive: "Sub-Zero Trail (25% enemy slow)",
        tactical: "Cryo Grenade (15s CD)",
        ultimate: "Absolute Zero Blizzard (120s CD)"
    },
    {
        code: "OP_PHANTOM",
        name: "Phantom",
        role: "Infiltrator",
        bio: "Deception operative utilizing quantum holographic clones and temporal position anchors.",
        passive: "Agile Reflexes (+30% reload/swap)",
        tactical: "Holographic Decoy (12s CD)",
        ultimate: "Quantum Backtrack (90s CD)"
    },
    {
        code: "OP_VECTOR",
        name: "Vector",
        role: "Support",
        bio: "Tactical quartermaster supplying frontline teams with reinforced armor and combat stimulants.",
        passive: "Resource Scavenger (+25% shards)",
        tactical: "Supply Pod Drop (25s CD)",
        ultimate: "Overdrive Surge (105s CD)"
    },
    {
        code: "OP_ZEPHYR",
        name: "Zephyr",
        role: "Scout",
        bio: "Hyper-mobile parkour operative capable of defying gravitational velocity limits.",
        passive: "Momentum Stacker (+20% velocity)",
        tactical: "Grappling Cable (10s CD)",
        ultimate: "Hypersonic Burst (95s CD)"
    },
    {
        code: "OP_CHRONO",
        name: "Chrono",
        role: "Specialist",
        bio: "Experimental quantum chronologist able to bend local temporal flows around fracture nodes.",
        passive: "Temporal Anomaly (-10% squad CDs)",
        tactical: "Time Stasis Field (17s CD)",
        ultimate: "Chronal Rewind (135s CD)"
    }
];

const NODES_DATA = [
    { id: "NODE_ALPHA", name: "Alpha Core (Sublevel 1)", state: "Harmonized", team: "Team Alpha (Blue)", energy: 8450, stability: 82 },
    { id: "NODE_BRAVO", name: "Bravo Reactor (Chasm Bridge)", state: "Overloaded", team: "Team Omega (Red)", energy: 12400, stability: 34 },
    { id: "NODE_CHARLIE", name: "Charlie Silo (Extraction Hub)", state: "Capturing", team: "Contested", energy: 3100, stability: 96 }
];

const PLAYERS_DATA = [
    { username: "VortexRunner", display: "VortexRunner", level: 42, rank: "Ascendant II", credits: 24800, shards: 1450, status: "In Match" },
    { username: "CipherGhost", display: "CipherGhost", level: 29, rank: "Vanguard I", credits: 16200, shards: 620, status: "Lobby" },
    { username: "QuantumZero", display: "QuantumZero", level: 58, rank: "Grandmaster", credits: 68400, shards: 4800, status: "In Match" },
    { username: "ShadowEcho", display: "ShadowEcho", level: 14, rank: "Cadet III", credits: 7500, shards: 200, status: "Offline" }
];

const STORE_DATA = [
    { code: "SKIN_APEX_CYBERPUNK", name: "Apex: Neon Ronin", type: "Legendary Skin", icon: "🤖", priceCredits: 12000, priceShards: 1000 },
    { code: "SKIN_BASTION_WARHAMMER", name: "Bastion: Obsidian Dreadnought", type: "Epic Skin", icon: "🛡️", priceCredits: 8000, priceShards: 600 },
    { code: "WRAP_VORTEX_DRAGON", name: "Vortex-44: Quantum Shimmer", type: "Rare Wrap", icon: "🔫", priceCredits: 3500, priceShards: 300 }
];

// Initialize on DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
    setupTabNavigation();
    renderOperatives();
    renderNodes();
    renderPlayers();
    renderStore();
    setupRefreshButton();
});

function setupTabNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetTab = item.getAttribute("data-tab");

            navItems.forEach(n => n.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            item.classList.add("active");
            const activePane = document.getElementById(`tab-${targetTab}`);
            if (activePane) activePane.classList.add("active");
        });
    });
}

function renderOperatives() {
    const grid = document.getElementById("operatives-grid");
    if (!grid) return;

    grid.innerHTML = OPERATIVES_DATA.map(op => `
        <div class="op-card">
            <div class="op-card-header">
                <span class="op-name">${op.name}</span>
                <span class="op-role">${op.role}</span>
            </div>
            <p class="op-bio">${op.bio}</p>
            <div class="op-abilities">
                <div class="ability-row">
                    <span class="ability-type">PASSIVE</span>
                    <span class="ability-title">${op.passive}</span>
                </div>
                <div class="ability-row">
                    <span class="ability-type">TACTICAL</span>
                    <span class="ability-title">${op.tactical}</span>
                </div>
                <div class="ability-row">
                    <span class="ability-type">ULTIMATE</span>
                    <span class="ability-title">${op.ultimate}</span>
                </div>
            </div>
        </div>
    `).join("");
}

function renderNodes() {
    const grid = document.getElementById("nodes-grid");
    if (!grid) return;

    grid.innerHTML = NODES_DATA.map(node => `
        <div class="node-card">
            <div class="node-header">
                <h3>${node.name}</h3>
                <span class="badge ${node.state === 'Overloaded' ? 'warning' : 'mode-fracture'}">${node.state}</span>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px;">Control: <strong>${node.team}</strong></p>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-dim);">
                <span>Stability</span>
                <span>${node.stability}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${node.stability}%;"></div>
            </div>
            <div style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--primary);">
                ⚡ Total Energy: ${node.energy.toLocaleString()} EU
            </div>
        </div>
    `).join("");
}

function renderPlayers() {
    const tbody = document.getElementById("players-tbody");
    if (!tbody) return;

    tbody.innerHTML = PLAYERS_DATA.map(p => `
        <tr>
            <td><code>${p.username}</code></td>
            <td><strong>${p.display}</strong></td>
            <td><span class="badge" style="background: rgba(255,255,255,0.1);">${p.level}</span></td>
            <td><span style="color: #38bdf8; font-weight: 600;">${p.rank}</span></td>
            <td>${p.credits.toLocaleString()} CR</td>
            <td style="color: #fbbf24;">${p.shards} ✦</td>
            <td><span class="status-pill in-progress">${p.status}</span></td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="inspectPlayer('${p.username}')">Inspect</button>
            </td>
        </tr>
    `).join("");
}

function renderStore() {
    const grid = document.getElementById("store-grid");
    if (!grid) return;

    grid.innerHTML = STORE_DATA.map(item => `
        <div class="store-card">
            <div class="store-preview">${item.icon}</div>
            <div class="store-title">${item.name}</div>
            <div class="store-rarity">${item.type}</div>
            <div class="store-price">${item.priceCredits.toLocaleString()} Credits / ${item.priceShards} Shards</div>
        </div>
    `).join("");
}

function inspectPlayer(username) {
    alert(`[ECHOFRONT AUDIT] Player Profile: ${username}\nState: Active in match\nIntegrity: Clean`);
}

function setupRefreshButton() {
    const btn = document.getElementById("btn-refresh");
    if (!btn) return;
    btn.addEventListener("click", () => {
        btn.innerText = "Syncing...";
        setTimeout(() => {
            btn.innerText = "⟳ Refresh Telemetry";
            const ccu = document.getElementById("stat-ccu");
            if (ccu) {
                const current = parseInt(ccu.innerText.replace(",", "")) || 1482;
                ccu.innerText = (current + Math.floor(Math.random() * 15 - 5)).toLocaleString();
            }
        }, 400);
    });
}
