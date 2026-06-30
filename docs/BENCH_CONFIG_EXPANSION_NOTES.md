# Bench Config Expansion Notes

## Current Bench Config Layout

Each bench now has its own folder under `data/knowledge_base/Bench_Config/`:

- `ABT-C-0047D/`
- `ABT-C-003WE/`
- `RNG-C-0050F/`

Each folder contains:

- `trail.yaml` for bench/device inventory and physical roles.
- `graph_trail.yaml` for node/edge connectivity.
- `troubleshooting_trail.yaml` for dependencies, failure modes, and diagnostic rules.

## Comments Converted Into YAML Fields

The useful comments in the new files were converted into structured fields so retrievers and the LLM can read them:

- `status: missing_on_current_bench` for 3WE ECU2 paths that are expected but not physically present.
- `expected_device: ecu_2` for PMB ports where an ECU is expected.
- `status: expected_but_not_connected` for configured-but-missing ECU entries.
- `status: needs_verification` where the PDU/port mapping needs bench-side confirmation.
- `note:` fields for details such as ECU COM2 usage, RT rack participation, and IP-based PSU control.

## Information Still Required

### ABT-C-003WE

- Confirm whether `ecu_2` should remain modeled as expected-but-missing, or should be removed from active diagnostic paths.
- Confirm whether `pmb.port_4`, `vn5650.can14`, and `vn5650.eth2` are truly absent or only temporarily disconnected.
- Confirm the exact VX1161/POD naming used on the bench, including whether there are separate `pod_1` and `pod_2` devices.
- Add serial numbers or hardware IDs for `vn5650`, `vx1161`, PSU, PMB, PDU, and netgear switch if available.
- Add IP addresses for PC, PMB, VX1161, PDU, RT rack, and netgear switch if diagnosis should reason about network failures.

### RNG-C-0050F

- Confirm the official bench name. The folder and YAML currently use `RNG-C-0050F`; update this if the official naming is `RNG-C0050F`.
- Add the bench IP address to `Bench_mapping.csv` when known.
- Confirm `pdu.port_3 -> pmb`; it is marked `needs_verification` because the original comment asked to check the existing physical mapping.
- Confirm whether `pmb.port_4` really expects `ecu_2`; the original comment may have been copied from another bench.
- Add exact Lauterbach model, serial number, interface type, and IP/USB connection details.
- Add ECU sample type/version and whether the ECU is powered only through `psu.channel_2`.
- Add any Vector/VN hardware if this bench uses CAN/Ethernet measurement in addition to Lauterbach debugging.

### ABT-C-0047D

- Existing config is structurally complete, but it would benefit from serial numbers, IP addresses, and explicit Trace32 device IDs.
- If multiple Lauterbach devices are present, add separate device entries and debug paths per ECU.

## Recommended YAML Pattern

Use structured fields instead of comments whenever the information should affect retrieval:

```yaml
port_4:
  connected_device: null
  expected_device: ecu_2
  status: missing_on_current_bench
  note: ECU2 harness expected here, but not installed on the current bench.
```

This keeps the YAML human-readable while making the information available to the retrievers and diagnostic trace.