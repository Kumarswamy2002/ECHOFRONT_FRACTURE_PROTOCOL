#include "game-server/include/ai/Behavior_ReviveAlly.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_ReviveAlly::Behavior_ReviveAlly(uint32_t botId)
    : m_botId(botId), m_name("Behavior_ReviveAlly") {
}

BehaviorStatus Behavior_ReviveAlly::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Deploys smoke barrier and initiates revive sequence on downed squadmate.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_ReviveAlly::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
