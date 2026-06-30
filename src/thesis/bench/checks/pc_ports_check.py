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
            ),
        ]
        output = subprocess.check_output(cmd, text=True)
        data = json.loads(output)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception:
        return []


def get_com_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append(
            {
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid,
            }
        )
    return ports


def run_check():
    ports = get_com_ports()
    details = []
    pnp_devices = get_pnp_devices()

    for port in ports:
        match = None
        for device in pnp_devices:
            friendly_name = str(device.get("FriendlyName", ""))
            if port["port"] in friendly_name:
                match = {
                    "name": friendly_name,
                    "status": device.get("Status"),
                    "instance_id": device.get("InstanceId"),
                }
                break
        details.append({"port": port, "pnp": match})

    return {
        "status": "OK",
        "count": len(ports),
        "ports": details,
    }


def main():
    result = run_check()
    print("\\nCOM PORTS:\\n")
    for item in result["ports"]:
        port = item["port"]
        print(f"{port['port']} : {port['description']}")


if __name__ == "__main__":
    main()
