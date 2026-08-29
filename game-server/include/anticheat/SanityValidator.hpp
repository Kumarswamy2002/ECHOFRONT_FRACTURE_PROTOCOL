#pragma once
#include <string>
#include <unordered_map>
#include <iostream>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::AntiCheat {

struct PlayerMoveRecord {
    Simulation::Vector3 lastPosition;
    double lastTimestamp{0.0};
    int consecutiveViolations{0};
};

struct WeaponFireRecord {
    double lastShotTimestamp{0.0};
    int rapidFireViolations{0};
};

class SanityValidator {
public:
    static constexpr float MAX_ALLOWED_SPEED_MPS = 16.5f; // Max velocity including grapples/slides (m/s)
    static constexpr float MAX_TELEPORT_DISTANCE_M = 25.0f;

    bool ValidateMovement(
        const std::string& playerId,
        const Simulation::Vector3& newPos,
        double currentTimestamp,
        bool isTeleportAbilityActive = false
    ) {
        auto& record = m_moveRecords[playerId];
        if (record.lastTimestamp == 0.0) {
            record.lastPosition = newPos;
            record.lastTimestamp = currentTimestamp;
            return true;
        }

        double dt = currentTimestamp - record.lastTimestamp;
        if (dt <= 0.0001) return true;

        float distance = record.lastPosition.DistanceTo(newPos);
        float calculatedSpeed = distance / static_cast<float>(dt);

        if (distance > MAX_TELEPORT_DISTANCE_M && !isTeleportAbilityActive) {
            record.consecutiveViolations++;
            std::cout << "[ANTI-CHEAT ALERT] Impossible Teleport Detected for Player: " << playerId 
                      << " Distance: " << distance << "m\n";
            return false;
        }

        if (calculatedSpeed > MAX_ALLOWED_SPEED_MPS && !isTeleportAbilityActive) {
            record.consecutiveViolations++;
            std::cout << "[ANTI-CHEAT ALERT] Speedhack detected for Player: " << playerId 
                      << " Speed: " << calculatedSpeed << " m/s\n";
            return false;
        }

        // Accept valid move
        record.lastPosition = newPos;
        record.lastTimestamp = currentTimestamp;
        if (record.consecutiveViolations > 0) {
            record.consecutiveViolations--;
        }
        return true;
    }

    bool ValidateFireRate(
        const std::string& playerId,
        double currentTimestamp,
        float weaponMinShotIntervalSeconds
    ) {
        auto& record = m_fireRecords[playerId];
        if (record.lastShotTimestamp == 0.0) {
            record.lastShotTimestamp = currentTimestamp;
            return true;
        }

        double dt = currentTimestamp - record.lastShotTimestamp;
        // Allow small network jitter margin of 10%
        if (dt < (weaponMinShotIntervalSeconds * 0.90f)) {
            record.rapidFireViolations++;
            std::cout << "[ANTI-CHEAT ALERT] Rapid-fire violation for Player: " << playerId << "\n";
            return false;
        }

        record.lastShotTimestamp = currentTimestamp;
        return true;
    }

private:
    std::unordered_map<std::string, PlayerMoveRecord> m_moveRecords;
    std::unordered_map<std::string, WeaponFireRecord> m_fireRecords;
};

} // namespace Echofront::AntiCheat
