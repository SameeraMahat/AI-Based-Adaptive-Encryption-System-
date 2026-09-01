"""
Reads real-time device performance stats (CPU load, battery level) using
psutil. This feeds into the AI decision engine as one of the context
factors alongside sensitivity, file size, user role, and threat level.

Note: Battery info is only available on laptops/devices with a battery.
On a desktop PC (no battery), battery_percent will return None, and the
decision engine treats that as "not a constraint" (plugged-in power assumed).
"""

import psutil


def get_device_stats() -> dict:
    """
    Returns current device performance stats:
    {
        "cpu_percent": float (0-100),
        "battery_percent": float (0-100) or None if no battery present,
        "is_plugged_in": bool or None
    }
    """
    cpu_percent = psutil.cpu_percent(interval=0.5)

    battery = psutil.sensors_battery()
    if battery is not None:
        battery_percent = battery.percent
        is_plugged_in = battery.power_plugged
    else:
        battery_percent = None
        is_plugged_in = None

    return {
        "cpu_percent": cpu_percent,
        "battery_percent": battery_percent,
        "is_plugged_in": is_plugged_in,
    }


if __name__ == "__main__":
    stats = get_device_stats()
    print("Current device stats:")
    print(f"  CPU usage:       {stats['cpu_percent']}%")
    print(f"  Battery level:   {stats['battery_percent']}%")
    print(f"  Plugged in:      {stats['is_plugged_in']}")
