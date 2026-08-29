# CHATGPT CORE — Update Addendum

Date: 2026-08-29

## Verified OpenAI updates

- OpenAI's ChatGPT Release Notes show a new Temporary Chat control rollout on 2026-08-27: users can choose whether a temporary chat is personalized with memory, plugins, and custom instructions; temporary chats do not create new memories and normally remain outside chat history unless saved.
- OpenAI's Codex managed-configuration documentation states that configurations pinning `gpt-5.4` or `gpt-5.4-mini` for ChatGPT-authenticated Codex users must be updated before 2026-08-31 to `gpt-5.6-terra` and `gpt-5.6-luna` respectively. API-key-authenticated Codex is not affected by this migration notice.

## Current repository verification

PR #79 remains OPEN, DRAFT, and NOT MERGED. Its HEAD is `f18cdc08800c8220fdd5c7b56992362a590b9854`. GitHub reports `mergeable=false`.

For this exact HEAD, current workflow evidence is:

- MARSEL Unified Control Plane: success
- MARSEL Secret Guard: success
- MARSEL Integration Health: success
- Codex Plugin Validation: success
- MARSEL Live Integration Probes: success
- MARSEL Language Quality: success
- test: success
- MCP production readiness: success
- CodeQL: success
- MARSEL release readiness: failure

The release-readiness failure occurs at the `Release readiness check` step. The check is intentionally fail-closed when required external evidence is absent; no evidence is fabricated or marked PASS without proof.

## Decision

Do not merge PR #79 and do not claim the ChatGPT Core audit baseline is fully verified until the release-readiness state is independently resolved or intentionally excluded from the PR's required checks. No production mutation is authorized by this addendum.

## Source references

- OpenAI ChatGPT Release Notes: https://help.openai.com/en/articles/6825453-chatgpt-release-notes
- OpenAI Codex managed configuration: https://developers.openai.com/codex/enterprise/managed-configuration
