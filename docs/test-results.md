> 과거 실행 명령과 분석 파일 경로는 당시 기록입니다. 이전 코드·설정·데이터는 `docs/archive/robot-trials-2026-10-17.zip`에 원래 경로로 보관되어 있습니다. 현재 실행 방법은 README와 learning.md를 따릅니다.

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

## 로봇 트라이얼 초기 코드 검증

이번 변경에서는 mock만 실행했습니다. 실물 연결·이동은 수행하지 않았습니다.

- 명령: `PYTHONPATH=src python3.11 -m unittest discover -s tests -v`
- 확인 항목: 시작/읽기 무명령, 승인 거부, 초과 이동 거부, 기존 토크 ON 거부, 대상 관절만 제어, 관찰 중단 시 정리, 6개 관절 지원, 범위 검사, 실물 transport의 빈 포트 거부. Python 3.11.17에서 9개 테스트 통과.
- 모의 명령: `PYTHONPATH=src python3.11 -m robot_trial.cli move --joint wrist_roll --delta-ticks -5`
- 측정 구분: 가상 시작 2470 ticks → 목표/가상 실제 2465 ticks. 물리적 관찰 없음.

## 실물 BMT 기록 양식

- 일시 / 작업자 / 코드·라이브러리 버전:
- 실행 명령 / 관절 / 설정 / 명시적 쓰기 동의:
- 팔 지지 / 전원 차단 수단 / 초기 토크:
- 시작 ticks / 목표 ticks / 실제 ticks / 소요 시간:
- 물리적 관찰 / 방향 / 오류 / 종료 후 상태:
- 반복 횟수 / 실패 횟수 / 다음 조치:

과거 실험의 정확한 명령은 완전히 복원되지 않았습니다. 과거 측정값을 현재 목표값으로 재사용하지 않습니다.

## 실물 USB / 집게 단일 구동 — 2026-10-17

사용자는 팔 지지, 집게에 물체 없음, 전원 차단 접근 가능을 확인하고 집게 +5 raw ticks 구동에 동의했습니다. 포트는 실행 시 USB 목록과 기존 역할 식별 기록을 대조해 CLI 인자로 전달했습니다. 코드 기본값으로 저장하지 않았습니다.

- 장치 확인 명령: `.venv/bin/python -m serial.tools.list_ports -v`
- 읽기 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.cli read --live --port "$FOLLOWER_PORT"`
- 실행 결과: shoulder_pan 1966, shoulder_lift 2052, elbow_flex 2040, wrist_flex 2041, wrist_roll 3167, gripper 2541 raw ticks.
- 구동 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.cli move --live --port "$FOLLOWER_PORT" --joint gripper --delta-ticks 5 --arm-supported`
- 실물 쓰기 승인: 사용자 확인 후 `MOVE gripper` 입력.
- 측정값: 시작 2541 → 목표 2546 → 실제 2541 ticks, 오차 -5 ticks.
- 종료: 대상 집게 토크 OFF 명령과 전체 토크를 변경하지 않는 연결 해제 경로로 정상 종료(exit 0). 종료 후 토크 레지스터 재측정은 수행하지 않았습니다.
- 물리적 관찰: 에이전트는 볼 수 없어 미확인. CLI 관찰 대기는 측정 및 토크 해제를 위해 종료했으며 사용자의 실제 움직임 관찰 보고는 아직 없습니다.
- 판정: USB 통신과 명령 실행은 성공했으나 위치 변화가 측정되지 않아 기계적 동작 성공으로 판단하지 않습니다. 더 큰 이동이나 반복 명령은 실행하지 않았습니다.
- 환경: 최초 샌드박스의 USB 접근 거부 후 명시적 권한 승인으로 실행했습니다.

## 실물 집게 가시성 시험 — 2026-10-17

- 동의: 사용자가 명시적으로 “집게 +20 ticks 1회 구동 승인” 응답. 팔 지지·빈 집게·전원 차단 접근 조건 확인 질문에 대한 승인입니다.
- 설정: `config/gripper-visibility-trial.toml` (집게에만 20 raw ticks 허용, 기계적 한계 미검증).
- 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.cli move --live --port "$FOLLOWER_PORT" --joint gripper --delta-ticks 20 --arm-supported --config config/gripper-visibility-trial.toml`
- 포트: 직전 USB 검색으로 확인한 Follower 경로를 실행 인자로 전달. 코드에 기본값으로 저장하지 않았습니다.
- 측정: 시작 2541 → 목표 2561 → 실제 2558 raw ticks. 측정된 변화 +17 ticks, 목표 오차 -3 ticks.
- 물리적 관찰: 에이전트는 볼 수 없으며 사용자의 육안 관찰 결과는 아직 미확인. 위치 레지스터 변화만 확인했습니다.
- 종료: 집게 토크 OFF 명령 후 `disconnect(disable_torque=False)`로 정상 종료(exit 0). 종료 후 토크 레지스터 재측정은 수행하지 않았습니다.
- 범위: 한 번만 구동했으며 왕복·추가 구동·다른 관절 제어는 하지 않았습니다.

## 6개 관절 단일 왕복 — 2026-10-17

사용자는 이전 집게 +20 ticks 구동에서 실제 움직임을 육안 확인했다고 보고했습니다. 이후 전체 팔을 움직임을 방해하지 않으면서 지지할 수 있음을 확인했으며, 손목을 제외하지 않도록 요청했습니다. 최종적으로 “6개 관절 +20 ticks 왕복 각 1회 승인” 응답을 받았습니다.

- 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.roundtrip --live --port "$FOLLOWER_PORT" --arm-supported --delta-ticks 20 --config config/all-joints-visibility-trial.toml`
- 프로필: 관절별 소프트웨어 offset/step 20 raw ticks, 매 방향 대기 0.833333초, 총 12회 대기 합계 10초. 통신·진단 시간은 별도이며 실제 전체 실행 시간을 정확히 계측하지 않았습니다.
- 사전 점검: 6개 관절 모두 Torque_Enable=0, Operating_Mode=0, 현재/목표 위치가 모터에 저장된 Min/Max_Position_Limit 이내. 이 설정값이 기계적 안전 한계임을 검증한 것은 아닙니다.
- 방식: 관절 하나씩 시작 위치 목표 설정 → 대상 토크 ON → +20 ticks 목표 → 대기/측정 → 시작 위치 복귀 목표 → 대기/측정 → 대상 토크 OFF 및 레지스터 0 확인.

| 관절 | 시작 | 전진 목표 | 전진 실제 | 실제 변화 | 복귀 실제 | 복귀 오차 |
|---|---:|---:|---:|---:|---:|---:|
| shoulder_pan | 1966 | 1986 | 1983 | +17 | 1971 | +5 |
| shoulder_lift | 2052 | 2072 | 2058 | +6 | 2054 | +2 |
| elbow_flex | 2040 | 2060 | 2044 | +4 | 2043 | +3 |
| wrist_flex | 2041 | 2061 | 2053 | +12 | 2045 | +4 |
| wrist_roll | 3167 | 3187 | 3182 | +15 | 3171 | +4 |
| gripper | 2558 | 2578 | 2575 | +17 | 2562 | +4 |

단위는 모두 raw ticks입니다. 각 복귀 목표는 해당 시작값입니다. 6개 관절에서 위치 레지스터 변화와 대상 토크 OFF를 확인하고 정상 종료(exit 0)했습니다. 완전한 시작 위치 복귀는 확인되지 않았으며 어깨 들기/팔꿈치의 전진 변화가 작았습니다. 물리적 방향·가시성·하중 상태에 대한 이번 왕복 시험의 사용자 관찰 보고는 아직 없습니다. 모든 관절의 정상 동작이나 기계적 안전성 검증으로 판단하지 않습니다. 무한 루프·추가 반복·이동량 자동 증가는 수행하지 않았습니다.

코드 검증 명령: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` (12개 통과). 실물 전에는 `PYTHONPATH=src .venv/bin/python -m robot_trial.roundtrip --delta-ticks 20 --config config/all-joints-visibility-trial.toml`로 6개 관절 mock 왕복을 확인했습니다.

## 저속·저토크 집게 범위 1단계 — 2026-10-17

### 읽기 전용 원본 기록

명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.diagnostics --port "$FOLLOWER_PORT" --output logs/baseline-before-range-trial.json`

6개 관절의 Torque_Limit는 raw 500, Goal_Velocity는 raw 0, Acceleration은 raw 254였습니다. Max_Torque_Limit는 집게 500, 다른 관절 1000이었습니다. 모터별 위치/토크/모드/범위/오프셋/전류/부하/전압/온도/데드존의 원본 raw 값은 로컬 JSON 파일에 보관했습니다. 설정 쓰기는 하지 않았습니다.

### 실물 시험

- 동의: 사용자가 Torque_Limit 250, Goal_Velocity 50, Acceleration 10, 집게 ±40 raw ticks/10 ticks 단계 시험 및 종료 후 복원을 명시적으로 승인했습니다.
- 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.range_trial --live --port "$FOLLOWER_PORT" --arm-supported --config config/gripper-range-stage1.toml --output logs/gripper-stage1-live.jsonl`
- 경로: 현재 위치 → +40 → 현재 위치 → -40 → 현재 위치. 10 ticks 단위, 각 목표 오차 8 ticks 이내 확인 후 다음 목표. 목표별 타임아웃 2초. 물리적 충돌 감지 기능은 아닙니다.
- 측정: 시작 2562, 양끝 목표 2602/2522, 양끝 샘플 실제 2596/2528, 최종 실제 2556 ticks (시작 대비 -6).
- 종료: 집게 Torque_Enable=0을 읽어 확인했고, Torque_Limit=500, Goal_Velocity=0, Acceleration=254 복원 후 읽기 검증 성공. exit 0.
- 사용자 물리적 관찰: “움직임이 작아서 판단 어려움”. 이상이 없었다고 확인된 것은 아닙니다.
- 판정: 설정 적용/복원 및 작은 구간 위치 응답만 확인. 기계적 범위 검증·정확한 원점 복귀·전체 관절 저토크 시험은 미완료입니다.
- 코드 검증: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` 16개 통과.

### 다음 단계 준비 (실물 미실행)

`config/gripper-range-stage2.toml`: 집게만 동일한 임시 설정(250/50/10), 시작 위치 ±120 ticks, 목표 간격 10 ticks의 1회 양방향 경로. mock만 검증했습니다. 실제 쓰기 동의 전에는 실행하지 않습니다. 물리적 끝점 찾기나 자동 캘리브레이션이 아닙니다.

## 저속·저토크 집게 범위 2단계 — 2026-10-17

- 동의: 사용자가 “집게 ±120 ticks 1회 시험 승인”으로 해당 임시 설정과 경로를 명시적으로 승인했습니다. 팔 지지·빈 집게·전원 차단 접근 조건을 유지하는 질문에 대한 응답입니다.
- 포트: 실행 직전 직렬 장치 목록으로 Follower 경로를 확인하고 실행 인자로 전달했습니다. 코드 기본값으로 저장하지 않았습니다.
- 명령: `PYTHONPATH=src .venv/bin/python -m robot_trial.range_trial --live --port "$FOLLOWER_PORT" --arm-supported --config config/gripper-range-stage2.toml --output logs/gripper-stage2-live.jsonl`
- 설정(raw): Torque_Limit 500→250, Goal_Velocity 0→50, Acceleration 254→10.
- 경로: 시작 → +120 → 시작 → -120 → 시작, 목표 간격 10 ticks, 유한 1회.
- 시작: 2558 ticks.
- +120 목표 2678 / 해당 샘플 실제 2670 ticks (시작 대비 +112).
- -120 목표 2438 / 해당 샘플 실제 2445 ticks (시작 대비 -113).
- 마지막 복귀 목표 2558 / 실제 2552 ticks (오차 -6).
- 단계별 샘플 범위: 2445~2670 ticks. 샘플 사이의 연속 최솟값/최댓값은 측정하지 않았습니다.
- 종료: Torque_Enable=0 읽기 확인 및 원래 SRAM 설정 500/0/254 복원·읽기 검증 성공, exit 0.
- 물리적 관찰: 사용자가 “움직임이 보였어”라고 보고하여 이번 시험의 움직임을 육안 확인했습니다. 양방향 각각의 관찰과 걸림·떨림·이상음 유무는 별도로 확인되지 않았습니다. 기계적 끝점이나 검증된 가동 범위로 기록하지 않습니다.
- 다른 관절 구동·추가 반복·추가 범위 확장은 하지 않았습니다.

## 후속 운영 방향 — 2026-10-17

사용자는 집게 ±120 ticks 시험에서 움직임을 육안 확인했고 걸림·떨림·이상음이 없었다고 보고했습니다. Leader는 엉뚱한 동작을 경험하여 사용하지 않기로 했습니다. Follower 단독 jog·자세 저장·시퀀스 재생 중심으로 개발 계획을 변경했으며, 이번 계획 수립 중 추가 모터 쓰기는 하지 않았습니다.

## 공개 동작 메타데이터 검사 — 2026-10-17

- 대상: `lerobot/svla_so101_pickplace`, `gpudad/so101_pick_cube`의 고정 revision 메타데이터 및 카드.
- 실행: `PYTHONPATH=src .venv/bin/python -m robot_trial.dataset_inspect data/reference/gpudad__so101_pick_cube`
- 결과: 30 FPS, 6개 관절 action. 우리 순서와 다른 source index 매핑 확인. 단위·action 의미 미확인, 실물 재생 불허 표시.
- 테스트: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q` — 19개 통과.
- 물리적 관찰: 해당 없음. 실물 연결·모터 쓰기 없음.

## 공개 에피소드 수치 분석·모의 미리보기 — 2026-10-17

- 대상: 고정 revision의 gpudad SO101 및 lerobot svla 에피소드 0. 301/303프레임 확인.
- 실행 명령과 분석 결과: `docs/analysis/README.md`, 각 하위 폴더 JSON/CSV.
- 모의 미리보기: svla의 변화 패턴을 별도 외부 설정 진폭으로 축소한 303프레임. 절대 모터 목표값 없음, 실물 재생 불허.
- 검사: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q` — 23개 통과.
- 물리적 관찰: 해당 없음. USB 연결과 모터 구동 없음. 안전한 실물 궤적이나 작업 성공으로 판단하지 않음.

## 구조 통합 검증 — 2026-10-17

- 변경: 통신/제어/CLI 및 독립 안전 검사로 통합. 시험별 코드·설정·예제·공개 데이터 산출물은 단일 보관 ZIP으로 이동 후 활성 경로에서 제거했습니다.
- 공통 설정: config/robot.toml. 초기 config/poses.json은 빈 자세 목록입니다.
- 테스트: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`.
- 관찰: mock jog → 자세 저장 → preview → 저장 위치 이동을 같은 세션에서 확인. 연결/읽기/생성 시 무명령, 연속 jog 시작 기준 고정, 오류 후 이동 거부 및 대상 토크 정리, mock/live 자세 구분을 검증했습니다.
- 물리적 관찰: 해당 없음. 이번 구조 변경 중 USB 연결·모터 쓰기는 하지 않았습니다.

통합 후 최종 검증: 위 unittest 명령으로 17개 테스트 통과. 실물 단일 관절 저장 자세 이동 정책도 mock transport로 검증했으며 실제 USB에 접근하지 않았습니다. 중복 parquet 캐시 약 144.8 MB는 추출한 에피소드가 보관 ZIP에 있음을 확인한 뒤 제거했고, 기존 실물 로그는 유지했습니다.
