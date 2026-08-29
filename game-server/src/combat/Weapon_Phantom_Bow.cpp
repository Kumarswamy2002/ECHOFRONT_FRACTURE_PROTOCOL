#include "game-server/include/combat/Weapon_Phantom_Bow.hpp"
#include <iostream>
#include <algorithm>

namespace Echofront::Combat {

Weapon_Phantom_Bow::Weapon_Phantom_Bow()
    : m_weaponName("Phantom_Bow"),
      m_weaponClass("Tactical Bow"),
      m_baseDamage(85.0f),
      m_fireRateRPM(75.0f),
      m_currentAmmo(1),
      m_maxMagazine(1),
      m_reserveAmmo(30),
      m_reloadTimeSeconds(0.9f),
      m_effectiveRange(80.0f),
      m_armorPenetration(0.75f) {
    m_shotIntervalSeconds = 60.0f / m_fireRateRPM;
}

bool Weapon_Phantom_Bow::Fire(const Simulation::Vector3& origin, const Simulation::Vector3& direction, double currentTimestamp) {
    if (m_bIsReloading || m_currentAmmo <= 0) return false;
    if (currentTimestamp - m_lastShotTimestamp < (m_shotIntervalSeconds * 0.95)) return false;

    m_currentAmmo--;
    m_lastShotTimestamp = currentTimestamp;
    std::cout << "[WEAPON FIRE] " << m_weaponName << " discharged bullet. Ammo remaining: " << m_currentAmmo << "\n";
    return true;
}

bool Weapon_Phantom_Bow::StartReload(double currentTimestamp) {
    if (m_bIsReloading || m_currentAmmo == m_maxMagazine || m_reserveAmmo <= 0) return false;
    m_bIsReloading = true;
    m_reloadStartTimestamp = currentTimestamp;
    std::cout << "[WEAPON RELOAD] " << m_weaponName << " reload initiated.\n";
    return true;
}

void Weapon_Phantom_Bow::Update(double currentTimestamp) {
    if (m_bIsReloading) {
        if (currentTimestamp - m_reloadStartTimestamp >= m_reloadTimeSeconds) {
            int needed = m_maxMagazine - m_currentAmmo;
            int transfer = std::min(needed, m_reserveAmmo);
            m_currentAmmo += transfer;
            m_reserveAmmo -= transfer;
            m_bIsReloading = false;
            std::cout << "[WEAPON READY] " << m_weaponName << " reload complete. Mag: " << m_currentAmmo << "\n";
        }
    }
}

} // namespace Echofront::Combat
