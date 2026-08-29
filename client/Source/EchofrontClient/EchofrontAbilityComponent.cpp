#include "EchofrontAbilityComponent.h"

AEchofrontAbilityComponent::AEchofrontAbilityComponent()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
}

void AEchofrontAbilityComponent::BeginPlay()
{
    Super::BeginPlay();
}

void AEchofrontAbilityComponent::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AEchofrontAbilityComponent::ExecuteSystemUpdate()
{
    // Executes client-side prediction for abilities, particle cues, and sound effects.
}
