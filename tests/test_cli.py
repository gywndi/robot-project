import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def run_cli(self, *args, input=None):
        env = dict(os.environ, PYTHONPATH='src')
        env.pop('FOLLOWER_PORT', None)
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / 'robot.toml'
            text = Path('config/robot.toml').read_text()
            text = text.replace('directory = \"logs\"', 'directory = ' + json.dumps(str(Path(folder) / 'logs')))
            config.write_text(text)
            return subprocess.run([sys.executable, '-m', 'robot_trial.cli', *args, '--config', str(config)],
                                  env=env, text=True, input=input, capture_output=True)

    def test_mock_jog_save_preview_and_return(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'poses.json'
            result = self.run_cli('jog', '--joint', 'gripper', '--poses', str(path),
                                 input='save ready\n+\nsave a\npreview ready\ngo ready\nq\n')
            self.assertEqual(result.returncode, 0, result.stderr)
            poses = json.loads(path.read_text())['poses']
            self.assertEqual(poses['a']['positions']['gripper'] - poses['ready']['positions']['gripper'], 10)
            self.assertIn('"mode": "mock"', result.stdout)
            self.assertIn('Log:', result.stdout)

    def test_live_missing_port_rejected_before_connect(self):
        result = self.run_cli('read', '--live')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires --port', result.stderr)

    def test_live_pose_playback_blocked_before_connect(self):
        result = self.run_cli('move-to', '--live', '--name', 'ready')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not implemented', result.stderr)
