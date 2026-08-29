#include "game-server/include/ai/Behavior_CaptureNode.hpp"
#include <iostream>
#include <cmath>

namespace Echofront::AI {

Behavior_CaptureNode::Behavior_CaptureNode(uint32_t botId)
    : m_botId(botId), m_name("Behavior_CaptureNode") {
}

BehaviorStatus Behavior_CaptureNode::Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos) {
    m_timer += deltaTime;
    float dist = botPos.DistanceTo(targetPos);

    // Dynamic execution logic: Routes bot squad towards uncaptured or contested Fracture Nodes.
    if (dist < 5.0f) {
        m_status = BehaviorStatus::Success;
        return m_status;
    }

    m_status = BehaviorStatus::Running;
    return m_status;
}

void Behavior_CaptureNode::Reset() {
    m_timer = 0.0f;
    m_status = BehaviorStatus::Idle;
}

} // namespace Echofront::AI
