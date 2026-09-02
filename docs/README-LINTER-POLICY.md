# MARSEL ROAPP — ReadMe Linter Policy

This document is the canonical style policy for the ReadMe AI Linter configuration.

## Style Guide

- Use the canonical business name **Ювелирная студия MARSEL**. Do not rename it to “мастерская” when referring to the business entity.
- Use **MARSEL ROAPP** for the unified project name. Use MARSEL for the business contour and ROAPP for the technical contour.
- Use **RO App** when referring to the external RO App platform.
- Use **ReadMe** with this exact capitalization.
- Use **GitHub**, **GitHub Actions**, **OpenAPI**, **API**, **MCP**, and **SAML** with standard capitalization.
- Define an acronym on first use when the audience may not know it.
- Prefer short, direct sentences and active voice.
- Use imperative language for procedures: “Open”, “Select”, “Run”, “Verify”.
- Do not use vague or hedged wording when a verified fact is available.
- Distinguish verified facts, configuration requirements, and pending external actions.
- Never invent endpoints, credentials, project IDs, API responses, integration states, or successful production tests.
- Treat the documented API contract as the source of truth. Keep examples consistent with the imported OpenAPI specification.
- Keep authentication instructions consistent with the actual API security scheme.
- Use code formatting for commands, paths, environment variables, headers, endpoint names, and code identifiers.
- Keep headings concise and descriptive.
- Prefer one task or concept per section.
- Use tables only when they materially improve comparison or reference value.
- Avoid marketing language, unnecessary exclamation marks, and filler.
- Security-sensitive values must never appear in documentation: API keys, access tokens, private keys, passwords, cookies, or secrets.
- Do not document a production write operation unless the operation is explicitly approved and its contract is verified.

## Errors

- Never publish placeholder text such as `TODO`, `FIXME`, `PLACEHOLDER`, `TBD`, or `Lorem ipsum`.
- Never publish fabricated URLs, endpoint paths, credentials, identifiers, or response examples.
- Never expose secrets or secret-like values.
- Never use inconsistent names for MARSEL, MARSEL ROAPP, RO App, or ReadMe.
- Do not document an authentication method that conflicts with the verified OpenAPI contract.
- Do not state that an external ReadMe/Auth0 configuration is complete unless it has been directly verified.

## Warnings

- Prefer active voice over passive voice.
- Prefer direct instructions over “you can”, “you might”, or similar hedging.
- Prefer concrete examples over abstract explanations.
- Explain security and read-only constraints where they affect a procedure.
- Keep API examples minimal and aligned with the verified contract.
- When a value is environment-specific, name the variable rather than embedding the value.
- When an external dashboard action is required, clearly mark it as an external configuration step.

## External ReadMe configuration

In ReadMe, configure these rules under **Admin Tools → AI → Linter** in the Style Guide, Errors, and Warnings sections. ReadMe's AI Linter applies to Guides and API Reference pages and automatically checks broken links; API Reference endpoints themselves are excluded from AI Linter page linting.

## CI relationship

The repository should also run ReadMe's local CLI linter for Git-backed documentation where applicable. The CLI validates documentation structure, frontmatter, links, MDX-ish content, slugs, ordering, and related structural issues. CI linting is a repository gate; the ReadMe dashboard AI Linter remains the content/style gate.
