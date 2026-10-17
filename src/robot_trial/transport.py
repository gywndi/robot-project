"""Device I/O only. Imports and constructors never connect or enable torque."""
import hashlib
import json
from typing import Protocol

JOINTS = ('shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper')


class Transport(Protocol):
    mode: str
    def connect(self) -> None: ...
    def close(self) -> None: ...
    def read(self, joint: str) -> int: ...
    def torque(self, joint: str) -> int: ...
    def write(self, joint: str, target: int) -> None: ...
    def enable(self, joint: str) -> None: ...
    def disable(self, joint: str) -> None: ...
    def fingerprint(self) -> str: ...


class MockTransport:
    mode = 'mock'

    def __init__(self, starts: dict[str, int]):
        if set(starts) != set(JOINTS) or any(type(v) is not int for v in starts.values()):
            raise ValueError('Explicit mock position required for every joint')
        self.positions = dict(starts)
        self.enabled = dict.fromkeys(JOINTS, 0)
        self.commands = []
        self.connected = False

    def connect(self):
        self.connected = True

    def close(self):
        self.connected = False

    def fingerprint(self):
        self._check()
        return 'mock-raw-ticks-v1'

    def _check(self):
        if not self.connected:
            raise RuntimeError('Transport is not connected')

    def read(self, joint):
        self._check()
        return self.positions[joint]

    def torque(self, joint):
        self._check()
        return self.enabled[joint]

    def write(self, joint, target):
        self._check()
        self.commands.append(('goal', joint, target))
        self.positions[joint] = target

    def enable(self, joint):
        self._check()
        self.commands.append(('enable', joint))
        self.enabled[joint] = 1

    def disable(self, joint):
        self._check()
        self.commands.append(('disable', joint))
        self.enabled[joint] = 0


class LeRobotTransport:
    mode = 'live'

    def __init__(self, port: str):
        if not isinstance(port, str) or not port.strip():
            raise ValueError('An explicit nonempty serial port is required')
        self.port = port.strip()
        self.bus = None

    def connect(self):
        from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
        self.bus = SO101Follower(SO101FollowerConfig(port=self.port)).bus
        # Avoid high-level connect/configure/calibrate and their hardware writes.
        self.bus.connect()

    def close(self):
        if self.bus is not None and self.bus.is_connected:
            self.bus.disconnect(disable_torque=False)

    def read(self, joint):
        return int(self.bus.read('Present_Position', joint, normalize=False))

    def torque(self, joint):
        return int(self.bus.read('Torque_Enable', joint, normalize=False))

    def write(self, joint, target):
        self.bus.write('Goal_Position', joint, target, normalize=False)

    def enable(self, joint):
        self.bus.enable_torque(joint)

    def disable(self, joint):
        self.bus.disable_torque(joint)

    def fingerprint(self):
        # Read-only signature; a match does NOT validate mechanical limits.
        registers = ('Operating_Mode', 'Homing_Offset', 'Min_Position_Limit', 'Max_Position_Limit')
        values = {joint: {name: int(self.bus.read(name, joint, normalize=False))
                          for name in registers} for joint in JOINTS}
        if any(value['Operating_Mode'] != 0 for value in values.values()):
            raise RuntimeError('Position mode required; configuration will not be changed automatically')
        return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()
