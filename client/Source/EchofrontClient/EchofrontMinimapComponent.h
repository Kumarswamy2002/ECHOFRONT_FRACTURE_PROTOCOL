#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontMinimapComponent.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontMinimapComponent : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontMinimapComponent();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontMinimapComponent"};

protected:
    virtual void BeginPlay() override;
};
