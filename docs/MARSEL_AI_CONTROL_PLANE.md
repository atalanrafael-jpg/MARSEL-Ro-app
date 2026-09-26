# MARSEL ROAPP — AI CONTROL PLANE

## Purpose

Add a governed AI layer above the existing read-only audit/control plane without granting the AI implicit production-write authority.

## Layers

1. **Evidence layer** — facts are tagged by evidence class.
2. **Exception layer** — anomalies are normalized into reviewable records.
3. **Decision layer** — impact and risk are assessed before a recommendation.
4. **Approval gate** — critical domains require explicit authorization.
5. **Action layer** — actions are permitted only by an explicit policy and verified capability.
6. **Verification layer** — expected vs actual state is compared after an approved action.
7. **Audit layer** — decision, evidence, approval and result are recorded.

## Decision contract

`OBSERVE → VALIDATE → CLASSIFY → ASSESS_IMPACT → ASSESS_RISK → RECOMMEND → APPROVAL_GATE → ACTION → VERIFY → DOCUMENT`

A recommendation is not an action. `PROPOSED` and `UNVERIFIED` evidence cannot be promoted to `VERIFIED` by the AI itself.

## Exception management

Exceptions use controlled categories:

- FACTUAL
- DUPLICATE
- MISSING_DATA
- INVALID_RELATION
- CLASSIFICATION
- CONFIGURATION
- API
- SECURITY
- INTEGRATION
- PERFORMANCE
- LEGAL_TAX
- UNVERIFIED

Default action is `REVIEW_REQUIRED`.

## Automation contract

`TRIGGER → VALIDATE → ACTION → LOG → VERIFY → ALERT`

Automation must remain idempotent where applicable and must fail closed when a required capability, schema, authorization or evidence condition is missing.

## Production safety

The current implementation is **READ-ONLY**. Production WRITE remains disabled. No AI component may infer an endpoint, identifier, schema, credential, backup, restore result, synchronization state or legal/tax requirement.

Before any future controlled WRITE, the repository's existing safety chain remains mandatory:

`backup/export → restore integrity → schema reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → explicit approval → controlled write → post-write verification`

## Owner Control Center target

The eventual owner dashboard should prioritize exceptions and decisions rather than raw event volume:

- money / profitability;
- orders and repairs requiring attention;
- inventory anomalies;
- customer follow-ups;
- integration/API failures;
- security alerts;
- AI recommendations awaiting approval;
- forecast values clearly separated from verified facts.

This document defines the target control model. It does not claim that every target UI, integration or automation is already implemented.
