# MARSEL ROAPP — Agent Control Rules

1. Treat MARSEL and ROAPP as one system and one project.
2. Use `main` and the canonical repository `atalanrafael-jpg/MARSEL-Ro-app` as the source of truth.
3. Prefer existing canonical implementations over creating versioned duplicates.
4. Default all live data operations to READ-ONLY.
5. Never claim live verification, backup, restore, OAuth, MCP authorization or WRITE readiness without direct evidence.
6. Do not guess identifiers or mutate production data to discover API behavior.
7. Keep credentials out of source, documentation, logs and artifacts.
8. Use `.github/workflows/marsel-unified-control-plane.yml` for the unified audit path.
9. When a duplicate PR or audit implementation is superseded, close the duplicate and preserve the canonical implementation.
10. After changes, run CI and verify the resulting state before declaring the task complete.
