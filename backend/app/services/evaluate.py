from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import ROOT
from app.db import get_conn
from app.services.answer import answer_question

QUESTIONS_PATH = ROOT / "evaluation" / "questions.json"


def _contains_any(text: str, needles: list[str]) -> bool:
    blob = text or ""
    return any(n.lower() in blob.lower() for n in needles)


async def _one(item: dict) -> dict:
    result = await answer_question(item["question"], conversation_id=None)
    status = result.get("status")
    expect = item.get("expect", "grounded")
    blob = " ".join(
        [
            result.get("source_quote") or "",
            result.get("explanation") or "",
            " ".join(p.get("excerpt") or "" for p in result.get("source_passages") or []),
        ]
    )
    pages = [c.get("page") for c in result.get("citations") or []]
    passed = True
    reasons = []
    if expect == "grounded":
        if status not in {"grounded", "partial"}:
            passed = False
            reasons.append(f"status={status}")
        keywords = item.get("keywords") or []
        if keywords and not _contains_any(blob, keywords):
            passed = False
            reasons.append("keywords_missing")
        expected_pages = item.get("pages") or []
        if expected_pages and not any(p in pages for p in expected_pages):
            # page hint is soft if keywords hit; hard if marked strict_page
            if item.get("strict_page"):
                passed = False
                reasons.append(f"pages={pages}")
            else:
                reasons.append(f"page_soft_miss={pages}")
        quote = result.get("source_quote") or ""
        if quote:
            from app.db import get_conn as gc

            with gc() as conn:
                ok = False
                for page in pages or []:
                    row = conn.execute("SELECT original_ocr, cleaned_text FROM pages WHERE page_number = ?", (page,)).fetchone()
                    if not row:
                        continue
                    src = (row["original_ocr"] or "") + "\n" + (row["cleaned_text"] or "")
                    fragment = quote[:80].replace("…", "").strip()
                    if fragment and fragment in src:
                        ok = True
                if not ok and pages:
                    passed = False
                    reasons.append("quote_not_in_page")
        suggestion = result.get("pure_soul_suggestion") or ""
        if suggestion and "स्वामीजी कहते हैं" in suggestion:
            passed = False
            reasons.append("suggestion_attributed")
        if item.get("language") and result.get("language") != item["language"]:
            passed = False
            reasons.append(f"lang={result.get('language')}")
    elif expect == "insufficient":
        if status != "insufficient":
            passed = False
            reasons.append(f"status={status}")
        if result.get("source_quote"):
            passed = False
            reasons.append("invented_quote")
    elif expect == "refused_full_text":
        if status != "refused_full_text":
            passed = False
            reasons.append(f"status={status}")
    elif expect == "refused_persona":
        if status != "refused_persona":
            passed = False
            reasons.append(f"status={status}")
    return {
        "id": item.get("id"),
        "question": item["question"],
        "expect": expect,
        "status": status,
        "pages": pages,
        "passed": passed,
        "reasons": reasons,
        "confidence": result.get("confidence"),
        "language": result.get("language"),
    }


def run() -> dict:
    items = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = asyncio.get_event_loop().run_until_complete(_all(items)) if False else None
    results = asyncio.run(_all(items))
    passed = sum(1 for r in results if r["passed"])
    by_expect: dict[str, dict] = {}
    for r in results:
        bucket = by_expect.setdefault(r["expect"], {"n": 0, "passed": 0})
        bucket["n"] += 1
        bucket["passed"] += int(r["passed"])
    grounded = [r for r in results if r["expect"] == "grounded"]
    refused = [r for r in results if r["expect"] != "grounded"]
    hallucination_fail = [r for r in refused if not r["passed"]]
    report = {
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0,
        "by_expect": by_expect,
        "grounded_pass_rate": round(sum(r["passed"] for r in grounded) / len(grounded), 4) if grounded else None,
        "refusal_pass_rate": round(sum(r["passed"] for r in refused) / len(refused), 4) if refused else None,
        "hallucination_failures": len(hallucination_fail),
        "results": results,
    }
    with get_conn() as conn:
        for r in results:
            conn.execute(
                """
                INSERT INTO evaluation_results(id, run_id, question_id, question, expected, actual_status, passed, detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    report["run_id"],
                    r["id"],
                    r["question"],
                    r["expect"],
                    r["status"],
                    1 if r["passed"] else 0,
                    json.dumps(r, ensure_ascii=False),
                    report["created_at"],
                ),
            )
    out = ROOT / "evaluation" / "latest_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


async def _all(items: list[dict]) -> list[dict]:
    out = []
    for item in items:
        out.append(await _one(item))
    return out
