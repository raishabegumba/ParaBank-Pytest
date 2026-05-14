"""Generate an HTML report listing all PASSed testcases.

This reads the JSON test artifacts produced by the framework:
- reports/html/test_report_<test_name>.json

It then creates:
- reports/html/passed_testcases.html

Usage:
  python generate_pass_html_report.py

Optional:
  python generate_pass_html_report.py --reports-dir reports/html
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PassedTest:
    test_name: str
    test_file: str
    status: str
    duration: float
    error_message: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def _safe_get(d: Dict[str, Any], key: str, default: Any = "") -> Any:
    return d.get(key, default)


def load_passed_tests(reports_dir: Path) -> List[PassedTest]:
    passed: List[PassedTest] = []

    if not reports_dir.exists():
        # Allow running even if the framework didn't generate HTML/JSON report artifacts yet.
        return []


    for json_path in sorted(reports_dir.glob("test_report_*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        status = str(payload.get("status", "unknown")).lower()
        if status != "passed":
            continue

        test_name = str(payload.get("test_name") or json_path.stem.replace("test_report_", ""))
        passed.append(
            PassedTest(
                test_name=test_name,
                test_file=str(payload.get("test_file", "")),
                status=status,
                duration=float(payload.get("duration") or 0.0),
                error_message=str(payload.get("error_message") or ""),
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
                metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
            )
        )

    return passed


def generate_html(passed_tests: List[PassedTest], output_path: Path, reports_dir: Path) -> str:
    total = len(passed_tests)
    total_duration = sum(t.duration for t in passed_tests)
    avg_duration = (total_duration / total) if total else 0.0

    rows = []
    for t in sorted(passed_tests, key=lambda x: x.test_name.lower()):
        err_preview = (t.error_message or "").strip()
        if len(err_preview) > 120:
            err_preview = err_preview[:120] + "..."

        rows.append(
            """
            <tr>
              <td><code>{test_name}</code></td>
              <td>{duration:.3f}s</td>
              <td>{start_time}</td>
              <td>{end_time}</td>
              <td>{test_file}</td>
              <td>{error_message}</td>
            </tr>
            """.format(
                test_name=t.test_name,
                duration=t.duration,
                start_time=(t.start_time or ""),
                end_time=(t.end_time or ""),
                test_file=t.test_file,
                error_message=(err_preview or ""),
            )
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Passed Testcases Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f7f7f7; }}
    .header {{ background: #111827; color: #fff; padding: 18px 20px; border-radius: 10px; }}
    h1 {{ margin: 0 0 6px 0; font-size: 20px; }}
    .meta {{ opacity: 0.85; font-size: 13px; }}
    .stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 14px 0; }}
    .card {{ background: #ffffff; padding: 14px 16px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .card .k {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
    .card .v {{ font-size: 18px; font-weight: 700; margin-top: 6px; }}

    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; font-size: 12px; color: #374151; }}
    td {{ font-size: 13px; color: #111827; }}
    tr:hover td {{ background: #fafafa; }}

    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; }}
    .pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 12px; background: #dcfce7; color: #166534; }}

    .note {{ margin-top: 10px; font-size: 12px; color: #6b7280; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>✅ Passed Testcases</h1>
    <div class="meta">Generated on {now} | Source: <code>{reports_dir.as_posix()}</code></div>
  </div>

  <div class="stats">
    <div class="card"><div class="k">Total Passed</div><div class="v">{total}</div></div>
    <div class="card"><div class="k">Total Duration</div><div class="v">{total_duration:.3f}s</div></div>
    <div class="card"><div class="k">Average Duration</div><div class="v">{avg_duration:.3f}s</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Test Name</th>
        <th>Duration</th>
        <th>Start</th>
        <th>End</th>
        <th>Test File</th>
        <th>Error (should be empty)</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows) if rows else '<tr><td colspan="6">No passed tests found. Ensure test_report_*.json artifacts exist and status is "passed".</td></tr>'}
    </tbody>
  </table>

  <div class="note">Tip: run your test suite first so the framework generates <code>reports/html/test_report_*.json</code> artifacts.</div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default="reports/html", help="Directory containing test_report_*.json")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    passed_tests = load_passed_tests(reports_dir)

    output_path = reports_dir / "passed_testcases.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_html(passed_tests, output_path=output_path, reports_dir=reports_dir)


    print(f"Passed testcases HTML report generated: {output_path}")
    print(f"Total passed tests found: {len(passed_tests)}")


if __name__ == "__main__":
    main()

