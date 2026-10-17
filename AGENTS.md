# Agent instructions — SO-ARM101

Goal: Independent SO-ARM101 Follower control, eventually camera-guided shiitake harvesting.

Environment: Apple Silicon macOS, Python 3.11, LeRobot, FeetechMotorsBus.
Verified import:
`from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig`

Motor names: shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper.

Rules:
1. Never move motors automatically on startup or in unit tests.
2. Hardware writes require explicit user consent.
3. Keep transport, safety, controller, UI, vision separate.
4. Use mock mode and configuration-driven ports/limits.
5. Keep raw servo ticks distinct from calibrated degrees.
6. Do not automatically calibrate, rewrite motor IDs, or flash firmware.
7. Enable torque only for the target joint during early tests.
8. Shoulder/elbow are gravity-loaded; torque-off can cause a fall.
9. Ctrl+C is NOT a hardware emergency stop. Keep physical power cutoff accessible.
10. Earlier unexpected ~360-degree wrist rotation remains unresolved.
11. Never claim mechanical limits are validated without measurements.
12. Document each test's command, measured values, and physical observation.

Next: Build reusable RobotController, mock mode, joint bounds, read-only Leader telemetry, keyboard CLI, and safety tests.
