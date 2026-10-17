"""CO2 hysteresis policy. Construction never sends actuator commands."""
from .safety import validate_reading, validate_thresholds
from .transport import Reading, Sensor, Ventilation


class CultivationController:
    def __init__(self, sensor: Sensor, ventilation: Ventilation,
                 on_ppm: float, off_ppm: float):
        validate_thresholds(on_ppm, off_ppm)
        self.sensor = sensor
        self.ventilation = ventilation
        self.on_ppm = on_ppm
        self.off_ppm = off_ppm
        self.enabled = False

    def step(self) -> tuple[Reading, bool]:
        reading = self.sensor.read()
        validate_reading(reading)
        desired = self.enabled
        if reading.co2_ppm >= self.on_ppm:
            desired = True
        elif reading.co2_ppm <= self.off_ppm:
            desired = False
        if desired != self.enabled:
            self.ventilation.set_enabled(desired)
            self.enabled = desired
        return reading, self.enabled
