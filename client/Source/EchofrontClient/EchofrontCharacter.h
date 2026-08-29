#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "EchofrontCharacter.generated.h"

UENUM(BlueprintType)
enum class EEchofrontStance : uint8
{
    Standing UMETA(DisplayName = "Standing"),
    Crouching UMETA(DisplayName = "Crouching"),
    Sliding UMETA(DisplayName = "Sliding"),
    Mantling UMETA(DisplayName = "Mantling"),
    KnockedDown UMETA(DisplayName = "Knocked Down"),
    Eliminated UMETA(DisplayName = "Eliminated")
};

UCLASS(config=Game)
class ECHOFRONTCLIENT_API AEchofrontCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AEchofrontCharacter();

    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    // Movement & Stance
    UFUNCTION(BlueprintCallable, Category = "Movement")
    void StartSprint();

    UFUNCTION(BlueprintCallable, Category = "Movement")
    void StopSprint();

    UFUNCTION(BlueprintCallable, Category = "Movement")
    void StartSlide();

    UFUNCTION(BlueprintCallable, Category = "Abilities")
    void CastTacticalAbility();

    UFUNCTION(BlueprintCallable, Category = "Abilities")
    void CastUltimateAbility();

    UFUNCTION(Server, Reliable, WithValidation)
    void Server_SendClientInput(uint32 InputTick, FVector_NetQuantize MoveVelocity, FRotator AimRotation, uint16 ButtonMask);

    // Dynamic Combat Stats (Replicated)
    UPROPERTY(ReplicatedUsing = OnRep_Health, BlueprintReadOnly, Category = "Stats")
    float CurrentHealth;

    UPROPERTY(ReplicatedUsing = OnRep_Shield, BlueprintReadOnly, Category = "Stats")
    float CurrentShield;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    EEchofrontStance CurrentStance;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Operative")
    FString OperativeCodeId;

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnRep_Health();

    UFUNCTION()
    void OnRep_Shield();

private:
    float BaseWalkSpeed{600.0f};
    float SprintSpeedMultiplier{1.5f};
    bool bIsSprinting{false};
    bool bIsSliding{false};
};
