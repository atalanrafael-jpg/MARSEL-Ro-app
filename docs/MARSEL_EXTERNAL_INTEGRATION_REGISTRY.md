# MARSEL ROAPP — External Integration Registry

## Purpose

Single registry for external systems, accounts, connectors, applications, servers, domains, search/discovery services, maps, social profiles, and automation dependencies related to MARSEL ROAPP.

This registry is a **control plane**, not a claim that every integration is connected. A row is `VERIFIED` only when current direct evidence exists.

## Status vocabulary

- `VERIFIED` — current direct evidence proves access/configuration.
- `PARTIAL` — some components are verified; important scope remains open.
- `BLOCKED` — required external action/permission is missing.
- `NOT_VERIFIED` — no current direct evidence.
- `PROPOSED` — design only; not connected.

## Canonical systems

| Domain | System | Role | Status | Evidence / owner action |
|---|---|---|---|---|
| Source | GitHub | Canonical source repository | VERIFIED | `atalanrafael-jpg/MARSEL-Ro-app`, `main` |
| ERP | RO App | Operational system/API | PARTIAL | API read-only evidence exists; completeness/warehouse/restore gates remain open |
| AI | ChatGPT | AI control/analysis surface | PARTIAL | App/MCP capabilities exist, but RO App MCP authorization is not independently verified |
| AI/Dev | Codex | Development/automation surface | NOT_VERIFIED | Account/session capability must be verified separately |
| AI/Dev | GitHub Copilot | Code/agent assistance | NOT_VERIFIED | Account-level Copilot configuration must be verified |
| Docs | ReadMe | RO App API documentation | BLOCKED | GitHub ↔ ReadMe synchronization requires external ReadMe configuration |
| Email | Gmail | Operational communication | BLOCKED | OAuth requires user-authorized live verification |
| Web | MARSEL website / domains | Public web presence | NOT_VERIFIED | Domain/site inventory and ownership must be verified |
| Social | MARSEL social profiles | Social commerce / reputation | NOT_VERIFIED | Each profile must be verified from the authoritative account |
| Maps | Map services / business listings | NAP/location discovery | NOT_VERIFIED | Each listing must be verified from authoritative provider data |
| Search | Search engines / webmaster tools | Indexing/discovery | NOT_VERIFIED | Provider accounts and ownership must be verified |
| Analytics | Web analytics / attribution | KPI and conversion measurement | NOT_VERIFIED | Account/property IDs and access must be verified |
| Cloud | Vercel / Cloudflare / hosting | Runtime/deployment | NOT_VERIFIED | Live project/account linkage must be verified |
| Data | Supabase/PostgreSQL | Application data layer | NOT_VERIFIED | Connection and environment must be verified |
| Ads | OpenAI Ads / other ad systems | Marketing measurement | NOT_VERIFIED | IDs, permissions and live event delivery must be verified |

## Security rules

1. Never store API keys, OAuth tokens, passwords, cookies, recovery codes, or private credentials in this registry.
2. Store only secret **names/references** such as `ROAPP_API_KEY`, never secret values.
3. External account identifiers are included only when non-sensitive and directly verified.
4. Personal geolocation is never stored here unless explicitly required, authorized, and necessary for a documented business function.
5. A link alone does not prove authentication, ownership, synchronization, or write capability.

## Synchronization model

Every integration must follow:

`SOURCE → AUTH → MAPPING → TRANSFORMATION → VALIDATION → DESTINATION → RECONCILIATION → VERIFY → EVIDENCE`

For read-only discovery:

`DISCOVER → READ → NORMALIZE → DIFF → REPORT`

No production write is implied by this registry.

## Evidence rule

Fresh direct evidence from the current system takes precedence over historical documents. Historical project files are context only. `PASS`/`VERIFIED` is forbidden without evidence.

## Required next verification gates

1. Verify current GitHub account/repository security controls and branch protection.
2. Verify RO App current live GET coverage and official endpoint contracts.
3. Complete permitted backup/export and independent restore/integrity test.
4. Verify RO App MCP authorization from the actual ChatGPT/Codex environment.
5. Verify Gmail OAuth only after user authorization.
6. Verify ReadMe synchronization externally.
7. Build authoritative MARSEL website/social/maps/search/analytics inventory without collecting unnecessary personal data.
8. Verify Vercel/Cloudflare/Supabase or other runtime services only if they are actually used by the current application.
9. Reconcile all verified integrations into this registry and the project master control.

## Source of truth

The canonical technical source remains `main` in `atalanrafael-jpg/MARSEL-Ro-app`. This registry does not override `docs/PROJECT_MASTER_CONTROL.md` or current live evidence.
