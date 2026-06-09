import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from inventory_retriever import get_bench_info
from device_identifier import identify_devices
from diagnostic_engine import run_diagnostic


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

        print("❌ No bench found")
        continue

    device_result = identify_devices(q, bench)

    print(f"\n🏷️ Bench: {bench['bench']}")

    print("\n🤖 Diagnostic Result:\n")

    result = run_diagnostic(
        q,
        bench,
        device_result
    )

    print(result)

    print("\n====================================================")