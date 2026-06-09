import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from inventory_retriever import get_bench_info
from device_identifier import identify_devices


queries = [

    "target power fail during T32 attach on 3WE",

    "relay card not working on 3VJ",

    "PSU not connecting on ABT-C-003WE",

    "CAN communication fail on 483"
]


for q in queries:

    print("\n====================================================")
    print("QUERY:")
    print(q)

    bench = get_bench_info(q)

    if not bench:
        print("\n❌ Bench not found")
        continue

    result = identify_devices(q, bench)

    print(f"\n🏷️ Bench: {bench['bench']}")

    # ==========================================
    # QUERY DEVICE DETECTION
    # ==========================================

    if result["query_devices"]:

        print("\n🔍 Detected Issue Devices:")

        for dev in result["query_devices"]:

            print(f"- {dev}")

    else:

        print("\n⚠️ No explicit device detected from query")

    # ==========================================
    # VALID DEVICES
    # ==========================================

    if result["valid_devices"]:

        print("\n✅ Devices exist on this bench:")

        for dev in result["valid_devices"]:

            print(f"- {dev}")

    # ==========================================
    # INVALID DEVICES
    # ==========================================

    if result["invalid_devices"]:

        print("\n❌ Device mismatch detected:")

        for dev in result["invalid_devices"]:

            print(
                f"- {dev} is NOT available on bench {bench['bench']}"
            )

        print("\nPossible reasons:")
        print("- Wrong bench mentioned")
        print("- Outdated inventory")
        print("- External hardware connected manually")

    print("\n====================================================")