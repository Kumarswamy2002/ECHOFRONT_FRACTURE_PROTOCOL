#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontGameMode.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontGameMode : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontGameMode();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontGameMode"};

protected:
    virtual void BeginPlay() override;
};
