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

## 초기 구성 검증 — 2026-10-17

하드웨어를 연결하거나 조작하지 않은 소프트웨어 검증입니다.

| 명령 | 측정/확인 항목 | 물리적 관찰 |
|---|---|---|
| `PYTHONPATH=src python -m unittest discover -s tests -v` | 4개 테스트: 시작 시 무명령, 히스테리시스, 잘못된 센서 값/설정 거부 | 해당 없음, mock만 사용 |
| `PYTHONPATH=src python -m mushroom_control.cli --config config/cultivation.toml` | 예시 CO₂ 1300 ppm, 가상 환기 true, 가상 명령 `[true]` | 해당 없음, 실측 아님 |

### 이후 실물 시험 기록 양식

- 일시 / 작업자 / 코드 버전:
- 명시적 쓰기 동의 및 대상 장치:
- 실행 명령 / 설정 파일:
- 단위 / 초기 측정 / 목표 / 실제 측정:
- 물리적 관찰 / 오류 / 종료 후 장치 상태:
- 판정 / 다음 조치:

과거 시험의 정확한 실행 명령은 원본 기록에서 완전히 복원되지 않았습니다. 과거 값은 현재 목표값으로 재사용하지 않습니다.

초기 검증은 `python3` (Python 3.14.0)으로 실행했고, 이후 `/opt/homebrew/bin/python3.11`로 위 두 명령을 재실행하여 4개 테스트 통과 및 동일한 CLI 출력을 확인했습니다. 실제 재검증 명령은 `PYTHONPATH=src /opt/homebrew/bin/python3.11 -m unittest discover -s tests -v` 및 `PYTHONPATH=src /opt/homebrew/bin/python3.11 -m mushroom_control.cli --config config/cultivation.toml`입니다. LeRobot 설치나 import 검증은 이번 시험에 포함하지 않았습니다.
