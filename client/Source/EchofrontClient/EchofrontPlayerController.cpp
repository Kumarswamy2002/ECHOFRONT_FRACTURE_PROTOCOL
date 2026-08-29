#include "EchofrontPlayerController.h"

AEchofrontPlayerController::AEchofrontPlayerController()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
}

void AEchofrontPlayerController::BeginPlay()
{
    Super::BeginPlay();
}

void AEchofrontPlayerController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AEchofrontPlayerController::ExecuteSystemUpdate()
{
    // Handles input bindings, client prediction, reconciliation RPCs, and UI routing.
}
