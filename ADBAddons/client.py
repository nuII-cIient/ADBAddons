import subprocess
import time
import re
import threading
from typing import Optional, List, Dict

class ADBAddons:
    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self._running = False
        self._thread = None
        self.connected_device = None

    def _run_command(self, *args) -> str:
        try:
            result = subprocess.run(
                [self.adb_path] + list(args),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def _run_shell(self, command: str) -> str:
        return self._run_command("shell", command)

    def checkForUsb(self) -> bool:
        output = self._run_command("devices")
        devices = []
        for line in output.split('\n')[1:]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    serial = parts[0].strip()
                    state = parts[1].strip()
                    devices.append((serial, state))
                    if state == "device":
                        self.connected_device = serial
        usb_connected = any(
            state == "device" and ":" not in serial
            for serial, state in devices
        )
        return usb_connected

    def wirelessAdbConnect(self, IP: str) -> bool:
        address = f"{IP}:5555"
        output = self._run_command("connect", address)
        if "connected" in output.lower() or "already connected" in output.lower():
            self.connected_device = address
            return True
        return False

    def usbAdbConnect(self) -> bool:
        self._run_command("kill-server")
        time.sleep(1)
        self._run_command("start-server")
        time.sleep(1)
        return self.checkForUsb()

    def setOculusBattery(self, level: Optional[int] = None, status: Optional[int] = None,
                         smooth: bool = False, delay: float = 0.1) -> bool:
        try:
            if level is not None:
                if not 0 <= level <= 100:
                    return False
                if smooth:
                    current_output = self._run_shell("dumpsys battery")
                    current_match = re.search(r'level:\s*(\d+)', current_output)
                    current_level = int(current_match.group(1)) if current_match else 0
                    step = 1 if current_level < level else -1
                    status_to_use = status or (2 if current_level < level else 3)
                    for lvl in range(current_level, level + step, step):
                        self._run_shell(f"dumpsys battery set level {lvl}")
                        if status_to_use:
                            self._run_shell(f"dumpsys battery set status {status_to_use}")
                        time.sleep(delay)
                else:
                    self._run_shell(f"dumpsys battery set level {level}")
            if status is not None and not smooth:
                self._run_shell(f"dumpsys battery set status {status}")
            return True
        except Exception:
            return False

    def setOculusBrightness(self, brightness: int) -> bool:
        try:
            if not 0 <= brightness <= 255:
                return False
            self._run_shell(f"echo {brightness} > /sys/class/leds/lcd-backlight/brightness")
            self._run_shell(f"settings put system screen_brightness {brightness}")
            self._run_shell(f"settings put system oculus_brightness {brightness}")
            self._run_shell(f"echo {brightness} > /sys/class/backlight/panel/brightness")
            return True
        except Exception:
            return False

    def set_status(self, status: int) -> str:
        return self._run_shell(f"dumpsys battery set status {status}")

    def set_level(self, level: int) -> str:
        return self._run_shell(f"dumpsys battery set level {level}")

    def reset(self) -> str:
        return self._run_shell("dumpsys battery reset")

    def get_status(self) -> str:
        return self._run_shell("dumpsys battery")

    def get_controller_battery(self) -> Dict[str, int]:
        output = self._run_shell("dumpsys OVRRemoteService | grep Paired")
        controllers = {}
        right_match = re.search(r'Type:\s+Right.*?Battery:\s+(\d+)%', output)
        if right_match:
            controllers['right'] = int(right_match.group(1))
        left_match = re.search(r'Type:\s+Left.*?Battery:\s+(\d+)%', output)
        if left_match:
            controllers['left'] = int(left_match.group(1))
        return controllers

    def check_connection(self) -> bool:
        output = self._run_command("devices")
        return "\tdevice" in output

    def get_device_info(self) -> Dict:
        info = {}
        model = self._run_shell("getprop ro.product.model").strip()
        if model:
            info['model'] = model
        android = self._run_shell("getprop ro.build.version.release").strip()
        if android:
            info['android_version'] = android
        return info


def connect(adb_path: str = "adb") -> ADBAddons:
    client = ADBAddons(adb_path)
    if client.check_connection():
        return client
    else:
        raise ConnectionError("No ADB device connected")
