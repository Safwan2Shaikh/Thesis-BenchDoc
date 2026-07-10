import requests
import time


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

    def _send_command(self, outlet, operation):

        params = {
            f"outlet{outlet - 1}": 1,
            "op": operation,
            "submit": "Apply"
        }

        r = self.session.get(
            f"{self.base_url}/control_outlet.htm",
            params=params,
            timeout=5
        )

        r.raise_for_status()

        return True

    def switch_on(self, outlet):

        return self._send_command(
            outlet,
            0
        )

    def switch_off(self, outlet):

        return self._send_command(
            outlet,
            1
        )

    def power_cycle(self, outlet):

        return self._send_command(
            outlet,
            2
        )


if __name__ == "__main__":

    pdu = ValuePDU()

    # Turn Outlet 1 OFF
    pdu.switch_off(1)

    time.sleep(5)

    # Turn Outlet 1 ON
    pdu.switch_on(1)

    print("Done")