import os
import time
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

STEP, MAX_OFFSET = 10, 60
MOTORS = ("wrist_roll", "gripper")
COMMANDS = {"a": ("wrist_roll", -STEP), "d": ("wrist_roll", STEP),
            "o": ("gripper", -STEP), "p": ("gripper", STEP)}

if input("Live motor motion. Type MOVE to proceed: ").strip() != "MOVE":
    raise SystemExit("Cancelled")
port = os.getenv("FOLLOWER_PORT", "/dev/cu.usbmodem5B901011021")
bus = SO101Follower(SO101FollowerConfig(port=port, id="my_follower")).bus
enabled = []
try:
    bus.connect()
    start = {m: bus.read("Present_Position", m, normalize=False) for m in MOTORS}
    for m in MOTORS:
        if bus.read("Torque_Enable", m, normalize=False) != 0:
            raise RuntimeError(f"{m}: torque already on")
    for m in MOTORS:
        bus.write("Goal_Position", m, start[m], normalize=False)
        bus.enable_torque(m)
        enabled.append(m)
    print("a/d wrist, o/p gripper, s status, q quit (press Enter)")
    while True:
        try:
            key = input("command > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if key == "q":
            break
        if key == "s":
            for m in MOTORS:
                print(m, bus.read("Present_Position", m, normalize=False))
            continue
        if key not in COMMANDS:
            continue
        motor, delta = COMMANDS[key]
        current = bus.read("Present_Position", motor, normalize=False)
        target = current + delta
        if not start[motor] - MAX_OFFSET <= target <= start[motor] + MAX_OFFSET:
            print("Software range exceeded")
            continue
        bus.write("Goal_Position", motor, target, normalize=False)
        time.sleep(0.4)
        print(motor, "target:", target,
              "actual:", bus.read("Present_Position", motor, normalize=False))
finally:
    if bus.is_connected:
        for m in reversed(enabled):
            try:
                bus.disable_torque(m)
            except Exception as e:
                print("Failed to disable torque:", m, e)
        bus.disconnect()
