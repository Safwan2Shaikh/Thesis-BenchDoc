# Vector Serial Number Invalid

## Symptom

OpenPort fails during startup.

## Error

Serial Number is not valid.
Please check Vector Hardware Config.

OpenPort has failed.

## Impact

CAN communication cannot start.

## Root Cause Candidates

- Wrong Vector Hardware Configuration
- Wrong device connected
- Hardware replaced
- Serial number mismatch
- Invalid channel mapping

## Recommended Actions

1. Open Vector Hardware Config
2. Check configured serial number
3. Verify connected VN5650 device
4. Reassign channels
5. Restart Vector services

## Component

VN5650