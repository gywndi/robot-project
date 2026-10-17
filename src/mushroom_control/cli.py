"""Single-cycle mock CLI. Live configuration is explicitly rejected."""
import argparse
import json
from pathlib import Path
import tomllib
from .controller import CultivationController
from .transport import MockSensor, MockVentilation, Reading


def main() -> None:
    parser = argparse.ArgumentParser(description="모의 재배 환경 제어 (실물 연결 없음)")
    parser.add_argument("--config", type=Path, default=Path("config/cultivation.toml"))
    args = parser.parse_args()
    config = tomllib.loads(args.config.read_text(encoding="utf-8"))
    if config.get("mode") != "mock":
        parser.error("Only mock mode is implemented; hardware access is disabled")
    sensor = MockSensor(Reading(**config["mock_sensor"]))
    actuator = MockVentilation()
    thresholds = config["ventilation"]
    controller = CultivationController(sensor, actuator,
        thresholds["co2_on_ppm"], thresholds["co2_off_ppm"])
    reading, enabled = controller.step()
    print(json.dumps({"mode": "mock", "temperature_c": reading.temperature_c,
        "humidity_percent": reading.humidity_percent, "co2_ppm": reading.co2_ppm,
        "ventilation_enabled": enabled, "mock_commands": actuator.commands},
        ensure_ascii=False))


if __name__ == "__main__":
    main()
