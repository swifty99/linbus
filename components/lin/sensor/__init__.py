from esphome.components import sensor
import esphome.config_validation as cv
import esphome.codegen as cg

from esphome.const import (
    CONF_ID,
    STATE_CLASS_MEASUREMENT,
)
from .. import (
    linbus_ns, 
    CONF_LINBUS_ID, 
    LinBus,
    SENSOR_VALUE_TYPE,
    CONF_VALUE_TYPE,
)

DEPENDENCIES = ["linbus"]
CODEOWNERS = ["@swifty1101"]

LinSensor = linbus_ns.class_(
    "LinSensor", sensor.Sensor, cg.Component)


CONFIG_SCHEMA = sensor.sensor_schema(
    state_class=STATE_CLASS_MEASUREMENT
).extend(
    {
        cv.GenerateID(): cv.declare_id(LinSensor),
        cv.GenerateID(CONF_LINBUS_ID): cv.use_id(LinBus),
        cv.Optional(CONF_VALUE_TYPE, default="U_WORD"): cv.enum(SENSOR_VALUE_TYPE),
    }
).extend(cv.COMPONENT_SCHEMA)
#FINAL_VALIDATE_SCHEMA = set_default_based_on_type()


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    value_type = config[CONF_VALUE_TYPE]
    await cg.register_component(var, config)
    await sensor.register_sensor(var, config)
    await cg.register_parented(var, config[CONF_LINBUS_ID])


    await cg.register_component(var, config)
    await sensor.register_sensor(var, config)

    paren = await cg.get_variable(config[CONF_LINBUS_ID])
    cg.add(paren.add_sensor_item(var))
    #await add_linbus_base_properties(var, config, LinSensor)
