# Verified LeRobot API

```python
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
robot = SO101Follower(SO101FollowerConfig(port="/dev/cu.usbmodem5B901011021", id="my_follower"))
bus = robot.bus
bus.connect()
position = bus.read("Present_Position", "wrist_roll", normalize=False)
torque = bus.read("Torque_Enable", "gripper", normalize=False)
# Writes only with explicit operator approval:
# bus.write("Goal_Position", "gripper", position + 20, normalize=False)
# bus.enable_torque("gripper")
# bus.disable_torque("gripper")
bus.disconnect()
```

`normalize=False` = raw motor ticks, NOT calibrated degrees.
`Goal_Position` is an absolute target.
`SO101Follower.connect(calibrate=False)` still runs `configure()`, which changes motor configuration.
Read-only experiments used `robot.bus.connect()` instead.
`SOFollowerRobot` import failed; `SO101Follower` worked.
