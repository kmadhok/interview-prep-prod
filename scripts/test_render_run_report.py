#!/usr/bin/env python3
"""Regression tests for render_run_report.py.

The primary fixture is built by driving the real trace_step.py CLI into an
isolated TRACE_RUNS_DIR so the renderer sees the same JSONL shape as production
runs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import render_run_report


TRACE_SCRIPT = Path(__file__).with_name("trace_step.py")
TOKENS = json.dumps(
    {
        "input": 10,
        "output": 20,
        "cache_read": 5,
        "cache_write": 7,
        "total": 42,
        "source": "manual",
        "notes": "test fixture",
    }
)


class RenderRunReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs_dir = self.root / "runs"
        self.env = os.environ.copy()
        self.env["TRACE_RUNS_DIR"] = str(self.runs_dir)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(TRACE_SCRIPT), *args],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result

    def build_cli_fixture(self) -> Path:
        result = self.run_cmd(
            "start-run",
            "--run-id",
            "run-render-fixture",
            "--run-type",
            "primitive",
            "--skill",
            "tailor-resume",
            "--company",
            "Acme",
            "--role",
            "Agent Builder",
        )
        run_id = result.stdout.strip()
        self.run_cmd(
            "begin",
            "--step",
            "main",
            "--primitive",
            "tailor-resume",
            "--mode",
            "",
            "--prediction",
            "resume is tailored",
            "--reason",
            "tailor the resume against the canonical achievement bank",
            "--sources",
            json.dumps(["workspace/Resume Achievements Master.md", "workspace/Roles/x/Job Description.md"]),
        )
        self.run_cmd(
            "tool-event",
            "--tool-name",
            "apply_patch",
            "--status",
            "completed",
            "--summary",
            "wrote tailored resume",
        )
        self.run_cmd(
            "end",
            "--step",
            "main",
            "--primitive",
            "tailor-resume",
            "--mode",
            "",
            "--status",
            "ok",
            "--prediction-met",
            "true",
            "--produced",
            json.dumps(["workspace/Roles/x/resume.md"]),
            "--gaps",
            json.dumps(
                [
                    {
                        "source": "tailor-resume",
                        "kind": "no-canonical-match",
                        "detail": "x",
                    }
                ]
            ),
            "--failure-pattern",
            "",
            "--tokens",
            TOKENS,
        )
        self.run_cmd("finish-run", "--status", "ok", "--gaps", "[]", "--files-written", "[]")
        return self.runs_dir / run_id

    def test_render_writes_report_in_run_dir_and_returns_path(self) -> None:
        run_dir = self.build_cli_fixture()

        report_path = render_run_report.render(run_dir)

        self.assertEqual(report_path, run_dir / "report.md")
        self.assertTrue(report_path.exists())

    def test_report_explains_how_to_change_outputs_with_sources(self) -> None:
        report_path = render_run_report.render(self.build_cli_fixture())
        report = report_path.read_text(encoding="utf-8")

        self.assertIn("## How to change an output", report)
        self.assertIn("workspace/Resume Achievements Master.md", report)

    def test_report_contains_steps_gaps_tokens_and_tool_call_count(self) -> None:
        report_path = render_run_report.render(self.build_cli_fixture())
        report = report_path.read_text(encoding="utf-8")

        self.assertIn("| Step |", report)
        self.assertIn("Gaps", report)
        self.assertIn("Tokens", report)
        self.assertIn("Tool-call count: 1", report)

    def test_v1_trace_tolerates_missing_reason_sources_schema_and_skill(self) -> None:
        run_dir = self.root / "legacy-run"
        run_dir.mkdir()
        events = [
            {"event": "run_start", "run_id": "legacy-run", "company": "Acme", "role": "Analyst"},
            {"event": "step_begin", "run_id": "legacy-run", "step": "main", "status": "running"},
            {"event": "step_end", "run_id": "legacy-run", "step": "main", "status": "ok"},
            {"event": "run_finish", "run_id": "legacy-run", "status": "ok"},
        ]
        trace = run_dir / "trace.jsonl"
        trace.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")

        report_path = render_run_report.render(run_dir)
        report = report_path.read_text(encoding="utf-8")

        self.assertIn("—", report)


if __name__ == "__main__":
    unittest.main()
