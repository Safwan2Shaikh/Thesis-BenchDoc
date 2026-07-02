"""
com_check.py

Checks COM port availability and status on the local PC.
Used to verify serial communication channels are accessible.
"""

import serial.tools.list_ports


def list_available_ports():
    """List all available COM ports on the system."""
    ports = list(serial.tools.list_ports.comports())
    return ports


def check_port_accessible(port_name):
    """
    Check if a specific COM port is accessible.
    
    Args:
        port_name: COM port name (e.g., 'COM1', '/dev/ttyUSB0')
    
    Returns:
        bool: True if port is accessible, False otherwise.
    """
    try:
        ser = serial.Serial(port_name, timeout=1)
        ser.close()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("Available COM ports:")
    for port in list_available_ports():
        print(f"  {port.device}: {port.description}")
