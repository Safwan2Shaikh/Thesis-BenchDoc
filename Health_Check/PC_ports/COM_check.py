import json
import subprocess
import serial.tools.list_ports


# --------------------------------------------------
# Get all Windows PnP devices
# --------------------------------------------------

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

        print(f"Error getting PnP devices: {e}")

        return []


# --------------------------------------------------
# Get COM ports
# --------------------------------------------------

def get_com_ports():

    devices = []

    try:

        ports = serial.tools.list_ports.comports()

        for port in ports:

            devices.append(
                {
                    "port": port.device,
                    "description": port.description,
                    "hwid": port.hwid
                }
            )

    except Exception as e:

        print(f"Error scanning COM ports: {e}")

    return devices


# --------------------------------------------------
# Pico Technology Devices
# --------------------------------------------------

def get_picoscope_devices(pnp_devices):

    devices = []

    for device in pnp_devices:

        name = str(device.get("FriendlyName", ""))

        if "Pico" in name:

            devices.append(
                {
                    "name": name,
                    "status": device.get("Status"),
                    "instance_id": device.get("InstanceId")
                }
            )

    return devices


# --------------------------------------------------
# TRACE32 / Lauterbach
# --------------------------------------------------

def get_trace32_devices(pnp_devices):

    devices = []

    keywords = [
        "TRACE32",
        "Lauterbach"
    ]

    for device in pnp_devices:

        name = str(device.get("FriendlyName", ""))

        if any(keyword.lower() in name.lower()
               for keyword in keywords):

            devices.append(
                {
                    "name": name,
                    "status": device.get("Status"),
                    "instance_id": device.get("InstanceId")
                }
            )

    return devices


# --------------------------------------------------
# Generic USB devices
# --------------------------------------------------

def get_usb_devices(pnp_devices):

    devices = []

    for device in pnp_devices:

        if device.get("Class") == "USB":

            devices.append(
                {
                    "name": device.get("FriendlyName"),
                    "status": device.get("Status"),
                    "instance_id": device.get("InstanceId")
                }
            )

    return devices


# --------------------------------------------------
# Full scan
# --------------------------------------------------

def system_scan():

    pnp_devices = get_pnp_devices()

    return {
        "com_ports": get_com_ports(),
        "picoscopes": get_picoscope_devices(pnp_devices),
        "trace32_devices": get_trace32_devices(pnp_devices),
        "usb_devices": get_usb_devices(pnp_devices)
    }


# --------------------------------------------------
# Standalone test
# --------------------------------------------------

if __name__ == "__main__":

    result = system_scan()

    print(
        json.dumps(
            result,
            indent=4
        )
    )
