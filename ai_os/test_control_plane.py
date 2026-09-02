import unittest

from control_plane import (
    CANONICAL_PIPELINE,
    Permission,
    State,
    Task,
    classify_request,
    route_language,
)


class ControlPlaneTests(unittest.TestCase):
    def _to_safety_gate(self, task):
        for state in CANONICAL_PIPELINE[1:7]:
            task.transition(state)

    def test_done_requires_evidence(self):
        task = Task("T1", "demo")
        self._to_safety_gate(task)
        task.transition(State.VERIFY)
        task.transition(State.LOG)
        task.transition(State.CHECKPOINT)
        task.transition(State.NEXT)
        with self.assertRaisesRegex(ValueError, "evidence"):
            task.transition(State.DONE)

    def test_verified_read_only_task_can_finish_without_write(self):
        task = Task("T2", "demo")
        self._to_safety_gate(task)
        task.transition(State.VERIFY)
        task.add_evidence("test://evidence")
        task.transition(State.LOG)
        task.transition(State.CHECKPOINT)
        task.transition(State.NEXT)
        task.transition(State.DONE)
        self.assertIs(task.state, State.DONE)
        self.assertIs(task.permission, Permission.READ_ONLY)

    def test_write_is_fail_closed_by_default(self):
        task = Task("T3", "demo")
        self._to_safety_gate(task)
        with self.assertRaisesRegex(ValueError, "explicit write permission"):
            task.transition(State.WRITE)

    def test_write_requires_explicit_safety_gate(self):
        task = Task("T4", "demo")
        with self.assertRaisesRegex(ValueError, "passed safety gate"):
            task.grant_write(safety_gate_passed=False)
        self._to_safety_gate(task)
        task.grant_write(safety_gate_passed=True)
        task.transition(State.WRITE)
        self.assertIs(task.permission, Permission.WRITE)

    def test_request_classification_is_conservative(self):
        self.assertEqual(classify_request("backup"), "backup")
        self.assertEqual(classify_request("API"), "api")
        self.assertEqual(classify_request("not-a-known-kind"), "unknown")

    def test_language_router(self):
        self.assertEqual(route_language("web"), "typescript")
        self.assertEqual(route_language("automation"), "python")
        self.assertEqual(route_language("database"), "sql")
        self.assertEqual(route_language("ci"), "shell")
        self.assertEqual(route_language("backup"), "python")

    def test_invalid_transition_is_rejected(self):
        task = Task("T5", "demo")
        with self.assertRaises(ValueError):
            task.transition(State.DONE)

    def test_checkpoint_is_deterministic(self):
        a = Task("T6", "demo")
        b = Task("T6", "demo")
        self.assertEqual(a.checkpoint(), b.checkpoint())
        a.add_evidence("test://evidence")
        self.assertNotEqual(a.checkpoint(), b.checkpoint())


if __name__ == "__main__":
    unittest.main()
