"""
pmb_fullcheck.py

Full system check for PMB (Power Management Board).
Performs comprehensive diagnostics on all PMB functions.
"""

from ds2824_control import DS2824Controller


def run_full_pmb_check(i2c_address: int = 0x40) -> dict:
    """
    Run full PMB diagnostics.
    
    Args:
        i2c_address: I2C address of the PMB
    
    Returns:
        dict: Full check results
    """
    results = {
        "pmb_address": hex(i2c_address),
        "accessible": False,
        "relays": {},
        "voltages": {},
        "errors": []
    }
    
    try:
        controller = DS2824Controller(i2c_address)
        results["accessible"] = True
        results["relays"] = controller.get_relay_status()
        
        # Check voltage on typical channels
        for channel in range(1, 5):
            try:
                voltage = controller.read_voltage(channel)
                results["voltages"][f"ch{channel}"] = voltage
            except Exception as exc:
                results["errors"].append(f"Channel {channel} read failed: {exc}")
    
    except Exception as exc:
        results["errors"].append(f"PMB initialization failed: {exc}")
    
    return results


if __name__ == "__main__":
    print("Running PMB full check...")
    result = run_full_pmb_check()
    
    import json
    print(json.dumps(result, indent=2))
