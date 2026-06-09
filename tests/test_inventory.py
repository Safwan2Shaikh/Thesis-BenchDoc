import sys
import os

# Add src folder to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from inventory_retriever import get_bench_info


queries = [
    "what devices are connected on 3WE",
    "show config for 483",
    "what is connected on 3VJ",
    "bench ABT-C-003WE"
]


def pretty_print(result):

    if not result:
        print("❌ No bench found")
        return

    print(f"""
✅ Bench Configuration: {result['bench']}

========================================

🔧 Samples
Sample 1:{result['sample1']}
Sample 2:{result['sample2']}
Sample 3:{result['sample3']}
========================================

⚙️ Devices
PSU:{result['psu']}
Vector Box 1:{result['vector1']}
Vector Box 2:{result['vector2']}
Relay Card:{result['relay']}
NetGear:{result['netgear']}
Lauterbach 1:{result['lauterbach1']}
Lauterbach 2:{result['lauterbach2']}
PDU:{result['pdu']}
========================================

🧩 Extras
""")
    for extra in result["extras"]:
        if extra not in ["No", "", "nan"]:
            print(f"- {extra}")

for q in queries:

    print("\n\n==================================================")
    print("QUERY:", q)
    print("==================================================")

    result = get_bench_info(q)

    pretty_print(result)