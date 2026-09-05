# Event Triggers

Candidate events:
- github.pull_request.opened
- github.workflow.failed
- data.quality.violation
- integration.sync.failed
- scheduled.audit.due

Every event must define source, event_id, deduplication_key, target_agent, risk_level and evidence requirements.

Events are specifications only until a runtime consumer is implemented.