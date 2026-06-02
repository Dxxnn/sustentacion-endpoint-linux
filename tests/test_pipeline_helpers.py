from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from build_features import assign_labels  # noqa: E402
from parse_audit_log import parse_kv  # noqa: E402


class ParseAuditLogTests(unittest.TestCase):
    def test_numeric_syscall_values_are_not_decoded_as_hex(self) -> None:
        fields = parse_kv(
            'type=SYSCALL msg=audit(1.0:1): pid=4242 ppid=2034 uid=1000 comm="bash"',
            "SYSCALL",
        )
        self.assertEqual(fields["pid"], "4242")
        self.assertEqual(fields["ppid"], "2034")
        self.assertEqual(fields["uid"], "1000")

    def test_execve_arguments_are_decoded_when_hex_encoded(self) -> None:
        fields = parse_kv(
            "type=EXECVE msg=audit(1.0:1): argc=2 a0=2F62696E2F7368 a1=2D63",
            "EXECVE",
        )
        self.assertEqual(fields["a0"], "/bin/sh")
        self.assertEqual(fields["a1"], "-c")


class LabelAssignmentTests(unittest.TestCase):
    def test_separated_windows_keep_normal_and_suspicious_labels(self) -> None:
        events = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2026-06-02T19:31:33.000Z",
                        "2026-06-02T19:33:53.000Z",
                    ],
                    utc=True,
                )
            }
        )
        labels = pd.DataFrame(
            [
                {
                    "run_id": "normal-1",
                    "scenario": "normal_activity",
                    "expected_label": "normal",
                    "start_time_utc": "2026-06-02T19:31:32.900Z",
                    "end_time_utc": "2026-06-02T19:31:34.000Z",
                    "description": "normal",
                },
                {
                    "run_id": "suspicious-1",
                    "scenario": "unusual_parent_child",
                    "expected_label": "suspicious",
                    "start_time_utc": "2026-06-02T19:33:52.800Z",
                    "end_time_utc": "2026-06-02T19:33:54.000Z",
                    "description": "suspicious",
                },
            ]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            labels_path = Path(tmp_dir) / "labels.csv"
            labels.to_csv(labels_path, index=False)
            assigned = assign_labels(events, labels_path)

        self.assertEqual(assigned["label"].tolist(), ["normal", "suspicious"])
        self.assertEqual(
            assigned["scenario"].tolist(),
            ["normal_activity", "unusual_parent_child"],
        )


if __name__ == "__main__":
    unittest.main()

