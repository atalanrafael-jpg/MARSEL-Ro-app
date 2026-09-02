# MARSEL ROAPP — ЕДИНАЯ СИСТЕМА

Дата контрольной ревизии: 2026-09-02

MARSEL и ROAPP — единая система Ювелирной студии MARSEL, а не независимые проекты.

- MARSEL — бизнес-контур: клиенты, заказы, изделия, ремонт, производство, склад, материалы, финансы, продажи и маркетинг.
- ROAPP — технологический контур той же системы: API, данные, интеграции, автоматизация, MCP и CI/CD.
- Канонический GitHub repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Каноническая ветка: `main`.
- Канонический live audit control plane: `.github/workflows/marsel-unified-control-plane.yml`.
- Исторические реализации находятся в `старые данные/` и не являются текущим источником истины.

## Canonical control plane

`.github/workflows/marsel-unified-control-plane.yml` — единственный канонический live RO App audit workflow. Вспомогательные workflow разрешены только для явно отличающихся инженерных, security или gate-функций и не должны создавать второй live audit path.

Основная цепочка:

`API inventory → data quality → entity audit → product-code review → warehouse contract → safety gate → evidence`

Все live-аудиты RO App выполняются READ-ONLY. Идентификаторы не угадываются. Недостаточные или конфликтующие доказательства дают `REVIEW_REQUIRED`, а не `PASS`.

## Canonical implementations

- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_3.py`
- `scripts/marsel_warehouse_contract_v20_47.py`
- `scripts/marsel_api_v2_probe_v1.py`
- `scripts/marsel_api_v2_canonical_registry_v1.py`
- `scripts/marsel_canonical_self_check.py`

Внутренние зависимости API inventory `v20_31` и `v20_29` остаются активными до отдельного рефакторинга и повторной проверки; их нельзя удалять только из-за номера версии.

## Production safety

**Production WRITE остаётся запрещённым.** До рассмотрения controlled write должны существовать прямые доказательства:

`backup/export → restore integrity → schema reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`

Наличие write-методов, успешного CI или документации не является доказательством выполнения production WRITE или готовности к нему.

## Current external gates

По последнему проверенному состоянию остаются открытыми:

- backup/export и независимый restore/integrity test;
- полнота текущего API/entity coverage;
- официальный live warehouse-list contract;
- классификация/актуальная reconciliation collision findings;
- user-authorized Gmail OAuth read-only verification;
- official RO App MCP authorization;
- credential-exposure remediation evidence;
- GitHub account/ruleset/security controls, которые требуют account-level проверки.

## Control rule

Каждая существенная задача проходит `OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`.

Старые успешные запуски не заменяют свежую проверку текущего `main`. `DONE` допускается только при наличии прямого evidence.
