---
applyTo: ".github/workflows/**/*.yml,.github/workflows/**/*.yaml"
---
# MARSEL ROAPP GitHub Actions rules

- Treat workflow changes as production-sensitive.
- Follow least privilege: start with read-only permissions and grant only documented permissions required by a job.
- Never expose secrets in logs, artifacts, outputs, cache keys, or committed files.
- Do not use secrets in untrusted pull-request contexts.
- Pin action references according to the repository's existing security policy; do not silently weaken supply-chain controls.
- Keep live RO App operations READ-ONLY unless a documented production gate explicitly authorizes WRITE.
- Before changing a workflow, inspect triggers, permissions, secrets, artifacts, retention, concurrency, and downstream effects.
- Preserve evidence for audits without storing credentials or personal data.
- Add timeouts and bounded retries where appropriate; do not loop indefinitely.
- A successful workflow is evidence only for checks actually executed. Do not treat CI success as proof of production data correctness.
- After workflow changes, validate YAML and inspect the resulting run status and logs before declaring success.
- Never bypass failing checks by disabling jobs, changing exit codes, or weakening assertions unless the requirement itself is intentionally changed and documented.
