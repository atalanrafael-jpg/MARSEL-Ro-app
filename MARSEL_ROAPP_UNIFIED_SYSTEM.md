# MARSEL ROAPP — ЕДИНАЯ СИСТЕМА

MARSEL ROAPP — единая система ювелирной студии. MARSEL и ROAPP не являются независимыми проектами.

- MARSEL — бизнес-контур: бренд, клиенты, заказы, изделия, ремонт, производство, склад, материалы, финансы, продажи и маркетинг.
- ROAPP — технологический контур той же системы: API, данные, интеграции, автоматизация, MCP и CI/CD.
- `atalanrafael-jpg/Ro-app` — единый исходный контур; `main` — каноническая ветка.
- Единый источник истины запрещает параллельные сущности, дублирующие audit implementations и независимые MARSEL/ROAPP контуры.

## Canonical control plane

`.github/workflows/marsel-unified-control-plane.yml` объединяет API inventory, data-quality, entity audit, product-code collision review, warehouse contract audit и единый READ-ONLY evidence gate.

## Production safety

WRITE запрещён до прямого evidence по backup/export, restore integrity, schema reconciliation, READ-ONLY inventory, duplicate/orphan/reference analysis, dry-run, idempotency, rollback и post-write verification.

## External verification gates

Gmail OAuth, официальный RO App MCP authorization и production backup/restore требуют внешней авторизации или доступа к фактической среде. Они не должны объявляться выполненными без прямого evidence.

## Current verified state — 2026-08-19

- Repository: `atalanrafael-jpg/Ro-app`.
- Default branch: `main`.
- Unified MARSEL ROAPP architecture is canonical.
- Test workflow run #879 completed successfully.
- OpenAI Ads CAPI hardening has been integrated into `main`.
- Production WRITE remains disabled.
