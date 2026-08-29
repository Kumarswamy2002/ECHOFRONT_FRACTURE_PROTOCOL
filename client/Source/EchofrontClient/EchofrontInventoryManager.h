#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontInventoryManager.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontInventoryManager : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontInventoryManager();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontInventoryManager"};

protected:
    virtual void BeginPlay() override;
};
