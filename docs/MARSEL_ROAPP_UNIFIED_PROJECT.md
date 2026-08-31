# MARSEL ROAPP — ЕДИНЫЙ ПРОЕКТ

## Канонический проект

`MARSEL ROAPP` использует один GitHub repository как единый технический проект:

`atalanrafael-jpg/Ro-app`

## Единый контур

Repository + Issues + Pull Requests + Actions + Evidence + Production Gates

связаны одной цепочкой:

`Issue → PR → CI/Actions → Evidence → Gate → Result`

## Точки входа

- Repository: https://github.com/atalanrafael-jpg/Ro-app
- Issues: https://github.com/atalanrafael-jpg/Ro-app/issues
- Pull Requests: https://github.com/atalanrafael-jpg/Ro-app/pulls
- Actions: https://github.com/atalanrafael-jpg/Ro-app/actions
- Control Plane: https://github.com/atalanrafael-jpg/Ro-app/blob/main/docs/MARSEL_ROAPP_CONTROL_PLANE.md
- Production Gates: https://github.com/atalanrafael-jpg/Ro-app/blob/main/docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md
- Write Gate: https://github.com/atalanrafael-jpg/Ro-app/blob/main/docs/WRITE-GATE.md
- Task Registry: https://github.com/atalanrafael-jpg/Ro-app/blob/main/docs/MARSEL_ROAPP_TASK_REGISTRY.md
- Unified Control Issue: https://github.com/atalanrafael-jpg/Ro-app/issues/92

## Правила

1. Issue является источником требования или блокера.
2. PR содержит изменение.
3. Actions проверяют изменение.
4. Evidence подтверждает фактический результат.
5. Production Gate принимает решение.
6. `DONE` разрешён только при наличии достаточного evidence.
7. Отсутствие evidence не компенсируется закрытием Issue/PR.
8. Production WRITE остаётся отключённым до прохождения обязательных gates.

## Цель

Не создавать несколько конкурирующих проектов. MARSEL ROAPP управляется как один технический проект, а Repository, Issues, Pull Requests и Actions являются его связанными контурами.
