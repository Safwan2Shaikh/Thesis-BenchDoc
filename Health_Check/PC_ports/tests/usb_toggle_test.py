# test_usb.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from usb_control import reset

INSTANCE_ID = r"USB\\VID_0897&PID_0004\\5&AC91B4A&0&11"


result = reset(INSTANCE_ID)

print(result["disconnect"].stdout)
print(result["disconnect"].stderr)

print(result["connect"].stdout)
print(result["connect"].stderr)