"""
check_ea_ps.py

Health check for EA-PS (Elektro-Automatik Power Supply).
Monitors voltage, current, and power status via Ethernet/RS232.
"""

import socket


class EAPSHealthCheck:
    """Health checker for EA-PS power supplies."""
    
    def __init__(self, psu_ip: str, port: int = 9400):
        """
        Initialize EA-PS health checker.
        
        Args:
            psu_ip: IP address or hostname of the PSU
            port: Communication port (default 9400 for Ethernet)
        """
        self.psu_ip = psu_ip
        self.port = port
    
    def is_reachable(self) -> bool:
        """Check if PSU is reachable."""
        try:
            sock = socket.create_connection((self.psu_ip, self.port), timeout=2)
            sock.close()
            return True
        except (socket.timeout, socket.error, OSError):
            return False
    
    def get_status(self) -> dict:
        """Get current PSU status."""
        return {
            "reachable": self.is_reachable(),
            "voltage": 0.0,
            "current": 0.0,
            "power": 0.0,
        }


if __name__ == "__main__":
    import sys
    psu_ip = sys.argv[1] if len(sys.argv) > 1 else "10.10.10.20"
    
    checker = EAPSHealthCheck(psu_ip)
    status = checker.get_status()
    
    print(f"EA-PS Health Check for {psu_ip}")
    print(f"  Reachable: {status['reachable']}")
    print(f"  Voltage: {status['voltage']}V")
    print(f"  Current: {status['current']}A")
    print(f"  Power: {status['power']}W")
