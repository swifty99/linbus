#pragma once

#include "esphome/components/sensor/sensor.h"
#include "esphome/components/linbus/LinBus.h"

namespace esphome {
namespace linbus {


class LinSensor : public Component, public sensor::Sensor, public Parented<LinBus> {
 public:
  void setup() override;
  void dump_config() override;


 protected:

 private:
};
}  // namespace linbus
}  // namespace esphome