# KMS Authorization Failure

## Error

HTTP 401 Unauthorized

You are not authorized to access the KMS backend.

## Evidence

CBDP Client Authentication is valid.

Error CBDP Client Response:
401 unauthorized

## Interpretation

Authentication succeeded.

Authorization failed.

Failure occurred after communication with ECU.

## Root Cause Candidates

- Missing KMS role
- Missing permissions
- Invalid authorization mapping
- Backend policy restriction
- Wrong user profile

## Recommended Actions

1. Verify KMS role assignment
2. Verify authorization profile
3. Verify certificate mapping
4. Verify backend permissions
5. Contact KMS administrator