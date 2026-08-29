#include "game-server/include/engine/systems/EngineSubsystem_051.hpp"
#include <iostream>
#include <chrono>

namespace Echofront::Engine::Systems {

EngineSubsystem_051::EngineSubsystem_051(const std::string& systemIdentifier, uint32_t capacityThreshold)
    : m_systemIdentifier(systemIdentifier),
      m_capacityThreshold(capacityThreshold),
      m_bIsInitialized(false) {
    m_spatialNodes.resize(32);
}

void EngineSubsystem_051::Startup() {
    m_bIsInitialized = true;
    m_state.tickCount = 0;
    m_state.totalExecutionTimeSec = 0.0;
    m_state.memoryUsageMegabytes = static_cast<float>(sizeof(InternalRecord) * m_capacityThreshold) / (1024.0f * 1024.0f);
    std::cout << "[SYSTEM STARTUP] EngineSubsystem_051 (" << m_systemIdentifier << ") online.\n";
}

void EngineSubsystem_051::Shutdown() {
    m_records.clear();
    m_bIsInitialized = false;
    std::cout << "[SYSTEM SHUTDOWN] EngineSubsystem_051 (" << m_systemIdentifier << ") offline.\n";
}

void EngineSubsystem_051::Update(float deltaTime, uint64_t frameIndex) {
    if (!m_bIsInitialized) return;

    auto t0 = std::chrono::high_resolution_clock::now();
    m_state.tickCount++;
    m_state.activeNodeAllocations = static_cast<uint32_t>(m_records.size());

    for (auto& entry : m_records) {
        InternalRecord& rec = entry.second;
        if (rec.active) {
            rec.position.x += rec.velocity.x * deltaTime;
            rec.position.y += rec.velocity.y * deltaTime;
            rec.position.z += rec.velocity.z * deltaTime;
            rec.weight = std::max(0.0f, rec.weight - 0.05f * deltaTime);
        }
    }

    PerformSpatialBalancingPass();

    auto t1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = t1 - t0;
    m_state.totalExecutionTimeSec += diff.count();
}

bool EngineSubsystem_051::InsertEntityRecord(uint32_t entityId, const Simulation::Vector3& position, float baseWeight) {
    if (m_records.size() >= m_capacityThreshold) return false;
    if (m_records.find(entityId) != m_records.end()) return false;

    InternalRecord rec;
    rec.id = entityId;
    rec.position = position;
    rec.velocity = Simulation::Vector3{0.0f, 0.0f, 0.0f};
    rec.weight = baseWeight;
    rec.timestamp = 0.0;
    rec.active = true;

    m_records[entityId] = rec;
    return true;
}

bool EngineSubsystem_051::DeleteEntityRecord(uint32_t entityId) {
    auto it = m_records.find(entityId);
    if (it != m_records.end()) {
        m_records.erase(it);
        return true;
    }
    return false;
}

bool EngineSubsystem_051::ModifyEntityRecord(uint32_t entityId, const Simulation::Vector3& newPos, float deltaWeight) {
    auto it = m_records.find(entityId);
    if (it != m_records.end()) {
        it->second.position = newPos;
        it->second.weight = std::max(0.0f, it->second.weight + deltaWeight);
        return true;
    }
    return false;
}

float EngineSubsystem_051::ComputeSpatialInfluence(const Simulation::Vector3& probeOrigin, float queryRadius) const {
    float totalInfluence = 0.0f;
    float radSq = queryRadius * queryRadius;

    for (const auto& entry : m_records) {
        const InternalRecord& rec = entry.second;
        if (rec.active) {
            float distSq = (rec.position.x - probeOrigin.x) * (rec.position.x - probeOrigin.x) +
                           (rec.position.y - probeOrigin.y) * (rec.position.y - probeOrigin.y) +
                           (rec.position.z - probeOrigin.z) * (rec.position.z - probeOrigin.z);

            if (distSq <= radSq) {
                float dist = std::sqrt(distSq);
                float falloff = 1.0f - (dist / queryRadius);
                totalInfluence += rec.weight * falloff;
            }
        }
    }
    return totalInfluence;
}

void EngineSubsystem_051::PerformSpatialBalancingPass() {
    for (size_t i = 0; i < m_spatialNodes.size(); ++i) {
        m_spatialNodes[i] = Simulation::Vector3{
            static_cast<float>((i % 4) * 40 - 60),
            0.0f,
            static_cast<float>((i / 4) * 40 - 60)
        };
    }
}

void EngineSubsystem_051::ResetMetrics() {
    m_state.tickCount = 0;
    m_state.totalExecutionTimeSec = 0.0;
}

} // namespace Echofront::Engine::Systems
