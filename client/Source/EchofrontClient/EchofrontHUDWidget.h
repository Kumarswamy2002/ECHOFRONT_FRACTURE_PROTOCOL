#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "EchofrontHUDWidget.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API UEchofrontHUDWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void UpdateHealthDisplay(float CurrentHealth, float MaxHealth);

    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void UpdateShieldDisplay(float CurrentShield, float MaxShield);

    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void UpdateAmmoDisplay(int32 CurrentMag, int32 ReserveAmmo);

    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void UpdateNodeCaptureState(const FString& NodeName, float CapturePercentage, int32 ControllingTeam);

    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void TriggerHitmarker(bool bIsHeadshot, bool bIsElimination);

    UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
    void ShowDestabilizationWarning(float RemainingSeconds);
};
