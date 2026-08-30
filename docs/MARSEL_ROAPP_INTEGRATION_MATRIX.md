# MARSEL ROAPP — Integration Ownership Matrix

| System/domain | Enters MARSEL ROAPP through | Canonical entity | Write policy |
|---|---|---|---|
| RO App | Public API v2 / MCP | RO App account data | Controlled |
| Website | Integration layer | Lead / product / order | Contract + gate |
| Marketplace | Integration layer | Listing / stock / order | Contract + gate |
| Social Commerce | Integration layer | Product/content/order | Contract + gate |
| Webhooks | Event ingress | Event record | Idempotent |
| Analytics | Read interfaces | Metrics/reconciliation | Read-only |
| AI assistants | MCP/documentation | No independent source of truth | No direct production write by default |
| GitHub | CI/CD | Code/configuration | Protected deployment path |

## Conflict rule

If two systems disagree, do not guess. Mark the entity `REVIEW_REQUIRED`, preserve both observed values, and resolve according to the domain's declared source of truth.

## Data lifecycle

`INGRESS → VALIDATE → NORMALIZE → DEDUPLICATE → RECONCILE → DRY-RUN → APPROVE → WRITE → VERIFY → AUDIT`

The production WRITE stage is disabled until the MARSEL ROAPP production gate is satisfied.
