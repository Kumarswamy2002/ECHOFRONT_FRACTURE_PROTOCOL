#include "game-server/include/simulation/subsystems/SimulationSubsystem_09.hpp"
#include <iostream>
#include <algorithm>
#include <chrono>

namespace Echofront::Simulation::Subsystems {

SimulationSubsystem_09::SimulationSubsystem_09(const std::string& subsystemTag, uint32_t maxCapacity)
    : m_subsystemTag(subsystemTag), m_maxCapacity(maxCapacity) {
    m_spatialGridCells.resize(64);
}

void SimulationSubsystem_09::Initialize() {
    m_bIsInitialized = true;
    m_metrics.totalTicksExecuted = 0;
    m_metrics.memoryAllocatedBytes = sizeof(EntityRecord) * m_maxCapacity;
    std::cout << "[SUBSYSTEM INITIALIZED] " << m_subsystemTag << " initialized with capacity: " << m_maxCapacity << "\n";
}

void SimulationSubsystem_09::Shutdown() {
    m_entityTable.clear();
    m_bIsInitialized = false;
    std::cout << "[SUBSYSTEM SHUTDOWN] " << m_subsystemTag << " gracefully terminated.\n";
}

void SimulationSubsystem_09::Tick(float deltaTime, uint64_t tickNumber) {
    if (!m_bIsInitialized) return;

    auto startTime = std::chrono::high_resolution_clock::now();
    m_metrics.totalTicksExecuted++;
    m_metrics.activeEntityCount = static_cast<uint32_t>(m_entityTable.size());

    // Update entity states
    for (auto& pair : m_entityTable) {
        EntityRecord& rec = pair.second;
        if (rec.bIsActive) {
            rec.position.x += rec.velocity.x * deltaTime;
            rec.position.y += rec.velocity.y * deltaTime;
            rec.position.z += rec.velocity.z * deltaTime;

            // Decay energy level
            rec.energyLevel = std::max(0.0f, rec.energyLevel - 0.1f * deltaTime);
        }
    }

    PerformSpatialPartitioningRebalance();

    auto endTime = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = endTime - startTime;
    m_metrics.totalExecutionTimeMs += elapsed.count();
    m_metrics.averageTickDurationMs = m_metrics.totalExecutionTimeMs / m_metrics.totalTicksExecuted;
    m_metrics.systemLoadFactor = static_cast<float>(m_metrics.activeEntityCount) / static_cast<float>(m_maxCapacity);
}

bool SimulationSubsystem_09::RegisterEntity(uint32_t entityId, const Simulation::Vector3& initialPos) {
    if (m_entityTable.size() >= m_maxCapacity) return false;
    if (m_entityTable.find(entityId) != m_entityTable.end()) return false;

    EntityRecord rec;
    rec.entityId = entityId;
    rec.position = initialPos;
    rec.velocity = Simulation::Vector3{0.0f, 0.0f, 0.0f};
    rec.energyLevel = 100.0f;
    rec.lastUpdatedTimestamp = 0.0;
    rec.bIsActive = true;

    m_entityTable[entityId] = rec;
    return true;
}

bool SimulationSubsystem_09::UnregisterEntity(uint32_t entityId) {
    auto it = m_entityTable.find(entityId);
    if (it != m_entityTable.end()) {
        m_entityTable.erase(it);
        return true;
    }
    return false;
}

bool SimulationSubsystem_09::UpdateEntityState(uint32_t entityId, const Simulation::Vector3& newPos, float energyDelta) {
    auto it = m_entityTable.find(entityId);
    if (it != m_entityTable.end()) {
        it->second.position = newPos;
        it->second.energyLevel = std::max(0.0f, std::min(100.0f, it->second.energyLevel + energyDelta));
        return true;
    }
    return false;
}

float SimulationSubsystem_09::CalculateSpatialResonance(const Simulation::Vector3& origin, float radius) const {
    float totalResonance = 0.0f;
    float radiusSq = radius * radius;

    for (const auto& pair : m_entityTable) {
        const EntityRecord& rec = pair.second;
        if (rec.bIsActive) {
            float distSq = (rec.position.x - origin.x) * (rec.position.x - origin.x) +
                           (rec.position.y - origin.y) * (rec.position.y - origin.y) +
                           (rec.position.z - origin.z) * (rec.position.z - origin.z);

            if (distSq <= radiusSq) {
                float dist = std::sqrt(distSq);
                float factor = 1.0f - (dist / radius);
                totalResonance += rec.energyLevel * factor;
            }
        }
    }
    return totalResonance;
}

void SimulationSubsystem_09::PerformSpatialPartitioningRebalance() {
    for (size_t i = 0; i < m_spatialGridCells.size(); ++i) {
        m_spatialGridCells[i] = Simulation::Vector3{
            static_cast<float>((i % 8) * 20 - 80),
            0.0f,
            static_cast<float>((i / 8) * 20 - 80)
        };
    }
}

void SimulationSubsystem_09::FlushStaleStateRecords(double maxAgeSeconds) {
    // Flush stale cached metrics
}

} // namespace Echofront::Simulation::Subsystems
