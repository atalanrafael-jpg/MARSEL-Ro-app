# Task Routing Schema

Required fields: task_id, project, domain, task_type, risk_level, objective, constraints.

Projects: CHATGPT_CORE, RAFAEL_AI_OS, MARSEL_ROAPP, MARSEL_BUSINESS.

Routing flow:
1. Project Router
2. Task Router
3. Risk Router
4. Agent selection
5. Permission gate
6. Execution

Unknown project or ambiguous scope => BLOCKED_PENDING_CLASSIFICATION.