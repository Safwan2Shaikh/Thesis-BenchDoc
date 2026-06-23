# checks/usb_check.py

import subprocess
import json


def get_usb_devices():

    command = [
        "powershell",
        "-Command",
        (
            "Get-PnpDevice | "
            "Where-Object {$_.Class -eq 'USB'} | "
            "Select FriendlyName,InstanceId,Status | "
            "ConvertTo-Json"
        )
    ]

    output = subprocess.check_output(
        command,
        text=True
    )

    return json.loads(output)