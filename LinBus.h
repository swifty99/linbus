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

struct StatusFrameListener {
  std::function<void(const StatusFrameHeater *)> on_heater_change = nullptr;
  std::function<void(const StatusFrameTimer *)> on_timer_change = nullptr;
  std::function<void(const StatusFrameClock *)> on_clock_change = nullptr;
  std::function<void(const StatusFrameConfig *)> on_config_change = nullptr;
};


class TrumaiNetBoxApp : public LinBusProtocol {
 public:
  TrumaiNetBoxApp(u_int8_t expected_listener_count);

  void update() override;

  const std::array<u_int8_t, 4> lin_identifier() override;
  void lin_heartbeat() override;
  void lin_reset_device() override;

  bool get_status_heater_valid() { return this->status_heater_valid_; }
  const StatusFrameHeater *get_status_heater() { return &this->status_heater_; }
  void register_listener(const std::function<void(const StatusFrameHeater *)> &func);

  bool get_status_timer_valid() { return this->status_timer_valid_; }
  const StatusFrameTimer *get_status_timer() { return &this->status_timer_; }
  void register_listener(const std::function<void(const StatusFrameTimer *)> &func);

  bool get_status_clock_valid() { return this->status_clock_valid_; }
  const StatusFrameClock *get_status_clock() { return &this->status_clock_; }
  void register_listener(const std::function<void(const StatusFrameClock *)> &func);

  bool get_status_config_valid() { return this->status_config_valid_; }
  const StatusFrameConfig *get_status_config() { return &this->status_config_; }
  void register_listener(const std::function<void(const StatusFrameConfig *)> &func);

  bool truma_heater_can_update() { return this->status_heater_valid_; }
  StatusFrameHeaterResponse *update_heater_prepare();
  void update_heater_submit() { this->update_status_heater_unsubmitted_ = true; }

  bool truma_timer_can_update() { return this->status_timer_valid_; }
  StatusFrameTimerResponse *update_timer_prepare();
  void update_timer_submit() { this->update_status_timer_unsubmitted_ = true; }

  int64_t get_last_cp_plus_request() { return this->device_registered_; }

  // Automation
  void add_on_heater_message_callback(std::function<void(const StatusFrameHeater *)> callback) {
    this->state_heater_callback_.add(std::move(callback));
  }

protected:
  // Truma CP Plus needs init (reset). This device is not registered.
  uint32_t device_registered_ = 0;
  uint32_t init_requested_ = 0;
  uint32_t init_recieved_ = 0;
  u_int8_t message_counter = 1;

  // Truma heater conected to CP Plus.
  TRUMA_DEVICE heater_device_ = TRUMA_DEVICE::HEATER_COMBI4;
  TRUMA_DEVICE aircon_device_ = TRUMA_DEVICE::UNKNOWN;

  std::vector<StatusFrameListener> listeners_heater_;

  // https://esphome.io/api/classesphome_1_1_callback_manager_3_01void_07_ts_8_8_8_08_4.html
  CallbackManager<void(const StatusFrameHeater *)> state_heater_callback_{};

  bool status_heater_valid_ = false;
  // Value has changed notify listeners.
  bool status_heater_updated_ = false;
  StatusFrameHeater status_heater_;

}  // namespace linbus
}  // namespace esphome
