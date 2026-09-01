# MARSEL ROAPP — ЕДИНЫЙ PROJECT CONTROL PLANE

## Единый источник

**Repository:** `atalanrafael-jpg/MARSEL-Ro-app`

Repository является единственным техническим проектом MARSEL ROAPP. Внутри него связаны:

- код и документация;
- GitHub Issues — задачи и блокеры;
- GitHub Pull Requests — изменения кода;
- GitHub Actions — CI/CD, проверки и evidence;
- Production Gates — разрешение/запрет production mutation.

## Правило связи

`Issue → PR → CI/Actions → Evidence → Gate → Result`

Каждое изменение должно иметь проверяемый результат. `DONE` допускается только при наличии соответствующего evidence.

## Текущие ключевые ссылки

- Repository: https://github.com/atalanrafael-jpg/MARSEL-Ro-app
- Issues: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/issues
- Pull Requests: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/pulls
- Actions: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/actions
- Production Gates: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/blob/main/docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md
- Write Gate: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/blob/main/docs/WRITE-GATE.md
- Task Registry: https://github.com/atalanrafael-jpg/MARSEL-Ro-app/blob/main/docs/MARSEL_ROAPP_TASK_REGISTRY.md

## Безопасность

Production WRITE остаётся `0` до прохождения всех обязательных production gates. Issues, PR и Actions не считаются отдельными проектами: они являются управляемыми контурами одного MARSEL ROAPP repository/control plane.
