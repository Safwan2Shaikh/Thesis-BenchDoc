"""
pmb_fullcheck.py

Full system check for PMB (Power Management Board).

Uses ds2824_control.py to verify communication and relay control.
"""

import time
from ds2824_control import execute_command


def run_full_pmb_check():
    """
    Run PMB communication test.

    Returns:
        dict: PMB check results
    """

    results = {
        "accessible": False,
        "relay_tests": {},
        "errors": []
    }

    try:
        # Relay 1 Test
        rc = execute_command("SR 1 on")

        if rc == 0:
            results["accessible"] = True
            results["relay_tests"]["relay_1_on"] = "PASS"

            time.sleep(0.5)

            rc = execute_command("SR 1 off")

            if rc == 0:
                results["relay_tests"]["relay_1_off"] = "PASS"
            else:
                results["relay_tests"]["relay_1_off"] = "FAIL"

        else:
            results["relay_tests"]["relay_1_on"] = "FAIL"

        # Relay 4 Test
        rc = execute_command("SR 4 on")

        if rc == 0:
            results["relay_tests"]["relay_4_on"] = "PASS"

            time.sleep(0.5)

            rc = execute_command("SR 4 off")

            if rc == 0:
                results["relay_tests"]["relay_4_off"] = "PASS"
            else:
                results["relay_tests"]["relay_4_off"] = "FAIL"

        else:
            results["relay_tests"]["relay_4_on"] = "FAIL"

    except Exception as exc:
        results["errors"].append(str(exc))

    return results


if __name__ == "__main__":
    import json

    print("Running PMB full check...")

    result = run_full_pmb_check()

    print(json.dumps(result, indent=2))