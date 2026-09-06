# MARSEL ROAPP — ERP COSTING AUDIT

Дата: 2026-09-06
Статус: AUDIT COMPLETE / IMPLEMENTATION NOT VERIFIED / WRITE=0

## 1. Вывод

По доступному репозиторию подтверждена архитектура расчёта себестоимости, но не подтверждена рабочая production-реализация ERP Costing или её live-интеграция с RO App.

Поэтому `ERP-COST = NOT VERIFIED`, а не PASS.

## 2. Что подтверждено

### 2.1 Архитектура

ERP Master Architecture определяет отдельный модуль `ERP-COST` с компонентами: металл, камни, труд, накладные, плановая и фактическая себестоимость.

### 2.2 Reference model

Reference Directories specification определяет component-level costing:
- металл: масса × применимый коэффициент пробы/чистоты × выбранная ценовая база + определённые processing components;
- камни: идентичность + масса/размер + quality attributes + acquisition price/source + определённые setting/processing components;
- итоговая себестоимость должна сохранять происхождение компонентов и версию расчёта.

Точные формулы и источник цены прямо обозначены как конфигурационные решения, которые должны быть утверждены до production use.

### 2.3 Product model

Catalog Data Model содержит у продукта `cost`, а у Metal — `cost_basis`, `source`, `effective_at`; у Stone — `cost`.
Это является моделью данных, но не доказательством фактического расчётного движка.

### 2.4 Profitability

Master Operating System требует раздельного хранения:
- revenue;
- material/part cost;
- labor/operation cost;
- other approved cost;
- gross profit;
- margin.

## 3. Что НЕ подтверждено

Не найдено достаточного текущего evidence для утверждения production implementation следующих элементов:

| Capability | Status |
|---|---|
| Live material-cost engine | NOT VERIFIED |
| Live metal price source | NOT VERIFIED |
| Live stone price source | NOT VERIFIED |
| Labor-rate engine | NOT VERIFIED |
| Overhead allocation engine | NOT VERIFIED |
| Planned cost calculation | NOT VERIFIED |
| Actual cost calculation | NOT VERIFIED |
| Cost versioning in production | NOT VERIFIED |
| Cost component provenance in production | NOT VERIFIED |
| RO App cost endpoint | NOT VERIFIED |
| Live cost sync with RO App | NOT VERIFIED |
| Finance posting integration | NOT VERIFIED |
| Cost reconciliation against stock/production | NOT VERIFIED |

## 4. Контрольное решение

Не создавать второй параллельный costing engine только потому, что архитектурная модель уже описана.

Сначала необходимо:

1. найти и проверить существующую реализацию расчёта себестоимости в коде/интеграциях;
2. определить authoritative source для цен металлов и камней;
3. определить unit conventions и conversion rules;
4. определить labor/operation rates;
5. определить overhead policy;
6. определить planned vs actual cost lifecycle;
7. связать cost components с canonical product/material/stone IDs;
8. выполнить READ_ONLY reconciliation против фактических данных, если API предоставляет соответствующие сущности;
9. только после этого проектировать controlled write.

## 5. Safety

Никакие цены, нормы металла, нормы камней, трудовые ставки или накладные расходы не были придуманы или записаны в production.

Production WRITE остаётся `0`.

## 6. Gate

`ERP_COST_ARCHITECTURE = VERIFIED AS DESIGN`
`ERP_COST_IMPLEMENTATION = NOT VERIFIED`
`ROAPP_COST_API = NOT VERIFIED`
`FINANCE_COST_POSTING = NOT VERIFIED`
`ERP_READINESS = BLOCKED`
`PRODUCTION_WRITE = 0`

## Sources in repository

- `docs/MARSEL_ERP_MASTER_ARCHITECTURE_V1.md`
- `docs/MARSEL-REFERENCE-DIRECTORIES-SPEC-V1.md`
- `docs/MARSEL-CATALOG-DATA-MODEL.md`
- `docs/MARSEL-MASTER-OPERATING-SYSTEM-V1.md`

These are design/control sources. They do not constitute live production evidence.
