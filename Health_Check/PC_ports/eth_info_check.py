import psutil
import socket
import subprocess
import json


def get_gateway():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetRoute -DestinationPrefix 0.0.0.0/0 | ConvertTo-Json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout:
            data = json.loads(result.stdout)

            if isinstance(data, list):
                return data[0].get("NextHop", "Unknown")
            else:
                return data.get("NextHop", "Unknown")

    except Exception:
        pass

    return "Unknown"


gateway = get_gateway()

stats = psutil.net_if_stats()
addrs = psutil.net_if_addrs()

print("=" * 80)
print("NETWORK CONNECTIONS")
print("=" * 80)

for interface_name, addresses in addrs.items():

    print(f"\nAdapter Name : {interface_name}")

    if interface_name in stats:
        print(f"Status       : {'UP' if stats[interface_name].isup else 'DOWN'}")
        print(f"Speed        : {stats[interface_name].speed} Mbps")
        print(f"MTU          : {stats[interface_name].mtu}")

    ipv4 = "N/A"
    ipv6 = "N/A"
    mac = "N/A"

    for addr in addresses:

        if addr.family == socket.AF_INET:
            ipv4 = addr.address

        elif addr.family == socket.AF_INET6:
            ipv6 = addr.address

        elif str(addr.family) == "AddressFamily.AF_LINK":
            mac = addr.address

    print(f"IPv4 Address : {ipv4}")
    print(f"IPv6 Address : {ipv6}")
    print(f"MAC Address  : {mac}")
    print(f"Gateway      : {gateway}")

print("\n" + "=" * 80)