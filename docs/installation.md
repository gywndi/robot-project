# Installation — Apple Silicon Mac

```bash
brew install python@3.11
mkdir -p ~/robot-project && cd ~/robot-project
$(brew --prefix python@3.11)/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "lerobot[feetech]"
python -c "import lerobot; print('LeRobot OK')"
python -c "from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig; print('SO101 OK')"
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
pip freeze > requirements-lock.txt
```

Exact installed LeRobot version has not yet been captured. The above recreates the setup process, but newer library versions can differ.
Run interactive Python from a `.py` file, NOT `python - <<'PY'`, because `input()` otherwise raises EOFError.
