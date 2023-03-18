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

A Lin Master starts all communication by sending a PID header. A slave will answer the request.
