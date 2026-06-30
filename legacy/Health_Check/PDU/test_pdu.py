"""
PDU Integration Test

Purpose:
- Validate graph mapping
- Validate communication with DCC-PDU
- Validate socket switching
- Validate state verification

Author: Safwan
"""

import logging
import subprocess
import time
import yaml
from pathlib import Path

from topology import BenchTopology


# =====================================================
# Configuration
# =====================================================

PDU_EXE = (
    r"D:\tools\INT_8Port_PDU"
    r"\DCC-PDU_control_0.3.2"
    r"\dcc-pdu-terminal.exe"
)

PDU_CFG = (
    r"D:\tools\INT_8Port_PDU"
    r"\DCC-PDU_control_0.3.2"
    r"\PDU_VALUE_8-WAY.yaml"
)

GRAPH_FILE = (
    Path(__file__).resolve().parents[2]
    / "knowledgeBase"
    / "Bench_Config"
    / "47D_graph_trail.yaml"
)

TEST_SOCKET = 8
WAIT_TIME = 3


# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)

logger = logging.getLogger("PDU_TEST")


# =====================================================
# Controller
# =====================================================

class PDUController:

    def __init__(self, exe_path: str, config_file: str):
        self.exe = exe_path
        self.config = config_file

    def read_states(self) -> dict:

        cmd = [
            self.exe,
            "-c",
            "-p",
            "-f",
            self.config
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return yaml.safe_load(result.stdout)

    def set_socket(self, socket_number: int, state: bool):

        cmd = [
            self.exe,
            "-c",
            "-s",
            "-i",
            "-f",
            self.config,
            f"SOCKET{socket_number}.STATE={'true' if state else 'false'}"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout

    def get_socket_state(self, socket_number: int) -> bool:

        states = self.read_states()

        socket_name = f"SOCKET{socket_number}"

        return states[socket_name]["STATE"]["value_read"]


# =====================================================
# Test Logic
# =====================================================

def verify_socket_state(
        controller,
        socket_number,
        expected_state
):
    """
    Re-read socket state and verify.
    """

    actual = controller.get_socket_state(socket_number)

    if actual != expected_state:
        raise AssertionError(
            f"Socket {socket_number}: "
            f"Expected={expected_state} "
            f"Actual={actual}"
        )

    logger.info(
        f"Verification successful: "
        f"Socket {socket_number} = {actual}"
    )


def main():

    logger.info("=" * 60)
    logger.info("PDU Integration Test Started")
    logger.info("=" * 60)

    # -------------------------------------------------
    # Graph parsing
    # -------------------------------------------------

    topology = BenchTopology(str(GRAPH_FILE))

    mapping = topology.get_pdu_mapping()

    logger.info("Device Mapping:")
    for device, socket_ in mapping.items():
        logger.info(f"{device} -> Socket {socket_}")

    # -------------------------------------------------
    # Controller
    # -------------------------------------------------

    controller = PDUController(
        PDU_EXE,
        PDU_CFG
    )

    logger.info("Reading current states...")

    states = controller.read_states()

    logger.info("Current PDU Status:")

    for socket_name, data in states.items():

        state = data["STATE"]["value_read"]

        logger.info(f"{socket_name}: {state}")

    # -------------------------------------------------
    # OFF TEST
    # -------------------------------------------------

    logger.info("")
    logger.info("Switching OFF test socket")

    controller.set_socket(
        TEST_SOCKET,
        False
    )

    time.sleep(WAIT_TIME)

    verify_socket_state(
        controller,
        TEST_SOCKET,
        False
    )

    # -------------------------------------------------
    # ON TEST
    # -------------------------------------------------

    logger.info("")
    logger.info("Switching ON test socket")

    controller.set_socket(
        TEST_SOCKET,
        True
    )

    time.sleep(WAIT_TIME)

    verify_socket_state(
        controller,
        TEST_SOCKET,
        True
    )

    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST PASSED")
    logger.info("=" * 60)


if __name__ == "__main__": 
    main()