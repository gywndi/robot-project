import unittest
from mushroom_control.controller import CultivationController
from mushroom_control.transport import MockSensor, MockVentilation, Reading


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.sensor = MockSensor(Reading(22, 80, 1300))
        self.fan = MockVentilation()
        self.controller = CultivationController(self.sensor, self.fan, 1200, 900)

    def test_startup_has_no_commands(self):
        self.assertEqual(self.fan.commands, [])

    def test_hysteresis_and_no_repeated_commands(self):
        for co2 in (1300, 1100, 900, 1000):
            self.sensor.reading = Reading(22, 80, co2)
            self.controller.step()
        self.assertEqual(self.fan.commands, [True, False])

    def test_invalid_readings_never_send_commands(self):
        for reading in (Reading(22, 101, 1300), Reading(22, 80, -1),
                        Reading(float('nan'), 80, 1300)):
            self.sensor.reading = reading
            with self.assertRaises(ValueError):
                self.controller.step()
        self.assertEqual(self.fan.commands, [])

    def test_invalid_thresholds(self):
        for on, off in ((900, 1200), (900, 900), (1200, -1), (float('inf'), 900)):
            with self.assertRaises(ValueError):
                CultivationController(self.sensor, self.fan, on, off)


if __name__ == "__main__":
    unittest.main()
