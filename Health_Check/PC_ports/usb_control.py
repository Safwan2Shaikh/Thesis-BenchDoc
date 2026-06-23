import subprocess
import time

from logger import info


def disconnect(instance_id):

    info("Disabling USB device")

    result = subprocess.run(
        [
            "pnputil",
            "/disable-device",
            instance_id
        ],
        capture_output=True,
        text=True
    )

    return result


def connect(instance_id):

    info("Enabling USB device")

    result = subprocess.run(
        [
            "pnputil",
            "/enable-device",
            instance_id
        ],
        capture_output=True,
        text=True
    )

    return result


def reset(instance_id, wait_time=3):

    disconnect_result = disconnect(instance_id)

    time.sleep(wait_time)

    connect_result = connect(instance_id)

    return {
        "disconnect": disconnect_result,
        "connect": connect_result
    }