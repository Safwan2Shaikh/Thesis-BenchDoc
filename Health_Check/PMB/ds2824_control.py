"""
ds2824_control.py

Controls and monitors the DS2824 PMB (Power Management Board) module.
Handles relay control and voltage monitoring.
"""

import socket
import sys
import time


def execute_command(command_to_execute):
    """
    Execute a DS2824 command.

    Args:
        command_to_execute (str): Command to send, e.g.
                                  "SR 1 on"
                                  "SR 1 off"
                                  "all off"
                                  "all on"

    Returns:
        int: Return code (0 = success, >0 = error)
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    IP_ADDRESS = "192.168.0.123"
    PORT = 17123
    cnt = 0

    if command_to_execute != "":
        try:
            print("Connecting")
            s.connect((IP_ADDRESS, PORT))
        except:
            print("can not connect")
            cnt = cnt + 1

        try:
            if command_to_execute.find("all on") >= 0:
                for el in range(24):
                    str_to_send = "SR " + str(el + 1) + " on"
                    s.sendall(str_to_send.encode())
                    time.sleep(0.01)

            else:
                if command_to_execute == "all off":
                    for el in range(24):
                        str_to_send = "SR " + str(el + 1) + " off"
                        iRet = s.sendall(str_to_send.encode())
                        print(iRet)
                        time.sleep(0.01)

                else:
                    s.sendall(command_to_execute.encode())

        except:
            print("can not send on TCP")
            cnt = cnt + 1

        try:
            s.close()
        except:
            pass

        if cnt == 0:
            print("Successfully Done")

        print("Return Code = ", cnt)

    return cnt


def main():
    if len(sys.argv) > 1:
        command_to_execute = str(sys.argv[1])

        print("command_to_execute (raw) = ", command_to_execute)

        command_to_execute = command_to_execute.replace("_", " ")

        print("command_to_execute = ", command_to_execute)

        return execute_command(command_to_execute)

    else:
        print("!!!MISSING ARGUMENTS like <SR_1_on>")


if __name__ == "__main__":
    print("Number of arguments:", len(sys.argv), "arguments.")
    print("Argument List:", str(sys.argv))

    main()