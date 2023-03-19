#include "helpers.h"
#include "esphome/core/helpers.h"
#include "LinBus.h"

namespace esphome {
namespace lin_bus {

u_int8_t addr_parity(const u_int8_t PID) {
  u_int8_t P0 = ((PID >> 0) + (PID >> 1) + (PID >> 2) + (PID >> 4)) & 1;
  u_int8_t P1 = ~((PID >> 1) + (PID >> 3) + (PID >> 4) + (PID >> 5)) & 1;
  return (P0 | (P1 << 1));
}

// sum = 0 LIN 1.X CRC, sum = PID LIN 2.X CRC Enhanced
u_int8_t data_checksum(const u_int8_t *message, u_int8_t length, uint16_t sum) {
  for (u_int8_t i = 0; i < length; i++) {
    sum += message[i];

    if (sum >= 256)
      sum -= 255;
  }
  return (~sum);
}




}  // namespace lin_bus
}  // namespace esphome