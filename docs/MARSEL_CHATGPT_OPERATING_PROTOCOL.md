# MARSEL ROAPP — WORKING WITH CHATGPT

## 1. Operating principle

ChatGPT is the control/orchestration interface for MARSEL ROAPP. The repository is the canonical technical source of truth; ChatGPT must read current canonical state before changing it.

Canonical:
- System: MARSEL ROAPP
- Repository: atalanrafael-jpg/MARSEL-Ro-app
- Technical canonical branch: main
- Legacy/default branch: main-MARSEL-ROAPP until GitHub administration changes the default
- Production WRITE: disabled

## 2. Correct request pattern

Short commands are acceptable when the task is already established:
- "Действуй" — continue from the current canonical checkpoint.
- "Проверь" — inspect current state and evidence.
- "Исправь" — fix safe defects, then verify.
- "Закрой" — close only tasks whose acceptance criteria are directly satisfied.
- "Далее" — continue to the next safe highest-priority task.

For new work, specify:
1. OBJECTIVE — desired outcome.
2. SCOPE — MARSEL ROAPP, GitHub, RO App, deployment, data, etc.
3. AUTHORITY — READ-ONLY or explicitly authorized WRITE.
4. ACCEPTANCE — what proves completion.

Example:
"MARSEL ROAPP. Проверь текущий main, найди следующий безопасный блокер, исправь всё доступное без моего участия, перепроверь и закрой подтверждённые задачи."

## 3. Mandatory ChatGPT execution loop

READ CURRENT STATE
→ CHECK EVIDENCE/FRESHNESS
→ IDENTIFY HIGHEST-PRIORITY SAFE TASK
→ ACT
→ READ BACK
→ TEST
→ VERIFY
→ RECORD EVIDENCE
→ UPDATE CANONICAL STATE
→ CONTINUE

Never restart from historical branches, old chats, old checkpoints or closed tasks unless the current evidence explicitly requires it.

## 4. Evidence statuses

VERIFIED = current direct evidence.
PARTIAL = some evidence exists, gate incomplete.
BLOCKED = required external authorization/control is unavailable.
NOT VERIFIED = current direct evidence is absent.
CODED = implementation exists but execution/acceptance is not proven.
PROPOSED = planned only.

Never convert CODED, ASSUMED, OLD_PASS, repository-only or synthetic evidence into VERIFIED.

## 5. What ChatGPT should do automatically

When tools/capabilities permit, ChatGPT should:
- inspect the canonical GitHub repository and current main;
- inspect open issues/PRs and avoid duplicates;
- inspect CI/workflow evidence before declaring PASS;
- repair safe code/config/documentation defects;
- run available tests/checks;
- verify changes by read-back;
- keep production WRITE fail-closed;
- use official current documentation for external APIs;
- maintain one canonical MARSEL ROAPP system;
- record durable decisions and acceptance criteria in the repository;
- stop only at external authorization, credential, account-admin, irreversible-write or unavailable-control gates.

## 6. What the owner should provide

The owner should provide only inputs that cannot be obtained through connected tools:
- explicit authorization for irreversible or production WRITE;
- OAuth consent when required;
- account-level GitHub/ReadMe/Cloudflare/Vercel/Wix settings not exposed to tools;
- real business decisions: prices, margins, workflows, permissions, priorities;
- files/photos when visual or document evidence is required.

Never send passwords, API keys, bearer tokens or other secrets in chat.

## 7. Tool/app routing

GitHub — canonical code, issues, PRs, CI evidence, repository governance.
RO App API/MCP — live business data and API contract verification, initially READ-ONLY.
Supabase — database, Auth, protected routes and server-side data controls when it is the selected application backend.
Vercel/Railway/Cloudflare — deployment/runtime/network edge, only where actually used.
Figma/Canva/Adobe — product UI, brand assets, catalog/media production.
Linear/Notion — optional operational/project documentation only; they must not become a competing source of truth.
Make/Automations — scheduled workflows and external orchestration where justified.
Floot/Lovable — application prototyping/building only when they are the selected implementation path.
OpenAI/Codex/MCP — AI engineering, agent/tool orchestration and controlled automation.

Do not connect an application merely because a connector exists. Every integration needs a defined role, owner, source of truth, authorization model and acceptance test.

## 8. Data hierarchy

1. Current direct production/staging evidence with provenance and timestamp.
2. Current CI evidence tied to canonical main.
3. Current canonical repository state.
4. Official current RO App/API documentation.
5. Historical project documents.
6. Chat conversation memory.

Lower-level information cannot override fresher direct evidence.

## 9. Launch strategy

MARSEL ROAPP should be launched in controlled stages:

### Stage A — Canonical foundation
Repository/main governance, CI, secrets, security, evidence contracts.

### Stage B — Read-only business truth
RO App API/MCP authorization, API/entity inventory, warehouse/stock contract, data-quality and duplicate/reference reconciliation.

### Stage C — Application
Authenticated application UI, database schema, protected routes, catalog/orders/inventory/repairs, observability.

### Stage D — Controlled integrations
Wix/website, payments, marketplaces, social commerce and other adapters through MARSEL ROAPP, with idempotency, reconciliation and rollback.

### Stage E — Controlled write
Only after all applicable safety gates pass, with explicit authorization and post-write verification.

Do not expand the architecture faster than the evidence and working product justify.

## 10. What was previously going wrong

- Treating `main-MARSEL-ROAPP` as canonical because GitHub still reports it as default.
- Repeating historical audits after their evidence was already verified.
- Mixing implementation, external authorization and production readiness into one status.
- Adding integrations before defining their role and acceptance criteria.
- Treating repository code as proof of live external access.
- Spending effort on future modules before the minimum launch path is proven.
- Using conversation as the only task registry instead of recording durable state in the repository.
- Asking ChatGPT to "do everything" without an acceptance condition for new work.

These are corrected by the execution and evidence contracts in this document.

## 11. Default command for MARSEL ROAPP

"MARSEL ROAPP. Начни с текущего canonical main. Не возвращайся к закрытым этапам. Проверь свежие доказательства, выбери самый высокий безопасный приоритет, выполни всё доступное без моего участия, исправь ошибки, протестируй, перепроверь, зафиксируй результат в GitHub и продолжай до первого реального внешнего блокера. Production WRITE не включать."

## 12. Launch definition

The project is launch-ready only when the minimum production path is directly verified. Architecture completeness, number of integrations, number of agents, or amount of documentation are not launch criteria by themselves.
