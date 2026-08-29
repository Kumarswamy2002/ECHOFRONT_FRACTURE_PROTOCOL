#pragma once
#include <string>
#include <vector>
#include <chrono>
#include <cmath>

namespace Echofront::Simulation {

enum class NodeState {
    Dormant = 0,
    Capturing = 1,
    Harmonized = 2,    // Controlled by a team, generating energy
    Overloaded = 3,    // High yield, unstable pulse hazards
    Destabilized = 4   // Near collapse, massive shockwaves, imminent extraction trigger
};

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    float DistanceTo(const Vector3& other) const {
        float dx = x - other.x;
        float dy = y - other.y;
        float dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

class FractureNode {
public:
    std::string nodeId;
    Vector3 position;
    NodeState state{NodeState::Dormant};
    
    int controllingTeam{-1}; // -1 for Neutral, 1 for Alpha, 2 for Omega
    float captureProgress{0.0f}; // 0.0f to 100.0f
    float stabilityPercentage{100.0f}; // Decreases under Overload
    float energyHarvestRate{10.0f}; // Energy per second
    float totalHarvestedEnergy{0.0f};

    float captureRadius{15.0f}; // Meters
    float hazardPulseTimer{0.0f};
    float pulseIntervalSeconds{8.0f};

    FractureNode(const std::string& id, Vector3 pos)
        : nodeId(id), position(pos) {}

    void Tick(float deltaTime, int team1Contestants, int team2Contestants) {
        // Handle Capture Mechanics
        if (team1Contestants > 0 && team2Contestants == 0) {
            ProgressCapture(1, team1Contestants, deltaTime);
        } else if (team2Contestants > 0 && team1Contestants == 0) {
            ProgressCapture(2, team2Contestants, deltaTime);
        }

        // Energy Generation & Destabilization
        if (state == NodeState::Harmonized || state == NodeState::Overloaded) {
            float multiplier = (state == NodeState::Overloaded) ? 2.5f : 1.0f;
            totalHarvestedEnergy += energyHarvestRate * multiplier * deltaTime;

            // Decay stability
            stabilityPercentage -= 0.5f * multiplier * deltaTime;
            if (stabilityPercentage <= 25.0f && state == NodeState::Harmonized) {
                state = NodeState::Overloaded;
            } else if (stabilityPercentage <= 0.0f) {
                state = NodeState::Destabilized;
            }

            // Hazard Pulses
            if (state == NodeState::Overloaded || state == NodeState::Destabilized) {
                hazardPulseTimer += deltaTime;
                if (hazardPulseTimer >= pulseIntervalSeconds) {
                    hazardPulseTimer = 0.0f;
                    TriggerEnergyShockwave();
                }
            }
        }
    }

    void OverclockNode() {
        if (state == NodeState::Harmonized) {
            state = NodeState::Overloaded;
            energyHarvestRate *= 1.5f;
        }
    }

private:
    void ProgressCapture(int team, int contestantCount, float deltaTime) {
        float captureSpeed = 15.0f * (1.0f + (contestantCount - 1) * 0.4f);

        if (controllingTeam == -1) {
            captureProgress += captureSpeed * deltaTime;
            state = NodeState::Capturing;
            if (captureProgress >= 100.0f) {
                captureProgress = 100.0f;
                controllingTeam = team;
                state = NodeState::Harmonized;
            }
        } else if (controllingTeam != team) {
            // Decapturing
            captureProgress -= captureSpeed * deltaTime;
            if (captureProgress <= 0.0f) {
                captureProgress = 0.0f;
                controllingTeam = -1;
                state = NodeState::Dormant;
            }
        }
    }

    void TriggerEnergyShockwave() {
        // Emits dynamic spatial shockwave damaging unshielded operatives in 25m
    }
};

} // namespace Echofront::Simulation
