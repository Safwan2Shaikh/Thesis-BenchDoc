"""
com_reset_test.py

Test module to verify COM port reset and reconnection capability.
"""

def test_com_reset():
    """Test COM port reset functionality."""
    from Health_Check.PC_ports.com_control import ComController
    from Health_Check.PC_ports.com_check import list_available_ports
    
    ports = list_available_ports()
    if not ports:
        print("No COM ports available for reset test")
        return False
    
    test_port = ports[0].device
    controller = ComController(test_port)
    
    # Test open
    if not controller.open():
        return False
    
    is_open = controller.is_open()
    
    # Test close and reopen
    controller.close()
    if controller.is_open():
        return False
    
    result = controller.open()
    controller.close()
    
    return result and is_open


if __name__ == "__main__":
    result = test_com_reset()
    print(f"COM reset test: {'PASS' if result else 'FAIL'}")
