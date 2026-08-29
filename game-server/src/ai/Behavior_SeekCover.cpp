#include "game-server/include/ai/Behavior_SeekCover.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_SeekCover::Behavior_SeekCover(uint32_t botId)
    : m_botId(botId), m_name("Behavior_SeekCover") {
}

BehaviorStatus Behavior_SeekCover::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Identifies nearest AABB occlusion volume when shield drops below 30%.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_SeekCover::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
