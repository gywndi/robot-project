# Safety

This is experimental hardware. Joint mechanical limits and calibration have NOT been validated.
- Secure robot and clear workspace.
- Keep a physical motor power cutoff reachable. Ctrl+C is not an emergency stop.
- Read present position first; set goal to present before enabling torque.
- Energize only the selected joint for initial testing.
- Begin with tiny movements and confirm physical motion.
- ±60 ticks from startup is a software envelope, not a verified mechanical limit.
- Do not drop gravity-loaded shoulder/elbow joints by disabling torque without support.
- Do not run calibration or motor-ID setup automatically.
- Investigate prior unexpected wrist ~360° rotation before automated motion.
