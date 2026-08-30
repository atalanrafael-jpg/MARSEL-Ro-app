---
applyTo: "**/*"
---
# MARSEL ROAPP security review rules

- Treat credentials, API keys, OAuth tokens, refresh tokens, cookies and private keys as secrets.
- Flag hardcoded secrets and unsafe secret propagation immediately.
- Validate authentication, authorization, input validation, output encoding and error handling for security-sensitive changes.
- Never expose secrets in logs, artifacts, test fixtures, screenshots, documentation or PR comments.
- Treat external API data as untrusted input.
- For RO App production integrations, preserve READ-ONLY defaults unless an explicit reviewed requirement authorizes a WRITE operation.
- Never infer or guess security-sensitive identifiers or permissions.
- Prefer least privilege and fail-closed behavior for security controls.
- Do not remove or weaken a security gate without a documented replacement of equal or stronger protection.
