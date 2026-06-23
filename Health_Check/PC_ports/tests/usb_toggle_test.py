import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from usb_control import reset


INSTANCE_ID = r"PASTE_INSTANCE_ID_HERE"

result = reset(INSTANCE_ID)

print("=== DISCONNECT ===")
print(result["disconnect"].stdout)
print(result["disconnect"].stderr)

print("=== CONNECT ===")
print(result["connect"].stdout)
print(result["connect"].stderr)