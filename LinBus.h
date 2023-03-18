#pragma once

#include "esphome/core/component.h"

#include "esphome/core/automation.h"

#include <list>
#include <queue>
#include <set>
#include <vector>

#include "LinBusProtocol.h"

namespace esphome {
namespace linbus {

class LinBus;


#define LIN_SID_RESPONSE 0x40
#define LIN_SID_READ_STATE_BUFFER 0xBA
#define LIN_SID_FIll_STATE_BUFFFER 0xBB



enum class SensorValueType : uint8_t {
  RAW = 0x00,     // variable length
  U_WORD = 0x1,   // 1 Register unsigned
  U_DWORD = 0x2,  // 2 Registers unsigned
  S_WORD = 0x3,   // 1 Register signed
  S_DWORD = 0x4,  // 2 Registers signed
  BIT = 0x5,
  U_DWORD_R = 0x6,  // 2 Registers unsigned
  S_DWORD_R = 0x7,  // 2 Registers unsigned
  U_QWORD = 0x8,
  S_QWORD = 0x9,
  U_QWORD_R = 0xA,
  S_QWORD_R = 0xB,
  FP32 = 0xC,
  FP32_R = 0xD
};

/* struct StatusFrameListener {
  std::function<void(const StatusFrameHeater *)> on_heater_change = nullptr;
  std::function<void(const StatusFrameTimer *)> on_timer_change = nullptr;
  std::function<void(const StatusFrameClock *)> on_clock_change = nullptr;
  std::function<void(const StatusFrameConfig *)> on_config_change = nullptr;
};
 */

class LinBus : public LinBusProtocol {
 public:
  LinBus(u_int8_t expected_listener_count);

  void update() override;

  const std::array<u_int8_t, 4> lin_identifier() override;
  void lin_heartbeat() override;
  void lin_reset_device() override;


protected:
  uint8_t pid_{0x00};


}  // namespace linbus
}  // namespace esphome
