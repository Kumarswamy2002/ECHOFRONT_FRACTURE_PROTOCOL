#include "EchofrontMinimapComponent.h"

AEchofrontMinimapComponent::AEchofrontMinimapComponent()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
}

void AEchofrontMinimapComponent::BeginPlay()
{
    Super::BeginPlay();
}

void AEchofrontMinimapComponent::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AEchofrontMinimapComponent::ExecuteSystemUpdate()
{
    // Renders radar pings, contested Fracture Node icons, and ally position triangles.
}
