"""Common controller: session limits, single-joint jog, poses and mock playback."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
import tomllib
from .safety import JointLimits, positive_seconds
from .transport import JOINTS, Transport


def load_config(path):
    config = tomllib.loads(Path(path).read_text(encoding='utf-8'))
    if set(config['joints']) != set(JOINTS):
        raise ValueError('Configure exactly the six known joints')
    for values in config['joints'].values():
        JointLimits(values['max_offset_ticks'], values['max_step_ticks'], values['tolerance_ticks'])
        if type(values['mock_start_ticks']) is not int:
            raise ValueError('Mock positions must be integer ticks')
    positive_seconds(config['control']['timeout_seconds'])
    positive_seconds(config['control']['poll_seconds'])
    if not isinstance(config['logging']['directory'], str) or not config['logging']['directory'].strip():
        raise ValueError('Logging directory must be nonempty')
    return config


class RobotController:
    def __init__(self, transport: Transport, config: dict):
        self.transport = transport
        self.config = config
        self.limits = {joint: JointLimits(v['max_offset_ticks'], v['max_step_ticks'], v['tolerance_ticks'])
                       for joint, v in config['joints'].items()}
        self.anchors = {}
        self.session_fingerprint = None
        self.state = 'disconnected'

    def connect(self):
        if self.state != 'disconnected':
            raise RuntimeError('Close the previous session first')
        try:
            self.transport.connect()
            self.anchors = self.positions()
            self.session_fingerprint = self.transport.fingerprint()
            self.state = 'ready'
        except BaseException:
            self.state = 'fault'
            raise

    def close(self):
        # Does not globally disable torque. Each approved movement owns cleanup.
        self.transport.close()
        self.state = 'disconnected'
        self.anchors = {}

    def positions(self):
        return {joint: self.transport.read(joint) for joint in JOINTS}

    def status(self):
        return {'units': 'raw_ticks', 'positions': self.positions(),
                'torque': {joint: self.transport.torque(joint) for joint in JOINTS}}

    def _ready(self):
        if self.state != 'ready':
            raise RuntimeError('Controller must be connected and ready')

    def move(self, joint: str, delta: int, *, approved=False):
        self._ready()
        if not approved:
            raise PermissionError('Explicit operator approval required')
        if joint not in JOINTS or type(delta) is not int or delta == 0:
            raise ValueError('Known joint and nonzero integer raw-tick delta required')
        bus = self.transport
        if self.session_fingerprint != bus.fingerprint():
            self.state = 'fault'
            raise RuntimeError('Motor configuration changed during session')
        limit = self.limits[joint]
        current = bus.read(joint)
        target = current + delta
        # Anchor remains fixed across all jogs in this connection.
        limit.check_step(self.anchors[joint], current, target)
        if any(bus.torque(name) != 0 for name in JOINTS):
            raise RuntimeError('All joints must initially be torque-off; support the arm')
        self.state = 'moving'
        try:
            try:
                bus.write(joint, current)
                bus.enable(joint)
                bus.write(joint, target)
                deadline = time.monotonic() + self.config['control']['timeout_seconds']
                while True:
                    actual = bus.read(joint)
                    limit.check_target(self.anchors[joint], actual)
                    if abs(actual - target) <= limit.tolerance_ticks:
                        break
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Target not reached; no automatic retry or range increase')
                    time.sleep(self.config['control']['poll_seconds'])
                result = {'joint': joint, 'units': 'raw_ticks', 'start_ticks': current,
                          'target_ticks': target, 'actual_ticks': actual,
                          'error_ticks': actual - target}
            finally:
                bus.disable(joint)
                if bus.torque(joint) != 0:
                    raise RuntimeError('Torque-off verification failed; physical intervention required')
            self.state = 'ready'
            return result
        except BaseException:
            self.state = 'fault'
            raise

    def capture(self, name: str, path):
        self._ready()
        if not name.strip():
            raise ValueError('Pose name is required')
        path = Path(path)
        data = self._pose_file(path) if path.exists() else {
            'schema_version': 1, 'units': 'raw_ticks', 'poses': {}}
        if name in data['poses']:
            raise ValueError('Pose already exists; use a new name')
        record = {'mode': self.transport.mode, 'calibration_verified': False,
                  'configuration_fingerprint': self.transport.fingerprint(),
                  'captured_at_utc': datetime.now(timezone.utc).isoformat(),
                  'positions': self.positions()}
        data['poses'][name] = record
        # A complete pose is read before creating/replacing the file.
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.tmp')
        with temporary.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(data, indent=2) + '\n')
        temporary.replace(path)
        return record

    @staticmethod
    def _pose_file(path):
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if data.get('schema_version') != 1 or data.get('units') != 'raw_ticks' or not isinstance(data.get('poses'), dict):
            raise ValueError('Expected pose schema 1 with explicit raw_ticks units')
        return data

    def preview(self, name: str, path, *, duration: float, joint=None):
        self._ready()
        positive_seconds(duration)
        record = self._pose_file(path)['poses'][name]
        if record.get('mode') != self.transport.mode:
            raise ValueError('Mock and live poses cannot be mixed')
        if record.get('configuration_fingerprint') != self.transport.fingerprint():
            raise ValueError('Pose configuration fingerprint mismatch; recapture/review required')
        if joint is not None and joint not in JOINTS:
            raise ValueError('Unknown joint')
        target = dict(record['positions'])
        if set(target) != set(JOINTS):
            raise ValueError('Incomplete pose')
        start = self.positions()
        selected_joint = joint
        if selected_joint is not None:
            target = {j: target[j] if j == selected_joint else start[j] for j in JOINTS}
        for joint in JOINTS:
            self.limits[joint].check_target(self.anchors[joint], start[joint])
            self.limits[joint].check_target(self.anchors[joint], target[joint])
        count = max(1, max(math.ceil(abs(target[j] - start[j]) / self.limits[j].max_step_ticks) for j in JOINTS))
        frames = [{joint: round(start[joint] + (target[joint] - start[joint]) * i / count)
                   for joint in JOINTS} for i in range(1, count + 1)]
        previous = start
        for frame in frames:
            for joint in JOINTS:
                self.limits[joint].check_step(self.anchors[joint], previous[joint], frame[joint])
            previous = frame
        return {'pose': name, 'units': 'raw_ticks', 'duration_seconds': duration,
                'start': start, 'target': target, 'frames': frames,
                'hardware_replay_allowed': False, 'selected_joint': selected_joint}

    def move_to(self, name: str, path, *, duration: float, approved=False, joint=None):
        self._ready()
        if self.transport.mode == 'live' and joint is None:
            raise RuntimeError('Live multi-joint pose playback is not implemented; select one --joint')
        if not approved:
            raise PermissionError('Explicit playback request required')
        plan = self.preview(name, path, duration=duration, joint=joint)
        # One-joint steps use the same cleanup and bounds as manual jog.
        # Live duration is a pacing target; communication/settling adds time.
        for frame in plan['frames']:
            for target_joint in JOINTS:
                delta = frame[target_joint] - self.transport.read(target_joint)
                if delta:
                    self.move(target_joint, delta, approved=True)
            if self.transport.mode == 'live':
                time.sleep(duration / len(plan['frames']))
        return {'pose': name, 'mode': self.transport.mode, 'selected_joint': joint,
                'requested_duration_seconds': duration, 'positions': self.positions()}
