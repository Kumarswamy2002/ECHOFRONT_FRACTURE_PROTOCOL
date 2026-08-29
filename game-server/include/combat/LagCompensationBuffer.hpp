#pragma once
#include <string>
#include <vector>
#include <deque>
#include <unordered_map>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Combat {

struct BoundingBox {
    Simulation::Vector3 min;
    Simulation::Vector3 max;

    bool IntersectsRay(const Simulation::Vector3& rayOrigin, const Simulation::Vector3& rayDir, float maxDist) const {
        // Slab method ray-AABB intersection test
        float tmin = 0.0f;
        float tmax = maxDist;

        // X axis
        if (std::abs(rayDir.x) < 1e-6f) {
            if (rayOrigin.x < min.x || rayOrigin.x > max.x) return false;
        } else {
            float invD = 1.0f / rayDir.x;
            float t1 = (min.x - rayOrigin.x) * invD;
            float t2 = (max.x - rayOrigin.x) * invD;
            if (t1 > t2) std::swap(t1, t2);
            tmin = std::max(tmin, t1);
            tmax = std::min(tmax, t2);
            if (tmin > tmax) return false;
        }

        // Y axis
        if (std::abs(rayDir.y) < 1e-6f) {
            if (rayOrigin.y < min.y || rayOrigin.y > max.y) return false;
        } else {
            float invD = 1.0f / rayDir.y;
            float t1 = (min.y - rayOrigin.y) * invD;
            float t2 = (max.y - rayOrigin.y) * invD;
            if (t1 > t2) std::swap(t1, t2);
            tmin = std::max(tmin, t1);
            tmax = std::min(tmax, t2);
            if (tmin > tmax) return false;
        }

        // Z axis
        if (std::abs(rayDir.z) < 1e-6f) {
            if (rayOrigin.z < min.z || rayOrigin.z > max.z) return false;
        } else {
            float invD = 1.0f / rayDir.z;
            float t1 = (min.z - rayOrigin.z) * invD;
            float t2 = (max.z - rayOrigin.z) * invD;
            if (t1 > t2) std::swap(t1, t2);
            tmin = std::max(tmin, t1);
            tmax = std::min(tmax, t2);
            if (tmin > tmax) return false;
        }

        return true;
    }
};

struct PlayerHistoricalFrame {
    uint64_t tickNumber;
    double timestampSeconds;
    Simulation::Vector3 headPosition;
    Simulation::Vector3 torsoPosition;
    BoundingBox headBox;
    BoundingBox torsoBox;
    BoundingBox legsBox;
};

class LagCompensationBuffer {
public:
    static constexpr size_t MAX_HISTORY_FRAMES = 120; // 2 seconds of history at 60Hz

    void RecordPlayerFrame(const std::string& playerId, const PlayerHistoricalFrame& frame) {
        auto& history = m_playerHistory[playerId];
        history.push_back(frame);
        if (history.size() > MAX_HISTORY_FRAMES) {
            history.pop_front();
        }
    }

    bool VerifyHit(
        const std::string& targetPlayerId,
        double targetTimestamp,
        const Simulation::Vector3& rayOrigin,
        const Simulation::Vector3& rayDirection,
        float maxRange,
        bool& outIsHeadshot
    ) {
        outIsHeadshot = false;
        auto it = m_playerHistory.find(targetPlayerId);
        if (it == m_playerHistory.end() || it->second.empty()) {
            return false;
        }

        const auto& frames = it->second;
        // Interpolate or find closest historical snapshot matching targetTimestamp
        const PlayerHistoricalFrame* bestFrame = &frames.back();
        double minDiff = std::abs(bestFrame->timestampSeconds - targetTimestamp);

        for (const auto& frame : frames) {
            double diff = std::abs(frame.timestampSeconds - targetTimestamp);
            if (diff < minDiff) {
                minDiff = diff;
                bestFrame = &frame;
            }
        }

        // Check Head Hitbox First
        if (bestFrame->headBox.IntersectsRay(rayOrigin, rayDirection, maxRange)) {
            outIsHeadshot = true;
            return true;
        }

        // Check Torso & Limbs Hitboxes
        if (bestFrame->torsoBox.IntersectsRay(rayOrigin, rayDirection, maxRange) ||
            bestFrame->legsBox.IntersectsRay(rayOrigin, rayDirection, maxRange)) {
            return true;
        }

        return false;
    }

    void Clear() {
        m_playerHistory.clear();
    }

private:
    std::unordered_map<std::string, std::deque<PlayerHistoricalFrame>> m_playerHistory;
};

} // namespace Echofront::Combat
