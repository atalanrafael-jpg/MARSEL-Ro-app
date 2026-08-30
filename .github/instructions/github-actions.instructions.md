---
applyTo: ".github/workflows/**/*.yml,.github/workflows/**/*.yaml"
---
# MARSEL ROAPP GitHub Actions rules

- Treat workflows as production infrastructure.
- Use least-privilege `permissions`; default to read-only and grant only required write permissions.
- Pin third-party actions to immutable commit SHAs where practical.
- Never print secrets or sensitive response bodies to logs.
- Do not expose production secrets to pull requests from untrusted forks.
- Keep production and destructive operations behind explicit gates and protected environments.
- Preserve READ-ONLY behavior of audit workflows.
- Use bounded timeouts and avoid unbounded retry loops.
- Upload only non-sensitive audit evidence as artifacts.
- Do not disable CodeQL, secret scanning, production gates or required tests to make a workflow green.
- After workflow changes, validate YAML syntax and inspect the resulting Actions run.
