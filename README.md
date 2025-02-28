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
  - the sensor value must stay below the Lower Limit for the specified amount for triggering action
  - optional: if not specified, setting will be ignored and actor will switch as soon as limit is met
- Sensor Upper Limit Time
  - time in seconds
  - the sensor value must stay above the Upper Limit for the specified amount for triggering action
  - optional: if not specified, setting will be ignored and actor will switch as soon as limit is met
- Behaviour on lower limit:
  - switch off:
    - actor will be switched off when lower limit is met
    - switched on if upper limit is met
  - switch on:
    - actor will be switched on when lower limit is met
    - switched off if upper limit is met
- Mode on startup:
  - the actor has two modes:
    - manual:
      - no automatic switching, sensor value is ignored.
      - actor behaves exactly like basic GPIOActor
    - automatic:
      - actor is switched based on specified sensor limits
  - this parameter defines which mode is used after initialization of the actor
  - the mode can be changed in the UI with actor action
