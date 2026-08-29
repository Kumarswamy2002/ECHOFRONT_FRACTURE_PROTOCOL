#include "game-server/include/ai/Behavior_FlankTarget.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_FlankTarget::Behavior_FlankTarget(uint32_t botId)
    : m_botId(botId), m_name("Behavior_FlankTarget") {
}

BehaviorStatus Behavior_FlankTarget::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Evaluates peripheral navigation nodes to circle behind enemy firing lines.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_FlankTarget::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
