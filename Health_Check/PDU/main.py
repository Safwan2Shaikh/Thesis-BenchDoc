"""
main.py

PDU (Power Distribution Unit) health check main entry point.
Runs diagnostics on PDU connectivity and power distribution status.
"""

from pdu_controller import PDUController
from pdu_service import PDUService


def run_pdu_health_check(pdu_ip: str, port: int = 161):
    """
    Run health check on PDU device.
    
    Args:
        pdu_ip: IP address of the PDU
        port: SNMP port (default 161)
    
    Returns:
        dict: Health check results
    """
    service = PDUService(pdu_ip, port)
    
    results = {
        "pdu_ip": pdu_ip,
        "reachable": service.is_reachable(),
        "ports": [],
        "power_state": None,
        "errors": []
    }
    
    if not results["reachable"]:
        results["errors"].append(f"PDU at {pdu_ip} is not reachable")
        return results
    
    try:
        controller = PDUController(pdu_ip)
        results["power_state"] = controller.get_power_state()
        results["ports"] = controller.get_port_status()
    except Exception as exc:
        results["errors"].append(str(exc))
    
    return results


if __name__ == "__main__":
    # Example: python main.py
    import sys
    pdu_ip = sys.argv[1] if len(sys.argv) > 1 else "10.10.10.10"
    
    print(f"Running PDU health check on {pdu_ip}...")
    result = run_pdu_health_check(pdu_ip)
    
    import json
    print(json.dumps(result, indent=2))
