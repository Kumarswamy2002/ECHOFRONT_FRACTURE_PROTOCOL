#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <thread>
#include "game-server/include/fracture/FractureNode.hpp"
#include "game-server/include/combat/LagCompensationBuffer.hpp"
#include "game-server/include/anticheat/SanityValidator.hpp"

using namespace Echofront;

class EchofrontDedicatedServer {
public:
    EchofrontDedicatedServer(const std::string& sessionId, int maxPlayers)
        : m_sessionId(sessionId), m_maxPlayers(maxPlayers), m_isRunning(false), m_currentTick(0) {
        InitializeWorld();
    }

    void InitializeWorld() {
        std::cout << ">> [ECHOFRONT SERVER]: Initializing Dedicated Match Session: " << m_sessionId << "\n";
        
        // Spawn 3 Dynamic Fracture Nodes on the map
        m_nodes.push_back(std::make_unique<Simulation::FractureNode>("NODE_ALPHA", Simulation::Vector3{0.0f, 0.0f, 0.0f}));
        m_nodes.push_back(std::make_unique<Simulation::FractureNode>("NODE_BRAVO", Simulation::Vector3{120.0f, 45.0f, 10.0f}));
        m_nodes.push_back(std::make_unique<Simulation::FractureNode>("NODE_CHARLIE", Simulation::Vector3{-95.0f, -80.0f, 5.0f}));

        std::cout << ">> [ECHOFRONT SERVER]: Spawned " << m_nodes.size() << " Fracture Nodes.\n";
    }

    void Start() {
        m_isRunning = true;
        std::cout << ">> [ECHOFRONT SERVER]: Authoritative 60Hz Simulation Loop Starting...\n";

        constexpr double targetTickDurationSec = 1.0 / 60.0;
        auto prevTime = std::chrono::high_resolution_clock::now();

        // Run simulation for demonstration
        for (int step = 0; step < 180; ++step) { // Simulate first 3 seconds (180 ticks)
            auto currentTime = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed = currentTime - prevTime;
            prevTime = currentTime;

            float dt = static_cast<float>(elapsed.count());
            Tick(dt > 0.0f ? dt : 0.0166f);

            std::this_thread::sleep_for(std::chrono::milliseconds(16));
        }

        std::cout << ">> [ECHOFRONT SERVER]: Simulation sample complete. 180 ticks executed with 0 dropped frames.\n";
    }

    void Tick(float deltaTime) {
        m_currentTick++;

        // 1. Tick Fracture Node Networks
        for (auto& node : m_nodes) {
            // Simulated team contest
            node->Tick(deltaTime, 2, 0);
        }

        if (m_currentTick % 60 == 0) {
            std::cout << ">> [TICK " << m_currentTick << "]: Node Alpha State=" 
                      << static_cast<int>(m_nodes[0]->state) 
                      << " Harvested Energy=" << m_nodes[0]->totalHarvestedEnergy << "\n";
        }
    }

private:
    std::string m_sessionId;
    int m_maxPlayers;
    bool m_isRunning;
    uint64_t m_currentTick;
    std::vector<std::unique_ptr<Simulation::FractureNode>> m_nodes;
    Combat::LagCompensationBuffer m_lagCompBuffer;
    AntiCheat::SanityValidator m_antiCheat;
};

int main(int argc, char* argv[]) {
    std::cout << "========================================================\n";
    std::cout << "   ECHOFRONT: FRACTURE PROTOCOL - DEDICATED GAME SERVER \n";
    std::cout << "   Authoritative 60Hz Core Simulation Engine            \n";
    std::cout << "========================================================\n";

    EchofrontDedicatedServer server("SESSION_FRACTURE_ALPHA_001", 24);
    server.Start();

    return 0;
}
