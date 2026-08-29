#pragma once
#include <cstdint>
#include <vector>
#include <unordered_map>
#include <memory>
#include <bitset>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::ECS {

using EntityID = uint32_t;
constexpr size_t MAX_COMPONENTS = 64;
using ComponentMask = std::bitset<MAX_COMPONENTS>;

struct TransformComponent {
    Simulation::Vector3 position;
    Simulation::Vector3 velocity;
    float yaw{0.0f};
    float pitch{0.0f};
};

struct HealthComponent {
    float currentHealth{100.0f};
    float maxHealth{100.0f};
    float currentShield{100.0f};
    float maxShield{100.0f};
    bool bIsDowned{false};
    bool bIsDead{false};
};

struct WeaponStateComponent {
    int activeSlot{0};
    int currentAmmo{30};
    int reserveAmmo{180};
    bool bIsReloading{false};
    float reloadTimer{0.0f};
};

struct NetworkReplicationComponent {
    uint32_t lastSyncedTick{0};
    bool bIsDirty{true};
    uint8_t interestGroup{0};
};

class EntityManager {
public:
    EntityManager() : m_nextEntityId(1) {}

    EntityID CreateEntity() {
        EntityID id = m_nextEntityId++;
        m_entities.push_back(id);
        m_componentMasks[id] = ComponentMask();
        return id;
    }

    void DestroyEntity(EntityID id) {
        m_componentMasks.erase(id);
        m_transforms.erase(id);
        m_healths.erase(id);
        m_weapons.erase(id);
        m_replications.erase(id);
        auto it = std::find(m_entities.begin(), m_entities.end(), id);
        if (it != m_entities.end()) {
            m_entities.erase(it);
        }
    }

    TransformComponent& AddTransform(EntityID id) {
        m_componentMasks[id].set(0);
        return m_transforms[id];
    }

    HealthComponent& AddHealth(EntityID id) {
        m_componentMasks[id].set(1);
        return m_healths[id];
    }

    WeaponStateComponent& AddWeapon(EntityID id) {
        m_componentMasks[id].set(2);
        return m_weapons[id];
    }

    NetworkReplicationComponent& AddReplication(EntityID id) {
        m_componentMasks[id].set(3);
        return m_replications[id];
    }

    TransformComponent* GetTransform(EntityID id) {
        auto it = m_transforms.find(id);
        return it != m_transforms.end() ? &it->second : nullptr;
    }

    HealthComponent* GetHealth(EntityID id) {
        auto it = m_healths.find(id);
        return it != m_healths.end() ? &it->second : nullptr;
    }

    const std::vector<EntityID>& GetAllEntities() const { return m_entities; }

private:
    EntityID m_nextEntityId;
    std::vector<EntityID> m_entities;
    std::unordered_map<EntityID, ComponentMask> m_componentMasks;
    std::unordered_map<EntityID, TransformComponent> m_transforms;
    std::unordered_map<EntityID, HealthComponent> m_healths;
    std::unordered_map<EntityID, WeaponStateComponent> m_weapons;
    std::unordered_map<EntityID, NetworkReplicationComponent> m_replications;
};

} // namespace Echofront::ECS
