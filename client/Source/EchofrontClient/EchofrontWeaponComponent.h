#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "EchofrontWeaponComponent.generated.h"

USTRUCT(BlueprintType)
struct FEchofrontWeaponStats
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    FString WeaponCode{"WEAPON_AR_VORTEX"};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float BaseDamage{24.0f};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float FireRateRPM{680.0f};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    int32 MaxMagazineCapacity{30};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float ReloadTimeSeconds{2.1f};

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float EffectiveRangeMeters{55.0f};
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class ECHOFRONTCLIENT_API UEchofrontWeaponComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UEchofrontWeaponComponent();

    UFUNCTION(BlueprintCallable, Category = "Weapon")
    void FireWeapon();

    UFUNCTION(BlueprintCallable, Category = "Weapon")
    void ReloadWeapon();

    UFUNCTION(Server, Reliable, WithValidation)
    void Server_NotifyWeaponFire(FVector_NetQuantize MuzzleLocation, FVector_NetQuantize FireDirection, uint32 ClientTick);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    FEchofrontWeaponStats WeaponStats;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Weapon")
    int32 CurrentAmmoInMag;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Weapon")
    int32 ReserveAmmo;

protected:
    virtual void BeginPlay() override;

private:
    double LastShotTime{0.0};
};
