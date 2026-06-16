import sys
import time
import subprocess
import serial
import struct
from eaps2000 import eaps2k


# =========================
# CONFIGURATION
# =========================
SERIAL_PORT = 'COM3'
PMB_CONTROL_SCRIPT = "ds2824_control.py"

RELAY_SEQUENCE = [1, 4, 15]

# Relay-specific delays (seconds)
RELAY_DELAYS = {
    1: 1,
    4: 1,
    15: 7
}

# Binary PSU config
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
        subprocess.run([sys.executable, PMB_CONTROL_SCRIPT, command], check=True)
        return True
    except Exception as e:
        print(f"ERROR (PMB): {e}")
        return False


# =========================
# PSU ASCII (DEVICE INFO)
# =========================
def get_device_info():
    print("\n===================================")
    print("         DEVICE INFO (ASCII)")
    print("===================================")

    try:
        with eaps2k(SERIAL_PORT, verbosity_level=0) as ps:
            print(f"Connected to PSU on {SERIAL_PORT}")
            print(f"Device Name: {ps.get_type()}")
            print(f"Device Serial: {ps.get_serial()}")
            print(f"Device Class: {ps.get_device_class()}")

    except Exception as e:
        print(f"Device info failed: {e}")


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

    # Voltage
    resp = send_and_receive(ser, create_telegram(True, 4, 0, 0x02))
    if resp and len(resp) >= 9:
        NOM_V = struct.unpack('>f', resp[3:7])[0]
        print(f"Nominal Voltage: {NOM_V:.2f} V")

    # Current
    resp = send_and_receive(ser, create_telegram(True, 4, 0, 0x03))
    if resp and len(resp) >= 9:
        NOM_I = struct.unpack('>f', resp[3:7])[0]
        print(f"Nominal Current: {NOM_I:.2f} A")


def read_output(ser, dn):
    resp = send_and_receive(ser, create_telegram(True, 6, dn, 0x47))

    if not resp or len(resp) < 11:
        return None

    status1 = resp[4]
    v_pct = int.from_bytes(resp[5:7], 'big')
    i_pct = int.from_bytes(resp[7:9], 'big')

    voltage = NOM_V * v_pct / 25600
    current = NOM_I * i_pct / 25600

    return {
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "status": "ON" if (status1 & 1) else "OFF"
    }


# =========================
# MAIN WORKFLOW
# =========================
def main():

    print("===================================")
    print("     FULL HEALTH CHECK START")
    print("===================================")

    # Store results
    results = []

    # 1. Device info
    get_device_info()

    # 2. Open binary serial
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT
        )
    except Exception as e:
        print(f"Serial error: {e}")
        return

    # 3. Get nominal values
    get_nominals(ser)

    # 4. Relay testing
    for relay in RELAY_SEQUENCE:

        print("\n===================================")
        print(f" TESTING RELAY SR_{relay}")
        print("===================================")

        # Turn ON
        if not run_pmb_command(f"SR_{relay}_on"):
            break

        delay = get_measurement_delay(relay)
        print(f"Waiting {delay} seconds for stabilization...")
        time.sleep(delay)

        # Measure
        out1 = read_output(ser, 0)
        out2 = read_output(ser, 1)

        results.append({
            "relay": relay,
            "output1": out1,
            "output2": out2
        })

        # Turn OFF
        if not run_pmb_command(f"SR_{relay}_off"):
            break

    ser.close()

    # =========================
    # FINAL SUMMARY
    # =========================
    print("\n===================================")
    print("         FINAL SUMMARY")
    print("===================================")

    for entry in results:
        relay = entry["relay"]
        o1 = entry["output1"]
        o2 = entry["output2"]

        print(f"\nRelay SR_{relay}")
        print("-----------------------------")

        if o1:
            print(f"Output 1 -> Voltage: {o1['voltage']} V | Current: {o1['current']} A | Status: {o1['status']}")
        else:
            print("Output 1 -> No Data")

        if o2:
            print(f"Output 2 -> Voltage: {o2['voltage']} V | Current: {o2['current']} A | Status: {o2['status']}")
        else:
            print("Output 2 -> No Data")

    print("\n✅ HEALTH CHECK COMPLETE")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()