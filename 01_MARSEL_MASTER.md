# 01_MARSEL_MASTER

**Purpose:** canonical business/process layer for MARSEL + ROAPP.

## 1. Source of truth
- Canonical branch: `main`.
- MARSEL = business contour; ROAPP = technical contour; one unified system.
- Project documentation is not evidence of live ROAPP configuration. Live facts must be marked separately.
- Status vocabulary: VERIFIED / PARTIAL / FAILED / BLOCKED / NOT VERIFIED / PROPOSED.

## 2. Business structure
**Target business scope (PROJECT CONFIGURATION / BUSINESS REQUIREMENT):** jewelry studio with jewelry manufacturing/sales, jewelry repair and watch repair; 1 branch; 3 employees; RUB. These target parameters are not by themselves proof that all corresponding objects exist in the live ROAPP account.

### Catalog
- Jewelry
- Watches
- Spare parts
- Components
- Materials
- Metals
- Precious/jewelry stones
- Consumables
- Services

### Production
- Manufacturing stages
- Technological operations
- Masters
- Production tasks
- Quality control
- Readiness

### Repair
- Jewelry repair
- Watch repair
- Diagnostics
- Defect report
- Approval
- Cost
- сроки
- Status
- Delivery
- Warranty

### Customers
- Individuals / legal entities
- Contacts
- Order history
- Repair history
- Purchases
- Communications
- Segments

## 3. Warehouse model
`Warehouse -> Zone/Cell (if supported) -> Item -> Stock -> Movement -> Order -> Write-off/Transfer/Sale`

Live warehouse IDs: **do not invent or promote IDs to official status without API evidence**. Current warehouse API contract remains NOT VERIFIED.

## 4. Documents and templates
Target templates:
- order;
- repair;
- acceptance;
- delivery;
- act;
- invoice;
- production task;
- item card;
- warranty document;
- internal documents;
- commercial offer.

Legal necessity of individual requisites must be verified separately against current Russian law.

## 5. Cost accounting
Target structure:
`Item -> Metal + Stones + Components + Labor + Other direct costs = Cost`

Required attributes where actually available: fineness, mass, metal cost, stone characteristics/cost, labor, additional direct costs. Never calculate factual cost without source data.

## 6. Automation catalog
Every automation must follow:
`TRIGGER -> INPUT -> VALIDATION -> ACTION -> LOG -> VERIFY -> ALERT`

Priority:
- P0: ROAPP audit, API control, data quality, backup, security.
- P1: orders, repairs, stock, notifications, reports.
- P2: marketing, CRM, repeat sales, analytics, forecasting.

## 7. Growth model
Each initiative must be evaluated as:
`COST -> EFFECT -> RISK -> TEST -> KPI -> RESULT`

Target: **3,000,000 RUB net profit/month** (business goal, not forecast or guarantee).

## 8. Development/document links
Technical implementation is governed by `02_ROAPP_TECHNICAL_MASTER.md`; data by `03_MARSEL_DATA_MASTER.md`; legal/finance by `04_MARSEL_LEGAL_FINANCE_MASTER.md`; current control point by `05_MARSEL_CURRENT_STATE.md`.

## 9. Historical material policy
Old branches and duplicated project notes are evidence/history only. The canonical current state is maintained in the five master files and the current `main` branch. Historical material must not overwrite newer verified facts.