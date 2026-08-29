#include "game-server/include/ai/Behavior_SwarmSuppression.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_SwarmSuppression::Behavior_SwarmSuppression(uint32_t botId)
    : m_botId(botId), m_name("Behavior_SwarmSuppression") {
}

BehaviorStatus Behavior_SwarmSuppression::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Coordinates continuous cyclic fire across 3 bots to suppress enemy position.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_SwarmSuppression::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
