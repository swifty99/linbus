#include "LinBusSensor.h"
#include "esphome/core/log.h"
#include "esphome/components/linbus/helpers.h"

namespace esphome {
namespace linbus {

static const char *const TAG = "linbus.sensor";

void LinSensor::setup() {
  this->parent_->register_listener([this](const StatusFrameHeater *status_heater) {
      
      // todo, publish the appropriate LIN PID content
      this->publish_state(temp_code_to_decimal(status_heater->current_temp_room));

  });
}

void LinSensor::dump_config() {
  LOG_SENSOR("", "LIN Sensor", this);
  // todo post LIN Data config: Master/Slave, PID, Bitoffset, Datatype
  //ESP_LOGCONFIG(TAG, "  Type '%s'", enum_to_c_str(this->type_));
}
}  // namespace truma_inetbox
}  // namespace esphome