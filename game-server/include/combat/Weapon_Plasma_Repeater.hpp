#pragma once
#include <string>
#include <vector>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Combat {

class Weapon_Plasma_Repeater {
public:
    Weapon_Plasma_Repeater();
    virtual ~Weapon_Plasma_Repeater() = default;

    bool Fire(const Simulation::Vector3& origin, const Simulation::Vector3& direction, double currentTimestamp);
    bool StartReload(double currentTimestamp);
    void Update(double currentTimestamp);

    int GetCurrentAmmo() const { return m_currentAmmo; }
    int GetReserveAmmo() const { return m_reserveAmmo; }
    int GetMaxMagazine() const { return m_maxMagazine; }
    bool IsReloading() const { return m_bIsReloading; }
    float GetBaseDamage() const { return m_baseDamage; }
    float GetEffectiveRange() const { return m_effectiveRange; }
    const std::string& GetWeaponName() const { return m_weaponName; }

private:
    std::string m_weaponName;
    std::string m_weaponClass;
    float m_baseDamage;
    float m_fireRateRPM;
    int m_currentAmmo;
    int m_maxMagazine;
    int m_reserveAmmo;
    float m_reloadTimeSeconds;
    float m_effectiveRange;
    float m_armorPenetration;

    double m_lastShotTimestamp{0.0};
    double m_reloadStartTimestamp{0.0};
    bool m_bIsReloading{false};
    float m_shotIntervalSeconds{0.0f};
};

} // namespace Echofront::Combat
