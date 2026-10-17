"""Device interfaces and mock transport. No hardware backend is provided."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Reading:
    temperature_c: float
    humidity_percent: float
    co2_ppm: float


class Sensor(Protocol):
    def read(self) -> Reading: ...


class Ventilation(Protocol):
    def set_enabled(self, enabled: bool) -> None: ...


class MockSensor:
    def __init__(self, reading: Reading):
        self.reading = reading

    def read(self) -> Reading:
        return self.reading


class MockVentilation:
    def __init__(self):
        self.enabled = False
        self.commands: list[bool] = []

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.commands.append(enabled)
