import can

configs = can.detect_available_configs(interfaces=["vector"])

if not configs:
    print("No Vector devices found")
    exit()

print(f"Found {len(configs)} channel configuration(s)\n")

for idx, config in enumerate(configs, start=1):
    print("=" * 80)
    print(f"Configuration {idx}")
    print("=" * 80)

    for key, value in config.items():

        if key != "vector_channel_config":
            print(f"{key}: {value}")

    channel_cfg = config.get("vector_channel_config")

    if channel_cfg:
        print("\n--- Vector Channel Details ---")

        for attr in dir(channel_cfg):

            if attr.startswith("_"):
                continue

            try:
                value = getattr(channel_cfg, attr)

                if callable(value):
                    continue

                print(f"{attr}: {value}")

            except Exception:
                pass

        print()