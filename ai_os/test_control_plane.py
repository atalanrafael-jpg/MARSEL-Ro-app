import unittest

from control_plane import State, Task, route_language


class ControlPlaneTests(unittest.TestCase):
    def test_done_requires_evidence(self):
        task = Task("T1", "demo")
        for state in [
            State.PLAN,
            State.ROUTE,
            State.EXECUTE,
            State.QA,
            State.VERIFY,
            State.EVIDENCE,
            State.UPDATE,
            State.NEXT,
        ]:
            task.transition(state)
        with self.assertRaisesRegex(ValueError, "evidence"):
            task.transition(State.DONE)

    def test_verified_task_can_finish(self):
        task = Task("T2", "demo")
        for state in [
            State.PLAN,
            State.ROUTE,
            State.EXECUTE,
            State.QA,
            State.VERIFY,
            State.EVIDENCE,
            State.UPDATE,
            State.NEXT,
        ]:
            task.transition(state)
        task.add_evidence("test://evidence")
        task.transition(State.DONE)
        self.assertIs(task.state, State.DONE)

    def test_language_router(self):
        self.assertEqual(route_language("web"), "typescript")
        self.assertEqual(route_language("automation"), "python")
        self.assertEqual(route_language("database"), "sql")
        self.assertEqual(route_language("ci"), "shell")

    def test_invalid_transition_is_rejected(self):
        task = Task("T3", "demo")
        with self.assertRaises(ValueError):
            task.transition(State.DONE)


if __name__ == "__main__":
    unittest.main()
