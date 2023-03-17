#pragma once

#include "LinBus.h"

namespace esphome {
namespace truma_inetbox {
// First byte is service identifier and to be ignored.
const std::array<u_int8_t, 11> truma_message_header = {0x00, 0x00, 0x1F, 0x00, 0x1E, 0x00,
                                                       0x00, 0x22, 0xFF, 0xFF, 0xFF};

u_int8_t addr_parity(const u_int8_t pid);
u_int8_t data_checksum(const u_int8_t *message, u_int8_t length, uint16_t sum);


}  // namespace truma_inetbox
}  // namespace esphome