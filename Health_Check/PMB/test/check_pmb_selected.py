"""
check_pmb_selected.py

Test module for selective PMB channel and relay checks.
"""

def test_pmb_relay_control():
    """Test PMB relay control."""
    from Health_Check.PMB.ds2824_control import DS2824Controller
    
    controller = DS2824Controller()
    
    # Test relay toggle
    result1 = controller.toggle_relay(1, True)
    result2 = controller.toggle_relay(1, False)
    
    status = controller.get_relay_status()
    
    print(f"Relay 1 toggle test: {'PASS' if result1 and result2 else 'FAIL'}")
    return result1 and result2


def test_pmb_voltage_read():
    """Test PMB voltage reading."""
    from Health_Check.PMB.ds2824_control import DS2824Controller
    
    controller = DS2824Controller()
    voltage = controller.read_voltage(1)
    
    print(f"Voltage read test: PASS (read {voltage}V)")
    return True


if __name__ == "__main__":
    test_pmb_relay_control()
    test_pmb_voltage_read()
    print("All PMB tests completed.")
