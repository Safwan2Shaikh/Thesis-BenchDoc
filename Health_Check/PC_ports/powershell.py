# utils/powershell.py

import subprocess


def run(command):

    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip()
    }