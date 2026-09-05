# Agent Registry

| ID | Agent | Domain | Permission | Verification |
|---|---|---|---|---|
| ORCH-001 | Master Orchestrator | CORE | route only | required |
| ROUTE-001 | Project Router | CORE | classify | required |
| ROUTE-002 | Task Router | CORE | classify | required |
| ROUTE-003 | Risk Router | CORE | classify | required |
| VER-001 | Verification Agent | CORE | verify | independent |
| RED-001 | Red Team Agent | CORE | critique | independent |

No agent receives production write permission by default.