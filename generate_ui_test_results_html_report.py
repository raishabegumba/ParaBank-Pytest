"""Generate an HTML report listing test results (PASS/FAIL/SKIP/UNKNOWN).

This script reads JSON test artifacts produced by the framework:
- reports/html/test_report_*.json

It then creates:
- reports/html/test_results.html

Each row includes:
- test_name
- status
- duration
- start/end
- test_file
- error_message (if any)

Usage:
  python generate_ui_test_results_html_report.py --reports-dir reports/html
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TestResult:
    test_name: str
    test_file: str
    status: str
    duration: float
    error_message: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def _safe_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    return str(v)


def load_test_results(reports_dir: Path) -> List[TestResult]:
    results: List[TestResult] = []

    if not reports_dir.exists():
        return []

    for json_path in sorted(reports_dir.glob("test_report_*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        status = str(payload.get("status", "unknown")).lower()
        test_name = str(payload.get("test_name") or json_path.stem.replace("test_report_", ""))
        results.append(
            TestResult(
                test_name=test_name,
                test_file=_safe_str(payload.get("test_file")),
                status=status,
                duration=float(payload.get("duration") or 0.0),
                error_message=_safe_str(payload.get("error_message")),
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
                metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
            )
        )

    return results


def _status_badge(status: str) -> str:
    s = (status or "unknown").lower()
    if s == "passed":
        return '<span class="pill pill-pass">PASS</span>'
    if s == "failed":
        return '<span class="pill pill-fail">FAIL</span>'
    if s in {"skipped", "skip"}:
        return '<span class="pill pill-skip">SKIP</span>'
    return f'<span class="pill pill-unknown">{s.upper()}</span>'


def generate_html(results: List[TestResult], output_path: Path, reports_dir: Path) -> str:
    total = len(results)
    counts = {"passed": 0, "failed": 0, "skipped": 0, "unknown": 0}
    for r in results:
        s = (r.status or "unknown").lower()
        if s == "passed":
            counts["passed"] += 1
        elif s == "failed":
            counts["failed"] += 1
        elif s in {"skipped", "skip"}:
            counts["skipped"] += 1
        else:
            counts["unknown"] += 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sort failed first, then passed.
    def sort_key(r: TestResult) -> tuple:
        s = (r.status or "unknown").lower()
        priority = 0
        if s == "failed":
            priority = 0
        elif s == "passed":
            priority = 1
        elif s in {"skipped", "skip"}:
            priority = 2
        else:
            priority = 3
        return (priority, r.test_name.lower())

    rows: List[str] = []
    for r in sorted(results, key=sort_key):
        err_preview = (r.error_message or "").strip()
        if len(err_preview) > 160:
            err_preview = err_preview[:160] + "..."
        rows.append(
            """
            <tr>
              <td><code>{test_name}</code></td>
              <td>{status_badge}</td>
              <td>{duration:.3f}s</td>
              <td>{start_time}</td>
              <td>{end_time}</td>
              <td>{test_file}</td>
              <td>{error_message}</td>
            </tr>
            """.format(
                test_name=r.test_name,
                status_badge=_status_badge(r.status),
                duration=r.duration,
                start_time=r.start_time or "",
                end_time=r.end_time or "",
                test_file=r.test_file,
                error_message=err_preview or "",
            )
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>UI Test Results</title>
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

    .pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 12px; }}
    .pill-pass {{ background: #dcfce7; color: #166534; }}
    .pill-fail {{ background: #fee2e2; color: #991b1b; }}
    .pill-skip {{ background: #fef9c3; color: #854d0e; }}
    .pill-unknown {{ background: #e5e7eb; color: #111827; }}

    .note {{ margin-top: 10px; font-size: 12px; color: #6b7280; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🧾 UI Test Results</h1>
    <div class="meta">Generated on {now} | Source: <code>{reports_dir.as_posix()}</code></div>
  </div>

  <div class="stats">
    <div class="card"><div class="k">Total Tests</div><div class="v">{total}</div></div>
    <div class="card"><div class="k">Passed</div><div class="v">{counts['passed']}</div></div>
    <div class="card"><div class="k">Failed</div><div class="v">{counts['failed']}</div></div>
    <div class="card"><div class="k">Skipped</div><div class="v">{counts['skipped']}</div></div>
    <div class="card"><div class="k">Unknown</div><div class="v">{counts['unknown']}</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Test Name</th>
        <th>Status</th>
        <th>Duration</th>
        <th>Start</th>
        <th>End</th>
        <th>Test File</th>
        <th>Error</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows) if rows else '<tr><td colspan="7">No test_report_*.json artifacts found or report artifacts do not include status.</td></tr>'}
    </tbody>
  </table>

  <div class="note">Artifacts used: <code>reports/html/test_report_*.json</code>. Ensure you run the UI test subset before generating this report.</div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default="reports/html", help="Directory containing test_report_*.json")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    results = load_test_results(reports_dir)

    output_path = reports_dir / "test_results.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_html(results, output_path=output_path, reports_dir=reports_dir)

    print(f"UI test results HTML report generated: {output_path}")
    print(f"Total tests found in artifacts: {len(results)}")


if __name__ == "__main__":
    main()

