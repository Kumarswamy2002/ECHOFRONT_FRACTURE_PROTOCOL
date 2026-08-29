#pragma once
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <iostream>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Abilities {

enum class AbilitySlot {
    Passive = 0,
    Tactical = 1,
    Ultimate = 2
};

enum class AbilityExecutionState {
    Ready = 0,
    Casting = 1,
    Active = 2,
    CoolingDown = 3,
    Blocked = 4
};

struct AbilityDefinition {
    std::string abilityCode;
    std::string name;
    AbilitySlot slot;
    float castTimeSeconds{0.0f};
    float activeDurationSeconds{0.0f};
    float cooldownSeconds{15.0f};
    float energyCost{0.0f};
    float effectRadiusMeters{0.0f};
    float baseDamage{0.0f};
};

class AbilityInstance {
public:
    AbilityDefinition def;
    AbilityExecutionState state{AbilityExecutionState::Ready};
    float remainingCooldown{0.0f};
    float remainingActiveTime{0.0f};

    AbilityInstance(const AbilityDefinition& definition)
        : def(definition) {}

    bool Trigger(const std::string& casterId, const Simulation::Vector3& castLocation, std::function<void()> onExecuteCallback) {
        if (state != AbilityExecutionState::Ready) {
            return false;
        }

        state = AbilityExecutionState::Active;
        remainingActiveTime = def.activeDurationSeconds;
        remainingCooldown = def.cooldownSeconds;

        if (onExecuteCallback) {
            onExecuteCallback();
        }

        std::cout << "[ABILITY EXECUTED] " << casterId << " triggered " << def.name << " (" << def.abilityCode << ")\n";
        return true;
    }

    void Tick(float deltaTime) {
        if (state == AbilityExecutionState::Active) {
            remainingActiveTime -= deltaTime;
            if (remainingActiveTime <= 0.0f) {
                remainingActiveTime = 0.0f;
                state = AbilityExecutionState::CoolingDown;
            }
        } else if (state == AbilityExecutionState::CoolingDown) {
            remainingCooldown -= deltaTime;
            if (remainingCooldown <= 0.0f) {
                remainingCooldown = 0.0f;
                state = AbilityExecutionState::Ready;
            }
        }
    }
};

class OperativeAbilitySet {
public:
    std::string operativeCode;
    std::unique_ptr<AbilityInstance> tactical;
    std::unique_ptr<AbilityInstance> ultimate;

    OperativeAbilitySet(const std::string& code) : operativeCode(code) {
        InitializeForCode(code);
    }

    void Tick(float deltaTime) {
        if (tactical) tactical->Tick(deltaTime);
        if (ultimate) ultimate->Tick(deltaTime);
    }

private:
    void InitializeForCode(const std::string& code) {
        if (code == "OP_APEX") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"APEX_TACTICAL", "Shockwave Dash", AbilitySlot::Tactical, 0.1f, 0.4f, 14.0f, 0.0f, 10.0f, 40.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"APEX_ULTIMATE", "Graviton Collapse", AbilitySlot::Ultimate, 0.5f, 5.0f, 110.0f, 0.0f, 12.0f, 120.0f});
        } else if (code == "OP_BASTION") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"BASTION_TACTICAL", "Hardlight Barricade", AbilitySlot::Tactical, 0.2f, 12.0f, 18.0f, 0.0f, 4.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"BASTION_ULTIMATE", "Citadel Lockdown", AbilitySlot::Ultimate, 1.0f, 25.0f, 130.0f, 0.0f, 20.0f, 0.0f});
        } else if (code == "OP_VAPOR") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"VAPOR_TACTICAL", "Echo Ping", AbilitySlot::Tactical, 0.1f, 6.0f, 16.0f, 0.0f, 25.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"VAPOR_ULTIMATE", "Orbital Recon Drone", AbilitySlot::Ultimate, 0.5f, 15.0f, 120.0f, 0.0f, 60.0f, 0.0f});
        } else if (code == "OP_NULL") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"NULL_TACTICAL", "EMP Dart", AbilitySlot::Tactical, 0.1f, 1.0f, 15.0f, 0.0f, 8.0f, 25.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"NULL_ULTIMATE", "Blackout Wave", AbilitySlot::Ultimate, 0.8f, 8.0f, 125.0f, 0.0f, 40.0f, 0.0f});
        } else if (code == "OP_FORGE") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"FORGE_TACTICAL", "Deployable Sentry", AbilitySlot::Tactical, 0.5f, 30.0f, 20.0f, 0.0f, 18.0f, 15.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"FORGE_ULTIMATE", "Resonance Core", AbilitySlot::Ultimate, 1.0f, 20.0f, 115.0f, 0.0f, 25.0f, 0.0f});
        } else if (code == "OP_AEGIS") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"AEGIS_TACTICAL", "Healing Nanite Cloud", AbilitySlot::Tactical, 0.2f, 8.0f, 14.0f, 0.0f, 10.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"AEGIS_ULTIMATE", "Revival Beacon", AbilitySlot::Ultimate, 0.5f, 10.0f, 140.0f, 0.0f, 15.0f, 0.0f});
        } else if (code == "OP_WRAITH") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"WRAITH_TACTICAL", "Optical Camouflage", AbilitySlot::Tactical, 0.1f, 6.0f, 18.0f, 0.0f, 0.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"WRAITH_ULTIMATE", "Phase Shift", AbilitySlot::Ultimate, 0.3f, 1.0f, 100.0f, 0.0f, 25.0f, 150.0f});
        } else if (code == "OP_CRYO") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"CRYO_TACTICAL", "Cryo Grenade", AbilitySlot::Tactical, 0.2f, 6.0f, 15.0f, 0.0f, 8.0f, 45.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"CRYO_ULTIMATE", "Absolute Zero Blizzard", AbilitySlot::Ultimate, 0.6f, 12.0f, 120.0f, 0.0f, 30.0f, 80.0f});
        } else if (code == "OP_PHANTOM") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"PHANTOM_TACTICAL", "Holographic Decoy", AbilitySlot::Tactical, 0.1f, 8.0f, 12.0f, 0.0f, 0.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"PHANTOM_ULTIMATE", "Quantum Backtrack", AbilitySlot::Ultimate, 0.2f, 0.5f, 90.0f, 0.0f, 0.0f, 0.0f});
        } else if (code == "OP_VECTOR") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"VECTOR_TACTICAL", "Supply Pod Drop", AbilitySlot::Tactical, 0.5f, 45.0f, 25.0f, 0.0f, 5.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"VECTOR_ULTIMATE", "Overdrive Surge", AbilitySlot::Ultimate, 0.3f, 12.0f, 105.0f, 0.0f, 20.0f, 0.0f});
        } else if (code == "OP_ZEPHYR") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"ZEPHYR_TACTICAL", "Grappling Cable", AbilitySlot::Tactical, 0.1f, 1.5f, 10.0f, 0.0f, 30.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"ZEPHYR_ULTIMATE", "Hypersonic Burst", AbilitySlot::Ultimate, 0.2f, 4.0f, 95.0f, 0.0f, 15.0f, 90.0f});
        } else if (code == "OP_CHRONO") {
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"CHRONO_TACTICAL", "Time Stasis Field", AbilitySlot::Tactical, 0.2f, 6.0f, 17.0f, 0.0f, 10.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"CHRONO_ULTIMATE", "Chronal Rewind", AbilitySlot::Ultimate, 0.8f, 1.0f, 135.0f, 0.0f, 20.0f, 0.0f});
        } else {
            // Default generic ability set
            tactical = std::make_unique<AbilityInstance>(AbilityDefinition{"GENERIC_TACTICAL", "Tactical Sprint", AbilitySlot::Tactical, 0.0f, 3.0f, 12.0f, 0.0f, 0.0f, 0.0f});
            ultimate = std::make_unique<AbilityInstance>(AbilityDefinition{"GENERIC_ULTIMATE", "Overload Pulse", AbilitySlot::Ultimate, 0.5f, 4.0f, 100.0f, 0.0f, 15.0f, 80.0f});
        }
    }
};

} // namespace Echofront::Abilities
