"""Writes per-test report entries and session summary to the session file."""
from __future__ import annotations
import datetime
from pathlib import Path


class Reporter:
    def __init__(self, session_path: Path) -> None:
        self._path = session_path
        self._path.touch()

    def write_entry(
        self,
        *,
        id: int,
        group: str,
        cmd: str,
        status: str,
        exit_code: int | None,
        expected_exit: int | None,
        duration: float,
        output_path: str | None,
        file_count: int | None,
        analysis: str,
        note: str,
    ) -> None:
        exit_display = str(exit_code) if exit_code is not None else "?"
        expected_display = str(expected_exit) if expected_exit is not None else "?"
        if expected_exit is not None and exit_code is not None:
            match_symbol = "✓" if exit_code == expected_exit else "✗"
        else:
            match_symbol = "?"

        lines = [
            f"\n## TEST {id} - {group}: {cmd}",
            f"- **Status**: {status}",
            f"- **Exit**: {exit_display} (expected {expected_display})  {match_symbol}",
            f"- **Duration**: {duration:.1f}s",
        ]
        if output_path:
            lines.append(f"- **Output**: {output_path}")
        if file_count is not None:
            lines.append(f"- **Files created**: {file_count}")
        lines.append(f"- **Auto-analysis**: {analysis}")
        lines.append(f"- **Note**: {note if note else '-'}")

        with self._path.open("a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def finalize(
        self,
        counts: dict[str, dict[str, int]],
        failed_tests: list[str],
    ) -> None:
        passed = sum(v.get("pass", 0) for v in counts.values())
        failed_count = sum(v.get("fail", 0) for v in counts.values())
        skipped = sum(v.get("skip", 0) for v in counts.values())
        total_run = passed + failed_count + skipped

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        rows = [
            "| Group           | Pass | Fail | Skip |",
            "|-----------------|------|------|------|",
        ]
        for group, v in sorted(counts.items()):
            rows.append(
                f"| {group:<15} | {v.get('pass', 0):<4} | {v.get('fail', 0):<4} | {v.get('skip', 0):<4} |"
            )

        header_lines = [
            f"# Capcat Acceptance Test Run - {now}",
            "",
            f"**Passed**: {passed}  **Failed**: {failed_count}  "
            f"**Skipped**: {skipped}  **Total run**: {total_run}",
            "",
        ] + rows

        if failed_tests:
            header_lines += ["", "### Failed Tests"]
            header_lines += [f"- {t}" for t in failed_tests]

        summary = "\n".join(header_lines) + "\n\n---\n"
        existing = self._path.read_text(encoding="utf-8")
        self._path.write_text(summary + existing, encoding="utf-8")
