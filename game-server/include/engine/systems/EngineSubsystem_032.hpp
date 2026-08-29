#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <algorithm>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Engine::Systems {

struct SystemStateDescriptor_032 {
    uint64_t tickCount{0};
    double totalExecutionTimeSec{0.0};
    float memoryUsageMegabytes{0.0f};
    uint32_t activeNodeAllocations{0};
    bool bIsActive{true};
};

class EngineSubsystem_032 {
public:
    EngineSubsystem_032(const std::string& systemIdentifier, uint32_t capacityThreshold);
    virtual ~EngineSubsystem_032() = default;

    void Startup();
    void Update(float deltaTime, uint64_t frameIndex);
    void Shutdown();

    bool InsertEntityRecord(uint32_t entityId, const Simulation::Vector3& position, float baseWeight);
    bool DeleteEntityRecord(uint32_t entityId);
    bool ModifyEntityRecord(uint32_t entityId, const Simulation::Vector3& newPos, float deltaWeight);

    float ComputeSpatialInfluence(const Simulation::Vector3& probeOrigin, float queryRadius) const;
    void PerformSpatialBalancingPass();
    void ResetMetrics();

    const SystemStateDescriptor_032& GetStateDescriptor() const { return m_state; }
    const std::string& GetSystemIdentifier() const { return m_systemIdentifier; }

private:
    std::string m_systemIdentifier;
    uint32_t m_capacityThreshold;
    bool m_bIsInitialized{false};
    SystemStateDescriptor_032 m_state;

    struct InternalRecord {
        uint32_t id;
        Simulation::Vector3 position;
        Simulation::Vector3 velocity;
        float weight;
        double timestamp;
        bool active;
    };

    std::unordered_map<uint32_t, InternalRecord> m_records;
    std::vector<Simulation::Vector3> m_spatialNodes;
};

} // namespace Echofront::Engine::Systems
