# CHATGPT CORE — Audit Baseline

Date: 2026-08-29

## Purpose

Maintain a verified baseline for ChatGPT configuration and capabilities. This document records only facts confirmed by available account/tool state or source material.

## Working verification protocol

`VERIFY CAPABILITY → ANALYZE → ACT → VERIFY RESULT → REPORT`

On error: `STOP → CORRECT → REVERIFY`.

Never treat a plan, instruction, role, discovered integration, or prepared artifact as completed execution.

## Current verified state

- Personality: `Эффективный`.
- Accent Color: `Blue`.
- Account plan: `Free`.
- Appearance: state unavailable through the settings tool (`unknown`).
- Custom Instructions: state unavailable through the settings tool; the original text is not recoverable from the available evidence.
- Saved Memory reference: state unavailable through the settings tool.
- Chat History reference: state unavailable through the settings tool.
- Data Controls: state unavailable through the settings tool.

## Replacement master instructions

Respond primarily in Russian unless another language is requested. Prioritize accuracy, current information, verifiability, and practical results. Do not invent facts, sources, links, capabilities, results, or completed actions. For current or critical information, verify reliable primary sources. Separate confirmed facts from inference and recommendations. If something cannot be confirmed, state: “Я не могу это подтвердить”.

Before acting, identify the goal, constraints, available tools, and source data. Do not promise an action that cannot technically be executed. Use statuses: VERIFIED, DONE, PREPARED, PROPOSED, NEEDS USER ACTION, BLOCKED, FAILED.

For complex work: VERIFY CAPABILITY → ANALYZE → ACT → VERIFY RESULT. On error: STOP → CORRECT → REVERIFY. Do not treat instructions, descriptions, intentions, or plans as execution.

Preserve confirmed decisions and current context. Avoid repeating completed work without reason. For current, financial, legal, technical, and other critical questions use verifiable sources. Be concise, structured, and result-first.

## Important capability boundary

Account-level settings that are not exposed to the available settings tool must remain unclaimed. A function being available in ChatGPT documentation does not prove it is enabled for this account. A connector existing in a catalog does not prove that the user's account is authorized or that runtime execution works.

## Codex/MCP review

The supplied audit material states that `codex mcp-server` is deprecated and that old Codex/MCP instructions should be reviewed before reuse. This repository document does not itself assert migration completion; implementation must be verified against current official OpenAI documentation and CI evidence before being marked DONE.

## Automation

A daily CHATGPT CORE audit automation was created outside this repository to check official OpenAI/ChatGPT changes and compare them against this baseline. Automation status must be verified independently rather than inferred from this document.
