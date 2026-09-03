# MARSEL ROAPP — Repository Link Registry

**Registry date:** 2026-09-02  
**Canonical repository:** `atalanrafael-jpg/MARSEL-Ro-app`  
**Canonical branch:** `main`  
**Policy:** links describe repository roles and permitted relationships; they do not imply live credentials, OAuth, MCP authorization, production access, or synchronization.

## 1. Canonical repository

| Repository | Role | Relationship | Status |
|---|---|---|---|
| `atalanrafael-jpg/MARSEL-Ro-app` | MARSEL ROAPP control plane, application, audit, CI/CD | Canonical source of truth | CONNECTED |

## 2. Confirmed supporting repositories in the same GitHub account

These repositories were independently observed in the account inventory and are classified here by intended technical role. No cross-repository runtime connection is claimed unless separately evidenced.

| Repository | Intended role | MARSEL ROAPP status | Required next evidence |
|---|---|---|---|
| `atalanrafael-jpg/codex` | Codex/tooling source | REFERENCE_ONLY | Explicit dependency or workflow reference |
| `atalanrafael-jpg/openai-agents-python` | Agent runtime/reference | REFERENCE_ONLY | Explicit dependency or deployment reference |
| `atalanrafael-jpg/openai-agents-js` | Agent runtime/reference | REFERENCE_ONLY | Explicit dependency or deployment reference |
| `atalanrafael-jpg/zapier-mcp` | MCP/integration tooling | CANDIDATE | Explicit MARSEL workflow + authorized MCP connection |
| `atalanrafael-jpg/n8n` | Workflow automation | CANDIDATE | Explicit MARSEL workflow + deployment/runtime evidence |
| `atalanrafael-jpg/chrome-devtools-mcp` | Browser diagnostics/testing | CANDIDATE | Explicit CI/test integration reference |
| `atalanrafael-jpg/smartbear-mcp` | Testing/API tooling | CANDIDATE | Explicit CI/test integration reference |
| `atalanrafael-jpg/WhatsApp-Business-API-Setup-Scripts` | WhatsApp integration tooling | LEGACY_REFERENCE | Current Cloud API implementation and MARSEL use case must be verified |
| `atalanrafael-jpg/ROAPP_API_KEY` | Credential/security-related repository | SECURITY_REVIEW_ONLY | Exposure/remediation evidence; never copy credentials into MARSEL ROAPP |

## 3. Integration boundary

The canonical MARSEL ROAPP repository remains the only project source of truth. Supporting repositories may provide tooling or implementation references, but they must not silently become alternate control planes.

Permitted relationship states:

- `CANONICAL` — project source of truth.
- `CONNECTED` — an explicit, currently evidenced runtime/build relationship exists.
- `REFERENCE_ONLY` — useful repository, but no runtime dependency is established.
- `CANDIDATE` — possible integration, pending explicit design and verification.
- `LEGACY_REFERENCE` — historical/legacy material; cannot be used as current integration evidence.
- `SECURITY_REVIEW_ONLY` — must be handled only through security controls; never treated as an application dependency.

## 4. Safety rules

1. Do not add cross-repository secrets, tokens, or credentials to source files.
2. Do not claim a runtime integration from repository ownership or repository names alone.
3. Do not make a supporting repository a second MARSEL control plane.
4. All production RO App operations remain READ-ONLY until the canonical production gates pass.
5. Any future cross-repository automation must be explicit, least-privilege, auditable, and fail-closed.

## 5. Current conclusion

Repository relationships are now classified centrally. No unverified supporting repository is promoted to `CONNECTED`. The next unfinished project item remains the fresh/current evidence chain and external production gates, not another duplicate integration declaration.
