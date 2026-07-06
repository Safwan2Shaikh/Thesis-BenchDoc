"""
check_ea_ps.py

Health check for EA-PS (Elektro-Automatik Power Supply).
Monitors voltage, current, and power status via Ethernet/RS232.
"""

import sys
import serial
from eaps2000 import eaps2k # Import the original class name

# --- CONFIGURATION ---
SERIAL_PORT = 'COM3'  # <<< --- CHANGE THIS TO YOUR ACTUAL SERIAL PORT ---
                      # e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux/macOS
VERBOSITY_LEVEL = 0   # 0: no extra info, 1: basic, 2: more, 3: detailed telegrams
# ---------------------

def main():
    try:
        # 1. Initialize and connect to the power supply
        # The 'with' statement ensures proper connection/disconnection and remote control handling.
        with eaps2k(SERIAL_PORT, verbosity_level=VERBOSITY_LEVEL) as ps:
            print(f"--- Connected to EA PS 2000 on {SERIAL_PORT} ---")

            # Get Device Name (Type)
            try:
                device_name = ps.get_type()
                device_serial = ps.get_serial()
                device_class = ps.get_device_class()
                print(f"Device Name: {device_name}")
                print(f"Device Serial: {device_serial}")
                print(f"Device Class: {device_class}")
            except Exception as e:
                print(f"Warning: Could not retrieve device info: {e}", file=sys.stderr)

            # Get Actual Output State (Voltage, Current, Power-on)
            # The get_actual() method provides measured real-time values.
            actual_state = ps.get_actual()
            
            current_voltage = actual_state.get('V', 0.0)
            current_current = actual_state.get('I', 0.0)
            is_output_on = actual_state.get('on', False)

            print(f"Current Voltage: {current_voltage:.3f} V")
            print(f"Current Current: {current_current:.3f} A")
            print(f"Output Status: {'ON' if is_output_on else 'OFF'}")

    except serial.SerialException as e:
        print(f"ERROR: Could not open serial port '{SERIAL_PORT}'. {e}", file=sys.stderr)
        print("Please check if the port is correct and not in use.", file=sys.stderr)
        sys.exit(1)
    except AssertionError as e:
        # Original code uses assert, so we catch AssertionError for communication issues
        print(f"ERROR: Communication assertion failed. {e}", file=sys.stderr)
        print("This often indicates a checksum mismatch or an unexpected device response.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"AN UNEXPECTED ERROR OCCURRED: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
