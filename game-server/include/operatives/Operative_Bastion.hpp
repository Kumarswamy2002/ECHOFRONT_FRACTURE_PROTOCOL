#pragma once
#include <string>
#include <vector>
#include <memory>
#include "game-server/include/fracture/FractureNode.hpp"
#include "game-server/include/ecs/EntityManager.hpp"

namespace Echofront::Operatives {

class Operative_Bastion {
public:
    Operative_Bastion(uint32_t playerId, const std::string& callsign);
    virtual ~Operative_Bastion() = default;

    // Attributes
    const std::string& GetCallsign() const { return m_callsign; }
    const std::string& GetRole() const { return m_role; }
    float GetHealth() const { return m_health; }
    float GetShield() const { return m_shield; }
    float GetSpeed() const { return m_speed; }

    // Gameplay Cycle
    void Tick(float deltaTime, const Simulation::Vector3& currentPos);
    void TakeDamage(float amount, const std::string& sourcePlayerId);
    void Heal(float amount);
    void RestoreShield(float amount);

    // Ability Handlers
    bool TriggerPassive();
    bool TriggerTactical(const Simulation::Vector3& targetLocation);
    bool TriggerUltimate(const Simulation::Vector3& targetLocation);

    // Getters for Ability State
    float GetTacticalCooldownRemaining() const { return m_tacticalCooldown; }
    float GetUltimateCooldownRemaining() const { return m_ultimateCooldown; }
    bool IsTacticalReady() const { return m_tacticalCooldown <= 0.0f; }
    bool IsUltimateReady() const { return m_ultimateCooldown <= 0.0f; }

private:
    uint32_t m_playerId;
    std::string m_callsign;
    std::string m_role;
    float m_health;
    float m_maxHealth;
    float m_shield;
    float m_maxShield;
    float m_speed;

    // Cooldown state
    float m_tacticalCooldown{0.0f};
    float m_tacticalMaxCooldown{15.0f};
    float m_ultimateCooldown{0.0f};
    float m_ultimateMaxCooldown{110.0f};
    float m_activeAbilityDuration{0.0f};
    bool m_bIsAbilityActive{false};

    Simulation::Vector3 m_lastReportedPosition;
};

} // namespace Echofront::Operatives
