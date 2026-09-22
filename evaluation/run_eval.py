#!/usr/bin/env python3
"""Run the grounded-answer evaluation suite and print a short report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import migrate  # noqa: E402
from app.services.evaluate import run  # noqa: E402
from app.services.ingest import corpus_ready, ingest_chunks_file, load_index_from_db  # noqa: E402
from app.config import settings  # noqa: E402


def main() -> int:
    migrate()
    if corpus_ready():
        load_index_from_db()
    else:
        ingest_chunks_file(settings.book_chunks_path)
    report = run()
    summary = {k: report[k] for k in ("total", "passed", "failed", "pass_rate", "grounded_pass_rate", "refusal_pass_rate", "hallucination_failures")}
    print(json.dumps(summary, indent=2))
    failed = [r for r in report["results"] if not r["passed"]]
    for row in failed:
        print(f"FAIL {row['id']} {row['status']} {row['reasons']} :: {row['question']}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
