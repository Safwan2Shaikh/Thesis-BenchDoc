# test_usb.py

from PC_ports.usb_control import reset


INSTANCE_ID = r"PASTE_INSTANCE_ID_HERE"


result = reset(INSTANCE_ID)

print(result["disconnect"].stdout)
print(result["disconnect"].stderr)

print(result["connect"].stdout)
print(result["connect"].stderr)