import subprocess
from pathlib import Path


class PDUController:

    def __init__(
        self,
        exe_path: str,
        config_file: str
    ):
        self.exe_path = Path(exe_path)
        self.config_file = Path(config_file)

    def set_socket(self, socket_num: int, state: bool):

        command = [
            str(self.exe_path),
            "-c",
            "-s",
            "-i",
            "-f",
            str(self.config_file),
            f"SOCKET{socket_num}.STATE={'true' if state else 'false'}"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout

    def socket_on(self, socket_num: int):
        return self.set_socket(socket_num, True)

    def socket_off(self, socket_num: int):
        return self.set_socket(socket_num, False)

    def read_states(self):

        command = [
            str(self.exe_path),
            "-c",
            "-p",
            "-f",
            str(self.config_file)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return result.stdout