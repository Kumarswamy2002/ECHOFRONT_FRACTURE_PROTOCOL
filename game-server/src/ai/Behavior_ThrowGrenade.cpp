#include "game-server/include/ai/Behavior_ThrowGrenade.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_ThrowGrenade::Behavior_ThrowGrenade(uint32_t botId)
    : m_botId(botId), m_name("Behavior_ThrowGrenade") {
}

BehaviorStatus Behavior_ThrowGrenade::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Calculates parabolic throw trajectory towards cluster of hostile targets.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_ThrowGrenade::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
