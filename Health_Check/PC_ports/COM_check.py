import json
import subprocess
import serial.tools.list_ports


# -------------------------------
# Run PowerShell and return structured list
# -------------------------------
def get_pnp_devices():
    try:
        cmd = [
            "powershell",
            "-Command",
            "Get-PnpDevice | Select-Object FriendlyName,Class,Status | ConvertTo-Json"
        ]
        output = subprocess.check_output(cmd, text=True)

        data = json.loads(output)

        # Handle case: single device vs list
        if isinstance(data, dict):
            return [data]
        return data

    except Exception as e:
        return []


# -------------------------------
# CATEGORY: Ports (COM & LPT)
# -------------------------------
def get_com_ports():
    ports = serial.tools.list_ports.comports()

    devices = []
    for port in ports:
        devices.append({
            "name": port.description,
            "port": port.device,
            "manufacturer": port.manufacturer
        })

    return {
        "count": len(devices),
        "devices": devices
    }


# -------------------------------
# CATEGORY: Pico Technology Instruments
# -------------------------------
def get_picoscope_devices(pnp_devices):
    devices = []

    for dev in pnp_devices:
        name = str(dev.get("FriendlyName", "")).lower()

        if "pico" in name:
            devices.append({
                "name": dev.get("FriendlyName"),
                "status": dev.get("Status")
            })

    return {
        "count": len(devices),
        "devices": devices
    }


# -------------------------------
# CATEGORY: TRACE32 Devices
# -------------------------------
def get_trace32_devices(pnp_devices):
    devices = []

    for dev in pnp_devices:
        name = str(dev.get("FriendlyName", "")).lower()

        if "lauterbach" in name or "trace32" in name:
            devices.append({
                "name": dev.get("FriendlyName"),
                "status": dev.get("Status")
            })

    return {
        "count": len(devices),
        "devices": devices
    }


# -------------------------------
# MAIN SYSTEM SCAN
# -------------------------------
def system_scan():
    pnp_devices = get_pnp_devices()

    result = {
        "device_manager_view": {
            "ports_com_lpt": get_com_ports(),
            "pico_technology_instruments": get_picoscope_devices(pnp_devices),
            "trace32_devices": get_trace32_devices(pnp_devices)
        }
    }

    return result


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    data = system_scan()
    print(json.dumps(data, indent=2))