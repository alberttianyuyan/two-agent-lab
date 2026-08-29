import json
import tempfile
import unittest
from pathlib import Path

from main import ReviewResult, RunRecord, run_review_loop, save_run, task_needs_file


class ScriptedAgentRunner:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def __call__(self, agent, prompt):
        self.calls.append((agent, prompt))
        return next(self.outputs)


class ReviewLoopTests(unittest.TestCase):
    def test_passes_without_revision(self):
        runner = ScriptedAgentRunner(
            [
                "First draft",
                ReviewResult(decision="PASS", reason="", suggested_fix=""),
            ]
        )

        record = run_review_loop(
            "Do the task", object(), object(), runner, on_status=lambda _m: None
        )

        self.assertTrue(record.approved)
        self.assertEqual(record.revisions_used, 0)
        self.assertEqual(record.final_result, "First draft")
        self.assertEqual(len(runner.calls), 2)

    def test_uses_at_most_two_revisions(self):
        fail = ReviewResult(
            decision="FAIL",
            reason="A requirement is missing.",
            suggested_fix="Add the missing requirement.",
        )
        runner = ScriptedAgentRunner(
            [
                "Draft 1",
                fail,
                "Draft 2",
                fail,
                "Draft 3",
                ReviewResult(decision="PASS", reason="", suggested_fix=""),
            ]
        )

        record = run_review_loop(
            "Do the task", object(), object(), runner, on_status=lambda _m: None
        )

        self.assertTrue(record.approved)
        self.assertEqual(record.revisions_used, 2)
        self.assertEqual(record.final_result, "Draft 3")
        self.assertEqual(len(runner.calls), 6)
        self.assertIn("Draft 2", runner.calls[4][1])

    def test_stops_when_revision_limit_is_reached(self):
        fail = ReviewResult(
            decision="FAIL",
            reason="Still incomplete.",
            suggested_fix="Complete it.",
        )
        runner = ScriptedAgentRunner(["Draft 1", fail, "Draft 2", fail, "Draft 3", fail])

        record = run_review_loop(
            "Do the task", object(), object(), runner, on_status=lambda _m: None
        )

        self.assertFalse(record.approved)
        self.assertEqual(record.revisions_used, 2)
        self.assertEqual(record.final_result, "Draft 3")
        self.assertEqual(len(record.reviews), 3)
        self.assertEqual(len(runner.calls), 6)

    def test_file_task_without_code_is_failed_by_python(self):
        runner = ScriptedAgentRunner(
            [
                "Here is how you would make a snake game.",
                "```html\n<html><body>Snake</body></html>\n```",
                ReviewResult(decision="PASS", reason="", suggested_fix=""),
            ]
        )

        record = run_review_loop(
            "write an html snake game",
            object(),
            object(),
            runner,
            on_status=lambda _m: None,
        )

        self.assertTrue(record.approved)
        self.assertEqual(record.reviews[0]["decision"], "FAIL")
        self.assertIn("```html", record.final_result)
        self.assertEqual(len(runner.calls), 3)
        self.assertTrue(task_needs_file("write an html snake game"))
        self.assertFalse(task_needs_file("Explain recursion"))


class OutputTests(unittest.TestCase):
    def test_saves_markdown_and_json(self):
        record = RunRecord(
            task="Test task",
            final_result="Test result",
            reviews=[{"decision": "PASS", "reason": "", "suggested_fix": ""}],
            revisions_used=0,
            approved=True,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path, json_path, extras = save_run(record, Path(temp_dir))
            self.assertEqual(extras, [])

            self.assertIn("Test result", markdown_path.read_text(encoding="utf-8"))
            saved = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(saved["approved"])
            self.assertEqual(saved["task"], "Test task")

    def test_extracts_html_file(self):
        record = RunRecord(
            task="Make a page",
            final_result="```html\n<html><body>Hi</body></html>\n```",
            reviews=[{"decision": "PASS", "reason": "", "suggested_fix": ""}],
            revisions_used=0,
            approved=True,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            _md, _json, extras = save_run(record, Path(temp_dir))
            self.assertEqual(len(extras), 1)
            self.assertEqual(extras[0].suffix, ".html")
            self.assertIn("<html>", extras[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
