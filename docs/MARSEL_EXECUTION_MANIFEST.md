# MARSEL ROAPP — Execution Manifest

## Purpose
Canonical manifest for repeatable, limits-resilient execution without bypassing platform controls.

## Control plane
- Project: MARSEL ROAPP
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main`
- Default operating mode: `READ_ONLY`
- Production WRITE: disabled / fail-closed

## Execution layers
| Layer | Responsibility | Mutation policy | Evidence |
|---|---|---|---|
| ChatGPT | orchestration, planning, review | no implicit production WRITE | conversation/action record |
| GitHub Actions | deterministic tests, audits, scheduled checks | read-only unless an explicit gated workflow exists | workflow run + artifacts |
| Control Agent | inspect, analyze, verify, guarded repository assistance | repository WRITE requires explicit local gate; production WRITE permanently blocked | action output + tests |
| RO App integration | live business-system reads | GET/read-only for audits | direct API evidence |

## Credential policy
- Secrets remain outside Git-tracked files.
- Canonical RO App secret name: `ROAPP_API_KEY`.
- Credentials must not appear in issues, PRs, logs, or artifacts.
- Account-level secret scanning/push protection remains an external GitHub setting and is not inferred from repository files.

## Reliability policy
- Use bounded retries/backoff for rate-limited automation.
- Do not bypass, evade, or parallelize around platform limits.
- Separate read-only audit jobs from mutation-capable jobs.
- Prefer idempotent operations and deterministic evidence.
- Stop on conflicting or missing evidence.

## Evidence policy
A CI success proves only the CI assertion it executed. It does not prove live RO App authorization, Gmail OAuth, backup/restore integrity, production readiness, or account-level GitHub settings.

## Production gate
`MARSEL_WRITE_APPROVED` remains `false` until all required production gates have fresh direct evidence and explicit authorization.

## Maintenance
Update this manifest when execution layers, credential scope, retry policy, or evidence locations materially change.
