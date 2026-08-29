#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontAbilityComponent.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontAbilityComponent : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontAbilityComponent();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontAbilityComponent"};

protected:
    virtual void BeginPlay() override;
};
