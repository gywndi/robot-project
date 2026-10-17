# Troubleshooting

**ImportError SOFollowerRobot:** use `SO101Follower` from `lerobot.robots.so_follower`.
**EOFError from input():** save code as `.py` and run `python file.py`; do not use stdin here-doc.
**Serial port unavailable:** check `/dev/cu.usb*`, close SenseCraft Robotics, reconnect one device at a time.
**Position changes but motion hard to see:** 10 ticks ≈ 0.88° for nominal 4096-tick/revolution servo; mark joint with tape.
**No movement:** check 12V supply, Torque_Enable, Goal_Position, Present_Position and physical obstruction. Do not force joint.
