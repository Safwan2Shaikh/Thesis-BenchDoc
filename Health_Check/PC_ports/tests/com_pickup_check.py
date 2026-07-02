"""
com_pickup_check.py

Test module to verify COM port pickup and availability detection.
"""

def test_com_pickup():
    """Test COM port discovery."""
    from Health_Check.PC_ports.com_check import list_available_ports
    
    ports = list_available_ports()
    print(f"Found {len(ports)} COM ports")
    for port in ports:
        print(f"  {port.device}")
    return len(ports) > 0


if __name__ == "__main__":
    result = test_com_pickup()
    print(f"COM pickup test: {'PASS' if result else 'FAIL'}")
