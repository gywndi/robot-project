"""Input validity checks, separate from control policy."""
import math
from .transport import Reading


def validate_reading(reading: Reading) -> None:
    if not all(math.isfinite(v) for v in (
        reading.temperature_c, reading.humidity_percent, reading.co2_ppm
    )):
        raise ValueError("Sensor values must be finite")
    if not 0 <= reading.humidity_percent <= 100 or reading.co2_ppm < 0:
        raise ValueError("Invalid humidity or CO2 reading")


def validate_thresholds(on_ppm: float, off_ppm: float) -> None:
    if not all(math.isfinite(v) for v in (on_ppm, off_ppm)):
        raise ValueError("Thresholds must be finite")
    if not 0 <= off_ppm < on_ppm:
        raise ValueError("Require 0 <= co2_off_ppm < co2_on_ppm")
