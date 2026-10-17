# Hardware & USB

- Computer: Apple Silicon Mac, macOS
- Robot: SO-ARM101 Follower Pro, USB + 12V
- Leader: SO-ARM101 Leader, USB; motor control untested
- Camera: planned, not integrated
- Bambu P2S: future custom parts

Observed ports:
- Leader: `/dev/cu.usbmodem5B790835571`
- Follower: `/dev/cu.usbmodem5B901011021`

```bash
ls /dev/cu.usb* /dev/tty.usb* 2>/dev/null
```
Ports can change. Disconnect one device to identify the other.
