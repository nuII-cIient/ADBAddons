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

    def check_for_usb_connection(self) -> bool:
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

    def connect_adb_wireless(self, IP: str) -> bool:
        address = f"{IP}:5555"
        output = self._run_command("connect", address)
        if "connected" in output.lower() or "already connected" in output.lower():
            self.connected_device = address
            return True
        return False

    def connect_adb_usb(self) -> bool:
        self._run_command("kill-server")
        time.sleep(1)
        self._run_command("start-server")
        time.sleep(1)
        return self.checkForUsb()

    def set_brightness(self, brightness: int) -> bool:
        try:
            if not 0 <= brightness <= 255:
                return False
            self._run_shell(f"settings put system screen_brightness {brightness}")
            return True
        except Exception:
            return False

    def set_battery_led_orange(self) -> str:
        return self._run_shell(f"dumpsys battery set status 2")

    def set_battery_led_green(self) -> str:
        return self._run_shell(f"dumpsys battery set status 5")

    def set_battery_charging(self, status: bool) -> str:
        value = 1 if status else 0
        return self._run_shell(f"adb shell dumpsys battery set usb {value}")

    def set_battery_status(self, status: int) -> str:
        return self._run_shell(f"dumpsys battery set status {status}")

    def get_battery_status(self) -> str:
        return self._run_shell("dumpsys battery")

    def set_battery_level(self, level: int) -> str:
        return self._run_shell(f"dumpsys battery set level {level}")

    def reset_battery(self) -> str:
        return self._run_shell("dumpsys battery reset")

    
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
