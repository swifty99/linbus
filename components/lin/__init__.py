from typing import Optional

import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.final_validate as fv
from esphome import pins, automation
from esphome.core import CORE
from esphome.components import uart
from esphome.const import (
    CONF_ID,
    CONF_TRIGGER_ID,
    CONF_DATA,
    CONF_NUMBER,
    CONF_BAUD_RATE,
    CONF_UART_ID,
    CONF_RX_PIN,
    CONF_TX_PIN,
    CONF_INVERTED,
    CONF_CS_PIN,
)
from esphome.components.uart import (
    CONF_STOP_BITS,
    CONF_DATA_BITS,
    CONF_PARITY,
    KEY_UART_DEVICES,
)
from esphome.core import CORE
from .entity_helpers import count_id_usage

DEPENDENCIES = ["uart"]
CODEOWNERS = ["@swifty99"]
#IS_PLATFORM_COMPONENT = True

CONF_LIN_ID = "lin_id"
CONF_LINBUS_ID = "linbus_id"
CONF_LIN_CHECKSUM = "lin_checksum"
CONF_FAULT_PIN = "fault_pin"
CONF_OBSERVER_MODE = "observer_mode"
CONF_ON_FRAME = "on_frame"
CONF_NUMBER_OF_CHILDREN = "number_of_children"


def validate_id(config):
    if CONF_LIN_ID in config:
        id_value = config[CONF_LIN_ID]
        if id_value > 0x40:
            raise cv.Invalid("Lin standard PIDs must be in the range of 0 ... 0x40")
    return config


def validate_raw_data(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, list):
        return cv.Schema([cv.hex_uint8_t])(value)
    raise cv.Invalid(
        "data must either be a string wrapped in quotes or a list of bytes"
    )

linbus_ns = cg.esphome_ns.namespace("linbus")
LinbusComponent = linbus_ns.class_("LinbusComponent", cg.Component)
LinbusTrigger = linbus_ns.class_(
    "LinbusTrigger",
    automation.Trigger.template(cg.std_vector.template(cg.uint8), cg.uint32),
    cg.Component,
)

# `LIN_CHECKSUM` is a enum class and not a namespace but it works.
LIN_CHECKSUM_dummy_ns = linbus_ns.namespace("LIN_CHECKSUM")

CONF_SUPPORTED_LIN_CHECKSUM = {
    "VERSION_1": LIN_CHECKSUM_dummy_ns.LIN_CHECKSUM_VERSION_1,
    "VERSION_2": LIN_CHECKSUM_dummy_ns.LIN_CHECKSUM_VERSION_2,
}

# [RP2040] Hardware serial of uart validation:
#   constexpr uint32_t valid_tx_uart_0 = __bitset({0, 12, 16, 28});
#   constexpr uint32_t valid_tx_uart_1 = __bitset({4, 8, 20, 24});
#   constexpr uint32_t valid_rx_uart_0 = __bitset({1, 13, 17, 29});
#   constexpr uint32_t valid_rx_uart_1 = __bitset({5, 9, 21, 25});
CONF_RP2040_HARDWARE_UART = {
    CONF_TX_PIN: {
        # Pin : Hardware UART number
        0: 0,
        12: 0,
        16: 0,
        28: 0,
        4: 1,
        8: 1,
        20: 1,
        24: 1,
    },
    CONF_RX_PIN: {
        # Pin : Hardware UART number
        1: 0,
        13: 0,
        17: 0,
        29: 0,
        5: 1,
        9: 1,
        21: 1,
        25: 1,
    }
}



def final_validate_device_schema(
    name: str,
    *,
    baud_rate: Optional[int] = None,
    require_tx: bool = False,
    require_rx: bool = False,
    stop_bits: Optional[int] = None,
    data_bits: Optional[int] = None,
    parity: str = None,
    require_hardware_uart: Optional[bool] = None,
):
    def validate_baud_rate(value):
        if value != baud_rate:
            raise cv.Invalid(
                f"Component {name} required baud rate {baud_rate} for the uart bus"
            )
        return value

    def validate_pin(opt, device):
        def validator(value):
            if opt in device:
                raise cv.Invalid(
                    f"The uart {opt} is used both by {name} and {device[opt]}, "
                    f"but can only be used by one. Please create a new uart bus for {name}."
                )
            device[opt] = name
            return value

        return validator

    def validate_stop_bits(value):
        if value != stop_bits:
            raise cv.Invalid(
                f"Component {name} required stop bits {stop_bits} for the uart bus"
            )
        return value

    def validate_data_bits(value):
        if value != data_bits:
            raise cv.Invalid(
                f"Component {name} required data bits {data_bits} for the uart bus"
            )
        return value

    def validate_parity(value):
        if value != parity:
            raise cv.Invalid(
                f"Component {name} required parity {parity} for the uart bus"
            )
        return value

    def validate_hardware_uart(opt, opt2=None, declaration_config=None):
        def validator(value):
            if (CORE.is_rp2040):
                if value[CONF_INVERTED]:
                    raise cv.Invalid(
                        f"Component {name} required Hardware UART. Inverted is not supported by Hardware UART.")
                if value[CONF_NUMBER] not in CONF_RP2040_HARDWARE_UART[opt]:
                    raise cv.Invalid(
                        f"Component {name} required Hardware UART. {opt} is not a Hardware UART pin.")
                if opt2 and declaration_config and CONF_RP2040_HARDWARE_UART[opt2][declaration_config[opt2][CONF_NUMBER]] != CONF_RP2040_HARDWARE_UART[opt][value[CONF_NUMBER]]:
                    raise cv.Invalid(
                        f"Component {name} required Hardware UART. {opt} and {opt2} are not a matching Hardware UART pin set.")

            return value
        return validator

    def validate_hub(hub_config):
        hub_schema = {}
        uart_id = hub_config[CONF_ID]
        devices = fv.full_config.get().data.setdefault(KEY_UART_DEVICES, {})
        device = devices.setdefault(uart_id, {})

        if require_tx:
            hub_schema[
                cv.Required(
                    CONF_TX_PIN,
                    msg=f"Component {name} requires this uart bus to declare a tx_pin",
                )
            ] = validate_pin(CONF_TX_PIN, device)
        if require_rx:
            hub_schema[
                cv.Required(
                    CONF_RX_PIN,
                    msg=f"Component {name} requires this uart bus to declare a rx_pin",
                )
            ] = validate_pin(CONF_RX_PIN, device)
        if baud_rate is not None:
            hub_schema[cv.Required(CONF_BAUD_RATE)] = validate_baud_rate
        if stop_bits is not None:
            hub_schema[cv.Required(CONF_STOP_BITS)] = validate_stop_bits
        if data_bits is not None:
            hub_schema[cv.Required(CONF_DATA_BITS)] = validate_data_bits
        if parity is not None:
            hub_schema[cv.Required(CONF_PARITY)] = validate_parity
        if require_hardware_uart is not None:
            fconf = fv.full_config.get()
            path = fconf.get_path_for_id(uart_id)[:-1]
            declaration_config = fconf.get_config_for_path(path)
            hub_schema[cv.Required(CONF_TX_PIN)] = validate_hardware_uart(
                CONF_TX_PIN)
            hub_schema[cv.Required(CONF_RX_PIN)] = validate_hardware_uart(
                CONF_RX_PIN, CONF_TX_PIN, declaration_config)
        return cv.Schema(hub_schema, extra=cv.ALLOW_EXTRA)(hub_config)

    return cv.Schema(
        {cv.Required(CONF_UART_ID)
                     : fv.id_declaration_match_schema(validate_hub)},
        extra=cv.ALLOW_EXTRA,
    )


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(LinbusComponent),
            cv.Optional(CONF_LIN_CHECKSUM, "VERSION_2"): cv.enum(CONF_SUPPORTED_LIN_CHECKSUM, upper=True),
            cv.Optional(CONF_CS_PIN): pins.gpio_output_pin_schema,
            cv.Optional(CONF_FAULT_PIN): pins.gpio_input_pin_schema,
            cv.Optional(CONF_OBSERVER_MODE): cv.boolean,        
            cv.Optional(CONF_ON_FRAME): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(LinbusTrigger),
                cv.Required(CONF_LIN_ID): cv.int_range(min=0, max=0x40),
            },
            validate_id,
        ),
        }
    )
    # Polling is for presenting data to sensors.
    # Reading and communication is done in a seperate thread/core.
    .extend(cv.polling_component_schema("500ms"))
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA),
    cv.only_on(["esp32", "rp2040"]),
) 

FINAL_VALIDATE_SCHEMA = cv.All(
    final_validate_device_schema(
        "linbus", baud_rate=9600, require_tx=True, require_rx=True, stop_bits=2, data_bits=8, parity="NONE", require_hardware_uart=True),
    count_id_usage(CONF_NUMBER_OF_CHILDREN, [
                   CONF_LINBUS_ID, CONF_ID], LinbusComponent),
)

async def setup_linbus_core_(var, config):
    if CORE.using_esp_idf:
        # Run interrupt on core 0. ESP Home runs on core 1.
        cg.add_build_flag("-DARDUINO_SERIAL_EVENT_TASK_RUNNING_CORE=0")
        # Default Stack Size is 2048. Not enough for my operation.
        cg.add_build_flag("-DARDUINO_SERIAL_EVENT_TASK_STACK_SIZE=4096")

    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NUMBER_OF_CHILDREN])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_lin_id([config[CONF_LIN_ID]]))

    if CONF_LIN_CHECKSUM in config:
        cg.add(var.set_lin_checksum(
            CONF_SUPPORTED_LIN_CHECKSUM[config[CONF_LIN_CHECKSUM]]))

    if CONF_CS_PIN in config:
        pin = await cg.gpio_pin_expression(config[CONF_CS_PIN])
        cg.add(var.set_cs_pin(pin))

    if CONF_FAULT_PIN in config:
        pin = await cg.gpio_pin_expression(config[CONF_FAULT_PIN])
        cg.add(var.set_fault_pin(pin))

    if CONF_OBSERVER_MODE in config:
        cg.add(var.set_observer_mode(config[CONF_OBSERVER_MODE]))

"""     for conf in config.get(CONF_ON_FRAME, []):
        lin_id = conf[CONF_LIN_ID]
        trigger = cg.new_Pvariable(
            conf[CONF_TRIGGER_ID], var, lin_id
        )
        await cg.register_component(trigger, conf)
        await automation.build_automation(
            trigger,
            [
                (cg.std_vector.template(cg.uint8), "x"),
                (cg.uint32, "lin_id"),
            ],
            conf,
        ) """



async def register_linbus(var, config):
    if not CORE.has_id(config[CONF_ID]):
        var = cg.new_Pvariable(config[CONF_ID], var)
    await setup_linbus_core_(var, config)

# Actions



# Actions
@automation.register_action(
    "linbus.send",
    linbus_ns.class_("LinbusSendAction", automation.Action),
    cv.maybe_simple_value(
        {
            cv.GenerateID(CONF_LINBUS_ID): cv.use_id(LinbusComponent),
            cv.Optional(CONF_LIN_ID): cv.int_range(min=0, max=0x1FFFFFFF),
            cv.Required(CONF_DATA): cv.templatable(validate_raw_data),
        },
        validate_id,
        key=CONF_DATA,
    ),
)
async def linbus_action_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_LINBUS_ID])

    if CONF_LIN_ID in config:
        lin_id = await cg.templatable(config[CONF_LIN_ID], args, cg.uint32)
        cg.add(var.set_lin_id(lin_id))

    data = config[CONF_DATA]
    if isinstance(data, bytes):
        data = [int(x) for x in data]
    if cg.is_template(data):
        templ = await cg.templatable(data, args, cg.std_vector.template(cg.uint8))
        cg.add(var.set_data_template(templ))
    else:
        cg.add(var.set_data_static(data))
    return var


