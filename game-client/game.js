// ECHOFRONT: FRACTURE PROTOCOL - 3D Playable Tactical Shooter Game Engine

class EchofrontGame {
    constructor() {
        this.container = document.getElementById("game-container");
        this.selectedOperative = "APEX";
        this.isGameActive = false;

        // Player State
        this.player = {
            health: 125,
            maxHealth: 125,
            shield: 100,
            maxShield: 100,
            speed: 18,
            sprintMultiplier: 1.6,
            isSprinting: false,
            score: 0,
            kills: 0,
            captures: 0
        };

        // Weapons
        this.weapons = [
            { name: "VORTEX-44 AR", damage: 28, rpm: 650, mag: 30, maxMag: 30, reserve: 180, reloadTime: 1.8, auto: true, spread: 0.02 },
            { name: "STORMBURST SMG", damage: 19, rpm: 900, mag: 36, maxMag: 36, reserve: 216, reloadTime: 1.4, auto: true, spread: 0.04 },
            { name: "TITAN-8 SHOTGUN", damage: 95, rpm: 80, mag: 8, maxMag: 8, reserve: 40, reloadTime: 2.5, auto: false, spread: 0.08 }
        ];
        this.currentWeaponIndex = 0;
        this.isReloading = false;
        this.lastShotTime = 0;
        this.isMouseDown = false;

        // Abilities Cooldowns
        this.cooldowns = {
            tactical: { max: 12, current: 0 },
            ultimate: { max: 45, current: 0 }
        };

        // Match State
        this.scores = { alpha: 0, omega: 0 };
        this.matchTimeSeconds = 600; // 10 minutes
        this.nodes = [];
        this.enemies = [];
        this.projectiles = [];
        this.particles = [];

        // Movement & Controls
        this.keys = {};
        this.moveDirection = new THREE.Vector3();
        this.velocity = new THREE.Vector3();
        this.canJump = true;

        this.initAudio();
        this.initThree();
        this.setupEventListeners();
    }

    initAudio() {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }

    playSynthSound(type) {
        if (!this.audioCtx) return;
        try {
            const ctx = this.audioCtx;
            if (ctx.state === "suspended") ctx.resume();

            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);

            const now = ctx.currentTime;

            if (type === "shoot") {
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(420, now);
                osc.frequency.exponentialRampToValueAtTime(60, now + 0.12);
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
                osc.start(now);
                osc.stop(now + 0.12);
            } else if (type === "hit") {
                osc.type = "sine";
                osc.frequency.setValueAtTime(800, now);
                osc.frequency.exponentialRampToValueAtTime(200, now + 0.08);
                gain.gain.setValueAtTime(0.4, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                osc.start(now);
                osc.stop(now + 0.08);
            } else if (type === "ability") {
                osc.type = "triangle";
                osc.frequency.setValueAtTime(200, now);
                osc.frequency.exponentialRampToValueAtTime(900, now + 0.35);
                gain.gain.setValueAtTime(0.5, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                osc.start(now);
                osc.stop(now + 0.35);
            } else if (type === "reload") {
                osc.type = "square";
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.setValueAtTime(500, now + 0.15);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }
        } catch (e) {
            // Audio fallback
        }
    }

    initThree() {
        // 1. Scene & Camera
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x06080e);
        this.scene.fog = new THREE.FogExp2(0x06080e, 0.012);

        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 3, 20);

        // 2. WebGL Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // 3. Lighting
        const ambientLight = new THREE.AmbientLight(0x223344, 1.2);
        this.scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.5);
        dirLight.position.set(30, 60, 20);
        dirLight.castShadow = true;
        this.scene.add(dirLight);

        // 4. Map Environment (Reactor Sector 07 Arena)
        this.buildArenaEnvironment();

        // 5. Spawn 3 Dynamic Fracture Nodes
        this.spawnFractureNode("NODE_A", new THREE.Vector3(0, 0, 0), "Alpha Core", 0x38bdf8);
        this.spawnFractureNode("NODE_B", new THREE.Vector3(45, 0, -35), "Bravo Reactor", 0xf59e0b);
        this.spawnFractureNode("NODE_C", new THREE.Vector3(-45, 0, -35), "Charlie Silo", 0xa855f7);

        // 6. Spawn Initial Hostile Combat Droids
        for (let i = 0; i < 4; i++) {
            this.spawnEnemyDroid(
                new THREE.Vector3((Math.random() - 0.5) * 80, 0, -40 - Math.random() * 30)
            );
        }

        // 7. FPS Weapon Viewmodel
        this.createWeaponViewmodel();

        window.addEventListener("resize", () => this.onWindowResize());
    }

    buildArenaEnvironment() {
        // Floor
        const floorGeo = new THREE.PlaneGeometry(160, 160);
        const floorMat = new THREE.MeshStandardMaterial({
            color: 0x0f172a,
            roughness: 0.6,
            metalness: 0.4
        });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        this.scene.add(floor);

        // Grid Floor Lines
        const grid = new THREE.GridHelper(160, 40, 0x38bdf8, 0x1e293b);
        grid.position.y = 0.05;
        this.scene.add(grid);

        // Perimeter Walls
        const wallMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.5, roughness: 0.5 });
        const wallGeo = new THREE.BoxGeometry(160, 15, 4);

        const northWall = new THREE.Mesh(wallGeo, wallMat);
        northWall.position.set(0, 7.5, -80);
        this.scene.add(northWall);

        const southWall = new THREE.Mesh(wallGeo, wallMat);
        southWall.position.set(0, 7.5, 80);
        this.scene.add(southWall);

        const eastWall = new THREE.Mesh(new THREE.BoxGeometry(4, 15, 160), wallMat);
        eastWall.position.set(80, 7.5, 0);
        this.scene.add(eastWall);

        const westWall = new THREE.Mesh(new THREE.BoxGeometry(4, 15, 160), wallMat);
        westWall.position.set(-80, 7.5, 0);
        this.scene.add(westWall);

        // Tactical Cover Pillars & Platforms
        const pillarMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.3, metalness: 0.7 });
        const coverPositions = [
            [-20, 3, -15], [20, 3, -15], [-20, 3, 15], [20, 3, 15],
            [-35, 4, -10], [35, 4, -10], [0, 2, -45], [0, 2, 45]
        ];

        coverPositions.forEach(pos => {
            const pillar = new THREE.Mesh(new THREE.BoxGeometry(6, 8, 6), pillarMat);
            pillar.position.set(pos[0], pos[1], pos[2]);
            pillar.castShadow = true;
            pillar.receiveShadow = true;
            this.scene.add(pillar);
        });
    }

    spawnFractureNode(id, pos, name, colorHex) {
        const group = new THREE.Group();
        group.position.copy(pos);

        // Base Ring
        const ringGeo = new THREE.TorusGeometry(8, 0.4, 16, 64);
        const ringMat = new THREE.MeshStandardMaterial({
            color: colorHex,
            emissive: colorHex,
            emissiveIntensity: 0.6,
            roughness: 0.2
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        group.add(ring);

        // Core Glowing Crystal
        const coreGeo = new THREE.OctahedronGeometry(2.2, 0);
        const coreMat = new THREE.MeshStandardMaterial({
            color: colorHex,
            emissive: colorHex,
            emissiveIntensity: 1.2,
            wireframe: false
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        core.position.y = 4.5;
        group.add(core);

        // Ambient Point Light
        const light = new THREE.PointLight(colorHex, 2, 25);
        light.position.y = 5;
        group.add(light);

        this.scene.add(group);

        this.nodes.push({
            id: id,
            name: name,
            position: pos,
            group: group,
            coreMesh: core,
            controllingTeam: "neutral", // "alpha", "omega", "neutral"
            captureProgress: 0, // -100 (Omega) to 100 (Alpha)
            colorHex: colorHex
        });
    }

    spawnEnemyDroid(pos) {
        const group = new THREE.Group();
        group.position.copy(pos);

        // Body Chassis
        const bodyGeo = new THREE.BoxGeometry(2, 3.2, 1.4);
        const bodyMat = new THREE.MeshStandardMaterial({ color: 0x991b1b, metalness: 0.8, roughness: 0.2 });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = 1.6;
        body.castShadow = true;
        group.add(body);

        // Glowing Eye Sensor
        const eyeGeo = new THREE.BoxGeometry(1.2, 0.4, 0.4);
        const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(0, 2.6, 0.7);
        group.add(eye);

        this.scene.add(group);

        this.enemies.push({
            group: group,
            health: 80,
            maxHealth: 80,
            speed: 8,
            lastShotTime: 0,
            targetNode: this.nodes[Math.floor(Math.random() * this.nodes.length)]
        });
    }

    createWeaponViewmodel() {
        this.gunGroup = new THREE.Group();

        const gunBodyGeo = new THREE.BoxGeometry(0.3, 0.4, 1.6);
        const gunMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.9, roughness: 0.2 });
        const gunMesh = new THREE.Mesh(gunBodyGeo, gunMat);
        gunMesh.position.set(0.6, -0.6, -1.2);
        this.gunGroup.add(gunMesh);

        // Barrel glow
        const barrelGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 16);
        const barrelMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        const barrel = new THREE.Mesh(barrelGeo, barrelMat);
        barrel.rotation.x = Math.PI / 2;
        barrel.position.set(0.6, -0.6, -1.9);
        this.gunGroup.add(barrel);

        this.camera.add(this.gunGroup);
        this.scene.add(this.camera);
    }

    setupEventListeners() {
        // Operative Selection
        document.querySelectorAll(".op-select-card").forEach(card => {
            card.addEventListener("click", () => {
                document.querySelectorAll(".op-select-card").forEach(c => c.classList.remove("active"));
                card.classList.add("active");
                this.selectedOperative = card.getAttribute("data-op");
            });
        });

        // Deploy Button
        document.getElementById("btn-deploy").addEventListener("click", () => {
            this.deployMatch();
        });

        document.getElementById("btn-restart").addEventListener("click", () => {
            location.reload();
        });

        // Keyboard Inputs
        window.addEventListener("keydown", (e) => {
            this.keys[e.code] = true;
            if (e.code === "KeyR") this.reloadCurrentWeapon();
            if (e.code === "Digit1") this.switchWeapon(0);
            if (e.code === "Digit2") this.switchWeapon(1);
            if (e.code === "Digit3") this.switchWeapon(2);
            if (e.code === "KeyQ") this.triggerTacticalAbility();
            if (e.code === "KeyZ") this.triggerUltimateAbility();
        });

        window.addEventListener("keyup", (e) => {
            this.keys[e.code] = false;
        });

        // Mouse Aim & Shoot
        window.addEventListener("mousedown", (e) => {
            if (!this.isGameActive) return;
            if (e.button === 0) {
                this.isMouseDown = true;
                this.fireCurrentWeapon();
            }
        });

        window.addEventListener("mouseup", (e) => {
            if (e.button === 0) this.isMouseDown = false;
        });

        window.addEventListener("mousemove", (e) => {
            if (document.pointerLockElement === document.body && this.isGameActive) {
                const movementX = e.movementX || 0;
                const movementY = e.movementY || 0;

                this.camera.rotation.y -= movementX * 0.0022;
                this.camera.rotation.x -= movementY * 0.0022;
                this.camera.rotation.x = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, this.camera.rotation.x));
            }
        });
    }

    deployMatch() {
        document.getElementById("start-screen").style.display = "none";
        document.body.requestPointerLock();
        this.isGameActive = true;
        this.updateHUD();

        // Update Operative Badge
        const nameMap = {
            "APEX": "APEX (AEX-01) // Vanguard",
            "BASTION": "BASTION-9 // Sentinel",
            "VAPOR": "VAPOR // Recon",
            "WRAITH": "WRAITH // Hunter"
        };
        document.getElementById("player-op-name").innerText = nameMap[this.selectedOperative] || "APEX";

        this.lastFrameTime = performance.now();
        requestAnimationFrame((t) => this.gameLoop(t));
    }

    gameLoop(timestamp) {
        if (!this.isGameActive) return;

        const dt = Math.min((timestamp - this.lastFrameTime) / 1000, 0.1);
        this.lastFrameTime = timestamp;

        this.updatePlayerMovement(dt);
        this.updateWeapons(dt);
        this.updateAbilities(dt);
        this.updateFractureNodes(dt);
        this.updateEnemyAI(dt);
        this.updateProjectilesAndParticles(dt);
        this.updateMatchTime(dt);

        // Render Frame
        this.renderer.render(this.scene, this.camera);
        requestAnimationFrame((t) => this.gameLoop(t));
    }

    updatePlayerMovement(dt) {
        this.player.isSprinting = !!this.keys["ShiftLeft"] || !!this.keys["ShiftRight"];
        const moveSpeed = this.player.speed * (this.player.isSprinting ? this.player.sprintMultiplier : 1.0);

        this.moveDirection.set(0, 0, 0);

        if (this.keys["KeyW"]) this.moveDirection.z -= 1;
        if (this.keys["KeyS"]) this.moveDirection.z += 1;
        if (this.keys["KeyA"]) this.moveDirection.x -= 1;
        if (this.keys["KeyD"]) this.moveDirection.x += 1;

        this.moveDirection.normalize();
        this.moveDirection.applyEuler(new THREE.Euler(0, this.camera.rotation.y, 0));

        this.camera.position.addScaledVector(this.moveDirection, moveSpeed * dt);

        // Clamp arena bounds
        this.camera.position.x = Math.max(-75, Math.min(75, this.camera.position.x));
        this.camera.position.z = Math.max(-75, Math.min(75, this.camera.position.z));
        this.camera.position.y = 3; // Camera eye height

        // Weapon bobbing animation
        if (this.moveDirection.lengthSq() > 0) {
            const bob = Math.sin(timestampNow() * 10) * 0.03;
            this.gunGroup.position.y = bob;
        }
    }

    updateWeapons(dt) {
        const wpn = this.weapons[this.currentWeaponIndex];
        if (this.isMouseDown && wpn.auto) {
            this.fireCurrentWeapon();
        }
    }

    fireCurrentWeapon() {
        const now = performance.now();
        const wpn = this.weapons[this.currentWeaponIndex];
        const shotDelay = 60000 / wpn.rpm;

        if (now - this.lastShotTime < shotDelay || this.isReloading) return;
        if (wpn.mag <= 0) {
            this.reloadCurrentWeapon();
            return;
        }

        this.lastShotTime = now;
        wpn.mag--;
        this.updateHUD();
        this.playSynthSound("shoot");

        // Visual Gun Kick
        this.gunGroup.position.z += 0.15;
        setTimeout(() => { if (this.gunGroup) this.gunGroup.position.z = 0; }, 60);

        // Raycast Hit Scan
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);

        // Check enemy droid hits
        this.enemies.forEach((enemy, index) => {
            const dist = this.camera.position.distanceTo(enemy.group.position);
            const dirToEnemy = enemy.group.position.clone().sub(this.camera.position).normalize();
            const camDir = new THREE.Vector3();
            this.camera.getWorldDirection(camDir);

            if (camDir.dot(dirToEnemy) > 0.985 && dist < 70) {
                // Enemy Hit
                enemy.health -= wpn.damage;
                this.triggerHitmarker();
                this.playSynthSound("hit");

                if (enemy.health <= 0) {
                    this.eliminateEnemy(enemy, index);
                }
            }
        });
    }

    reloadCurrentWeapon() {
        const wpn = this.weapons[this.currentWeaponIndex];
        if (this.isReloading || wpn.mag === wpn.maxMag || wpn.reserve <= 0) return;

        this.isReloading = true;
        this.playSynthSound("reload");

        setTimeout(() => {
            const needed = wpn.maxMag - wpn.mag;
            const transfer = Math.min(needed, wpn.reserve);
            wpn.mag += transfer;
            wpn.reserve -= transfer;
            this.isReloading = false;
            this.updateHUD();
        }, wpn.reloadTime * 1000);
    }

    switchWeapon(index) {
        if (index === this.currentWeaponIndex || this.isReloading) return;
        this.currentWeaponIndex = index;
        document.querySelectorAll(".slot-badge").forEach((b, i) => {
            b.classList.toggle("active", i === index);
        });
        this.updateHUD();
    }

    triggerTacticalAbility() {
        if (this.cooldowns.tactical.current > 0) return;
        this.cooldowns.tactical.current = this.cooldowns.tactical.max;
        this.playSynthSound("ability");

        // Apex Shockwave Dash
        const dashDir = new THREE.Vector3();
        this.camera.getWorldDirection(dashDir);
        dashDir.y = 0;
        dashDir.normalize();

        this.camera.position.addScaledVector(dashDir, 25);
        this.addKillfeedEntry(`⚡ Tactical Ability Activated: SHOCKWAVE DASH`);
    }

    triggerUltimateAbility() {
        if (this.cooldowns.ultimate.current > 0) return;
        this.cooldowns.ultimate.current = this.cooldowns.ultimate.max;
        this.playSynthSound("ability");

        // Apex Graviton Singularity (Damages all nearby enemies)
        this.enemies.forEach((enemy, index) => {
            if (this.camera.position.distanceTo(enemy.group.position) < 35) {
                enemy.health -= 120;
                if (enemy.health <= 0) this.eliminateEnemy(enemy, index);
            }
        });

        this.addKillfeedEntry(`💥 Ultimate Activated: GRAVITON COLLAPSE`);
    }

    updateAbilities(dt) {
        if (this.cooldowns.tactical.current > 0) {
            this.cooldowns.tactical.current = Math.max(0, this.cooldowns.tactical.current - dt);
            const pct = (this.cooldowns.tactical.current / this.cooldowns.tactical.max) * 100;
            document.getElementById("cd-tactical").style.height = `${pct}%`;
        }

        if (this.cooldowns.ultimate.current > 0) {
            this.cooldowns.ultimate.current = Math.max(0, this.cooldowns.ultimate.current - dt);
            const pct = (this.cooldowns.ultimate.current / this.cooldowns.ultimate.max) * 100;
            document.getElementById("cd-ultimate").style.height = `${pct}%`;
        }
    }

    updateFractureNodes(dt) {
        let isNearAnyNode = false;

        this.nodes.forEach((node, i) => {
            // Spin core animation
            node.coreMesh.rotation.y += 0.02;
            node.coreMesh.rotation.x += 0.01;

            const dist = this.camera.position.distanceTo(node.position);
            const hudFill = document.getElementById(`fill-node-${node.id.slice(-1).toLowerCase()}`);

            // Player Capture in radius (12 meters)
            if (dist < 12) {
                isNearAnyNode = true;
                node.captureProgress = Math.min(100, node.captureProgress + 25 * dt);
                if (node.captureProgress >= 100 && node.controllingTeam !== "alpha") {
                    node.controllingTeam = "alpha";
                    this.player.captures++;
                    this.addKillfeedEntry(`⚡ Team Alpha captured ${node.name}!`);
                }
            }

            // Sync HUD Fill
            if (hudFill) {
                hudFill.style.width = `${Math.abs(node.captureProgress)}%`;
                hudFill.style.background = node.controllingTeam === "alpha" ? "#38bdf8" : (node.controllingTeam === "omega" ? "#ef4444" : "#94a3b8");
            }

            // Generate Match Score
            if (node.controllingTeam === "alpha") {
                this.scores.alpha += 2.5 * dt;
            } else if (node.controllingTeam === "omega") {
                this.scores.omega += 2.5 * dt;
            }
        });

        document.getElementById("interact-prompt").style.display = isNearAnyNode ? "block" : "none";
        document.getElementById("score-alpha").innerText = Math.floor(this.scores.alpha);
        document.getElementById("score-omega").innerText = Math.floor(this.scores.omega);
    }

    updateEnemyAI(dt) {
        const now = performance.now();

        this.enemies.forEach((enemy) => {
            const distToPlayer = enemy.group.position.distanceTo(this.camera.position);

            // Move towards player or target node
            const targetPos = distToPlayer < 40 ? this.camera.position : enemy.targetNode.position;
            const dir = targetPos.clone().sub(enemy.group.position).normalize();
            dir.y = 0;

            enemy.group.position.addScaledVector(dir, enemy.speed * dt);
            enemy.group.lookAt(targetPos.x, enemy.group.position.y, targetPos.z);

            // Enemy Shooting
            if (distToPlayer < 35 && now - enemy.lastShotTime > 1600) {
                enemy.lastShotTime = now;
                this.damagePlayer(15);
            }
        });
    }

    damagePlayer(amount) {
        if (this.player.shield > 0) {
            this.player.shield = Math.max(0, this.player.shield - amount);
        } else {
            this.player.health = Math.max(0, this.player.health - amount);
        }

        // Damage flash UI
        const flash = document.getElementById("damage-flash");
        flash.style.opacity = "1";
        setTimeout(() => { flash.style.opacity = "0"; }, 200);

        this.updateHUD();

        if (this.player.health <= 0) {
            this.endGame(false);
        }
    }

    eliminateEnemy(enemy, index) {
        this.scene.remove(enemy.group);
        this.enemies.splice(index, 1);
        this.player.kills++;
        this.addKillfeedEntry(`💀 You eliminated Rogue Combat Droid`);

        // Respawn new droid
        setTimeout(() => {
            this.spawnEnemyDroid(new THREE.Vector3((Math.random() - 0.5) * 80, 0, -40 - Math.random() * 30));
        }, 4000);
    }

    triggerHitmarker() {
        const hm = document.getElementById("hitmarker");
        hm.style.opacity = "1";
        setTimeout(() => { hm.style.opacity = "0"; }, 100);
    }

    addKillfeedEntry(text) {
        const feed = document.getElementById("killfeed");
        const entry = document.createElement("div");
        entry.className = "killfeed-item";
        entry.innerText = text;
        feed.appendChild(entry);
        setTimeout(() => { entry.remove(); }, 4000);
    }

    updateProjectilesAndParticles(dt) {
        // Particle rotations and cleanup
    }

    updateMatchTime(dt) {
        this.matchTimeSeconds -= dt;
        if (this.matchTimeSeconds <= 0 || this.scores.alpha >= 1000) {
            this.endGame(true);
        }

        const mins = Math.floor(this.matchTimeSeconds / 60);
        const secs = Math.floor(this.matchTimeSeconds % 60);
        document.getElementById("match-timer").innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    updateHUD() {
        const wpn = this.weapons[this.currentWeaponIndex];
        document.getElementById("current-weapon-name").innerText = wpn.name;
        document.getElementById("ammo-current").innerText = wpn.mag;
        document.getElementById("ammo-reserve").innerText = wpn.reserve;

        // Health & Shield Bars
        const shieldPct = (this.player.shield / this.player.maxShield) * 100;
        const healthPct = (this.player.health / this.player.maxHealth) * 100;

        document.getElementById("shield-fill").style.width = `${shieldPct}%`;
        document.getElementById("shield-text").innerText = `${Math.floor(this.player.shield)} / ${this.player.maxShield}`;

        document.getElementById("health-fill").style.width = `${healthPct}%`;
        document.getElementById("health-text").innerText = `${Math.floor(this.player.health)} / ${this.player.maxHealth}`;
    }

    endGame(isVictory) {
        this.isGameActive = false;
        document.exitPointerLock();

        const modal = document.getElementById("gameover-screen");
        modal.style.display = "flex";
        document.getElementById("endgame-title").innerText = isVictory ? "MISSION ACCOMPLISHED // EXTRACTION SUCCESS" : "CRITICAL FAILURE // OPERATIVE DOWN";
        document.getElementById("endgame-summary").innerText = isVictory
            ? "You secured the Fracture Nodes and extracted with 240 Chronal Shards."
            : "Your operative sustained fatal damage in the unstable fracture zone.";

        document.getElementById("endgame-stats").innerHTML = `
            <div style="display: flex; justify-content: space-around; font-family: var(--font-mono); margin: 20px 0; font-size: 1.1rem;">
                <div>ELIMINATIONS: <strong style="color: #38bdf8;">${this.player.kills}</strong></div>
                <div>NODES CAPTURED: <strong style="color: #f59e0b;">${this.player.captures}</strong></div>
                <div>TEAM SCORE: <strong style="color: #10b981;">${Math.floor(this.scores.alpha)}</strong></div>
            </div>
        `;
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

function timestampNow() {
    return performance.now() / 1000;
}

// Start Game Instance
window.addEventListener("DOMContentLoaded", () => {
    window.echofrontGame = new EchofrontGame();
});
