# SO-ARM101 Python 로봇 트라이얼

Follower 단독 제어를 배우고 시험하는 프로젝트입니다. **한 CLI로 위치 읽기 → 관절 조작 → 자세 저장 → 미리보기 → 저장 자세로 이동**합니다. Leader와 AI 학습은 현재 범위에서 제외합니다.

## 구조

```text
src/robot_trial/
  transport.py     # mock / LeRobot 통신
  controller.py    # 공통 제어, 자세 저장, 미리보기·이동
  safety.py        # 단위·시간·관절별 제한 검사
  cli.py           # 하나의 조작 화면
config/
  robot.toml       # 포트·관절별 시험 설정·로그 위치
  poses.json       # 직접 저장할 자세, 초기에는 비어 있음
tests/            # 하드웨어 없는 회귀 테스트
logs/             # 실행마다 자동 저장, Git 제외
docs/
  learning.md      # 학습 순서와 실행 방법
  safety.md        # 실물 시험 조건
  test-results.md  # 과거 실측 결과
  archive/         # 이전 실험 코드·자료를 묶은 보관 파일 하나
```

## 시작

기존 Python 3.11 가상환경을 활성화하고 저장소 루트에서 실행합니다.

```bash
source .venv/bin/activate
PYTHONPATH=src python -m robot_trial.cli read
PYTHONPATH=src python -m robot_trial.cli jog --joint gripper
```

`jog`에서 아래 명령을 한 줄씩 입력합니다.

```text
save ready
+
save a
preview ready
go ready
q
```

`+`/`-`는 설정된 한 step 이동, `s`는 위치·토크, `save 이름`은 현재 자세 저장입니다. 같은 이름은 덮어쓰지 않습니다. mock은 새 실행마다 설정의 초기 위치로 시작하므로 조작·저장을 같은 jog 세션에서 해봅니다.

## 실제 로봇도 같은 명령

먼저 [안전 조건](docs/safety.md)을 준비하고 로컬에서 Follower 포트를 식별합니다.

```bash
PYTHONPATH=src python -m robot_trial.cli read --live --port "$FOLLOWER_PORT"
PYTHONPATH=src python -m robot_trial.cli jog --joint gripper --live --port "$FOLLOWER_PORT" --arm-supported
```

연결만으로 구동하지 않습니다. 각 이동은 대상 관절·이동량을 표시하고 `MOVE gripper +10` 같은 확인 입력을 받습니다. 다른 관절은 `--joint`로 선택합니다. 종료 시 대상 관절의 토크를 끄므로 팔과 집게 하중을 지지해야 합니다.

mock과 실물 자세는 섞지 않습니다. 실물 `go 이름`은 선택한 관절 하나만 저장 위치로 이동합니다. 실물 여러 관절 동시 자세 재생은 아직 제공하지 않습니다. 포트·보정·모터 설정을 자동으로 초기화하지 않습니다.

## 검증과 다음 학습

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

[학습 안내](docs/learning.md)를 본인 속도로 진행하면 됩니다. 기존 시험 코드는 공통 프로그램으로 통합했으며, 과거 자료는 [보관 파일](docs/archive/robot-trials-2026-10-17.zip)에 원래 경로와 함께 저장했습니다. 이전 문서의 명령은 현재 실행 안내가 아닙니다.
