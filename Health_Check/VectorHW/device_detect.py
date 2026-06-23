import can

configs = can.detect_available_configs(interfaces=["vector"])

print(f"Found {len(configs)} device(s)")

for i, config in enumerate(configs):
    print(f"\nDevice {i + 1}")

    serial = config.get("serial")
    if serial is not None:
        print("Serial:", serial)
        print("Last 4 Digits:", str(serial)[-4:])

    channel_cfg = config.get("vector_channel_config")
    if channel_cfg:
        print("Name:", channel_cfg.name)