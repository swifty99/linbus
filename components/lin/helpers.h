#pragma once

#include "LinBus.h"

namespace esphome {
namespace linbus {

u_int8_t addr_parity(const u_int8_t pid);
u_int8_t data_checksum(const u_int8_t *message, u_int8_t length, uint16_t sum);


}  // namespace linbus
}  // namespace esphome