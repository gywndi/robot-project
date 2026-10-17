import os
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

port = os.getenv("FOLLOWER_PORT", "/dev/cu.usbmodem5B901011021")
bus = SO101Follower(SO101FollowerConfig(port=port, id="my_follower")).bus
try:
    bus.connect()
    for motor in bus.motors:
        print(f"{motor:16s}: {bus.read('Present_Position', motor, normalize=False)}")
finally:
    if bus.is_connected:
        bus.disconnect()
