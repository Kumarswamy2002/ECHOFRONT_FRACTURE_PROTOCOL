#include "EchofrontCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Net/UnrealNetwork.h"

AEchofrontCharacter::AEchofrontCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
    SetReplicateMovement(true);

    CurrentHealth = 100.0f;
    CurrentShield = 100.0f;
    CurrentStance = EEchofrontStance::Standing;
    OperativeCodeId = TEXT("OP_APEX");

    GetCharacterMovement()->MaxWalkSpeed = BaseWalkSpeed;
    GetCharacterMovement()->BrakingDecelerationWalking = 2000.0f;
    GetCharacterMovement()->AirControl = 0.35f;
    GetCharacterMovement()->NavAgentProps.bCanCrouch = true;
}

void AEchofrontCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void AEchofrontCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AEchofrontCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    // Custom axis and action bindings (Sprint, Slide, Abilities)
}

void AEchofrontCharacter::StartSprint()
{
    if (!bIsSprinting)
    {
        bIsSprinting = true;
        GetCharacterMovement()->MaxWalkSpeed = BaseWalkSpeed * SprintSpeedMultiplier;
    }
}

void AEchofrontCharacter::StopSprint()
{
    if (bIsSprinting)
    {
        bIsSprinting = false;
        GetCharacterMovement()->MaxWalkSpeed = BaseWalkSpeed;
    }
}

void AEchofrontCharacter::StartSlide()
{
    if (bIsSprinting && !bIsSliding)
    {
        bIsSliding = true;
        CurrentStance = EEchofrontStance::Sliding;
        GetCharacterMovement()->AddImpulse(GetActorForwardVector() * 1200.0f, true);
    }
}

void AEchofrontCharacter::CastTacticalAbility()
{
    // Client prediction: Trigger immediate local VFX/SFX
    // Dispatch authoritative Server RPC
}

void AEchofrontCharacter::CastUltimateAbility()
{
    // Client prediction: Trigger immediate local VFX/SFX
    // Dispatch authoritative Server RPC
}

bool AEchofrontCharacter::Server_SendClientInput_Validate(uint32 InputTick, FVector_NetQuantize MoveVelocity, FRotator AimRotation, uint16 ButtonMask)
{
    // Server input validation
    return true;
}

void AEchofrontCharacter::Server_SendClientInput_Implementation(uint32 InputTick, FVector_NetQuantize MoveVelocity, FRotator AimRotation, uint16 ButtonMask)
{
    // Reconcile and apply inputs on dedicated server
}

void AEchofrontCharacter::OnRep_Health()
{
    // Notify UI HUD of health update
}

void AEchofrontCharacter::OnRep_Shield()
{
    // Notify UI HUD of shield update
}

void AEchofrontCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(AEchofrontCharacter, CurrentHealth);
    DOREPLIFETIME(AEchofrontCharacter, CurrentShield);
    DOREPLIFETIME(AEchofrontCharacter, CurrentStance);
}
