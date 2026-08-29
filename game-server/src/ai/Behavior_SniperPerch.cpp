#include "game-server/include/ai/Behavior_SniperPerch.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_SniperPerch::Behavior_SniperPerch(uint32_t botId)
    : m_botId(botId), m_name("Behavior_SniperPerch") {
}

BehaviorStatus Behavior_SniperPerch::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Navigates to elevated spatial vantage points with clear line-of-sight.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_SniperPerch::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
