#pragma once
#include <cstdint>
#include <vector>
#include <cstring>
#include <string>
#include "game-server/include/fracture/FractureNode.hpp"

namespace Echofront::Networking {

#pragma pack(push, 1)

enum class PacketType : uint8_t {
    ConnectRequest = 1,
    ConnectChallenge = 2,
    ConnectAck = 3,
    Disconnect = 4,
    ClientInput = 10,
    ServerWorldSnapshot = 11,
    DeltaSnapshot = 12,
    GameplayEvent = 20,
    Ping = 30,
    Pong = 31
};

struct PacketHeader {
    uint32_t protocolMagic{0x4543484F}; // 'ECHO'
    uint8_t packetType{0};
    uint32_t sequenceNumber{0};
    uint32_t ackSequence{0};
    uint32_t ackBitfield{0}; // Bitfield of previous 32 acknowledged packets
    uint64_t clientTimestampMs{0};
};

struct ClientInputPayload {
    uint32_t inputTickNumber{0};
    float moveForward{0.0f};  // -1.0 to 1.0
    float moveRight{0.0f};    // -1.0 to 1.0
    float aimPitch{0.0f};     // -89 to 89 deg
    float aimYaw{0.0f};       // 0 to 360 deg
    uint16_t buttonMask{0};   // Bit 0: Jump, Bit 1: Crouch, Bit 2: Sprint, Bit 3: PrimaryFire, Bit 4: Tactical, Bit 5: Ultimate
    uint8_t activeWeaponSlot{0};
};

struct OperativeSnapshot {
    uint16_t playerId{0};
    Simulation::Vector3 position;
    Simulation::Vector3 velocity;
    float aimPitch{0.0f};
    float aimYaw{0.0f};
    float health{100.0f};
    float shield{100.0f};
    uint8_t stanceState{0}; // Stand, Crouch, Slide, Knockdown, Dead
    uint8_t activeAbilityState{0};
};

struct NodeSnapshot {
    uint8_t nodeIndex{0};
    uint8_t state{0};
    int8_t controllingTeam{-1};
    uint8_t capturePercentage{0};
    uint8_t stabilityPercentage{100};
    uint32_t harvestedEnergy{0};
};

struct WorldSnapshotHeader {
    uint64_t serverTick{0};
    double serverTimestamp{0.0};
    uint16_t operativeCount{0};
    uint8_t nodeCount{0};
};

#pragma pack(pop)

class BitStreamWriter {
public:
    BitStreamWriter() { m_buffer.reserve(1024); }

    template<typename T>
    void Write(const T& value) {
        const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&value);
        m_buffer.insert(m_buffer.end(), ptr, ptr + sizeof(T));
    }

    void WriteBytes(const void* data, size_t size) {
        const uint8_t* ptr = reinterpret_cast<const uint8_t*>(data);
        m_buffer.insert(m_buffer.end(), ptr, ptr + size);
    }

    const uint8_t* GetData() const { return m_buffer.data(); }
    size_t GetSize() const { return m_buffer.size(); }
    const std::vector<uint8_t>& GetBuffer() const { return m_buffer; }

private:
    std::vector<uint8_t> m_buffer;
};

class BitStreamReader {
public:
    BitStreamReader(const uint8_t* data, size_t size)
        : m_data(data), m_size(size), m_offset(0) {}

    template<typename T>
    bool Read(T& outValue) {
        if (m_offset + sizeof(T) > m_size) return false;
        std::memcpy(&outValue, m_data + m_offset, sizeof(T));
        m_offset += sizeof(T);
        return true;
    }

    bool ReadBytes(void* outBuffer, size_t size) {
        if (m_offset + size > m_size) return false;
        std::memcpy(outBuffer, m_data + m_offset, size);
        m_offset += size;
        return true;
    }

    size_t RemainingBytes() const { return m_size - m_offset; }

private:
    const uint8_t* m_data;
    size_t m_size;
    size_t m_offset;
};

} // namespace Echofront::Networking
