#include "EchofrontGameMode.h"

AEchofrontGameMode::AEchofrontGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
}

void AEchofrontGameMode::BeginPlay()
{
    Super::BeginPlay();
}

void AEchofrontGameMode::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AEchofrontGameMode::ExecuteSystemUpdate()
{
    // Authoritative match rules, extraction countdowns, team ticket balances, and respawn waves.
}
