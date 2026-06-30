import subprocess
import time


def disconnect(instance_id):

    print(f"\nDisabling:\n{instance_id}\n")

    result = subprocess.run(
        [
            "powershell",
            "-Command",
            f'Disable-PnpDevice -InstanceId "{instance_id}" -Confirm:$false'
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    return result


def connect(instance_id):

    print(f"\nEnabling:\n{instance_id}\n")

    result = subprocess.run(
        [
            "powershell",
            "-Command",
            f'Enable-PnpDevice -InstanceId "{instance_id}" -Confirm:$false'
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    return result


def reset(instance_id, wait_time=3):

    disconnect(instance_id)

    time.sleep(wait_time)

    connect(instance_id)