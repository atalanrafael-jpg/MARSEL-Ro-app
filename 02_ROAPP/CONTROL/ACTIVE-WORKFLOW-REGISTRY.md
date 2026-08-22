# MARSEL / Ro App — Active Workflow Registry

Дата проверки: 2026-08-21

## Каноническая структура CI/CD

На `main` проверены все workflow-файлы в `.github/workflows/`.

### CORE

**`marsel-unified-control-plane.yml`**
- Основной read-only контрольный контур проекта.
- Проверяет canonical structure, API inventory, data quality, entity audit, product collisions, warehouse contract, safety/quality gates и evidence.
- Использует `ROAPP_API_KEY` только через GitHub Secret.
- Unified gate не переводится в PASS при `REVIEW_REQUIRED`.
- WRITE-запросы в этом контуре запрещены.

**`test.yml`**
- Канонический unit-test контур.
- Запускается на push, pull_request и вручную.
- Использует `requirements.txt` и pytest.

**`mcp-production.yml`**
- Контур production-readiness MCP.
- Проверяет compileall, tests, MCP import smoke test и pip-audit.

### SUPPORT

**`language-quality.yml`**
- Проверка русского правописания и базовой пунктуации.
- Не изменяет бизнес-данные.

**`generate-drafts.yml`**
- Отдельный scheduled/support контур для генерации черновиков.
- Имеет `issues: write`, поэтому не считается частью READ-ONLY control plane.
- При отсутствии `OPENAI_API_KEY` безопасно завершается без генерации.

## Правила

1. Не дублировать Unified Control Plane отдельными warehouse/API/data-quality workflows без доказанной необходимости.
2. Старые GitHub Actions runs и Git history не удалять.
3. Архивные файлы репозитория переносить в `старые данные/` только после проверки зависимостей.
4. Секреты и токены никогда не помещать в репозиторий.
5. Любой workflow с WRITE-разрешениями не считать READ-ONLY контуром.
6. Изменение активного workflow допускается только после проверки его triggers, secrets, scripts и downstream dependencies.
7. Этот registry является описанием фактически проверенной структуры; он не заменяет GitHub Actions configuration.
