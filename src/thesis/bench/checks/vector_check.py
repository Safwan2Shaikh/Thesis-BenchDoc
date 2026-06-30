configs = []


def detect_vector_devices():
    global configs

    try:
        import can
    except Exception as exc:
        configs = []
        return {
            "status": "WARNING",
            "error": f"python-can unavailable: {exc}",
            "devices": [],
            "count": 0,
        }

    try:
        configs = can.detect_available_configs(interfaces=["vector"])
    except Exception as exc:
        configs = []
        return {
            "status": "WARNING",
            "error": str(exc),
            "devices": [],
            "count": 0,
        }

    devices = []

    print(f"Found {len(configs)} device(s)")

    for i, config in enumerate(configs):
        print(f"\nDevice {i + 1}")

        serial = config.get("serial")
        if serial is not None:
            print("Serial:", serial)
            print("Last 4 Digits:", str(serial)[-4:])

        channel_cfg = config.get("vector_channel_config")
        channel_name = getattr(channel_cfg, "name", None) if channel_cfg else None
        if channel_name:
            print("Name:", channel_name)

        devices.append(
            {
                "serial": serial,
                "last_4_digits": str(serial)[-4:] if serial is not None else None,
                "channel": channel_name,
            }
        )

    return {
        "status": "OK",
        "count": len(devices),
        "devices": devices,
    }


def main():
    result = detect_vector_devices()
    if result.get("error"):
        print(result["error"])


if __name__ == "__main__":
    main()
