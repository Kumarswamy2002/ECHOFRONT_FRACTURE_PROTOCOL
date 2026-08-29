#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EchofrontSpatialAudio.generated.h"

UCLASS()
class ECHOFRONTCLIENT_API AEchofrontSpatialAudio : public AActor
{
    GENERATED_BODY()

public:
    AEchofrontSpatialAudio();

    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable, Category = "Echofront")
    void ExecuteSystemUpdate();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echofront")
    FString SystemTag{"EchofrontSpatialAudio"};

protected:
    virtual void BeginPlay() override;
};
