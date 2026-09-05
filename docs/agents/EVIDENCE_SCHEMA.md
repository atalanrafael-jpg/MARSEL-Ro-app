# Evidence Schema

A task record requires:
- task_id
- agent_id
- timestamp
- requested_action
- actual_action
- tool_or_system
- result
- evidence_reference
- verifier
- verification_result

DONE is prohibited without evidence_reference and verification_result=PASS.