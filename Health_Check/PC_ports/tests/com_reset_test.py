import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from COM_check import find_com_device
from com_control import reset


TARGET_COM = "COM4"


device = find_com_device(TARGET_COM)

if device is None:

    print(f"{TARGET_COM} not found")

else:

    print("\nFound Device:\n")

    print(device)

    reset(device["instance_id"])