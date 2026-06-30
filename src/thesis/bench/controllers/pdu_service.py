import time


class PDUService:

    def __init__(
        self,
        controller,
        mapping
    ):
        self.controller = controller
        self.mapping = mapping

    def power_on(self, device_name):

        socket_num = self.mapping[device_name.lower()]

        return self.controller.socket_on(socket_num)

    def power_off(self, device_name):

        socket_num = self.mapping[device_name.lower()]

        return self.controller.socket_off(socket_num)

    def power_cycle(
        self,
        device_name,
        wait_time=10
    ):
        socket_num = self.mapping[device_name.lower()]

        self.controller.socket_off(socket_num)

        time.sleep(wait_time)

        self.controller.socket_on(socket_num)
