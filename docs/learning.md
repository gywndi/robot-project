# 천천히 익히는 로봇 제어

새 기능보다 현재 동작을 이해하는 데 집중합니다. 정해진 기간 안에 끝낼 필요는 없습니다. 아래 내용을 나눠 익히고, 실물 시험에서는 한 관절씩 관찰합니다.

## 1. 읽기와 mock/실물 연결 이해

```bash
PYTHONPATH=src python -m robot_trial.cli read
```

결과의 `mode`, `positions`, `torque`를 확인합니다. 위치 단위는 raw ticks입니다. mock 수치는 `config/robot.toml`의 가상 시작값이며 현재 실물 자세가 아닙니다.

실물은 같은 명령에 `--live`와 직접 식별한 `--port`를 추가합니다. 포트 우선순위는 CLI → FOLLOWER_PORT 환경변수 → robot.toml의 빈 port 항목입니다. 기본 장치 경로는 없습니다. Leader는 사용하지 않습니다.

새 환경이라면 Python 3.11로 `python3.11 -m venv .venv`를 실행한 후 활성화합니다. mock에는 외부 패키지가 필요 없습니다. 실물에는 기존 검증된 LeRobot/Feetech 환경을 사용합니다. 새로 설치할 때는 `python -m pip install 'lerobot[feetech]'` 후 설치 버전을 기록하고, API 연결/종료 동작을 다시 확인합니다. 현재 transport는 `bus.disconnect(disable_torque=False)` 지원을 요구합니다.

## 2. 관절을 선택해 조작

```bash
PYTHONPATH=src python -m robot_trial.cli jog --joint gripper
```

- `+`, `-`: 해당 관절의 설정된 step만큼 이동.
- `s`: 위치·토크 읽기.
- `q`: 종료.

실물에서도 동일한 CLI에 `--live --port "$FOLLOWER_PORT" --arm-supported`를 사용합니다. 각 쓰기에 구체적인 확인 입력이 필요합니다. 시작 위치는 연결 시 읽어 고정하며 여러 번 jog해도 기준이 재설정되지 않습니다. 현재 `max_offset_ticks`는 세션 시작 주변 시험 범위이지, 기계적 최저/최고 위치가 아닙니다.

토크·속도·가속도 설정은 이 기본 프로그램에서 자동 변경하지 않습니다. 필요하면 구체적인 값과 복원 조건을 정한 후 별도 기능으로 추가합니다. 과거 저토크 실험을 연결할 때 자동 재실행하지 않습니다.

## 3. 자세 저장과 관찰

같은 jog 세션에서:

```text
save ready
+
save a
s
```

`config/poses.json`에는 6개 관절의 위치, mock/live 구분, 저장 시각, 설정 지문이 저장됩니다. 저장은 위치와 설정을 읽을 뿐 모터를 움직이지 않습니다. 기존 이름은 덮어쓰지 않습니다. 사용자별 자세가 들어갈 파일이므로 공유 전 내용을 확인합니다.

설정 지문은 운전 모드·오프셋·장치에 저장된 위치 범위가 바뀌었는지 비교하는 용도입니다. 기계적 한계나 보정 정확성을 검증하는 증명은 아닙니다.

## 4. 미리보기와 저장 위치 이동

같은 세션에서:

```text
preview ready
go ready
```

`preview`는 경로를 계산해 표시하며 쓰기를 하지 않습니다. `go`는 jog에서 선택한 관절 하나만 이동합니다. 실물에서는 대상과 총 이동량을 다시 확인받습니다. 작은 단계마다 위치 오차를 확인하고 대상 토크 OFF를 확인합니다. 따라서 현재 동작은 관절별 단계 시험이며, 토크를 계속 유지하는 부드러운 연속 궤적 제어는 아직 아닙니다.

명령행에서도 사용할 수 있습니다.

```bash
PYTHONPATH=src python -m robot_trial.cli capture --name ready
PYTHONPATH=src python -m robot_trial.cli preview --name ready --joint gripper
PYTHONPATH=src python -m robot_trial.cli move-to --name ready --joint gripper --duration 3
```

실물 `move-to`에는 `--joint`가 필수입니다. 선택하지 않은 관절은 저장 자세와 달라도 움직이지 않습니다. mock에서는 관절 전체 경로도 시험할 수 있지만 실물 여러 관절 동시 운전은 아직 막혀 있습니다.

`duration`은 mock에서 시뮬레이션 시간, 실물에서 단계 사이 대기시간의 기준입니다. 통신/목표 도달 대기 시간이 더해질 수 있어 정확한 동작시간 보장이 아닙니다. 도달 판정은 설정 오차 이내의 한 위치 샘플이며 물리적 안정성·충돌 없는 이동을 증명하지 않습니다.

## Python에서 사용

```python
from robot_trial import RobotController, MockTransport, load_config

config = load_config("config/robot.toml")
transport = MockTransport({
    joint: settings["mock_start_ticks"]
    for joint, settings in config["joints"].items()
})
robot = RobotController(transport, config)
try:
    robot.connect()  # 읽기만 수행
    print(robot.status())
    # 기존 이름이 없을 때만 저장. 초기 파일은 비어 있습니다.
    robot.capture("ready", config["files"]["poses"])
    robot.move("gripper", 10, approved=True)
    robot.move_to("ready", config["files"]["poses"], duration=3,
                  joint="gripper", approved=True)
finally:
    robot.close()
```

생성자는 연결하지 않습니다. API의 `approved=True`는 호출하는 프로그램이 구체적인 쓰기 동의를 이미 받았다는 계약입니다. 실물 프로그램에서 무조건 True로 지정하거나 반복 실행에 재사용하지 않습니다. CLI가 이 동의 흐름을 제공합니다.

## 이후 순서

현재 조작·자세 저장을 익힌 뒤, 관절별 실측 구간·회전 방향·중력 하중 유지/종료 방식을 확인합니다. 그다음 여러 관절을 유지하는 궤적 제어와 짧은 시퀀스/BMT를 추가합니다. 카메라 좌표 변환·역기구학·AI는 그 기반이 갖춰진 뒤 연결합니다.

공개 SO-101 데이터는 현재 참고 자료입니다. 관절 순서와 단위 해석에 미확인 사항이 있어 직접 실물 재생에 사용하지 않습니다. 원본 메타데이터·추출 에피소드·분석 코드와 결과는 보관 ZIP에 있습니다.

## 결과와 오류

실행 로그는 `logs/`에 JSONL로 자동 저장됩니다. 명령·요청·결과·오류·종료를 기록하며, 실제 물리적 관찰은 사용자가 `docs/test-results.md`에 별도로 남깁니다. 데이터 파일을 바꿔도 시험별 Python 스크립트를 추가하지 않습니다.

- 포트 누락/사용 중: 장치를 다시 식별하고 다른 직렬 프로그램을 종료합니다.
- 범위 초과: 설정을 임의 확대하지 말고 현재 위치와 시험 기준을 확인합니다.
- timeout/통신 오류: 추가 이동을 막고 fault 상태로 둡니다. 자동 재시도·자동 원점 복귀는 하지 않습니다.
- Ctrl+C/종료: 전체 관절 토크를 임의 변경하지 않습니다. 선택 관절의 정리도 통신 실패 시 보장되지 않습니다. 물리적 전원 차단과 지지가 필요합니다.
