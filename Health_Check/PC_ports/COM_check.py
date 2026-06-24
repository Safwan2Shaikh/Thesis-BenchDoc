import json
import subprocess
import serial.tools.list_ports


def get_pnp_devices():

    try:

        cmd = [
            "powershell",
            "-Command",
            (
                "Get-PnpDevice | "
                "Select-Object FriendlyName,Class,Status,InstanceId | "
                "ConvertTo-Json -Depth 2"
            )
        ]

        output = subprocess.check_output(
            cmd,
            text=True
        )

        return json.loads(output)

    except Exception as e:

        print(f"Error: {e}")
        return []


def get_com_ports():

    ports = []

    for port in serial.tools.list_ports.comports():

        ports.append(
            {
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid
            }
        )

    return ports


def find_com_device(com_port):

    pnp_devices = get_pnp_devices()

    for device in pnp_devices:

        friendly_name = str(
            device.get("FriendlyName", "")
        )

        if com_port in friendly_name:

            return {
                "name": friendly_name,
                "status": device.get("Status"),
                "instance_id": device.get("InstanceId")
            }

    return None


if __name__ == "__main__":

    print("\nCOM PORTS:\n")

    for port in get_com_ports():

        print(
            f"{port['port']} : "
            f"{port['description']}"
        )