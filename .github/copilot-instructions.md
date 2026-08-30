# MARSEL ROAPP — GitHub Copilot Instructions

## Project identity
- The canonical project name is **MARSEL ROAPP**.
- `MARSEL` is the business contour; `ROAPP` is the technical contour.
- Preserve the historical repository name `Ro-app`; do not rename it automatically.
- The product context is a jewelry/watch studio business system. It must also support jewelry repair, watch repair, and glasses repair where those capabilities already exist or are being added.

## Working rules
- Work from the existing repository architecture. Do not rewrite or replace working subsystems without evidence that the change is required.
- Before changing code, inspect the relevant files, tests, workflows, configuration, and API contracts.
- Do not invent APIs, environment variables, database fields, endpoints, business rules, or external service behavior. Verify them in repository documentation or authoritative vendor documentation.
- Preserve backward compatibility unless a breaking change is explicitly required and documented.
- Prefer small, reviewable changes with clear commit/PR scope.
- Never commit secrets, tokens, passwords, private keys, credentials, or real customer personal data.
- Do not disable security controls, CI gates, validation, tests, or branch protections merely to make a build pass.

## Quality gate
Every code change should be validated with the strongest relevant checks available in the repository:
1. formatting/linting;
2. type/static checks;
3. unit/integration tests;
4. build/package checks;
5. GitHub Actions/CI checks when applicable.

If a check cannot be run, state exactly which check was not run and why. Do not claim success without evidence.

## Error correction
- When a failure is found, identify the root cause before applying a fix.
- Fix the underlying defect rather than masking symptoms.
- After a fix, rerun the relevant failing check and verify that previously passing behavior remains intact.
- Avoid speculative changes unrelated to the task.

## GitHub Actions and CI
- Treat CI as a production gate.
- Do not weaken workflow permissions, remove validation steps, or bypass failing jobs unless the repository's documented requirements explicitly call for it.
- Keep workflow changes minimal and validate YAML/configuration syntax where practical.
- Do not add broad write permissions when read-only permissions are sufficient.

## API and integration rules
- Treat existing API contracts and vendor documentation as authoritative.
- Validate request/response shapes before changing integrations.
- Handle authentication, rate limits, retries, timeouts, validation errors, and external-service failures explicitly where relevant.
- Never hard-code production credentials or identifiers.

## Data and business integrity
- Preserve inventory, pricing, cost, order, repair, and catalog data integrity.
- Where cost accounting is involved, preserve separate metal and stone cost information when the existing data model supports it.
- Avoid destructive migrations or data deletion without an explicit migration/rollback strategy.

## Testing expectations
- Add or update tests for changed behavior whenever the repository's test architecture supports it.
- Include regression coverage for bugs that are fixed.
- Prefer deterministic tests and avoid dependence on live external services unless the existing integration-test architecture explicitly requires it.

## Documentation
- Update relevant project documentation when behavior, configuration, API contracts, workflows, or operational procedures change.
- Keep documentation factual and synchronized with the implementation.

## Final response for coding tasks
Report:
- what changed;
- files changed;
- validation performed and exact results;
- known limitations or checks not run.
Never report an unverified task as complete.
