#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <cmath>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Simulation::Subsystems {

struct SubsystemMetrics_20 {
    uint64_t totalTicksExecuted{0};
    double totalExecutionTimeMs{0.0};
    double averageTickDurationMs{0.0};
    uint32_t activeEntityCount{0};
    uint32_t memoryAllocatedBytes{0};
    float systemLoadFactor{0.0f};
    bool bIsHealthy{true};
};

class SimulationSubsystem_20 {
public:
    SimulationSubsystem_20(const std::string& subsystemTag, uint32_t maxCapacity);
    virtual ~SimulationSubsystem_20() = default;

    void Initialize();
    void Shutdown();
    void Tick(float deltaTime, uint64_t tickNumber);

    bool RegisterEntity(uint32_t entityId, const Simulation::Vector3& initialPos);
    bool UnregisterEntity(uint32_t entityId);
    bool UpdateEntityState(uint32_t entityId, const Simulation::Vector3& newPos, float energyDelta);

    const SubsystemMetrics_20& GetMetrics() const { return m_metrics; }
    const std::string& GetSubsystemTag() const { return m_subsystemTag; }

    // Complex algorithmic evaluation
    float CalculateSpatialResonance(const Simulation::Vector3& origin, float radius) const;
    void PerformSpatialPartitioningRebalance();
    void FlushStaleStateRecords(double maxAgeSeconds);

private:
    std::string m_subsystemTag;
    uint32_t m_maxCapacity;
    bool m_bIsInitialized{false};
    SubsystemMetrics_20 m_metrics;

    struct EntityRecord {
        uint32_t entityId;
        Simulation::Vector3 position;
        Simulation::Vector3 velocity;
        float energyLevel;
        double lastUpdatedTimestamp;
        bool bIsActive;
    };

    std::unordered_map<uint32_t, EntityRecord> m_entityTable;
    std::vector<Simulation::Vector3> m_spatialGridCells;
    double m_lastCleanupTimestamp{0.0};
};

} // namespace Echofront::Simulation::Subsystems
