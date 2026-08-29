#include "game-server/include/physics/PhysicsWorld.hpp"
#include <iostream>

namespace Echofront::Physics {

// Physics world explicit implementations
void InitializeDefaultArenaColliders(PhysicsWorld& world) {
    // Arena Boundaries
    world.AddStaticCollider(AABB{Simulation::Vector3{-80, 0, -82}, Simulation::Vector3{80, 15, -78}});
    world.AddStaticCollider(AABB{Simulation::Vector3{-80, 0, 78}, Simulation::Vector3{80, 15, 82}});
    world.AddStaticCollider(AABB{Simulation::Vector3{-82, 0, -80}, Simulation::Vector3{-78, 15, 80}});
    world.AddStaticCollider(AABB{Simulation::Vector3{78, 0, -80}, Simulation::Vector3{82, 15, 80}});

    // Tactical Center Pillars
    world.AddStaticCollider(AABB{Simulation::Vector3{-23, 0, -18}, Simulation::Vector3{-17, 8, -12}});
    world.AddStaticCollider(AABB{Simulation::Vector3{17, 0, -18}, Simulation::Vector3{23, 8, -12}});
    world.AddStaticCollider(AABB{Simulation::Vector3{-23, 0, 12}, Simulation::Vector3{-17, 8, 18}});
    world.AddStaticCollider(AABB{Simulation::Vector3{17, 0, 12}, Simulation::Vector3{23, 8, 18}});
}

} // namespace Echofront::Physics
