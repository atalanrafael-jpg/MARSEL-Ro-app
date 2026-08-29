# MARSEL ROAPP MASTER CORE

**Status:** CANONICAL PROJECT CORE
**Purpose:** consolidate the operational principles and verified context of the ChatGPT Core project into MARSEL ROAPP without treating unverified claims as facts.

## 1. Canonical architecture

- MARSEL = business contour.
- ROAPP = technology contour of the same system.
- One project/control plane.
- Canonical branch: `main`.
- Historical material must remain distinguishable from current canonical state.

## 2. Operating principle

`event → action → result → verification → checkpoint → next task`

At every continuation:
- continue from the latest factually verified checkpoint;
- do not repeat completed work without reason;
- distinguish `DONE / IN PROGRESS / BLOCKED / NOT VERIFIED`;
- do not declare an action complete without evidence;
- when sources conflict, prefer the later verified evidence;
- preserve links between versions, commits, workflow runs, audits and fixes.

## 3. No-guess / evidence-first rule

- Never invent API endpoints, identifiers, schemas, permissions, results or deployment status.
- `NOT_VERIFIED` remains `NOT_VERIFIED` until direct evidence exists.
- A successful CI run is not proof of successful production synchronization.
- READ-ONLY evidence must remain separate from WRITE evidence.

## 4. Production safety gate

Production mutation remains blocked until evidence exists for:

`backup/export → restore → reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`

No mass write, deletion or synchronization should bypass this gate.

## 5. Current verified project context

The project has established a working READ-ONLY RO App API audit path and a canonical control-plane model. Historical project evidence records successful order/API audits, but individual evidence artifacts must be treated according to their actual run and date; older snapshots must not override newer verified results.

Known external gates that require fresh evidence include:
- production backup/restore;
- complete API/entity coverage;
- warehouse live contract;
- collision classification/resolution;
- Gmail OAuth live-read, where required;
- official RO App MCP authorization, where required;
- final production safety gate.

## 6. ChatGPT Core integration

This document is the canonical project-side representation of the useful ChatGPT Core operating rules. It does **not** claim that the ChatGPT Project itself has been physically merged into this repository or that private ChatGPT project internals are accessible here.

Core principles to preserve:
- master context and decision continuity;
- cross-stage task continuity;
- source/evidence tracking;
- version and duplicate control;
- self-audit and error correction;
- proactive continuation to the next logical task when technically possible;
- transparent reporting of constraints and unverified states.

## 7. Scope boundary

MARSEL business requirements must remain canonical and explicit. Do not activate production features merely because they are described in historical project material. Current operational scope must be confirmed by the latest project decision and implementation evidence.

## 8. Change control

Any future change to this file must:
1. identify the source or reason;
2. preserve the previous decision history where material;
3. be validated against the canonical control plane;
4. never weaken production safety invariants silently.
