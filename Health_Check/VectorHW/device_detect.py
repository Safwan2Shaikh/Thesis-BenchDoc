import can

configs = can.detect_available_configs(interfaces=["vector"])

if configs:
    config = configs[0]

    serial = config.get("serial")
    if serial is not None:
        print(f"Serial Number: {serial:06d}")
        print(type(serial))
        print("Last 4 Digit Serial:", str(serial)[-4:])

    channel_cfg = config.get("vector_channel_config")
    if channel_cfg:
        print("Device Name:", channel_cfg.name[:6])
else:
    print("No Vector device found")