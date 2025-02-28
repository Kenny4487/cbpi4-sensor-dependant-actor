# craftbeerpi4 Sensor Dependant Actor
A craftbeerpi4 plugin for switching a GPIOActor based on the value of a sensor.

I used it for switching a pump on/off based on the volume left in a container, to avoid the pump running dry or the container to overflow. 
But I'm sure there are numerous other possible applications.

## Installation
follow the documentation <https://openbrewing.gitbook.io/craftbeerpi4_support/readme/plugin-installation>

use `pipx runpip cbpi4 install https://github.com/Kenny4487/cbpi4-sensor-dependant-actor/archive/main.zip`


## Parameters
- GPIO:
  - GPIO pin of the actor
- Inverted:
  - No: actor active on high
  - Yes: actor active on low
- Sensor:
  - the sensor that is monitored
- Sensor Lower Limit:
  - low sensor value for triggering action
  - optional: if not specified, limit will be ignored for automatic switching
- Sensor Upper Limit
  - high sensor value for triggering action
  - optional: if not specified, limit will be ignored for automatic switching
- Sensor Lower Limit Time
  - time in seconds
  - the sensor value must stay below `Sensor Lower Limit` for at least `Sensor Lower Limit Time` to trigger switching action
  - optional: if not specified, parameter will be ignored and actor will switch as soon the sensor value drops below `Sensor Lower Limit`
- Sensor Upper Limit Time
  - time in seconds
  - the sensor value must stay below `Sensor Upper Limit` for at least `Sensor Upper Limit Time` to trigger switching action
  - optional: if not specified, parameter will be ignored and actor will switch as soon the sensor value rises above `Sensor Upper Limit`
- Behaviour on lower limit:
  - switch off:
    - actor will be switched off when lower limit is crossed
    - switched on when upper limit is crossed
  - switch on:
    - actor will be switched on when lower limit is crossed
    - switched off if upper limit is crossed
- Mode on startup:
  - the actor has two modes:
    - manual:
      - actor behaves exactly like basic GPIOActor
      - no automatic switching, sensor value is ignored    
    - automatic:
      - actor is switched based on specified sensor limits and times
  - this parameter defines which mode is used after startup of the actor
  - the mode can be changed in the UI with actor action
