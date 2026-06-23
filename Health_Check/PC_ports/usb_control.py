# controls/usb_control.py

import subprocess
import time

from utils.logger import info


def disconnect(instance_id):

    info(f"Disabling USB device")

    subprocess.run(
        [
            "pnputil",
            "/disable-device",
            instance_id
        ]
    )


def connect(instance_id):

    info(f"Enabling USB device")

    subprocess.run(
        [
            "pnputil",
            "/enable-device",
            instance_id
        ]
    )


def reset(instance_id, wait_time=3):

    disconnect(instance_id)

    time.sleep(wait_time)

    connect(instance_id)