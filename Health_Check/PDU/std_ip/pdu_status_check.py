import requests
import xml.etree.ElementTree as ET
from datetime import datetime


class ValuePDU:

    def __init__(
        self,
        ip="192.168.0.22",
        username="admin",
        password="admin"
    ):

        self.base_url = f"http://{ip}"

        self.session = requests.Session()
        self.session.trust_env = False
        self.session.auth = (username, password)

    def get_status(self):

        r = self.session.get(
            f"{self.base_url}/status.xml",
            timeout=5
        )

        r.raise_for_status()

        root = ET.fromstring(r.text)

        info = {
            "timestamp": datetime.now().isoformat(),
            "current_A": float(root.find("curBan").text),
            "temperature_C": int(root.find("tempBan").text),
            "humidity_percent": int(root.find("humBan").text),
            "overall_status": root.find("statBan").text,
            "outlets": {}
        }

        for i in range(8):
            info["outlets"][f"OUTLET_{i+1}"] = (
                root.find(f"outletStat{i}").text
            )

        return info

    def ping(self):
        try:
            r = self.session.get(
                f"{self.base_url}/status.xml",
                timeout=3
            )
            return r.status_code == 200

        except Exception:
            return False


if __name__ == "__main__":

    pdu = ValuePDU()

    print("=" * 60)

    print("PDU Reachable:", pdu.ping())

    print("=" * 60)

    status = pdu.get_status()

    for key, value in status.items():
        print(key, ":", value)