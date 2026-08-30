---
applyTo: "**/*.py"
---
# MARSEL ROAPP Python rules

- Use Python 3.12-compatible syntax unless the repository declares another target.
- Preserve existing canonical implementations; do not create duplicate versioned scripts without a documented reason.
- For live RO App integrations, default to READ-ONLY.
- Never guess API endpoints, identifiers, schemas, pagination or authentication behavior.
- Keep credentials in environment variables or protected secret storage; never hardcode them.
- Use explicit timeouts and bounded retries for network calls.
- Make retry behavior safe for idempotent operations; do not retry unknown WRITE operations automatically.
- Validate external JSON/data before use and produce actionable errors.
- Add or update tests for behavior changes and regression fixes.
- Run the repository's relevant tests, linters and type checks before declaring a change complete.
- Do not weaken production gates, security checks or test coverage merely to make CI pass.
