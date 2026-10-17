import copy
import json
from pathlib import Path
import tempfile
import unittest
from robot_trial import RobotController, MockTransport, load_config
from robot_trial.transport import JOINTS, LeRobotTransport


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config('config/robot.toml')
        self.bus = MockTransport({j: v['mock_start_ticks'] for j, v in self.config['joints'].items()})
        self.robot = RobotController(self.bus, self.config)
        self.addCleanup(self.robot.close)

    def test_construct_connect_read_close_do_not_write(self):
        self.assertFalse(self.bus.connected)
        self.robot.connect()
        self.robot.status()
        self.robot.close()
        self.assertEqual(self.bus.commands, [])

    def test_unapproved_move_has_no_writes(self):
        self.robot.connect()
        with self.assertRaises(PermissionError):
            self.robot.move('gripper', 5)
        self.assertEqual(self.bus.commands, [])

    def test_all_joints_single_target_and_torque_cleanup(self):
        self.robot.connect()
        for joint in JOINTS:
            with self.subTest(joint=joint):
                self.bus.commands.clear()
                result = self.robot.move(joint, 5, approved=True)
                self.assertEqual(result['error_ticks'], 0)
                self.assertTrue(all(cmd[1] == joint for cmd in self.bus.commands))
                self.assertEqual(self.bus.commands[-1], ('disable', joint))
                self.assertEqual(self.bus.torque(joint), 0)

    def test_jog_anchor_does_not_reset_each_step(self):
        self.robot.connect()
        for _ in range(4):
            self.robot.move('wrist_roll', 5, approved=True)
        previous = list(self.bus.commands)
        with self.assertRaises(ValueError):
            self.robot.move('wrist_roll', 5, approved=True)
        self.assertEqual(self.bus.commands, previous)

    def test_existing_torque_does_not_get_modified(self):
        self.robot.connect()
        self.bus.enabled['shoulder_lift'] = 1
        with self.assertRaises(RuntimeError):
            self.robot.move('gripper', 5, approved=True)
        self.assertEqual(self.bus.commands, [])
        self.assertEqual(self.bus.enabled['shoulder_lift'], 1)

    def test_movement_error_disables_only_target_and_fault_latches(self):
        self.robot.connect()
        original = self.bus.write
        def fail(joint, value):
            if self.bus.enabled[joint]:
                raise OSError('Lost connection')
            original(joint, value)
        self.bus.write = fail
        with self.assertRaises(OSError):
            self.robot.move('gripper', 5, approved=True)
        self.assertEqual(self.bus.commands[-1], ('disable', 'gripper'))
        self.assertEqual(self.robot.state, 'fault')
        with self.assertRaises(RuntimeError):
            self.robot.move('wrist_roll', 5, approved=True)

    def test_timeout_disables_target(self):
        self.config['control']['timeout_seconds'] = 0.001
        self.robot.connect()
        self.bus.write = lambda joint, target: None
        with self.assertRaises(TimeoutError):
            self.robot.move('gripper', 10, approved=True)
        self.assertEqual(self.bus.torque('gripper'), 0)
        self.assertEqual(self.robot.state, 'fault')

    def test_capture_preview_and_playback(self):
        self.robot.connect()
        with tempfile.TemporaryDirectory() as folder:
            poses = Path(folder) / 'poses.json'
            self.robot.capture('ready', poses)
            self.robot.move('gripper', 10, approved=True)
            self.robot.capture('a', poses)
            before = list(self.bus.commands)
            plan = self.robot.preview('ready', poses, duration=3)
            self.assertEqual(before, self.bus.commands)
            self.assertFalse(plan['hardware_replay_allowed'])
            result = self.robot.move_to('ready', poses, duration=3, approved=True)
            self.assertEqual(result['positions']['gripper'], self.robot.anchors['gripper'])
            with self.assertRaises(ValueError):
                self.robot.capture('ready', poses)

    def test_pose_units_mode_and_envelope_are_checked(self):
        self.robot.connect()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'poses.json'
            self.robot.capture('a', path)
            original = json.loads(path.read_text())
            for change in ('units', 'mode', 'range'):
                data = copy.deepcopy(original)
                if change == 'units':
                    data['units'] = 'degrees'
                elif change == 'mode':
                    data['poses']['a']['mode'] = 'live'
                else:
                    data['poses']['a']['positions']['gripper'] += 1000
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    self.robot.preview('a', path, duration=3)

    def test_live_multi_joint_playback_blocked_without_writes(self):
        self.robot.connect()
        self.bus.mode = 'live'
        with self.assertRaises(RuntimeError):
            self.robot.move_to('ready', 'config/poses.json', duration=3, approved=True)
        self.assertEqual(self.bus.commands, [])

    def test_live_single_joint_path_uses_common_controller(self):
        # Exercise live-mode policy using a mock transport; never access USB.
        self.bus.mode = 'live'
        self.robot.connect()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'poses.json'
            self.robot.capture('ready', path)
            self.robot.move('gripper', 10, approved=True)
            self.bus.commands.clear()
            self.robot.move_to('ready', path, duration=0.001,
                               joint='gripper', approved=True)
            self.assertEqual(self.bus.read('gripper'), self.robot.anchors['gripper'])
            self.assertTrue(all(cmd[1] == 'gripper' for cmd in self.bus.commands))
            self.assertEqual(self.bus.torque('gripper'), 0)

    def test_changed_motor_configuration_blocks_new_writes(self):
        self.robot.connect()
        self.bus.fingerprint = lambda: 'changed'
        with self.assertRaises(RuntimeError):
            self.robot.move('gripper', 5, approved=True)
        self.assertEqual(self.bus.commands, [])
        self.assertEqual(self.robot.state, 'fault')

    def test_port_required(self):
        for port in (None, '', ' '):
            with self.assertRaises(ValueError):
                LeRobotTransport(port)

    def test_nan_duration_rejected_without_writes(self):
        self.robot.connect()
        with self.assertRaises(ValueError):
            self.robot.preview('a', 'config/poses.json', duration=float('nan'))
        self.assertEqual(self.bus.commands, [])
