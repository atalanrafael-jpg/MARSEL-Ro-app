# MARSEL ROAPP — Multi-Agent System v1

**Status:** implemented baseline
**Mode:** parallel specialist analysis; branch-only GitHub publication; production WRITE disabled

## 1. Operating model

MARSEL ROAPP uses a coordinator plus independent specialist agents. A task is decomposed once and specialist work can run independently before a verification aggregation step.

| Agent | Responsibility | Default capability |
|---|---|---|
| architect | architecture and contracts | read/plan/test/document |
| security | secrets, auth, permissions, threat controls | read/plan/test/document |
| data_integrity | duplicates, reconciliation, data quality | read/plan/test/document |
| integration | RO App/provider boundaries | read/plan/test/document |
| tester | regression and contract tests | read/plan/test/document |
| verifier | evidence and gate verification | read/plan/test/document |
| documenter | changelog, contracts, runbooks | read/plan/test/document |
| github | branch/PR change management | read/plan/publish_branch/open_pr |

## 2. Lifecycle

`DISCOVER → DECOMPOSE → PARALLEL_EXECUTE → AGGREGATE → VERIFY → PUBLISH_BRANCH → OPEN_PR → REVIEW → MERGE`

The coordinator does not merge pull requests and does not authorize production writes.

## 3. Task contract

Every task has a stable `task_id`, objective, risk, state, verification result and evidence reference. `DONE` is valid only after all participating results are `PASS` and an evidence reference exists.

`CRITICAL` tasks are blocked by default and require explicit external authorization.

## 4. GitHub reflection

The GitHub agent is a change-management role, not an unrestricted code writer. Its publication boundary requires:

1. a non-main feature branch;
2. an evidence reference;
3. explicit host-level publication enablement;
4. a reviewable pull request;
5. normal repository CI and human/repository review gates.

The bridge contains no credentials. A host implementation supplies GitHub authentication through its normal secret-management mechanism.

## 5. Parallelism policy

Independent read, analysis, test and documentation tasks may execute in parallel. Tasks with write dependencies, shared mutable state, or conflicting files must be serialized. Evidence aggregation occurs after all required specialists report.

## 6. Safety invariants

- Production WRITE is always denied by the coordinator.
- Deletion/merge decisions are never delegated to heuristic agents.
- Secrets and tokens are prohibited in logs, fixtures and committed artifacts.
- CI success is evidence of CI success, not production authorization.
- Real production evidence must originate from an authorized controlled system.
- Agent output is reviewable and traceable to a task and evidence reference.

## 7. GitHub implementation workflow

1. Create a feature branch.
2. Run specialist agents in parallel against the same task snapshot.
3. Aggregate findings and proposed changes.
4. Run tests and verification.
5. Publish only the verified change set to the feature branch.
6. Open/update a PR with task/evidence references.
7. Review and merge through repository policy.
8. Monitor post-merge CI and record follow-up tasks.

## 8. Initial MARSEL backlog for the swarm

- PR #132: RO App connector boundary hardening and readiness disclosure.
- PR #136: canonical integration, observability and adapter contracts.
- Issue #83: real production evidence intake / gate.
- Issue #133: master data/integration contract.
- Issue #134: observability/correlation implementation.
- Issue #135: provider adapters for website, marketplaces, payments and social commerce.

These are tracked as GitHub work items; the multi-agent runtime is the execution/control layer, not a replacement for repository governance.
