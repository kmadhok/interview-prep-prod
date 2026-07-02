#!/usr/bin/env python3
"""Regression tests for jd-to-ready trace_step.py.

The tests run the CLI against an isolated temporary JD_TO_READY_LOG_DIR so real
Claude logs are never touched.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("trace_step.py")
TOKENS = json.dumps(
    {
        "input": None,
        "output": None,
        "cache_read": None,
        "cache_write": None,
        "total": None,
        "source": None,
        "notes": "runtime did not expose token counts",
    }
)


class TraceStepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.log_dir = self.root / "logs"
        self.role_folder = self.root / "Roles" / "Acme - Agent Builder"
        self.env = os.environ.copy()
        self.env["JD_TO_READY_LOG_DIR"] = str(self.log_dir)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cmd(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if ok and result.returncode != 0:
            self.fail(f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
        if not ok and result.returncode == 0:
            self.fail(f"command unexpectedly succeeded: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result

    def start_and_bind(self) -> None:
        self.run_cmd("start-run", "--run-type", "full", "--company", "Acme", "--role", "Agent Builder")
        self.run_cmd(
            "set-role-folder",
            "--role-folder",
            str(self.role_folder),
            "--company",
            "Acme",
            "--role",
            "Agent Builder",
        )

    def close_step(self, step: str, status: str = "ok") -> None:
        self.run_cmd(
            "begin",
            "--step",
            step,
            "--primitive",
            f"primitive-{step}",
            "--mode",
            "",
            "--prediction",
            f"step {step} closes",
        )
        self.run_cmd(
            "end",
            "--step",
            step,
            "--primitive",
            f"primitive-{step}",
            "--mode",
            "",
            "--status",
            status,
            "--prediction-met",
            "true",
            "--produced",
            "[]",
            "--gaps",
            "[]",
            "--failure-pattern",
            "",
            "--tokens",
            TOKENS,
        )

    def read_trace(self) -> list[dict]:
        trace = self.role_folder / ".jd-to-ready-trace.jsonl"
        return [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]

    def test_happy_path_finishes_ok(self) -> None:
        self.start_and_bind()
        for step in ["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]:
            self.close_step(step)
        self.run_cmd("finish-run", "--status", "ok", "--gaps", "[]", "--files-written", "[]")

        summary = json.loads((self.log_dir / "jd-to-ready.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["steps_closed"], ["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"])
        events = self.read_trace()
        self.assertEqual([event["seq"] for event in events], list(range(1, len(events) + 1)))

    def test_finish_refuses_missing_steps(self) -> None:
        self.start_and_bind()
        for step in ["1", "2", "3"]:
            self.close_step(step)
        result = self.run_cmd("finish-run", "--status", "partial", "--gaps", "[]", "--files-written", "[]", ok=False)
        self.assertIn("missing closed steps: 3.5, 3.7, 4, 4b, 4c, 5, 6, 7", result.stderr)

    def test_finish_refuses_when_3_5_missing(self) -> None:
        self.start_and_bind()
        for step in ["1", "2", "3", "4", "4b", "4c", "5", "6", "7"]:
            self.close_step(step)
        result = self.run_cmd(
            "finish-run", "--status", "ok", "--gaps", "[]", "--files-written", "[]", ok=False
        )
        self.assertIn("missing closed steps: 3.5", result.stderr)

    def test_finish_refuses_when_4c_missing(self) -> None:
        self.start_and_bind()
        for step in ["1", "2", "3", "3.5", "3.7", "4", "4b", "5", "6", "7"]:
            self.close_step(step)
        result = self.run_cmd(
            "finish-run", "--status", "ok", "--gaps", "[]", "--files-written", "[]", ok=False
        )
        self.assertIn("missing closed steps: 4c", result.stderr)

    def test_steps_closed_order_places_3_5_and_4c(self) -> None:
        self.start_and_bind()
        for step in ["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]:
            self.close_step(step)
        self.run_cmd("finish-run", "--status", "ok", "--gaps", "[]", "--files-written", "[]")

        summary = json.loads((self.log_dir / "jd-to-ready.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        closed = summary["steps_closed"]
        self.assertEqual(closed.index("3.5"), closed.index("3") + 1)
        self.assertEqual(closed.index("3.7"), closed.index("3.5") + 1)
        self.assertEqual(closed.index("3.7"), closed.index("4") - 1)
        self.assertEqual(closed.index("4c"), closed.index("4b") + 1)
        self.assertEqual(closed.index("4c"), closed.index("5") - 1)

    def test_refuses_overlapping_steps(self) -> None:
        self.start_and_bind()
        self.run_cmd(
            "begin",
            "--step",
            "4",
            "--primitive",
            "find-contacts",
            "--mode",
            "full",
            "--prediction",
            "contacts are found",
        )
        result = self.run_cmd(
            "begin",
            "--step",
            "4b",
            "--primitive",
            "enrich-contacts",
            "--mode",
            "",
            "--prediction",
            "contacts are enriched",
            ok=False,
        )
        self.assertIn("step 4 is still open", result.stderr)

    def test_refuses_end_without_matching_begin(self) -> None:
        self.start_and_bind()
        result = self.run_cmd(
            "end",
            "--step",
            "4",
            "--primitive",
            "find-contacts",
            "--mode",
            "full",
            "--status",
            "ok",
            "--prediction-met",
            "true",
            "--produced",
            "[]",
            "--gaps",
            "[]",
            "--failure-pattern",
            "",
            "--tokens",
            TOKENS,
            ok=False,
        )
        self.assertIn("current open step is None", result.stderr)

    def test_abort_records_missing_steps_and_clears_state(self) -> None:
        self.start_and_bind()
        self.close_step("1")
        self.run_cmd("begin", "--step", "2", "--primitive", "jd-classification", "--mode", "", "--prediction", "classifies")
        self.run_cmd("abort-run", "--reason", "classification service unavailable", "--gaps", "[]")

        self.assertFalse((self.log_dir / "jd-to-ready-active.json").exists())
        summary = json.loads((self.log_dir / "jd-to-ready.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(summary["status"], "aborted")
        self.assertEqual(summary["open_step"], "2")
        self.assertIn("2", summary["missing_steps"])

    def test_missing_tokens_is_rejected(self) -> None:
        self.start_and_bind()
        self.run_cmd("begin", "--step", "1", "--primitive", "intake", "--mode", "", "--prediction", "intake closes")
        result = self.run_cmd(
            "end",
            "--step",
            "1",
            "--primitive",
            "intake",
            "--mode",
            "",
            "--status",
            "ok",
            "--prediction-met",
            "true",
            "--produced",
            "[]",
            "--gaps",
            "[]",
            "--failure-pattern",
            "",
            ok=False,
        )
        self.assertIn("required", result.stderr)

    def test_invalid_role_folder_rejected_for_production(self) -> None:
        self.run_cmd("start-run", "--run-type", "full", "--company", "Acme", "--role", "Agent Builder")
        result = self.run_cmd(
            "set-role-folder",
            "--role-folder",
            str(self.root / "Acme - Agent Builder"),
            ok=False,
        )
        self.assertIn("directly under Roles", result.stderr)

    def test_non_roles_folder_allowed_for_test_run(self) -> None:
        self.run_cmd("start-run", "--run-type", "full", "--company", "Acme", "--role", "Agent Builder", "--test-run")
        self.run_cmd("set-role-folder", "--role-folder", str(self.root / "sandbox" / "Acme"), "--test-run")


class RunTypeMapTests(unittest.TestCase):
    def setUp(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("trace_step", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_run_type_required_steps(self) -> None:
        self.assertEqual(self.mod.required_steps_for("jd-to-ready"), ["1", "2", "3", "3.5", "3.7", "6", "7"])
        self.assertEqual(self.mod.required_steps_for("stage-outreach"), ["4", "4b", "4c", "5", "6", "7"])

    def test_unknown_run_type_falls_back_to_full(self) -> None:
        # None / unknown → the legacy full list, so old callers keep working
        self.assertEqual(self.mod.required_steps_for(None), self.mod.REQUIRED_STEPS)
        self.assertEqual(self.mod.required_steps_for("bogus"), self.mod.REQUIRED_STEPS)

    def test_stage_outreach_run_finishes_with_apply_steps_only(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        log_dir = root / "logs"
        role_folder = root / "Roles" / "Acme - Agent Builder"
        role_folder.mkdir(parents=True)
        env = os.environ.copy()
        env["JD_TO_READY_LOG_DIR"] = str(log_dir)

        def run(*args):
            return subprocess.run(
                [sys.executable, str(SCRIPT), *args],
                env=env, capture_output=True, text=True,
            )

        self.assertEqual(run("start-run", "--run-type", "stage-outreach",
                             "--company", "Acme", "--role", "Agent Builder").returncode, 0)
        self.assertEqual(run("set-role-folder", "--role-folder", str(role_folder),
                             "--company", "Acme", "--role", "Agent Builder").returncode, 0)
        for step in ["4", "4b", "4c", "5", "6", "7"]:
            self.assertEqual(run("begin", "--step", step, "--primitive", "p",
                                 "--prediction", "x").returncode, 0, f"begin {step}")
            self.assertEqual(run("end", "--step", step, "--primitive", "p",
                                 "--status", "ok", "--prediction-met", "true",
                                 "--tokens", TOKENS).returncode, 0, f"end {step}")
        finished = run("finish-run", "--status", "ok")
        self.assertEqual(finished.returncode, 0, finished.stderr)

    def test_set_role_folder_binds_existing_folder_without_creating(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        env = os.environ.copy()
        env["JD_TO_READY_LOG_DIR"] = str(root / "logs")
        existing = root / "Roles" / "Acme - Agent Builder"
        existing.mkdir(parents=True)
        marker = existing / "Kanu Madhok Resume - Acme Agent Builder.md"
        marker.write_text("prepped", encoding="utf-8")

        def run(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *args],
                                  env=env, capture_output=True, text=True)

        self.assertEqual(run("start-run", "--run-type", "stage-outreach").returncode, 0)
        res = run("set-role-folder", "--role-folder", str(existing))
        self.assertEqual(res.returncode, 0, res.stderr)
        # binding must not clobber what Skill 1 wrote
        self.assertEqual(marker.read_text(encoding="utf-8"), "prepped")


class SessionScopeTests(unittest.TestCase):
    """The Stop-hook completeness check is scoped to the owning Claude session,
    so a background drip-runner's in-flight trace does not false-positive in an
    unrelated interactive session."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log_dir = Path(self.tmp.name) / "logs"

    def _run(self, *args: str, session: str | None = "__keep__") -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["JD_TO_READY_LOG_DIR"] = str(self.log_dir)
        if session is None:
            env.pop("CLAUDE_CODE_SESSION_ID", None)
        elif session != "__keep__":
            env["CLAUDE_CODE_SESSION_ID"] = session
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], env=env, capture_output=True, text=True
        )

    def test_check_suppressed_for_foreign_session(self) -> None:
        self.assertEqual(
            self._run("start-run", "--run-type", "jd-to-ready",
                      "--company", "Acme", "--role", "X", session="sess-A").returncode,
            0,
        )
        # Session B's Stop hook must NOT flag session A's run.
        other = self._run("check", "--strict", session="sess-B")
        self.assertEqual(other.returncode, 0, other.stderr)
        self.assertEqual(other.stderr, "")
        # The owning session A's Stop hook still flags it.
        mine = self._run("check", "--strict", session="sess-A")
        self.assertEqual(mine.returncode, 2)
        self.assertIn("incomplete", mine.stderr)

    def test_check_flags_unstamped_legacy_run(self) -> None:
        # No session id at start → owner_session=None → fail-closed default kept:
        # any session's check still flags an incomplete run.
        self.assertEqual(
            self._run("start-run", "--run-type", "jd-to-ready", session=None).returncode, 0
        )
        res = self._run("check", "--strict", session="sess-B")
        self.assertEqual(res.returncode, 2)
        self.assertIn("incomplete", res.stderr)


if __name__ == "__main__":
    unittest.main()
