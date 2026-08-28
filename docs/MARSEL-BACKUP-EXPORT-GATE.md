# MARSEL Backup Export Gate

## Purpose

Create a verifiable, read-only snapshot of explicitly configured RO App API
collections before any production write is considered.

## Safety contract

- The exporter issues GET requests only.
- API credentials are read from `ROAPP_API_TOKEN` and must never be written to
  snapshots, logs, evidence or repository files.
- The endpoint inventory is supplied at runtime through
  `MARSEL_BACKUP_ENDPOINTS_JSON`; repository code does not invent API paths.
- Every exported entity is canonicalized and SHA-256 hashed.
- The manifest records `readonly=true` and `write_requests_made=0`.
- A failed endpoint fails the complete export; partial output is not evidence.

## Evidence rule

`backup_evidence.json` may be produced only after:

1. the permitted endpoint inventory is reviewed against current RO App API
   documentation and the connected account permissions;
2. every planned endpoint returns successfully;
3. manifest hashes are recomputed and match;
4. secret scanning of the artifact passes;
5. the resulting snapshot is retained as an auditable CI artifact.

The exporter itself does not claim that all writable entities have been backed
up. Completeness is established by the approved runtime endpoint inventory.
