# MARSEL ROAPP — ЕДИНАЯ СИСТЕМА

## Канонический статус

**MARSEL ROAPP** — единая система. MARSEL и ROAPP не являются независимыми проектами.

- **MARSEL** — бизнес-контур: бренд, ювелирная студия, клиенты, заказы, изделия, ремонт, производство, склад, материалы, финансы, продажи и маркетинг.
- **ROAPP** — технологический контур той же системы: API, интеграции, данные, автоматизация, контроль качества, MCP и CI/CD.
- GitHub-репозиторий `atalanrafael-jpg/Ro-app` является единым исходным контуром системы.
- Единый источник истины: данные, контракты, API, аудит, workflow и документация не должны дублироваться между MARSEL и ROAPP.

## Единый контроль

Канонический CI-контур: `.github/workflows/marsel-unified-control-plane.yml`.

Он объединяет:
1. API inventory;
2. data-quality audit;
3. entity audit;
4. product-code collision review;
5. warehouse contract audit;
6. единый READ-ONLY safety gate;
7. единый evidence artifact.

Производственные WRITE-операции остаются заблокированными до прохождения production safety gates.

## Production gate

Нельзя считать систему WRITE-ready без прямого проверяемого evidence по всем пунктам:
- полный разрешённый backup/export;
- restore test с integrity verification;
- schema mapping и reconciliation;
- полный READ-ONLY live inventory;
- duplicate/orphan/reference analysis;
- dry-run всех мутаций;
- idempotency verification;
- проверенный rollback;
- только после этого — явно разрешённая обратимая тестовая запись;
- post-write verification.

## Правила устранения дублей

- Один canonical workflow для объединённых аудитов.
- Один canonical API/entity ledger.
- Один canonical data-quality/evidence контур.
- Новые версии аудитов не создаются без необходимости; улучшения вносятся в канонический контур.
- Дублирующие PR закрываются после сохранения лучшей реализации.
- Исторические документы не считаются текущим production state.

## Текущий проверяемый статус

На 2026-08-19:
- репозиторий: `atalanrafael-jpg/Ro-app`;
- default branch: `main`;
- единая архитектура MARSEL ROAPP зафиксирована;
- последний проверенный `test` workflow run #879 завершился успешно;
- production WRITE не разрешён;
- оставшиеся блокеры относятся к доказательствам API completeness, backup/restore, collision classification и внешней OAuth/MCP авторизации.

## Внешние зависимости

Некоторые acceptance criteria нельзя завершить только изменением GitHub-кода:
- Gmail OAuth требует отдельной OAuth-авторизации пользователя Google;
- RO App MCP authorization требует подтверждения официального доступа;
- production backup/restore требует доступа к фактическим данным и среде;
- реальные production credentials не должны помещаться в Git.

Такие пункты остаются явно обозначенными как external verification gates, а не выдаются за выполненные.
