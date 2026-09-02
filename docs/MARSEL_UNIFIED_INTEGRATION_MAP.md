# MARSEL ROAPP — Unified Integration Map

## Canonical contour

MARSEL ROAPP is one system:

`Ювелирная студия MARSEL → MARSEL business contour → ROAPP technical contour → GitHub main → Unified Control Plane → evidence/gates`

## Canonical sources

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Control workflow: `.github/workflows/marsel-unified-control-plane.yml`
- Project control: `docs/PROJECT_MASTER_CONTROL.md`
- Secret contract: `docs/MARSEL_SECRET_CONFIGURATION.md`
- API base: `https://api.roapp.io/v2`

## Runtime chain

1. GitHub Actions starts the canonical control workflow.
2. `ROAPP_API_KEY` is read only from GitHub Actions Secrets.
3. Secret presence is checked without disclosure.
4. RO App operations run READ_ONLY by default.
5. Results are converted into timestamped evidence/artifacts.
6. Evidence is evaluated against project gates.
7. Missing/conflicting evidence produces `REVIEW_REQUIRED`.
8. Production WRITE remains disabled until every required production gate has direct evidence and explicit authorization.

## Source-of-truth order

1. Current `main`.
2. Current Actions evidence tied to `main`.
3. Direct RO App API evidence.
4. Current official RO App documentation.
5. Historical Library/project material as context only.

## Library integration

Library documents are treated as project knowledge, not as a second source of operational truth. Canonical documents are mapped into the repository/control plane; historical and duplicate material remains archival and cannot override fresh `main` or live evidence.

## Credential rule

The API credential is never copied into source, issues, PRs, documentation, artifacts, or chat. The only canonical runtime secret name is `ROAPP_API_KEY`.

## Safety

No guessed endpoint or identifier. No automatic deletion. No production mutation merely to make CI green. No `PASS` without direct current evidence.
