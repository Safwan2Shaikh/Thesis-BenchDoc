import sys
import time
import serial
import struct
from typing import Iterable

from thesis.bench.controllers.pmb_controller import run_pmb_command as run_pmb_relay_command

try:
    from eaps2000 import eaps2k
except ImportError:
    eaps2k = None


# =========================
# CONFIGURATION
# =========================
SERIAL_PORT = "COM3"
RELAY_SEQUENCE = [1, 4, 15]
RELAY_DELAYS = {
    1: 1,
    4: 1,
    15: 7,
}

BAUD_RATE = 115200
PARITY = serial.PARITY_ODD
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 1

NOM_V = 0
NOM_I = 0


# =========================
# HELPER FUNCTIONS
# =========================
def get_measurement_delay(relay):
    return RELAY_DELAYS.get(relay, 1)


# =========================
# PMB CONTROL
# =========================
def run_pmb_command(command):
    try:
        print(f"  Executing: {command}")
        return run_pmb_relay_command(command)
    except Exception as exc:
        print(f"ERROR (PMB): {exc}")
        return False


# =========================
# PSU ASCII (DEVICE INFO)
# =========================
def get_device_info(serial_port=SERIAL_PORT):
    print("\n===================================")
    print("          DEVICE INFO              ")
    print("===================================")

    if eaps2k is None:
        print("Device info failed: eaps2000 package is not installed")
        return None

    try:
        with eaps2k(serial_port, verbosity_level=0) as ps:
            info = {
                "device_name": ps.get_type(),
                "device_serial": ps.get_serial(),
                "device_class": ps.get_device_class(),
            }
            print(f"Connected to PSU on {serial_port}")
            print(f"Device Name: {info['device_name']}")
            print(f"Device Serial: {info['device_serial']}")
            print(f"Device Class: {info['device_class']}")
            return info
    except Exception as exc:
        print(f"Device info failed: {exc}")
        return None


# =========================
# PSU BINARY
# =========================
def calculate_checksum(data):
    checksum_val = sum(data)
    return bytes([(checksum_val >> 8) & 0xFF, checksum_val & 0xFF])


def create_telegram(is_query, exp_len, dn, obj):
    sd_len = (exp_len - 1) & 0x0F
    sd = sd_len | (1 << 4) | (1 << 5)

    if is_query:
        sd |= (0b01 << 6)
    else:
        sd |= (0b11 << 6)

    telegram = bytes([sd, dn, obj])
    return telegram + calculate_checksum(telegram)


def send_and_receive(ser, cmd):
    ser.write(cmd)
    time.sleep(0.1)
    return ser.read(50)


def get_nominals(ser):
    global NOM_V, NOM_I

    print("\n--- NOMINAL VALUES ---")

    resp = send_and_receive(ser, create_telegram(True, 4, 0, 0x02))
    if resp and len(resp) >= 9:
        NOM_V = struct.unpack(">f", resp[3:7])[0]
        print(f"Nominal Voltage: {NOM_V:.2f} V")

    resp = send_and_receive(ser, create_telegram(True, 4, 0, 0x03))
    if resp and len(resp) >= 9:
        NOM_I = struct.unpack(">f", resp[3:7])[0]
        print(f"Nominal Current: {NOM_I:.2f} A")


def read_output(ser, dn):
    resp = send_and_receive(ser, create_telegram(True, 6, dn, 0x47))

    if not resp or len(resp) < 11:
        return None

    status1 = resp[4]
    v_pct = int.from_bytes(resp[5:7], "big")
    i_pct = int.from_bytes(resp[7:9], "big")

    voltage = NOM_V * v_pct / 25600
    current = NOM_I * i_pct / 25600

    return {
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "status": "ON" if (status1 & 1) else "OFF",
    }


def run_check(serial_port: str = SERIAL_PORT, relays: Iterable[int] = RELAY_SEQUENCE):
    result = {
        "status": "OK",
        "serial_port": serial_port,
        "device_info": None,
        "relay_results": [],
    }

    result["device_info"] = get_device_info(serial_port)

    try:
        ser = serial.Serial(
            port=serial_port,
            baudrate=BAUD_RATE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT,
        )
    except Exception as exc:
        result["status"] = "ERROR"
        result["serial_error"] = str(exc)
        return result

    try:
        get_nominals(ser)

        for relay in relays:
            print("\n===================================")
            print(f" TESTING RELAY SR_{relay}")
            print("===================================")

            on_ok = run_pmb_command(f"SR_{relay}_on")
            time.sleep(get_measurement_delay(relay))
            output1 = read_output(ser, 0)
            output2 = read_output(ser, 1)
            off_ok = run_pmb_command(f"SR_{relay}_off")

            result["relay_results"].append(
                {
                    "relay": relay,
                    "on": bool(on_ok),
                    "off": bool(off_ok),
                    "output1": output1,
                    "output2": output2,
                }
            )
    finally:
        ser.close()

    if any((not item["on"] or not item["off"]) for item in result["relay_results"]):
        result["status"] = "WARNING"

    return result


# =========================
# MAIN WORKFLOW
# =========================
def main():
    print("===================================")
    print("            PMB CHECK              ")
    print("===================================")

    result = run_check()

    print("\n===================================")
    print("             Results               ")
    print("===================================")

    for entry in result.get("relay_results", []):
        print(f"\nRelay SR_{entry['relay']}")
        print("-----------------------------")
        for output_name in ["output1", "output2"]:
            output = entry.get(output_name)
            label = output_name.replace("output", "Output ")
            if output:
                print(
                    f"{label} -> Voltage: {output['voltage']} V | "
                    f"Current: {output['current']} A | Status: {output['status']}"
                )
            else:
                print(f"{label} -> No Data")

    print("\nRELAY CHECK COMPLETE")


if __name__ == "__main__":
    main()
