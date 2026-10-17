# Agent instructions — SO-ARM101

Goal: SO-ARM101 robot trials and BMT: joint motion, telemetry, repeatability, and control behavior.

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

Next: Harden reusable RobotController, mock mode, joint bounds, Follower-only keyboard jog, pose capture, validated trajectory preview/replay, and safety tests. Leader telemetry/teleoperation is out of scope at user request.

13. Never hardcode USB/serial ports, device IDs, or machine-specific paths in executable code. Require explicit CLI arguments or external configuration/environment variables; missing values must fail before connection.
14. Do not use previously observed ports as defaults. Keep committed port examples empty; keep local port settings out of version control.
15. Keep trial step sizes and software envelopes in external configuration. These are not measured mechanical limits.

Project layout: Keep transport.py, controller.py, safety.py, and cli.py as the core. Reuse config/robot.toml and config/poses.json; do not add a new script/config file for each trial. Store runtime JSONL in logs/. Historical experiments are archived in docs/archive/robot-trials-2026-10-17.zip.
