import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from COM_check import find_com_device


TARGET_COM = "COM5"


device = find_com_device(TARGET_COM)

if device is None:

    print(
        f"{TARGET_COM} not found"
    )

else:

    print("\nDevice Found\n")

    print(
        f"Name       : {device['name']}"
    )

    print(
        f"Status     : {device['status']}"
    )

    print(
        f"InstanceID : {device['instance_id']}"
    )
