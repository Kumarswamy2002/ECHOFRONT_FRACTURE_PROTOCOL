#include "game-server/include/operatives/Operative_Zephyr.hpp"
#include <iostream>
#include <algorithm>

namespace Echofront::Operatives {

Operative_Zephyr::Operative_Zephyr(uint32_t playerId, const std::string& callsign)
    : m_playerId(playerId),
      m_callsign(callsign),
      m_role("Scout"),
      m_health(95.0f),
      m_maxHealth(95.0f),
      m_shield(95.0f),
      m_maxShield(95.0f),
      m_speed(8.5.0f),
      m_lastReportedPosition{0.0f, 0.0f, 0.0f} {
    std::cout << "[OPERATIVE SPAWNED] " << m_callsign << " (" << m_role << ") for Player " << m_playerId << "\n";
}

void Operative_Zephyr::Tick(float deltaTime, const Simulation::Vector3& currentPos) {
    m_lastReportedPosition = currentPos;

    // Cooldown decay
    if (m_tacticalCooldown > 0.0f) {
        m_tacticalCooldown = std::max(0.0f, m_tacticalCooldown - deltaTime);
    }
    if (m_ultimateCooldown > 0.0f) {
        m_ultimateCooldown = std::max(0.0f, m_ultimateCooldown - deltaTime);
    }

    // Active duration decay
    if (m_bIsAbilityActive) {
        m_activeAbilityDuration -= deltaTime;
        if (m_activeAbilityDuration <= 0.0f) {
            m_bIsAbilityActive = false;
            m_activeAbilityDuration = 0.0f;
            std::cout << "[ABILITY EXPIRED] " << m_callsign << " ability effect ended.\n";
        }
    }

    // Passive Ability Tick
    TriggerPassive();
}

void Operative_Zephyr::TakeDamage(float amount, const std::string& sourcePlayerId) {
    if (m_shield > 0.0f) {
        float shieldDamage = std::min(m_shield, amount);
        m_shield -= shieldDamage;
        amount -= shieldDamage;
    }
    if (amount > 0.0f) {
        m_health = std::max(0.0f, m_health - amount);
    }
    std::cout << "[DAMAGE] " << m_callsign << " taken hit from " << sourcePlayerId 
              << " | HP: " << m_health << " SHIELD: " << m_shield << "\n";
}

void Operative_Zephyr::Heal(float amount) {
    m_health = std::min(m_maxHealth, m_health + amount);
}

void Operative_Zephyr::RestoreShield(float amount) {
    m_shield = std::min(m_maxShield, m_shield + amount);
}

bool Operative_Zephyr::TriggerPassive() {
    // Passive: Momentum Stacker
    return true;
}

bool Operative_Zephyr::TriggerTactical(const Simulation::Vector3& targetLocation) {
    if (m_tacticalCooldown > 0.0f) return false;
    m_tacticalCooldown = m_tacticalMaxCooldown;
    m_bIsAbilityActive = true;
    m_activeAbilityDuration = 6.0f;
    std::cout << "[TACTICAL CAST] " << m_callsign << " executed Grappling Cable at (" 
              << targetLocation.x << ", " << targetLocation.y << ", " << targetLocation.z << ")\n";
    return true;
}

bool Operative_Zephyr::TriggerUltimate(const Simulation::Vector3& targetLocation) {
    if (m_ultimateCooldown > 0.0f) return false;
    m_ultimateCooldown = m_ultimateMaxCooldown;
    m_bIsAbilityActive = true;
    m_activeAbilityDuration = 10.0f;
    std::cout << "[ULTIMATE CAST] " << m_callsign << " executed Hypersonic Burst at (" 
              << targetLocation.x << ", " << targetLocation.y << ", " << targetLocation.z << ")\n";
    return true;
}

} // namespace Echofront::Operatives
