"""
com_control.py

Controls and manages COM port communication.
Handles serial communication setup and data transmission.
"""

import serial
from typing import Optional


class ComController:
    """Manages COM port communication."""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize COM controller.
        
        Args:
            port: COM port name
            baudrate: Baud rate for communication
            timeout: Read/write timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
    
    def open(self) -> bool:
        """Open the COM port."""
        try:
            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )
            return True
        except Exception as exc:
            print(f"Failed to open {self.port}: {exc}")
            return False
    
    def close(self) -> None:
        """Close the COM port."""
        if self.serial:
            self.serial.close()
    
    def send(self, data: bytes) -> bool:
        """Send data over the COM port."""
        if not self.serial:
            return False
        try:
            self.serial.write(data)
            return True
        except Exception:
            return False
    
    def read(self, size: int = 1024) -> Optional[bytes]:
        """Read data from the COM port."""
        if not self.serial:
            return None
        try:
            return self.serial.read(size)
        except Exception:
            return None
    
    def is_open(self) -> bool:
        """Check if COM port is open."""
        return self.serial is not None and self.serial.is_open


if __name__ == "__main__":
    print("COM Controller module for serial communication control.")
