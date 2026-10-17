# Actual test results — 2026-10-17

First read:
| Motor | Raw position |
|---|---:|
| shoulder_pan | 1966 |
| shoulder_lift | 2052 |
| elbow_flex | 2040 |
| wrist_flex | 2041 |
| wrist_roll | 3140 |
| gripper | 2470 |

Gripper:
- 2470 → target 2475 → actual 2470 (no movement)
- Torque_Enable after enable: 1
- 2470 → target 2490 → actual 2488
- Actual physical gripper open/close direction not yet verified.

Wrist:
- 3140 → target 3160 → actual 3156
- Round-trip start 3156, forward target 3211 / actual 3207, return target 3156 / actual 3159
- Physical slight wrist movement visually confirmed.

Keyboard:
- Here-doc input() caused EOFError.
- Saved Python file accepted Enter-based commands; user observed incremental motion.

Leader:
- USB identified; no read/control test completed.

Unresolved: Unexpected ~360° wrist movement during earlier Leader/Follower teleoperation.
