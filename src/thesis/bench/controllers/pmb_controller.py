import socket


DEFAULT_IP_ADDRESS = "192.168.0.123"
DEFAULT_PORT = 17123


def run_pmb_command(command: str, ip_address: str = DEFAULT_IP_ADDRESS, port: int = DEFAULT_PORT) -> bool:
    command_to_execute = command.replace("_", " ").strip()
    if not command_to_execute:
        return False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    errors = 0
    try:
        s.connect((ip_address, port))
        if command_to_execute == "all on":
            for idx in range(24):
                s.sendall(f"SR {idx + 1} on".encode())
        elif command_to_execute == "all off":
            for idx in range(24):
                s.sendall(f"SR {idx + 1} off".encode())
        else:
            s.sendall(command_to_execute.encode())
    except Exception:
        errors += 1
    finally:
        try:
            s.close()
        except Exception:
            pass

    return errors == 0
