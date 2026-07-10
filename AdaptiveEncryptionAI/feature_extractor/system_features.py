import psutil
import platform


def get_system_features():

    battery = psutil.sensors_battery()

    if battery:
        battery_level = battery.percent
    else:
        battery_level = "Not Available"

    return {

        "CPU Usage (%)": psutil.cpu_percent(interval=1),

        "RAM Usage (%)": psutil.virtual_memory().percent,

        "Available RAM (GB)": round(
            psutil.virtual_memory().available /
            (1024**3),
            2
        ),

        "Disk Usage (%)": psutil.disk_usage("/").percent,

        "Battery (%)": battery_level,

        "Operating System": platform.system()
        + " "
        + platform.release()

    }