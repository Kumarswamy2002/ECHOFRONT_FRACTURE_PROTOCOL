#include "game-server/include/ecs/EntityManager.hpp"
#include <iostream>

namespace Echofront::ECS {

void ProcessMovementSystem(EntityManager& manager, float deltaTime) {
    for (EntityID id : manager.GetAllEntities()) {
        auto* transform = manager.GetTransform(id);
        if (transform) {
            transform->position.x += transform->velocity.x * deltaTime;
            transform->position.y += transform->velocity.y * deltaTime;
            transform->position.z += transform->velocity.z * deltaTime;
        }
    }
}

void ProcessHealthRegenSystem(EntityManager& manager, float deltaTime) {
    for (EntityID id : manager.GetAllEntities()) {
        auto* health = manager.GetHealth(id);
        if (health && !health->bIsDead && health->currentShield < health->maxShield) {
            health->currentShield = std::min(health->maxShield, health->currentShield + 5.0f * deltaTime);
        }
    }
}

} // namespace Echofront::ECS
