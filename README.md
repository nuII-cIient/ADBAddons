```markdown
# ADBAddons

ADB wrapper for Oculus Quest stuff.

## Install

```bash
pip install ADBAddons
```

Need:
- Python 3.6+
- ADB in PATH
- Quest with dev mode on

## Quick Start

```python
from ADBAddons import ADBAddons

client = ADBAddons()

if client.checkForUsb():
    client.setOculusBattery(level=75)
```

## Functions

### Connection
```python
client.checkForUsb()                    # true if usb connected
client.wirelessAdbConnect("192.168.1.100")  # connect over wifi
client.usbAdbConnect()                  # reconnect usb
client.check_connection()               # any connection
```

### Battery
```python
client.setOculusBattery(level=50)                    # set level
client.setOculusBattery(level=80, status=2)          # set level + charging
client.setOculusBattery(level=100, smooth=True)      # animate to level
client.set_level(75)                                 # just level
client.set_status(3)                                 # just status
client.reset()                                       # back to real values
client.get_status()                                  # current battery info
```

### Brightness
```python
client.setOculusBrightness(128)  # 0-255
```

### Controllers
```python
batteries = client.get_controller_battery()
print(batteries.get('left'))
print(batteries.get('right'))
```

### Device Info
```python
info = client.get_device_info()
print(info.get('model'))
print(info.get('android_version'))
```

## Status Codes

1 = Unknown
2 = Charging AC
3 = Discharging
4 = Not charging
5 = Full
6 = USB charging
7 = Wireless charging

## Examples

### Battery drain test
```python
from ADBAddons import ADBAddons
import time

client = ADBAddons()

for level in range(100, -1, -5):
    client.setOculusBattery(level=level, status=3)
    time.sleep(1)
```

### Smooth charge
```python
client.setOculusBattery(level=100, smooth=True, delay=0.1)
```

### Monitor controllers
```python
while True:
    controllers = client.get_controller_battery()
    print(controllers)
    time.sleep(1)
```

### Wireless
```python
# plug in usb first
client.checkForUsb()

# find ip in quest settings > wifi
client.wirelessAdbConnect("192.168.1.100")

# unplug usb, still connected
```

## Problems

**No device found**
- usb cable bad
- dev mode not on
- didnt accept prompt in headset

**Wireless fails**
- same network?
- correct ip?
- try: `adb kill-server && adb start-server`

**Permission denied**
- some things need root
- try other methods in code

## Notes

- controller battery is read only
- battery changes are software only, not real hardware
- brightness might not work on all models
- wireless needs usb first time

## License

MIT
```
