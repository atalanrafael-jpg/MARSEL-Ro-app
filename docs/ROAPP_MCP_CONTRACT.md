# RO App MCP Contract — MARSEL ROAPP

## Status
- Repository configuration: PARTIAL
- Production WRITE through MCP: DISABLED
- Live MCP authorization: NOT VERIFIED
- Tool discovery: NOT VERIFIED

## Purpose
This document defines the evidence and safety requirements for connecting an MCP client to RO App without placing credentials or secrets in Git.

## Source of truth
Official RO App MCP documentation must be consulted before configuration and live use:
- https://roapp.readme.io/reference/mcp

No endpoint, authentication header, tool name, parameter, or write capability may be inferred from examples alone.

## Configuration policy
1. MCP client configuration is environment-local unless a public non-secret example is required.
2. API keys, bearer tokens, OAuth tokens, cookies, passwords, and secret headers are prohibited from repository files, issues, pull requests, workflow logs, and artifacts.
3. Production mode defaults to READ-ONLY.

## Authorization gate
PASS requires fresh direct evidence of:
- successful MCP client connection;
- authenticated tool discovery;
- identity/account scope where exposed;
- at least one safe read-only operation;
- zero write operations.

## Smoke-test sequence
READ -> CONNECT -> AUTHENTICATE -> DISCOVER TOOLS -> VALIDATE READ-ONLY TOOL -> EXECUTE SAFE READ -> LOG RESULT -> VERIFY ZERO WRITES.

Any authentication failure, undocumented capability, unexpected tool, or write requirement results in STOP and REVIEW_REQUIRED.

## Write prohibition
MCP must not be used for production mutations until all MARSEL ROAPP production gates are independently PASS:
backup/export, restore integrity, API contracts, dry-run, idempotency, rollback, post-write verification, and explicit authorization.

## Evidence
Evidence must include timestamp, client, non-secret configuration type, connection result, discovered capabilities, executed read-only action, and confirmation of zero mutations.

## Result rule
Configured is not Connected.
Connected is not Authorized.
Authorized is not Production-ready.
Only current direct evidence may produce VERIFIED.
