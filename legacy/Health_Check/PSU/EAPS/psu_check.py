#!/usr/bin/env python

import sys
import time
import struct
import serial

try:
    from eaps2000 import eaps2k
except ImportError:
    eaps2k = None


# ---------------- CONFIG ----------------
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
PARITY = serial.PARITY_ODD
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.5
VERBOSITY_LEVEL = 0
# ----------------------------------------


# ---------- Binary Helper Functions ----------
def calculate_checksum(data_bytes):
    checksum_val = sum(data_bytes)
    return bytes([(checksum_val >> 8) & 0xFF, checksum_val & 0xFF])


def create_telegram(is_query, expected_len, device_node, object_id, data_field=b""):
    sd_len = (expected_len - 1) & 0x0F
    sd_dir = 1 << 4
    sd_cast = 1 << 5

    if is_query:
        t_type = 0b01
    else:
        t_type = 0b11
        sd_len = (len(data_field) - 1) & 0x0F

    sd = sd_len | sd_dir | sd_cast | (t_type << 6)

    telegram = bytes([sd, device_node, object_id]) + data_field
    checksum = calculate_checksum(telegram)

    return telegram + checksum


def send_and_receive(ser, cmd, expected_len):
    ser.write(cmd)
    time.sleep(0.05)
    return ser.read(expected_len)


# ---------- Read Actual Values ----------
def read_actual_values(ser, output_node, nom_voltage, nom_current):
    print(f"\n--- Output {output_node + 1} ---")

    cmd = create_telegram(True, 6, output_node, 0x47)
    response = send_and_receive(ser, cmd, 11)

    if not response or len(response) != 11:
        print("Failed to read data")
        return None

    if calculate_checksum(response[:-2]) != response[-2:]:
        print("Checksum error")
        return None

    status1 = response[4]
    v_raw = int.from_bytes(response[5:7], "big")
    i_raw = int.from_bytes(response[7:9], "big")

    voltage = nom_voltage * v_raw / 25600
    current = nom_current * i_raw / 25600

    output_on = bool(status1 & 0x01)
    mode = "CV" if ((status1 >> 1) & 0x03) == 0 else "CC"

    print(f"Voltage: {voltage:.2f} V")
    print(f"Current: {current:.2f} A")
    print(f"Output: {'ON' if output_on else 'OFF'}")
    print(f"Mode: {mode}")

    return {
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "output_on": output_on,
        "mode": mode,
    }


def run_check(serial_port: str = SERIAL_PORT):
    result = {
        "status": "OK",
        "serial_port": serial_port,
        "device_info": None,
        "quick_status": None,
        "nominal_voltage": None,
        "nominal_current": None,
        "outputs": [],
    }

    if eaps2k is None:
        return {
            "status": "WARNING",
            "error": "eaps2000 package is not installed",
            "serial_port": serial_port,
        }

    try:
        with eaps2k(serial_port, verbosity_level=VERBOSITY_LEVEL) as ps:
            actual = ps.get_actual()
            result["device_info"] = {
                "device": ps.get_type(),
                "serial": ps.get_serial(),
                "class": ps.get_device_class(),
            }
            result["quick_status"] = {
                "voltage": actual.get("V", 0),
                "current": actual.get("I", 0),
                "output_on": bool(actual.get("on")),
            }
    except Exception as exc:
        result["status"] = "ERROR"
        result["device_info_error"] = str(exc)
        return result

    try:
        ser = serial.Serial(
            port=serial_port,
            baudrate=BAUD_RATE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT,
        )

        resp_v = send_and_receive(ser, create_telegram(True, 4, 0x00, 0x02), 9)
        nom_voltage = struct.unpack(">f", resp_v[3:7])[0]

        resp_i = send_and_receive(ser, create_telegram(True, 4, 0x00, 0x03), 9)
        nom_current = struct.unpack(">f", resp_i[3:7])[0]

        result["nominal_voltage"] = nom_voltage
        result["nominal_current"] = nom_current
        result["outputs"].append(read_actual_values(ser, 0, nom_voltage, nom_current))
        result["outputs"].append(read_actual_values(ser, 1, nom_voltage, nom_current))
    except Exception as exc:
        result["status"] = "WARNING"
        result["binary_error"] = str(exc)
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()

    return result


# ---------- Main ----------
def main():
    result = run_check()
    print(result)
    if result.get("status") == "ERROR":
        sys.exit(1)


if __name__ == "__main__":
    main()
