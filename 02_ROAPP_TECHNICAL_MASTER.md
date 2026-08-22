# 02_ROAPP_TECHNICAL_MASTER

**Purpose:** canonical technical layer: API, data contract, integrations, development, security and production gates.

## 1. Current repository control
- Repository: `atalanrafael-jpg/Ro-app`
- Canonical branch: `main`
- At creation checkpoint, main commit: `4e5e37104389817d6fdad95bfdfa6aac9cb4c0b2`.
- Current architecture already contains a Unified Control Plane; this document does not create a parallel architecture.

## 2. API contract policy
Only evidence from official documentation or successful live requests may be marked VERIFIED.
For every endpoint record: method, path, auth, parameters, pagination, schema, errors, rate/limits, version, evidence date.

### Verified live evidence currently available
- RO App API base used by project: `https://api.roapp.io/v2`.
- Bearer authentication is used by the project.
- `GET /orders` has been live-tested successfully with HTTP 200 in READ-ONLY mode.
- A historical live audit verified 4,373 orders, 4,373 unique IDs, zero duplicate IDs, zero missing IDs, zero missing client IDs and zero missing statuses; this is evidence for that audit run, not a perpetual current database count.
- A deeper READ-ONLY detail audit recorded 6,820 successful detail requests and `DETAIL_FAILURES=0`.

### Not verified / blocked
- Full API completeness is not proven.
- Warehouse live contract is NOT VERIFIED.
- Full backup/restore readiness is NOT VERIFIED.
- Two entity checks remain blocked in the latest documented audit state.
- Eleven product-code collision groups require classification; no automatic deletion is permitted.

## 3. MCP
- MCP integration exists in the repository and has had CI validation documented.
- Production WRITE remains blocked by safety policy until authorization, backup/restore and production gates are proven.
- Never place secrets in code, documentation, logs or artifacts.

## 4. Integration map
For each integration maintain:
`SYSTEM / PURPOSE / SOURCE / DESTINATION / AUTH / PERMISSIONS / FIELDS / MAPPING / TRIGGER / FREQUENCY / ERROR HANDLING / LOGGING / ROLLBACK / STATUS`

Systems:
- RO APP API
- RO APP MCP
- GitHub
- Gmail
- Google Workspace
- Website
- E-commerce
- Social networks
- Marketplaces
- Payments
- Analytics
- Accounting/tax

No integration is considered connected without live verification.

## 5. Development standard
- Python/API code must use explicit timeouts, bounded retries, structured logging and pagination.
- Read operations default to READ-ONLY.
- Mutating operations require idempotency where applicable, dry-run, explicit safety gate, backup/restore evidence and post-write verification.
- CI success does not equal production success.
- Secrets must come from secure secret storage.
- Changes must be reviewable and reversible.

## 6. Production gate
Required sequence:
`READ -> ANALYZE -> BACKUP -> RESTORE CHECK -> DRY-RUN -> WRITE -> VERIFY`

Before WRITE:
- endpoint contract VERIFIED;
- authorization VERIFIED;
- backup completed and independently restorable;
- expected affected IDs known;
- dry-run clean;
- rollback path proven;
- scope limited.

After WRITE:
`BEFORE -> ACTION -> AFTER -> DIFF -> INTEGRITY -> QA -> EVIDENCE`

## 7. Security
- No credentials in Git.
- No API keys in logs.
- Least privilege.
- READ and WRITE paths separated.
- Do not expose personal data unnecessarily.
- Do not infer authorization from a successful CI job.

## 8. Canonical technical documents
This master subsumes the intended roles of:
- `ROAPP_API_CONTRACT.md`
- `ROAPP_DATA_DICTIONARY.md` (technical portions)
- `MARSEL_BACKUP_RESTORE.md`
- `MARSEL_PRODUCTION_GATES.md`
- `MARSEL_INTEGRATION_MAP.md`
- `MARSEL_DEVELOPMENT_STANDARD.md`
- `MARSEL_AUTOMATION_CATALOG.md`

If individual files are later added, they must reference this master and must not contradict it.