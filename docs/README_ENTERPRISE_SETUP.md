# ReadMe Enterprise — MARSEL ROAPP

## Target architecture

ReadMe Enterprise provides a Group containing one or more Projects. Group-level controls can cover shared design, reusable content, authentication, roles, audit logs, and other enterprise settings; project-level configuration remains independent where required.

For MARSEL ROAPP, the intended initial model is one canonical ReadMe project for the ROAPP technical documentation, with the GitHub repository `atalanrafael-jpg/MARSEL-Ro-app` as the source-controlled documentation repository.

## Required ReadMe configuration

1. Create or confirm the ReadMe Enterprise Group.
2. Create or confirm the MARSEL ROAPP project inside that Group.
3. Confirm the project is using ReadMe Refactored. The repository workflow uses `readmeio/rdme@v10`, which ReadMe documents for Refactored projects.
4. Create the Guides category `documentation` before the first publication of `documentation/marsel-roapp-overview.md`.
5. Generate a project API key with the minimum required scope for documentation publishing.
6. Store the key in GitHub repository secrets as `README_API_KEY`. Never commit it to the repository.
7. Run the GitHub workflow manually once to validate the dry run and then publish from `main`.

## Enterprise access

If teammate SSO is required, configure SAML SSO at the Enterprise Group level and separately grant project access. SSO authentication alone does not grant project permissions.

## End-user access

If the documentation must be private, configure project access and End User Access in ReadMe. Do not make the project private solely by adding SSO; authentication and authorization are separate controls.

## GitHub publishing policy

- Pull requests: dry-run validation only.
- `main`: publish only when `README_API_KEY` exists.
- No API key is stored in Git.
- No production RO App WRITE operation is introduced by this integration.

## Verification checklist

- [ ] Enterprise Group confirmed.
- [ ] MARSEL ROAPP project confirmed.
- [ ] Refactored architecture confirmed.
- [ ] `documentation` Guides category exists.
- [ ] `README_API_KEY` stored as a GitHub Actions secret.
- [ ] Pull-request dry run passes.
- [ ] `main` publication succeeds.
- [ ] Published page is verified in ReadMe.
- [ ] Enterprise audit/access controls reviewed.
