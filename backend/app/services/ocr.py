"""OCR adapter for Hindi / Devanagari page images.

The sandbox cannot download the Drive scans, and Tesseract may be absent.
This module never invents text. If OCR cannot run, it fails loudly.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("aadhyatmik.ocr")


class OCRUnavailable(RuntimeError):
    pass


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def ocr_image(path: Path, lang: str = "hin+eng") -> dict:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if not tesseract_available():
        log.error("ocr_unavailable path=%s", path)
        raise OCRUnavailable(
            "Tesseract is not installed. Install tesseract-ocr and tesseract-ocr-hin, "
            "or ingest a JSON text export. No text was invented."
        )
    cmd = [
        "tesseract",
        str(path),
        "stdout",
        "-l",
        lang,
        "--psm",
        "6",
        "tsv",
    ]
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired as exc:
        log.exception("ocr_timeout path=%s", path)
        raise OCRUnavailable("OCR timed out") from exc
    if proc.returncode != 0:
        log.error("ocr_failed path=%s stderr=%s", path, proc.stderr[-500:])
        raise OCRUnavailable(proc.stderr.strip() or "tesseract failed")
    lines = []
    confs = []
    for row in proc.stdout.splitlines()[1:]:
        cols = row.split("\t")
        if len(cols) < 12:
            continue
        word = cols[11].strip()
        try:
            conf = float(cols[10])
        except ValueError:
            conf = -1
        if word:
            lines.append(word)
            if conf >= 0:
                confs.append(conf)
    text = " ".join(lines)
    confidence = (sum(confs) / len(confs) / 100.0) if confs else None
    return {
        "original_ocr": text,
        "confidence": confidence,
        "engine": "tesseract",
        "lang": lang,
        "word_count": len(lines),
    }
