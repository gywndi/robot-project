# 버섯 재배 Python 제어 프로젝트

표고 재배 환경을 관찰·기록하고, 검증된 장치부터 단계적으로 제어합니다. SO-ARM101 카메라 기반 수확은 후속 단계입니다.

현재 구현: **실물 연결 없는 mock 센서·환기 제어 CLI와 안전 검증 테스트**. 온습도·CO₂ 실측, 실물 환기/가습/냉난방, 카메라, 로봇 통합은 아직 구현하지 않았습니다. 설정의 수치는 개발용 예시이며 재배 권장값이 아닙니다.

## 1. 설치

Python 3.11 환경을 준비한 뒤 저장소 루트에서 실행합니다.

```bash
cd /Users/chan/git/robot-project
python3.11 -m venv .venv
source .venv/bin/activate
```

mock은 외부 패키지 없이 실행할 수 있습니다. 패키지 설치가 필요하면 `python -m pip install -e .`를 실행합니다. 기존 로봇 환경 설치와 과거 기록은 [설치 문서](docs/installation.md), [원본 환경 기록](docs/archive/so-arm101-environment-record.md)에 있습니다. 원본에 나오는 `~/robot-project`는 과거 경로이며 현재 저장소는 `~/git/robot-project`입니다.

## 2. 준비

[준비 목록](docs/preparation.md)에서 재배 단계, 센서, 제어 장치, 전원 및 통신 방식을 결정합니다. [설정 파일](config/cultivation.toml)은 `mode = "mock"`으로 시작합니다. 장치가 확정되기 전에는 하드웨어나 자동 재배 조건을 추정하지 않습니다.

## 3. 구현

[단계별 개발 계획](docs/roadmap.md)을 따라 센서 읽기 → 기록 → 장치 한 개 제어 → 통합 제어 → 영상 → 수확 순으로 진행합니다.

| 위치 | 역할 |
|---|---|
| `src/mushroom_control/transport.py` | 센서/환기 인터페이스와 mock |
| `src/mushroom_control/safety.py` | 측정값·설정 유효성 검사 |
| `src/mushroom_control/controller.py` | CO₂ 환기 정책, 히스테리시스 |
| `src/mushroom_control/cli.py` | 설정 로드와 1회 모의 실행 |
| `config/` | 장치·제어 설정 |
| `tests/` | 하드웨어 없는 자동 검증 |
| `examples/` | 과거 로봇 실험 코드; 아래 주의사항 참조 |

UI, transport, safety, controller, 향후 vision은 분리합니다. 로봇의 raw ticks와 보정된 degrees를 구분합니다.

## 4. 테스트

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

생성자 무명령, 환기 히스테리시스, 잘못된 센서 값 및 설정 거부를 검증합니다. 실물 시험은 자동 테스트에 포함하지 않습니다. 명령·측정값·물리적 관찰은 [시험 기록](docs/test-results.md)에 남깁니다.

## 5. 동작

```bash
PYTHONPATH=src python -m mushroom_control.cli --config config/cultivation.toml
```

한 번의 가상 측정과 환기 판단을 JSON으로 출력하고 종료합니다. 예시 CO₂ 1300 ppm에서는 가상 환기가 켜집니다. 실제 장치 명령은 전송하지 않습니다. `mock` 이외 모드는 거부합니다. 연속 운전 및 장애 복구는 후속 구현입니다.

로봇 실험 코드는 실물에 연결할 수 있으므로 초기 실행 절차에 포함하지 않습니다. 특히 기존 `examples/keyboard_control.py`는 두 관절 토크를 켜므로 초기 단일 관절 시험 규칙에 맞게 수정하기 전에는 실행하지 않습니다. [안전](docs/safety.md), [하드웨어](docs/hardware.md), [API 기록](docs/control-api.md), [문제 해결](docs/troubleshooting.md)을 먼저 확인합니다. 손목 약 360° 회전 원인은 미해결이며 기계적 한계는 검증되지 않았습니다.
