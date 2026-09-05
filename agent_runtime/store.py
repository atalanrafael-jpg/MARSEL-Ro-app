class TaskStore:
    def __init__(self): self._tasks = {}
    def save(self, task): self._tasks[task.task_id] = task
    def get(self, task_id): return self._tasks.get(task_id)
