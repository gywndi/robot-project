"""One CLI: read, jog, move, capture, preview and mock move-to."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid
from .controller import RobotController, load_config
from .transport import JOINTS, LeRobotTransport, MockTransport


def approve(joint, delta):
    print('Support the full arm and secure held objects. Keep physical power cutoff reachable.')
    print('Ctrl+C is not an E-stop. Only the selected joint is enabled and disabled.')
    phrase = f'MOVE {joint} {delta:+d}'
    return input(f'Type {phrase} to approve this single movement: ').strip() == phrase


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='read',
                        choices=('read', 'move', 'jog', 'capture', 'preview', 'move-to'))
    parser.add_argument('--config', type=Path, default=Path('config/robot.toml'))
    parser.add_argument('--poses', type=Path)
    parser.add_argument('--name')
    parser.add_argument('--joint', choices=JOINTS)
    parser.add_argument('--delta-ticks', type=int)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--port')
    parser.add_argument('--arm-supported', action='store_true')
    args = parser.parse_args()
    config = load_config(args.config)
    if args.action in ('capture', 'preview', 'move-to') and not args.name:
        parser.error('This action requires --name')
    if args.action in ('move', 'jog') and not args.joint:
        parser.error('This action requires --joint')
    if args.action == 'move' and args.delta_ticks is None:
        parser.error('move requires --delta-ticks')
    if args.live and args.action == 'move-to' and not args.joint:
        parser.error('Live multi-joint pose playback is not implemented; select --joint')
    port = args.port or os.getenv('FOLLOWER_PORT') or config.get('connection', {}).get('port')
    if args.live and (not isinstance(port, str) or not port.strip()):
        parser.error('Live mode requires --port, FOLLOWER_PORT or a nonempty configured port')
    if args.live and args.action in ('move', 'jog', 'move-to') and not args.arm_supported:
        parser.error('Live movement requires physically supported arm and --arm-supported')
    path = args.poses or Path(config['files']['poses'])
    duration = args.duration if args.duration is not None else config['control']['preview_duration_seconds']
    bus = LeRobotTransport(port) if args.live else MockTransport(
        {joint: config['joints'][joint]['mock_start_ticks'] for joint in JOINTS})
    robot = RobotController(bus, config)
    log_dir = Path(config['logging']['directory'])
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8] + '.jsonl')
    with log_path.open('x', encoding='utf-8') as stream:
        def record(event, data):
            entry = {'time_utc': datetime.now(timezone.utc).isoformat(), 'mode': bus.mode,
                     'action': args.action, 'event': event, 'data': data}
            stream.write(json.dumps(entry, ensure_ascii=False) + '\n')
            stream.flush()

        def output(result):
            record('result', result)
            print(json.dumps({'mode': bus.mode, 'result': result}, ensure_ascii=False))

        def move(delta):
            record('requested_move', {'joint': args.joint, 'delta_ticks': delta})
            if args.live and not approve(args.joint, delta):
                print('Cancelled')
                record('cancelled', {})
                return
            output(robot.move(args.joint, delta, approved=True))

        record('start', {'config': str(args.config), 'physical_observation': 'not recorded'})
        try:
            robot.connect()
            if args.action == 'read':
                output(robot.status())
            elif args.action == 'move':
                move(args.delta_ticks)
            elif args.action == 'jog':
                print(f'{args.joint}: + / -, s status, save NAME, preview NAME, go NAME (selected joint), q quit; press Enter')
                step = config['joints'][args.joint]['max_step_ticks']
                while True:
                    try:
                        key = input('jog > ').strip().lower()
                    except EOFError:
                        break
                    if key == 'q':
                        break
                    if key == 's':
                        output(robot.status())
                    elif key in ('+', '-'):
                        move(step if key == '+' else -step)
                    elif key.startswith('save '):
                        name = key.split(' ', 1)[1].strip()
                        output({'pose': name, **robot.capture(name, path)})
                    elif key.startswith('preview '):
                        output(robot.preview(key.split(' ', 1)[1].strip(), path, duration=duration, joint=args.joint))
                    elif key.startswith('go '):
                        name = key.split(' ', 1)[1].strip()
                        plan = robot.preview(name, path, duration=duration, joint=args.joint)
                        delta = plan['target'][args.joint] - plan['start'][args.joint]
                        if not args.live or approve(args.joint, delta):
                            output(robot.move_to(name, path, duration=duration, approved=True, joint=args.joint))
            elif args.action == 'capture':
                output({'pose': args.name, **robot.capture(args.name, path)})
            elif args.action == 'preview':
                output(robot.preview(args.name, path, duration=duration, joint=args.joint))
            elif args.action == 'move-to':
                plan = robot.preview(args.name, path, duration=duration, joint=args.joint)
                delta = plan['target'][args.joint] - plan['start'][args.joint] if args.joint else 0
                if not args.live or approve(args.joint, delta):
                    output(robot.move_to(args.name, path, duration=duration, approved=True, joint=args.joint))
        except BaseException as exc:
            record('error', {'type': type(exc).__name__, 'message': str(exc), 'state': robot.state})
            raise
        finally:
            try:
                robot.close()
                record('closed', {'state': robot.state})
            except BaseException as exc:
                record('close_error', {'type': type(exc).__name__, 'message': str(exc)})
                raise
            finally:
                print(f'Log: {log_path}')


if __name__ == '__main__':
    main()
