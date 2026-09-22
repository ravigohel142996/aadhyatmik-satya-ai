from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.db import get_conn, migrate
from app.services.answer import answer_question
from app.services.index import INDEX
from app.services.ingest import corpus_ready, ingest_chunks_file, ingest_records, load_index_from_db
from app.services.llm import llm_configured
from app.services.ocr import OCRUnavailable, ocr_image, tesseract_available
from app.services.plates import render_text_plate
from app.services.textutil import expand_query

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("aadhyatmik.api")

app = FastAPI(
    title="Aadhyatmik Satya AI",
    description="Source-grounded guide to the granth Aadhyatmik Satya. Answers stay with indexed pages.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.e2b\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_buckets: dict[str, deque] = defaultdict(deque)


class AskBody(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    conversation_id: str | None = None


class IngestJsonBody(BaseModel):
    pages: list[dict] = Field(default_factory=list)


def _rate_limit(request: Request, limit: int | None = None) -> None:
    limit = limit or settings.rate_limit_per_minute
    ip = request.client.host if request.client else "local"
    now = time.time()
    bucket = _buckets[ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    bucket.append(now)


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not x_admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Admin token required.")


def _drive_image(file_id: str | None) -> str | None:
    if not file_id:
        return None
    return f"https://lh3.googleusercontent.com/d/{file_id}=w1600"


def _drive_view(file_id: str | None) -> str | None:
    if not file_id:
        return None
    return f"https://drive.google.com/file/d/{file_id}/view"


@app.on_event("startup")
def startup() -> None:
    migrate()
    if corpus_ready():
        n = load_index_from_db()
        log.info("index_loaded chunks=%s", n)
        return
    path = settings.book_chunks_path
    if not path.exists():
        log.warning("corpus_missing path=%s", path)
        return
    status = ingest_chunks_file(path)
    log.info("startup_ingest %s", status)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    log.exception("unhandled path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "The guide could not complete this request."})


@app.get("/api/health")
def health():
    with get_conn() as conn:
        pages = conn.execute("SELECT COUNT(*) AS n FROM pages").fetchone()["n"]
        chunks = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()["n"]
        book = conn.execute("SELECT * FROM books LIMIT 1").fetchone()
    return {
        "status": "ok",
        "book_indexed": bool(book),
        "pages_indexed": pages,
        "chunks_indexed": chunks,
        "vectors_loaded": len(INDEX.chunks),
        "embedding_provider": INDEX.provider,
        "embedding_model": INDEX.model,
        "llm_configured": llm_configured(),
        "ocr_available": tesseract_available(),
        "vector_db": settings.vector_db_url or "local-sqlite",
        "database": "sqlite" if settings.database_url.startswith("sqlite") else "external",
    }


@app.get("/api/book")
def book():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM books LIMIT 1").fetchone()
        chapters = conn.execute(
            """
            SELECT chapter, MIN(page_number) AS start_page, MAX(page_number) AS end_page, COUNT(*) AS pages
            FROM pages WHERE chapter IS NOT NULL
            GROUP BY chapter ORDER BY start_page
            """
        ).fetchall()
    if not row:
        raise HTTPException(404, "Book index is empty.")
    return {
        "id": row["id"],
        "title": row["title"],
        "title_hi": row["title_hi"],
        "author": row["author"],
        "author_hi": row["author_hi"],
        "source_note": row["source_note"],
        "pages_indexed": row["page_count_indexed"],
        "page_min": row["page_min"],
        "page_max": row["page_max"],
        "missing_pages": json.loads(row["missing_pages"] or "[]"),
        "chunks_indexed": row["chunk_count"],
        "product_url": settings.product_url,
        "cover": {
            "drive_file_id": settings.cover_drive_id,
            "image_url": _drive_image(settings.cover_drive_id),
            "fallback": "/art/cover-fallback.jpg",
            "note": "Drive cover is the uploaded source photo when the browser can load it. Local artwork is a fallback, not the printed cover.",
        },
        "chapters": [dict(c) for c in chapters],
        "links": {
            "gurutattva": settings.gurutattva_url,
            "tattvatrends": settings.tattvatrends_url,
            "product": settings.product_url,
            "source_folder": f"https://drive.google.com/drive/folders/{settings.drive_folder_id}",
        },
    }


@app.post("/api/ask")
async def ask(body: AskBody, request: Request):
    _rate_limit(request)
    if not INDEX.chunks:
        raise HTTPException(503, "The granth index is not ready.")
    return await answer_question(body.question, body.conversation_id)


@app.get("/api/search")
def search(q: str, request: Request, limit: int = 8):
    _rate_limit(request, 60)
    if not q.strip():
        raise HTTPException(400, "Missing query.")
    tokens, weights = expand_query(q)
    hits = INDEX.search(q, weights or {q: 1.0}, limit=min(limit, 12))
    return {
        "query": q,
        "count": len(hits),
        "results": [
            {
                "page": h["chunk"].page_number,
                "chunk_id": h["chunk"].id,
                "chapter": h["chunk"].chapter,
                "score": h["score"],
                "coverage": h["coverage"],
                "hits": h["hits"],
                "excerpt": (h["chunk"].text or "")[:280],
            }
            for h in hits
        ],
    }


@app.get("/api/source/{page}")
def source_page(page: int, request: Request):
    _rate_limit(request, 80)
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM pages WHERE page_number = ?", (page,)).fetchone()
    if not row:
        raise HTTPException(404, "This page is not in the indexed corpus.")
    return {
        "page": row["page_number"],
        "book": settings.book_title,
        "chapter": row["chapter"],
        "text": row["cleaned_text"],
        "original_ocr": row["original_ocr"],
        "ocr_confidence": row["ocr_confidence"],
        "ocr_note": row["ocr_note"],
        "verification": "OCR/source text requires verification.",
        "image": {
            "kind": "drive_scan" if row["drive_file_id"] else "text_plate",
            "drive_file_id": row["drive_file_id"],
            "scan_url": _drive_image(row["drive_file_id"]),
            "view_url": _drive_view(row["drive_file_id"]),
            "plate_url": f"/api/source/{page}/plate",
            "folder_url": f"https://drive.google.com/drive/folders/{settings.drive_folder_id}",
            "filename": f"Page_{page:03d}.jpg",
        },
    }


@app.get("/api/source/{page}/plate")
def source_plate(page: int, highlight: str | None = None):
    with get_conn() as conn:
        row = conn.execute("SELECT cleaned_text FROM pages WHERE page_number = ?", (page,)).fetchone()
    if not row:
        raise HTTPException(404, "This page is not in the indexed corpus.")
    path = render_text_plate(page, row["cleaned_text"] or "", highlight)
    return FileResponse(path, media_type="image/png")


@app.get("/api/citations/{answer_id}")
def citations(answer_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT page_number, chunk_id, book_title, chapter, excerpt FROM citations WHERE answer_id = ?",
            (answer_id,),
        ).fetchall()
        trace = conn.execute(
            "SELECT status, retrieval_count, page_ids, latency_ms, created_at FROM retrieval_traces WHERE answer_id = ?",
            (answer_id,),
        ).fetchone()
    if not rows and not trace:
        raise HTTPException(404, "No citation record for this answer.")
    return {
        "answer_id": answer_id,
        "citations": [dict(r) for r in rows],
        "trace": dict(trace) if trace else None,
    }


@app.post("/api/ingest")
async def ingest(
    request: Request,
    file: UploadFile | None = File(default=None),
    page_number: int | None = Form(default=None),
    x_admin_token: str | None = Header(default=None),
):
    require_admin(x_admin_token)
    _rate_limit(request, 10)
    job_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO ingest_jobs(id, status, detail, created_at) VALUES (?, ?, ?, ?)",
            (job_id, "running", file.filename if file else "json", datetime.now(timezone.utc).isoformat()),
        )
    try:
        if file is None:
            raise HTTPException(400, "Upload a JSON corpus, a PDF, or a page image.")
        dest = settings.drive_catalog_path.parent / "uploads" / f"{job_id}-{Path(file.filename or 'upload').name}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = await file.read()
        dest.write_bytes(data)
        name = (file.filename or "").lower()
        if name.endswith(".json"):
            status = ingest_chunks_file(dest)
        elif name.endswith(".pdf"):
            status = _ingest_pdf(dest)
        elif name.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")):
            if page_number is None:
                raise HTTPException(400, "page_number is required for a single image.")
            status = _ingest_image(dest, page_number)
        else:
            raise HTTPException(400, "Unsupported file. Use JSON, PDF, or an image.")
        with get_conn() as conn:
            conn.execute(
                "UPDATE ingest_jobs SET status = ?, detail = ?, finished_at = ? WHERE id = ?",
                ("complete", json.dumps(status), datetime.now(timezone.utc).isoformat(), job_id),
            )
        return {"job_id": job_id, "status": status}
    except HTTPException:
        raise
    except OCRUnavailable as exc:
        log.error("ingest_ocr_unavailable %s", exc)
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        log.exception("ingest_failed")
        with get_conn() as conn:
            conn.execute(
                "UPDATE ingest_jobs SET status = ?, detail = ?, finished_at = ? WHERE id = ?",
                ("failed", str(exc)[:500], datetime.now(timezone.utc).isoformat(), job_id),
            )
        raise HTTPException(400, "Ingest failed. Check the file format and server logs.") from exc


def _ingest_pdf(path: Path) -> dict:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise HTTPException(503, "pypdf is not installed.") from exc
    reader = PdfReader(str(path))
    pages = {}
    for i, page in enumerate(reader.pages, start=1):
        pages[i] = page.extract_text() or ""
    if not any(pages.values()):
        raise HTTPException(
            422,
            "No extractable text in this PDF. It may be a scan. Upload page images for OCR, or a JSON text export.",
        )
    return ingest_records(pages, path.name)


def _ingest_image(path: Path, page_number: int) -> dict:
    result = ocr_image(path)
    with get_conn() as conn:
        existing = {
            row["page_number"]: row["original_ocr"]
            for row in conn.execute("SELECT page_number, original_ocr FROM pages").fetchall()
        }
    existing[page_number] = result["original_ocr"]
    status = ingest_records(existing, path.name)
    with get_conn() as conn:
        conn.execute(
            "UPDATE pages SET image_path = ?, ocr_confidence = ?, ocr_note = ? WHERE page_number = ?",
            (str(path), result["confidence"], f"tesseract:{result['engine']}", page_number),
        )
    status["ocr_confidence"] = result["confidence"]
    return status


@app.get("/api/admin/overview")
def admin_overview(_: None = Depends(require_admin)):
    with get_conn() as conn:
        book = conn.execute("SELECT * FROM books LIMIT 1").fetchone()
        failed = conn.execute("SELECT COUNT(*) AS n FROM failed_retrievals").fetchone()["n"]
        jobs = conn.execute("SELECT * FROM ingest_jobs ORDER BY created_at DESC LIMIT 8").fetchall()
    return {
        "book": dict(book) if book else None,
        "failed_retrievals": failed,
        "vectors_loaded": len(INDEX.chunks),
        "jobs": [dict(j) for j in jobs],
        "ocr_available": tesseract_available(),
        "llm_configured": llm_configured(),
    }


@app.get("/api/admin/pages")
def admin_pages(offset: int = 0, limit: int = 40, _: None = Depends(require_admin)):
    limit = min(limit, 100)
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT page_number, chapter, char_count, ocr_confidence, ocr_note, drive_file_id,
                   substr(cleaned_text, 1, 180) AS preview
            FROM pages ORDER BY page_number LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) AS n FROM pages").fetchone()["n"]
    return {"total": total, "pages": [dict(r) for r in rows]}


@app.get("/api/admin/pages/{page}")
def admin_page(page: int, _: None = Depends(require_admin)):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM pages WHERE page_number = ?", (page,)).fetchone()
        chunks = conn.execute(
            "SELECT id, chunk_index, substr(text, 1, 400) AS preview FROM chunks WHERE page_number = ? ORDER BY chunk_index",
            (page,),
        ).fetchall()
    if not row:
        raise HTTPException(404, "Page not found.")
    data = dict(row)
    data.pop("embedding", None)
    return {"page": data, "chunks": [dict(c) for c in chunks]}


@app.get("/api/admin/chunks")
def admin_chunks(q: str = "", offset: int = 0, limit: int = 30, _: None = Depends(require_admin)):
    limit = min(limit, 80)
    with get_conn() as conn:
        if q:
            rows = conn.execute(
                """
                SELECT c.id, c.page_number, c.chapter, substr(c.text, 1, 240) AS preview
                FROM chunks_fts f JOIN chunks c ON c.id = f.chunk_id
                WHERE chunks_fts MATCH ?
                LIMIT ? OFFSET ?
                """,
                (q, limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, page_number, chapter, substr(text, 1, 240) AS preview FROM chunks ORDER BY page_number, chunk_index LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
    return {"chunks": [dict(r) for r in rows]}


@app.get("/api/admin/failed")
def admin_failed(_: None = Depends(require_admin)):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT question, reason, answer_id, created_at FROM failed_retrievals ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return {"failed": [dict(r) for r in rows]}


@app.post("/api/admin/reindex")
def admin_reindex(_: None = Depends(require_admin)):
    path = settings.book_chunks_path
    if not path.exists():
        raise HTTPException(404, "book_chunks.json is missing.")
    status = ingest_chunks_file(path)
    return status


@app.get("/api/admin/trace/{answer_id}")
def admin_trace(answer_id: str, _: None = Depends(require_admin)):
    with get_conn() as conn:
        trace = conn.execute("SELECT * FROM retrieval_traces WHERE answer_id = ?", (answer_id,)).fetchone()
        citations = conn.execute("SELECT * FROM citations WHERE answer_id = ?", (answer_id,)).fetchall()
    if not trace:
        raise HTTPException(404, "Trace not found.")
    return {"trace": dict(trace), "citations": [dict(c) for c in citations]}


@app.post("/api/admin/evaluation/run")
def admin_eval(_: None = Depends(require_admin)):
    from app.services.evaluate import run as run_eval

    return run_eval()
