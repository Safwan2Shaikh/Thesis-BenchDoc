"""
check_pmb_selected.py

Test module for selective PMB relay checks.
"""

import time
from shs2rng.BenchDoc.Thesis-BenchDoc.Health_Check.PMB.ds2824_control import execute_command


def test_pmb_relay_control():
    """Test relay 1 and relay 4 operation."""

    relay1_on = execute_command("SR 1 on") == 0
    time.sleep(0.5)

    relay1_off = execute_command("SR 1 off") == 0
    time.sleep(0.5)

    relay4_on = execute_command("SR 4 on") == 0
    time.sleep(0.5)

    relay4_off = execute_command("SR 4 off") == 0

    success = relay1_on and relay1_off and relay4_on and relay4_off

    print(f"Relay 1 ON test: {'PASS' if relay1_on else 'FAIL'}")
    print(f"Relay 1 OFF test: {'PASS' if relay1_off else 'FAIL'}")
    print(f"Relay 4 ON test: {'PASS' if relay4_on else 'FAIL'}")
    print(f"Relay 4 OFF test: {'PASS' if relay4_off else 'FAIL'}")

    return success


if __name__ == "__main__":
    overall_result = test_pmb_relay_control()

    print(
        f"\nPMB Relay Test Result: {'PASS' if overall_result else 'FAIL'}"
    )