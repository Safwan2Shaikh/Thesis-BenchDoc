"""
topology.py

PDU topology and wiring configuration.
Maps physical PDU ports to bench devices and power rails.
"""


class PDUTopology:
    """Manages PDU port to device mapping."""
    
    def __init__(self):
        """Initialize PDU topology."""
        self.port_mapping = {}
    
    def add_port_mapping(self, port: int, device_name: str, rail: str = "main"):
        """
        Map a PDU port to a device.
        
        Args:
            port: PDU port number
            device_name: Name of connected device
            rail: Power rail identifier
        """
        self.port_mapping[port] = {
            "device": device_name,
            "rail": rail,
        }
    
    def get_device_ports(self, device_name: str) -> list:
        """Get PDU ports connected to a specific device."""
        return [
            port
            for port, info in self.port_mapping.items()
            if info["device"] == device_name
        ]
    
    def load_from_config(self, config_file: str):
        """Load topology from YAML configuration file."""
        import yaml
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'port_mapping' in config:
                    self.port_mapping = config['port_mapping']
        except Exception:
            pass


if __name__ == "__main__":
    topology = PDUTopology()
    topology.add_port_mapping(1, "PSU", "main")
    topology.add_port_mapping(2, "PDU", "main")
    print(f"Topology initialized with {len(topology.port_mapping)} port mappings.")
