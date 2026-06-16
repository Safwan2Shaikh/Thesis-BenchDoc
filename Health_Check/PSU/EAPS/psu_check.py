#!/usr/bin/env python

import sys
import time
import struct
import serial
from eaps2000 import eaps2k

# ---------------- CONFIG ----------------
SERIAL_PORT = 'COM3'
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


def create_telegram(is_query, expected_len, device_node, object_id, data_field=b''):
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
        return

    if calculate_checksum(response[:-2]) != response[-2:]:
        print("Checksum error")
        return

    status1 = response[4]
    v_raw = int.from_bytes(response[5:7], 'big')
    i_raw = int.from_bytes(response[7:9], 'big')

    voltage = nom_voltage * v_raw / 25600
    current = nom_current * i_raw / 25600

    print(f"Voltage: {voltage:.2f} V")
    print(f"Current: {current:.2f} A")

    # Status decoding
    output_on = bool(status1 & 0x01)
    mode = "CV" if ((status1 >> 1) & 0x03) == 0 else "CC"

    print(f"Output: {'ON' if output_on else 'OFF'}")
    print(f"Mode: {mode}")


# ---------- Main ----------
def main():

    # -------- 1. DEVICE INFO --------
    try:
        with eaps2k(SERIAL_PORT, verbosity_level=VERBOSITY_LEVEL) as ps:
            print(f"\n=== EA PS 2000 ({SERIAL_PORT}) ===")

            print(f"Device: {ps.get_type()}")
            print(f"Serial: {ps.get_serial()}")
            print(f"Class : {ps.get_device_class()}")

            actual = ps.get_actual()
            print("\n[Quick Status]")
            print(f"Voltage: {actual.get('V', 0):.2f} V")
            print(f"Current: {actual.get('I', 0):.2f} A")
            print(f"Output : {'ON' if actual.get('on') else 'OFF'}")

    except Exception as e:
        print(f"Failed to read device info: {e}")
        sys.exit(1)

    # -------- 2. BINARY COMMUNICATION --------
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT
        )

        # Get nominal voltage
        resp_v = send_and_receive(ser, create_telegram(True, 4, 0x00, 0x02), 9)
        nom_voltage = struct.unpack('>f', resp_v[3:7])[0]

        # Get nominal current
        resp_i = send_and_receive(ser, create_telegram(True, 4, 0x00, 0x03), 9)
        nom_current = struct.unpack('>f', resp_i[3:7])[0]

        print(f"\nNominal Voltage: {nom_voltage:.2f} V")
        print(f"Nominal Current: {nom_current:.2f} A")

        # Read outputs
        read_actual_values(ser, 0, nom_voltage, nom_current)
        read_actual_values(ser, 1, nom_voltage, nom_current)

    except Exception as e:
        print(f"\nBinary read failed: {e}")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


# ---------- RUN ----------
if __name__ == "__main__":
    main()