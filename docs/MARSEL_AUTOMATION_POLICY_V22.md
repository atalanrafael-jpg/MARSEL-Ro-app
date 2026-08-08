# MARSEL — Automation Policy V22

## Purpose

Keep the RO App API audit continuously verifiable without permitting production writes.

## Safety contract

- Automated API audit requests are GET-only.
- POST, PUT, PATCH and DELETE are prohibited by the audit workflow.
- Parameterized API paths are never probed with guessed identifiers.
- A successful audit does not imply complete API coverage; completeness remains unestablished until every relevant documented operation has explicit evidence.
- Production RO App data must not be mutated by the read-only audit pipeline.

## Automation

The API inventory/live-probe workflow is executed on relevant repository changes and on a scheduled basis. Each run must publish machine-readable evidence and SHA-256 hashes when the configured API credential is available.

## Escalation

If the audit fails, the failure is treated as an engineering defect to investigate. No automatic write or corrective mutation of RO App production data is permitted as a recovery action.
