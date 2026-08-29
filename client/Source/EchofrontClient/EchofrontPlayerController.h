#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontPlayerController.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontPlayerController : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontPlayerController();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontPlayerController"};

protected:
    virtual void BeginPlay() override;
};
