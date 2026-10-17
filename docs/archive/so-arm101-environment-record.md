# SO-ARM101 Python 환경 구성 기록

정리일: 2026-10-17  
대상: Apple Silicon Mac / Python 3.11 / LeRobot / Feetech / SO-ARM101

## 1. 기록의 범위

기존 「버섯 재배 온도 정보 - 로봇」 대화에서 확인된 환경과 실행 결과를 정리한 문서입니다. 원본 프로젝트 ZIP을 수정한 파일은 아닙니다.

대화에서 실제 확인된 사항:

- 프로젝트 경로: `/Users/chan/robot-project` (`~/robot-project`)
- 가상환경: 프로젝트 내부 `.venv`
- 오류 메시지의 설치 경로: `.venv/lib/python3.11/site-packages/lerobot/`
- `import lerobot` 실행 결과: `LeRobot OK`
- `SO101Follower`, `SO101FollowerConfig` 사용 성공
- Follower의 6개 모터 원시 위치 읽기 성공

Homebrew 설치 명령과 최초 환경 생성 명령은 대화의 일부 코드 블록이 누락되어 그대로 복원할 수 없었습니다. 아래 설치 절차는 위 환경을 다시 구성할 수 있도록 보완한 명령입니다. 당시 Python 패치 버전, LeRobot 버전 및 전체 패키지 목록의 실제 출력은 확인되지 않았으므로 임의로 기재하지 않았습니다.

## 2. Homebrew와 Python 3.11 준비

터미널에서 확인합니다.

```bash
uname -m
brew --version
```

Apple Silicon에서 네이티브로 실행 중이면 보통 `arm64`가 표시됩니다. Homebrew가 없다면 [공식 설치 안내](https://brew.sh/)에 따라 설치하고, 설치 마지막에 표시되는 셸 설정을 적용한 뒤 진행합니다.

```bash
brew install python@3.11
/opt/homebrew/bin/python3.11 --version
```

Apple Silicon Homebrew의 기본 경로는 `/opt/homebrew`입니다. 경로가 다르면 다음 명령으로 설치 위치를 확인합니다.

```bash
brew --prefix python@3.11
```

이 문서에서는 시스템 Python과 구분하기 위해 가상환경을 만들 때 Python 3.11 경로를 명시합니다. [Homebrew Python 3.11 안내](https://formulae.brew.sh/formula/python%403.11)

## 3. 프로젝트 디렉터리와 가상환경 생성

처음 구성할 때 실행합니다. 기존 `.venv`가 있으면 재생성하지 말고 다음 절의 활성화부터 진행합니다.

```bash
mkdir -p ~/robot-project
cd ~/robot-project
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
```

가상환경은 이 프로젝트에 필요한 패키지를 다른 프로젝트와 분리합니다. [Python 가상환경 안내](https://docs.python.org/3.11/tutorial/venv.html)

활성화 후 확인:

```bash
pwd
command -v python
python --version
python -m pip --version
```

대화의 사용자 환경에서는 `pwd`가 `/Users/chan/robot-project`, Python 경로가 `/Users/chan/robot-project/.venv/bin/python`을 가리키는 구성이었습니다. 버전은 `Python 3.11.x`, pip 경로는 `.venv` 내부인지 확인합니다.

## 4. pip 업데이트 및 LeRobot 설치

가상환경을 활성화한 상태에서 실행합니다.

```bash
python -m pip install --upgrade pip
python -m pip install 'lerobot[feetech]'
```

두 번째 명령은 요청한 `pip install 'lerobot[feetech]'`와 같은 목적이며, 현재 Python에 연결된 pip를 명확히 사용합니다. 따옴표는 zsh가 대괄호를 파일 패턴으로 해석하지 않게 합니다. Feetech 추가 의존성 설치 명령은 [LeRobot 공식 설치 문서](https://github.com/huggingface/lerobot/blob/main/docs/source/installation.mdx)를 참고했습니다.

버전을 지정하지 않은 설치는 당시 환경과 동일한 버전을 보장하지 않습니다. 기존 작동 환경이 있다면 먼저 6절의 버전 기록을 저장하세요. API 경로가 다르면 설치된 버전부터 확인합니다.

## 5. import 확인

USB 연결 없이 실행할 수 있는 확인 명령입니다.

```bash
python -c "import lerobot; print('LeRobot OK')"
python -c "from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig; print('SO101 OK')"
```

대화에서 첫 번째 명령의 `LeRobot OK` 출력과 SO101 클래스 사용 성공이 확인됐습니다.

당시 `SOFollowerRobot`을 import하려고 했을 때는 `ImportError`가 발생했습니다. 해당 환경에서 확인된 클래스는 `SO101Follower`입니다. 오류가 나면 다음으로 현재 모듈 내용을 확인합니다.

```bash
python -c "import lerobot.robots.so_follower as m; print(dir(m))"
```

`ModuleNotFoundError`이면 가상환경 활성화와 설치 위치를, `ImportError`이면 버전과 클래스·모듈 경로를 확인합니다. 설치를 반복하거나 무조건 업그레이드하기 전에 기존 버전을 기록합니다.

## 6. 설치 버전 및 전체 패키지 기록

```bash
cd ~/robot-project
source .venv/bin/activate
python --version
python -m pip --version
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
python -m pip show lerobot
python -m pip check
python -m pip freeze > requirements-freeze.txt
```

환경 정보를 별도 파일로 저장하려면:

```bash
python - <<'PY' > environment-info.txt
import sys
import platform
import importlib.metadata as metadata
print('Python:', sys.version)
print('Executable:', sys.executable)
print('Platform:', platform.platform())
print('Architecture:', platform.machine())
print('LeRobot:', metadata.version('lerobot'))
PY
```

`requirements-freeze.txt`는 실행 시점의 설치 패키지 목록입니다. 원래 대화 당시의 목록을 복원하는 것은 아닙니다. 새 Python 3.11 가상환경에서 같은 패키지를 설치할 때는 다음을 사용합니다.

```bash
python -m pip install -r requirements-freeze.txt
```

운영체제와 CPU, 외부 의존성 차이 때문에 이 파일만으로 완전한 환경 재현을 보장하지는 않습니다. `.venv` 폴더 자체를 복사하기보다 환경 정보와 패키지 목록을 함께 보관합니다.

## 7. 매번 작업을 시작하고 종료하는 방법

새 터미널을 열 때마다:

```bash
cd ~/robot-project
source .venv/bin/activate
python --version
```

작업 종료:

```bash
deactivate
```

가상환경 비활성화는 로봇의 정지 명령이 아닙니다. 제어 프로그램을 정상 종료하고 로봇 상태를 확인한 다음 실행합니다.

## 8. Leader / Follower USB 포트

대화에서 장치를 구분하여 확인한 경로:

| 역할 | 확인된 포트 |
|---|---|
| Leader | `/dev/cu.usbmodem5B790835571` |
| Follower | `/dev/cu.usbmodem5B901011021` |

재연결 후에는 이름이 달라질 수 있으므로 다시 확인합니다. SenseCraft Robotics와 다른 직렬 통신 프로그램을 먼저 종료합니다.

```bash
python -m serial.tools.list_ports
```

기존 대화에서 사용한 명령은 다음과 같습니다. zsh에서 일치하는 장치가 없으면 `no matches found`가 나올 수 있습니다.

```bash
ls /dev/cu.usb* /dev/tty.usb* 2>/dev/null
```

`cu`와 `tty` 경로가 같은 장치에 대해 함께 나타날 수 있습니다. 두 경로가 있다고 로봇이 두 대인 것은 아닙니다. 연결에는 대화에서 검증한 `/dev/cu.*` 경로를 사용합니다. 로봇을 지지하고 모든 제어를 종료한 상태에서 USB를 한 대씩 연결하여 어느 포트가 나타나는지 비교합니다.

## 9. 초기 확인 순서와 대화의 테스트 기록

1. 가상환경의 Python 경로 및 버전을 확인합니다.
2. LeRobot과 SO101 클래스 import를 확인합니다.
3. 버전과 `pip freeze`를 저장합니다.
4. Follower USB 포트를 식별합니다.
5. 설치된 API의 연결·해제 동작을 확인한 뒤 관절 위치 읽기를 진행합니다.
6. 캘리브레이션, 기계적 범위, 전원과 정지 수단을 확인한 뒤 관절 하나씩 소폭 구동합니다.

API 확인은 로봇 연결 없이 할 수 있습니다.

```bash
python - <<'PY'
import inspect
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
print('Config:', inspect.signature(SO101FollowerConfig))
print('Connect:', inspect.signature(SO101Follower.connect))
print(inspect.getsource(SO101Follower.connect))
print(inspect.getsource(SO101Follower.configure))
PY
```

기존 대화에서는 `robot.bus.connect()`와 `bus.read('Present_Position', motor, normalize=False)`로 위치를 읽었습니다. 실제 사용자 출력은 아래와 같습니다. 이 값은 과거 측정 기록이며 목표 위치로 재사용하면 안 됩니다.

```text
shoulder_pan    : 1966
shoulder_lift   : 2052
elbow_flex      : 2040
wrist_flex     : 2041
wrist_roll     : 3140
gripper        : 2470
```

추가 테스트 기록: 집게는 시작 2470 → 목표 2490 → 실제 2488, 손목 왕복은 시작 3156 → 최대 목표 3211 → 최대 실제 3207 → 최종 3159였습니다. 이후 사용자가 손목의 작은 실제 움직임을 확인했습니다. 이 성공 기록이 전체 관절의 안전한 동작이나 캘리브레이션 완료를 의미하지는 않습니다.

## 10. 실행 방식 및 안전 주의사항

- `input()`으로 키보드 입력을 받는 코드는 `.py` 파일로 저장하고 `python -u control.py`처럼 실행합니다. `python - <<'PY'`로 프로그램을 전달하면 stdin을 이미 사용하므로 대화에서처럼 `EOFError`가 발생할 수 있습니다.
- 기존 대화에서 손목이 한 바퀴 회전하는 문제가 보고됐고 원인은 해결된 것으로 확인되지 않았습니다. 큰 각도 이동과 전체 팔 동시 제어 전에 보정·회전 방향·기계적 범위를 확인합니다.
- `normalize=False`의 원시 위치값과 정규화된 각도·동작값을 섞지 않습니다.
- 당시 확인한 `SO101Follower.connect()`는 `calibrate=False`여도 `configure()`를 실행했습니다. 캘리브레이션을 생략한다고 설정 변경까지 생략되는 것은 아닙니다.
- 직접 버스 연결은 상위 로봇 객체의 보정·보호 설정을 우회할 수 있습니다. 연결·해제 시 토크 상태가 달라질 가능성에 대비해 팔을 안정적으로 지지합니다.
- 어깨·팔꿈치는 토크 해제나 전원 차단 시 처질 수 있습니다. 베이스를 고정하고 팔의 무게를 지지하며, 관절과 집게에 손을 넣지 않습니다.
- 전원 전압은 실제 장비와 어댑터 표기를 확인합니다. Leader/Follower 전원을 임의로 바꾸어 연결하지 않습니다.
- 프로그램 종료나 `Ctrl+C`만으로 정지가 보장되는 것은 아닙니다. 즉시 접근할 수 있는 전원 차단 수단을 준비합니다.
- 기존 모터의 ID나 보정값을 확인 없이 재설정하지 않습니다. SenseCraft의 보정 정보가 LeRobot으로 자동 공유된다고 가정하지 않습니다.

## 11. 권장 보관 구조

```text
~/robot-project/
├── .venv/                   # 로컬 가상환경
├── README.md                # 이 문서 내용을 통합할 위치
├── requirements-freeze.txt   # 실제 환경에서 생성
├── environment-info.txt      # 실제 환경에서 생성
├── control.py               # 기존 제어 코드가 있을 경우
└── docs/
    └── installation.md      # 기존 파일 유지
```

위 구조는 보관 안내입니다. 이 문서 작성 과정에서 사용자의 `~/robot-project`에 패키지를 설치하거나 로봇 테스트를 실행하지 않았습니다.

