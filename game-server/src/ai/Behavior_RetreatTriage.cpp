#include "game-server/include/ai/Behavior_RetreatTriage.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_RetreatTriage::Behavior_RetreatTriage(uint32_t botId)
    : m_botId(botId), m_name("Behavior_RetreatTriage") {
}

BehaviorStatus Behavior_RetreatTriage::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Disengages from combat when outnumbered to rendezvous with medic bot.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_RetreatTriage::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
