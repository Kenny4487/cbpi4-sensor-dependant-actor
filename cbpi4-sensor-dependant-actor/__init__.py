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
        Property.Select(
            label="SamplingTime",
            options=[2, 5],
            description="Time in seconds for power base interval (Default:5)",
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
            label="Behaviour on lower limit",
            options=["switch off", "switch on"],
            description="switch off: actor will be switched off once lower limit is met and switched on once upper limit is met, switch on: reversed behaviour",
        ),
    ]
)
class Dependant_GPIOActor(CBPiActor):


    # Custom property which can be configured by the user
    @action(
        "Set Power",
        parameters=[
            Property.Number(
                label="Power", configurable=True, description="Power Setting [0-100]"
            )
        ],
    )
    async def setpower(self, Power=100, **kwargs):
        self.power = int(Power)
        if self.power < 0:
            self.power = 0
        if self.power > 100:
            self.power = 100
        await self.set_power(self.power)



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
        self.sampleTime = int(self.props.get("SamplingTime", 5))
        self.sensor = self.props.get("Sensor")
        self.sensorLL = self.props.get("Sensor Lower Limit")
        self.sensorUL = self.props.get("Sensor Upper Limit")
        self.sensorLLTime = self.props.get("Sensor Lower Limit Time")
        self.sensorULTime = self.props.get("Sensor Upper Limit Time")
        self.behaviourOnLL = self.props.get("Behaviour on Lower Limit")
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False
        self.switch_on_timer = 0
        self.switch_off_timer = 0

    async def on(self, power=None):
        if power is not None:
            self.power = power
        else:
            self.power = 100
        #        await self.set_power(self.power)

        logger.info("ACTOR %s ON - GPIO %s " % (self.id, self.gpio))
        GPIO.output(self.gpio, self.get_GPIO_state(1))
        self.state = True

    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    def get_state(self):
        return self.state

    async def run(self):
        while self.running == True:
            sensor_value = self.get_sensor_value(self.sensor)
            if self.state == True:
                if self.sensorLL is not None and sensor_value < self.sensorLL:
                    self.switch_off_timer += 1
                    if self.sensorLLTime is None or self.sensorLLTime < 0 or self.switch_off_timer >= self.sensorLLTime:
                        if self.behaviourOnLL == "switch off":
                            await self.off()
                        else:
                            await self.on()
                        self.switch_off_timer = 0
                else:
                    self.switch_off_timer = 0
            else:
                if self.sensorUL is not None and sensor_value > self.sensorUL:
                    self.switch_on_timer += 1
                    if self.sensorULTime is None or self.sensorULTime < 0 or self.switch_on_timer >= self.sensorULTime:
                        await self.on()
                        self.switch_on_timer = 0
                else:
                    self.switch_on_timer = 0
            await asyncio.sleep(1)

    async def set_power(self, power):
        self.power = power
        await self.cbpi.actor.actor_update(self.id, power)
        pass

    def get_sensor_value(self, sensor):
        # This function should return the current value of the specified sensor
        sensor_value = float(self.get_sensor_value(self.sensor).get("value"))
        return sensor_value


def setup(cbpi):
    """
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    """

    cbpi.plugin.register("GPIOActor - sensor dependant", Dependant_GPIOActor)