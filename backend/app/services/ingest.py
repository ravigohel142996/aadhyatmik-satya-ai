from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.db import get_conn, reset_corpus
from app.services.index import INDEX, ChunkRec, embed_text, pack_vec
from app.services.textutil import clean_whitespace, strip_invisibles

log = logging.getLogger("aadhyatmik.ingest")

BOOK_ID = "aadhyatmik-satya"

CHAPTER_TITLES = [
    "समर्पण ध्यान का मिशन",
    "समर्पण ध्यान के सूत्र",
    "सद्गुरु एक माध्यम है",
    "आत्मसाक्षात्कार एक दूसरा जन्म",
    "आत्मसाक्षात्कार",
    "चित्त मोक्ष का द्वार है",
    "श्री गुरुशक्ति धाम",
    "गुरुशक्ति धाम",
    "आदर्श साधक",
    "आभामण्डल",
    "आभामंडल",
    "समर्पण आश्रम",
    "समर्पण ध्यान",
    "परमात्मा सर्वत्र है",
    "मनुष्य धर्म",
    "समाधि",
]

FRONT_MATTER = [
    ("अनुक्रमणिका", "अनुक्रमणिका"),
    ("अनुरोध", "अनुरोध"),
    ("भूमिका", "भूमिका"),
    ("परिचय", "परिचय"),
    ("समर्पण (हिमालयीन)", "समर्पण ध्यानयोग का परिचय"),
    (":: समर्पण ::", "समर्पण ध्यानयोग का परिचय"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_drive_catalog() -> dict[int, str]:
    path = settings.drive_catalog_path
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        log.exception("drive_catalog_invalid")
        return {}
    out = {}
    for key, value in raw.items():
        try:
            out[int(key)] = str(value)
        except (TypeError, ValueError):
            continue
    return out


def detect_chapter(page_number: int, text: str, current: str | None) -> str | None:
    head = "\n".join(text.splitlines()[:4])
    short_lines = [ln.strip() for ln in text.splitlines()[:3] if ln.strip()]
    blob = " ".join(short_lines)
    if len(blob) <= 80:
        for title in CHAPTER_TITLES:
            if title in blob and len(blob) <= len(title) + 24:
                return title
    for needle, label in FRONT_MATTER:
        if needle in head[:180] and page_number <= 12:
            return label
    if page_number <= 6 and not current:
        return "प्रारंभिक पृष्ठ"
    if page_number >= 253:
        return current or "परिशिष्ट"
    return current


def script_note(text: str) -> tuple[float | None, str]:
    if not text:
        return None, "empty"
    dev = len(re.findall(r"[\u0900-\u097F]", text))
    letters = len(re.findall(r"[A-Za-z\u0900-\u097F\u0A80-\u0AFF]", text)) or 1
    ratio = dev / letters
    # Confidence was not produced by the upstream extractor. Do not invent one.
    if ratio < 0.25 and len(text) > 80:
        return None, "low_devanagari_ratio_needs_verification"
    return None, "ocr_confidence_not_supplied_by_source"


def ingest_records(pages: dict[int, str], source_name: str) -> dict:
    catalog = load_drive_catalog()
    created = now()
    chapter = None
    page_rows = []
    chunk_rows = []
    for page_number in sorted(pages):
        original = strip_invisibles(pages[page_number] or "")
        cleaned = clean_whitespace(original)
        chapter = detect_chapter(page_number, cleaned, chapter)
        conf, note = script_note(cleaned)
        page_id = f"{BOOK_ID}-p{page_number}"
        drive_id = catalog.get(page_number)
        page_rows.append(
            {
                "id": page_id,
                "book_id": BOOK_ID,
                "page_number": page_number,
                "image_path": None,
                "drive_file_id": drive_id,
                "source_file": source_name,
                "original_ocr": original,
                "cleaned_text": cleaned,
                "ocr_confidence": conf,
                "ocr_note": note,
                "chapter": chapter,
                "section_title": chapter,
                "char_count": len(cleaned),
                "created_at": created,
            }
        )
        # Prefer paragraph / danda windows of roughly 420-700 characters.
        windows = semantic_windows(cleaned)
        if not windows and cleaned:
            windows = [cleaned]
        for idx, window in enumerate(windows, start=1):
            chunk_id = f"{page_id}-c{idx}"
            vec = embed_text(window)
            chunk_rows.append(
                {
                    "id": chunk_id,
                    "page_id": page_id,
                    "book_id": BOOK_ID,
                    "page_number": page_number,
                    "chunk_index": idx,
                    "text": window,
                    "cleaned_text": window,
                    "chapter": chapter,
                    "source_file": source_name,
                    "source_image": f"Page_{page_number:03d}",
                    "embedding": pack_vec(vec),
                    "created_at": created,
                    "vec": vec,
                }
            )
    present = set(pages)
    if present:
        missing = [n for n in range(min(present), max(present) + 1) if n not in present]
    else:
        missing = []
    with get_conn() as conn:
        reset_corpus(conn)
        conn.execute(
            """
            INSERT INTO books(id, title, title_hi, author, author_hi, source_note,
              page_count_indexed, page_min, page_max, missing_pages, chunk_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                BOOK_ID,
                settings.book_title,
                settings.book_title_hi,
                settings.author,
                settings.author_hi,
                "Indexed from the local extracted corpus (book_chunks.json) aligned to Drive scan page numbers. "
                "Not a verified 270-page ingest. OCR confidence was not supplied by the source extract.",
                len(present),
                min(present) if present else None,
                max(present) if present else None,
                json.dumps(missing),
                len(chunk_rows),
                created,
            ),
        )
        conn.executemany(
            """
            INSERT INTO pages(id, book_id, page_number, image_path, drive_file_id, source_file,
              original_ocr, cleaned_text, ocr_confidence, ocr_note, chapter, section_title, char_count, created_at)
            VALUES (:id, :book_id, :page_number, :image_path, :drive_file_id, :source_file,
              :original_ocr, :cleaned_text, :ocr_confidence, :ocr_note, :chapter, :section_title, :char_count, :created_at)
            """,
            page_rows,
        )
        conn.executemany(
            """
            INSERT INTO chunks(id, page_id, book_id, page_number, chunk_index, text, cleaned_text,
              chapter, source_file, source_image, embedding, created_at)
            VALUES (:id, :page_id, :book_id, :page_number, :chunk_index, :text, :cleaned_text,
              :chapter, :source_file, :source_image, :embedding, :created_at)
            """,
            chunk_rows,
        )
        conn.executemany(
            "INSERT INTO chunks_fts(chunk_id, page_number, chapter, text) VALUES (?, ?, ?, ?)",
            [(c["id"], c["page_number"], c["chapter"] or "", c["cleaned_text"]) for c in chunk_rows],
        )
    recs = [
        ChunkRec(
            id=c["id"],
            page_number=c["page_number"],
            page_id=c["page_id"],
            text=c["text"],
            cleaned_text=c["cleaned_text"],
            chapter=c["chapter"],
            source_image=c["source_image"],
            vec=c["vec"],
        )
        for c in chunk_rows
    ]
    INDEX.build(recs, settings.embedding_provider, settings.embedding_model)
    status = {
        "book_id": BOOK_ID,
        "pages_indexed": len(present),
        "page_min": min(present) if present else None,
        "page_max": max(present) if present else None,
        "missing_pages": missing,
        "chunks_indexed": len(chunk_rows),
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "vector_count": len(recs),
        "drive_links": sum(1 for p in page_rows if p["drive_file_id"]),
        "source": source_name,
        "indexed_at": created,
        "note": "270 printed pages were not verified. Indexed text pages are those present in the extracted corpus.",
    }
    (settings.drive_catalog_path.parent / "index_status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("ingest_complete pages=%s chunks=%s", len(present), len(chunk_rows))
    return status


def semantic_windows(text: str, target: int = 520, overlap_sentences: int = 1) -> list[str]:
    text = clean_whitespace(text)
    if not text:
        return []
    sentences = re.split(r"(?<=[।!?])\s+|\n+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return [text]
    windows = []
    buf: list[str] = []
    size = 0
    for sent in sentences:
        if size + len(sent) > target and buf:
            windows.append(" ".join(buf))
            buf = buf[-overlap_sentences:] if overlap_sentences else []
            size = sum(len(s) + 1 for s in buf)
        buf.append(sent)
        size += len(sent) + 1
    if buf:
        windows.append(" ".join(buf))
    # drop near-duplicates created by tiny pages
    deduped = []
    for w in windows:
        if not deduped or w != deduped[-1]:
            deduped.append(w)
    return deduped


def ingest_chunks_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    pages: dict[int, list[str]] = {}
    if isinstance(data, list) and data and "chunk_id" in data[0]:
        for item in data:
            pages.setdefault(int(item["page"]), []).append(item.get("text") or "")
        joined = {p: "\n".join(parts) for p, parts in pages.items()}
    elif isinstance(data, list) and data and "page" in data[0] and "text" in data[0]:
        joined = {}
        for item in data:
            p = int(item["page"])
            joined[p] = (joined.get(p, "") + "\n" + (item.get("text") or "")).strip()
    else:
        raise ValueError("Unsupported corpus JSON. Expected chunk or page records.")
    return ingest_records(joined, path.name)


def corpus_ready() -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return bool(row and row["n"] > 0)


def load_index_from_db() -> int:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, page_id, page_number, text, cleaned_text, chapter, source_image, embedding FROM chunks ORDER BY page_number, chunk_index"
        ).fetchall()
    recs = []
    for row in rows:
        vec = None
        if row["embedding"]:
            from app.services.index import unpack_vec

            vec = unpack_vec(row["embedding"])
        recs.append(
            ChunkRec(
                id=row["id"],
                page_number=row["page_number"],
                page_id=row["page_id"],
                text=row["text"],
                cleaned_text=row["cleaned_text"],
                chapter=row["chapter"],
                source_image=row["source_image"],
                vec=vec,
            )
        )
    INDEX.build(recs, settings.embedding_provider, settings.embedding_model)
    return len(recs)
