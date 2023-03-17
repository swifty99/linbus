#pragma once

#include "esphome/components/sensor/sensor.h"
#include "esphome/components/truma_inetbox/LinBus.h"

namespace esphome {
namespace truma_inetbox {


class TrumaSensor : public Component, public sensor::Sensor, public Parented<LinBus> {
 public:
  void setup() override;
  void dump_config() override;


 protected:

 private:
};
}  // namespace truma_inetbox
}  // namespace esphome