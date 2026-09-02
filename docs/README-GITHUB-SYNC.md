# ReadMe ↔ GitHub Sync Policy — MARSEL ROAPP

## Canonical architecture

`atalanrafael-jpg/MARSEL-Ro-app` remains the canonical application/code repository. It must not be connected to ReadMe bi-directional document sync unless the repository is intentionally designated as the ReadMe documentation repository.

ReadMe currently recommends an empty GitHub repository for initial bi-directional sync. The sync app requires repository-level metadata read access and contents read/write access.

## Required setup

1. In ReadMe: **Settings → Git Connection → GitHub**.
2. Authenticate the ReadMe GitHub App.
3. Select a dedicated, initially empty documentation repository.
4. Confirm the repository mapping.
5. Keep ReadMe version names and GitHub branch names exactly aligned.
6. If GitHub rulesets protect the target branch, explicitly add **ReadMe Sync (App • readmeio)** to the ruleset bypass list with **Always allow** only when direct synchronization to that protected branch is intentionally approved.

## MARSEL ROAPP safety gate

- Do not connect ReadMe Sync to `main` of the application repository by assumption.
- Do not grant ReadMe Sync bypass access to the application repository's protected `main` branch without an explicit repository-governance decision.
- Do not store ReadMe API keys, ROAPP API keys, Auth0 secrets, certificates, or tokens in Git.
- ReadMe external dashboard configuration is **not claimed complete** until an authenticated ReadMe administrator confirms the Git Connection and first synchronization.

## Preferred architecture

Use a dedicated documentation repository for ReadMe content. Keep application code and production controls in `MARSEL-Ro-app`. Use `rdme`/GitHub Actions for controlled, one-way publishing when a dedicated bidirectional repository is not available.

## Verification evidence

A sync is considered configured only after all of the following are observed:

- ReadMe Git Connection shows the intended GitHub repository.
- ReadMe Sync GitHub App has access only to the intended repository.
- A controlled documentation change syncs GitHub → ReadMe.
- A controlled documentation change syncs ReadMe → GitHub, if bidirectional mode is enabled.
- No application source, production configuration, or RO App data is changed by the documentation sync.
- Branch/version names match exactly.
