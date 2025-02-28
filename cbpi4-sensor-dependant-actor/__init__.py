import asyncio
import logging
from unittest.mock import MagicMock, patch

from cbpi.api import *

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    logger.warning("Failed to load RPi.GPIO. Using Mock instead")
    MockRPi = MagicMock()
    modules = {"RPi": MockRPi, "RPi.GPIO": MockRPi.GPIO}
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO

mode = GPIO.getmode()
if mode == None:
    GPIO.setmode(GPIO.BCM)


@parameters(
    [
        Property.Select(
            label="GPIO",
            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        ),
        Property.Select(
            label="Inverted",
            options=["Yes", "No"],
            description="No: Active on high; Yes: Active on low",
        ),
        Property.Sensor(
            label="Sensor",
            description="Select the sensor to monitor",
        ),
        Property.Number(
            label="Sensor Lower Limit",
            configurable=True,
            description="Lower limit value for the sensor",
        ),
        Property.Number(
            label="Sensor Upper Limit",
            configurable=True,
            description="Upper limit value for the sensor",
        ),
        Property.Number(
            label="Sensor Lower Limit Time",
            configurable=True,
            description="Time in seconds the sensor value must stay below the lower limit",
        ),
        Property.Number(
            label="Sensor Upper Limit Time",
            configurable=True,
            description="Time in seconds the sensor value must stay above the upper limit",
        ),
        Property.Select(
            label="Behaviour on Lower Limit",
            options=["switch off", "switch on"],
            description="switch off: actor will be switched off once lower limit is met and switched on once upper limit is met, switch on: reversed behaviour",
        ),
        Property.Select(
            label="Mode on startup",
            options=["manual", "automatic"],
            description="manual: actor will not start automatically, automatic: actor will start automatically based on sensor values",
        ),
    ]
)
class Dependant_GPIOActor(CBPiActor):

    @action("Select Mode", parameters=[Property.Select(label="autoMode", options=["manual", "automatic"], description="turn auto mode on or off")])
    async def selectMode(self, autoMode, **kwargs):        
        if autoMode is not None:
            self.autoMode = autoMode
        else:
             logger.info("####################### setting autoMode failed!  ########################### ")

    def get_GPIO_state(self, state):
        # ON
        if state == 1:
            return 1 if self.inverted == False else 0
        # OFF
        if state == 0:
            return 0 if self.inverted == False else 1
                

    async def on_start(self):
        self.power = None
        self.gpio = self.props.GPIO
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        self.sensor = self.props.get("Sensor")
        self.sensorLL = self.props.get("Sensor Lower Limit")
        self.sensorUL = self.props.get("Sensor Upper Limit")
        self.LLTime = self.props.get("Sensor Lower Limit Time")
        self.ULTime = self.props.get("Sensor Upper Limit Time")
        self.behaviourOnLL = self.props.get("Behaviour on Lower Limit")
        self.autoMode = self.props.get("Mode on startup", "manual")
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    async def on(self, power=None):
        if power is not None:
            self.power = power
        else:
            self.power = 100
        await self.set_power(self.power)    

        GPIO.output(self.gpio, self.get_GPIO_state(1))
        self.state = True   


    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    def get_state(self):
        return self.state

    async def run(self):
        below_LL_start_time = None
        above_UL_start_time = None

        while self.running:
            logger.info("####################### automode:  ########################### ")
            logger.info(self.autoMode)

            if self.autoMode == "automatic":
                sensor = self.props.get("Sensor")

                try:
                    if sensor is not None and sensor != "":
                        sensor_value = float(self.cbpi.sensor.get_sensor_value(sensor).get('value'))
                    else:
                        sensor_value = None
                except:
                    sensor_value = None

                logger.info("####################### sensor value %f ########################### %r" % (sensor_value, self.state))
                logger.info("####################### behaviour: %s ###########################" % (self.behaviourOnLL))  # debug

                current_time = asyncio.get_event_loop().time()

                if sensor_value is not None:
                    if self.sensorLL is not None and sensor_value < float(self.sensorLL):
                        if below_LL_start_time is None:
                            below_LL_start_time = current_time
                        if self.LLTime is not None and float(self.LLTime) >= 0:
                            if current_time - below_LL_start_time >= float(self.LLTime):
                                if self.behaviourOnLL == "switch off" and self.state:
                                    await self.off()
                                elif self.behaviourOnLL == "switch on" and not self.state:
                                    await self.on()
                        else:
                            if self.behaviourOnLL == "switch off" and self.state:
                                await self.off()
                            elif self.behaviourOnLL == "switch on" and not self.state:
                                await self.on()
                    else:
                        below_LL_start_time = None

                    if self.sensorUL is not None and sensor_value > float(self.sensorUL):
                        if above_UL_start_time is None:
                            above_UL_start_time = current_time
                        if self.ULTime is not None and float(self.ULTime) >= 0:
                            if current_time - above_UL_start_time >= float(self.ULTime):
                                if self.behaviourOnLL == "switch off" and not self.state:
                                    await self.on()
                                elif self.behaviourOnLL == "switch on" and self.state:
                                    await self.off()
                        else:
                            if self.behaviourOnLL == "switch off" and not self.state:
                                await self.on()
                            elif self.behaviourOnLL == "switch on" and self.state:
                                await self.off()
                    else:
                        above_UL_start_time = None
                else:
                    below_LL_start_time = None
                    above_UL_start_time = None
            elif self.autoMode == "manual":
                pass

            await asyncio.sleep(1)

    async def set_power(self, power):
        self.power = power
        await self.cbpi.actor.actor_update(self.id, power)
        pass


        
def setup(cbpi):
    cbpi.plugin.register("GPIOActor - sensor dependant", Dependant_GPIOActor)
    pass
