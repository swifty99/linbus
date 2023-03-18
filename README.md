# Esphome LINbus
A component to use LIN Devices with ESPHome.
Many, if not most car actuators in a vehicle are controlled by LIN a local interconect network. Bus Interface and components are cheap, it is easy to fin any kind of fans, flaps, motors, sensors, pumps, selenoids and whatsoever. 
Communicaten shall be as near as Esphome CANbus as possible. https://esphome.io/components/canbus.html

# State

Work in Progress.

based on https://github.com/Fabian-Schmidt/esphome-truma_inetbox which contains an excellent LIN Slave code for ESPHome.
I try to convert it do a generic LIN component. Any help welcome

Specification of LIN: https://lin-cia.org/fileadmin/microsites/lin-cia.org/resources/documents/LIN-Spec_Pac2_1.pdf


# Usage
A LIN node can only be master or slave. This configured in the linbus component, default is master.

A Lin Slave does not trigger communication. It listens for configurated PIDs and answers with the data provided. This is async and not yet implemented.  A listener for each PID shall be implemented

## Master

A Lin Master starts all communication by sending a PID header. A slave will answer the request.

Whatever data the master shall receive it needs to be configuredn in the on_frame trigger/automation

```# Example configuration entry
linbus:
  uart_id: lin_uart_bus
    on_frame:
    - lin_pid: 0x33
      then:
      - lambda: |-
          std::string b(x.begin(), x.end());
          ESP_LOGD("lin pid 0x33", "%s", &b[0] );
 ```


Trigger data request.
the master will never receive data unless triggered.
While the receive on frame is set, the master initiates communication_

### linbus.request_pid Action

To receive a PID as master the PID will be put on the bus, the slave will follow to answer:

```
on_...:
  - linbus.request_pid: 0x33
```

If the Slave ist alive it will answer and the `on_frame` automation (if configured) will be triggered.

### linbus.send_pid Action

Only the master can send a PID. It will send the data an the header with:

```
on_...:
  - linbus.send:
      data: [ 0x10, 0x20, 0x30 ]   #maximum 8 bytes
      lin_pid: 0x33
```



