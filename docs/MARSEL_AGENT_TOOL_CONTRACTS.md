# External Tool Contracts

## Rule
No external system is callable merely because an adapter exists.

## ROAPP
Status: NOT_VERIFIED.
Mode: READ_ONLY placeholder.
Required before live calls:
1. official endpoint verification;
2. method and auth verification;
3. request/response schema;
4. pagination;
5. error and rate-limit behavior;
6. safe live read test.

## GitHub
Status: PARTIAL.
The repository connector used by the operator is separate from this runtime adapter.
No credential is embedded in runtime code.

## Write tools
No WRITE tool may be registered as production-capable until a Production Gate evidence package exists.

## Registry controls
- unique tool names;
- explicit mode;
- explicit contract status;
- isolated handler.
