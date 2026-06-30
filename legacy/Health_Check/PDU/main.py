from topology import BenchTopology
from pdu_controller import PDUController
from pdu_service import PDUService


GRAPH_FILE = (
    "../../knowledgeBase/"
    "Bench_Config/"
    "47D_graph_trail.yaml"
)

PDU_EXE = (
    r"D:\tools\INT_8Port_PDU"
    r"\DCC-PDU_control_0.3.2"
    r"\dcc-pdu-terminal.exe"
)

PDU_CFG = (
    r"D:\tools\INT_8Port_PDU"
    r"\DCC-PDU_control_0.3.2"
    r"\PDU_VALUE_8-WAY.yaml"
)


topology = BenchTopology(GRAPH_FILE)

mapping = topology.get_pdu_mapping()

print(mapping)

controller = PDUController(
    exe_path=PDU_EXE,
    config_file=PDU_CFG
)

pdu = PDUService(
    controller,
    mapping
)

print("Available devices")

for device, socket in mapping.items():
    print(f"{device} -> Socket {socket}")

# Examples:

# pdu.power_off("pmb")
# pdu.power_on("pmb")
# pdu.power_cycle("lauterbach")