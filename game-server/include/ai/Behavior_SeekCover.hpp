#pragma once
#include <string>
#include <vector>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::AI {

enum class BehaviorStatus {
    Idle,
    Running,
    Success,
    Failure
};

class Behavior_SeekCover {
public:
    Behavior_SeekCover(uint32_t botId);
    virtual ~Behavior_SeekCover() = default;

    BehaviorStatus Execute(float deltaTime, const Simulation::Vector3& botPos, const Simulation::Vector3& targetPos);
    void Reset();

    const std::string& GetBehaviorName() const { return m_name; }
    float GetWeightScore() const { return m_weightScore; }

private:
    uint32_t m_botId;
    std::string m_name;
    float m_weightScore{1.0f};
    float m_timer{0.0f};
    BehaviorStatus m_status{BehaviorStatus::Idle};
};

} // namespace Echofront::AI
