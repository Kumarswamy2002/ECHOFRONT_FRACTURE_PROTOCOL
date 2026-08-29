#pragma once
#include <vector>
#include <memory>
#include <cmath>
#include <algorithm>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Physics {

struct AABB {
    Simulation::Vector3 min;
    Simulation::Vector3 max;

    bool Intersects(const AABB& other) const {
        if (max.x < other.min.x || min.x > other.max.x) return false;
        if (max.y < other.min.y || min.y > other.max.y) return false;
        if (max.z < other.min.z || min.z > other.max.z) return false;
        return true;
    }

    bool ContainsPoint(const Simulation::Vector3& pt) const {
        return (pt.x >= min.x && pt.x <= max.x) &&
               (pt.y >= min.y && pt.y <= max.y) &&
               (pt.z >= min.z && pt.z <= max.z);
    }
};

struct SphereCollider {
    Simulation::Vector3 center;
    float radius;

    bool IntersectsAABB(const AABB& box) const {
        float closestX = std::max(box.min.x, std::min(center.x, box.max.x));
        float closestY = std::max(box.min.y, std::min(center.y, box.max.y));
        float closestZ = std::max(box.min.z, std::min(center.z, box.max.z));

        float dx = closestX - center.x;
        float dy = closestY - center.y;
        float dz = closestZ - center.z;

        return (dx * dx + dy * dy + dz * dz) <= (radius * radius);
    }
};

struct RaycastHit {
    bool bHasHit{false};
    Simulation::Vector3 point;
    Simulation::Vector3 normal;
    float distance{0.0f};
    int entityId{-1};
};

class PhysicsWorld {
public:
    PhysicsWorld(float gravity = -9.80665f)
        : m_gravity(gravity) {}

    void AddStaticCollider(const AABB& box) {
        m_staticColliders.push_back(box);
    }

    bool Raycast(const Simulation::Vector3& origin, const Simulation::Vector3& direction, float maxDist, RaycastHit& outHit) const {
        outHit.bHasHit = false;
        outHit.distance = maxDist;

        for (const auto& box : m_staticColliders) {
            float tmin = 0.0f;
            float tmax = maxDist;

            // Slab X
            float invDx = 1.0f / (std::abs(direction.x) > 1e-6f ? direction.x : 1e-6f);
            float t1 = (box.min.x - origin.x) * invDx;
            float t2 = (box.max.x - origin.x) * invDx;
            if (t1 > t2) std::swap(t1, t2);
            tmin = std::max(tmin, t1);
            tmax = std::min(tmax, t2);
            if (tmin > tmax) continue;

            // Slab Y
            float invDy = 1.0f / (std::abs(direction.y) > 1e-6f ? direction.y : 1e-6f);
            float t3 = (box.min.y - origin.y) * invDy;
            float t4 = (box.max.y - origin.y) * invDy;
            if (t3 > t4) std::swap(t3, t4);
            tmin = std::max(tmin, t3);
            tmax = std::min(tmax, t4);
            if (tmin > tmax) continue;

            // Slab Z
            float invDz = 1.0f / (std::abs(direction.z) > 1e-6f ? direction.z : 1e-6f);
            float t5 = (box.min.z - origin.z) * invDz;
            float t6 = (box.max.z - origin.z) * invDz;
            if (t5 > t6) std::swap(t5, t6);
            tmin = std::max(tmin, t5);
            tmax = std::min(tmax, t6);
            if (tmin > tmax) continue;

            if (tmin < outHit.distance && tmin >= 0.0f) {
                outHit.bHasHit = true;
                outHit.distance = tmin;
                outHit.point.x = origin.x + direction.x * tmin;
                outHit.point.y = origin.y + direction.y * tmin;
                outHit.point.z = origin.z + direction.z * tmin;
            }
        }
        return outHit.bHasHit;
    }

    void ResolveMovement(Simulation::Vector3& position, Simulation::Vector3& velocity, float deltaTime, const AABB& playerBounds) {
        // Integrate gravity
        velocity.y += m_gravity * deltaTime;

        // Proposed new position
        Simulation::Vector3 newPos = position;
        newPos.x += velocity.x * deltaTime;
        newPos.y += velocity.y * deltaTime;
        newPos.z += velocity.z * deltaTime;

        // Ground collision clamp
        if (newPos.y < 0.0f) {
            newPos.y = 0.0f;
            velocity.y = 0.0f;
        }

        position = newPos;
    }

private:
    float m_gravity;
    std::vector<AABB> m_staticColliders;
};

} // namespace Echofront::Physics
