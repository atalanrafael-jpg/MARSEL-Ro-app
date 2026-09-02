# MARSEL ROAPP — Canonical Secret Configuration

## Canonical secret

The canonical RO App API credential is stored as a GitHub Actions secret named `ROAPP_API_KEY`.

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Secret name: `ROAPP_API_KEY`
- API base: `https://api.roapp.io/v2`
- Authentication: Bearer token
- Default execution mode: READ_ONLY
- Production WRITE: disabled unless the separate production gates are explicitly satisfied.

## Runtime contract

The canonical workflow `.github/workflows/marsel-unified-control-plane.yml` reads only `${{ secrets.ROAPP_API_KEY }}`. The credential must never be committed to source, documentation, issues, pull requests, workflow YAML, artifacts, or chat.

The workflow performs a non-disclosing presence check before live READ_ONLY audits. It must fail closed if the secret is unavailable.

## One-time external action

GitHub does not expose repository Actions Secrets through the currently connected GitHub interface, so this repository cannot truthfully claim that the secret value has been installed from this tool. The value must be entered once in the repository's Actions Secrets under the exact name `ROAPP_API_KEY`.

After that one-time setup, the canonical workflow can consume it automatically; the secret value itself never needs to be shared with ChatGPT.

## Verification rule

A successful live run of `MARSEL Unified Control Plane` that passes the `Verify RO App secret` step is the authoritative runtime evidence that the secret is available. No secret value is logged or reproduced.

## Security rule

If a real credential has previously appeared in public source, issues, PRs, logs, or documentation, treat it as compromised and rotate/revoke it before installing the replacement. Never copy an exposed historical token into this configuration.
