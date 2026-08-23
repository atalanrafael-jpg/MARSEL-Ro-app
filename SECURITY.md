# Security Policy

## Scope

This repository contains the MARSEL × ROAPP application, automation, audit tooling, and GitHub Actions control plane.

Security-sensitive areas include GitHub Actions, API/OAuth credentials, Gmail OAuth, RO App API access, Docker/deployment configuration, production gates, and dependency/supply-chain configuration.

## Reporting a vulnerability

Do not publish credentials, tokens, OAuth codes, refresh tokens, or exploitable details in a public issue. Use GitHub's private vulnerability reporting/security advisory mechanism when available. If private reporting is unavailable, contact the repository owner privately before disclosure.

## Secrets

Never commit RO App API keys, OpenAI API keys, Google OAuth client secrets, Gmail access/refresh tokens, encryption keys, production credentials, or real `.env` files.

Use GitHub Actions Secrets/Variables or the deployment platform's secret store.

## Production safety

Production WRITE operations remain disabled unless the documented evidence gates explicitly authorize them. READ-ONLY audits must remain READ-ONLY.

Missing or incomplete external evidence must produce a review/blocking state, not an inferred PASS.

## Pull requests

Security-sensitive changes require CODEOWNERS review and successful CI before merge.
