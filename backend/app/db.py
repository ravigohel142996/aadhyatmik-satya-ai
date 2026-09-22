from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from app.config import DATA_DIR, settings

_lock = threading.RLock()
_ready = False

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  title_hi TEXT,
  author TEXT NOT NULL,
  author_hi TEXT,
  source_note TEXT,
  page_count_indexed INTEGER DEFAULT 0,
  page_min INTEGER,
  page_max INTEGER,
  missing_pages TEXT,
  chunk_count INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pages (
  id TEXT PRIMARY KEY,
  book_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  image_path TEXT,
  drive_file_id TEXT,
  source_file TEXT,
  original_ocr TEXT,
  cleaned_text TEXT,
  ocr_confidence REAL,
  ocr_note TEXT,
  chapter TEXT,
  section_title TEXT,
  char_count INTEGER DEFAULT 0,
  created_at TEXT NOT NULL,
  UNIQUE(book_id, page_number)
);

CREATE TABLE IF NOT EXISTS chunks (
  id TEXT PRIMARY KEY,
  page_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  cleaned_text TEXT NOT NULL,
  chapter TEXT,
  source_file TEXT,
  source_image TEXT,
  embedding BLOB,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  answer_json TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
  id TEXT PRIMARY KEY,
  answer_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  chunk_id TEXT,
  book_title TEXT NOT NULL,
  chapter TEXT,
  excerpt TEXT
);

CREATE TABLE IF NOT EXISTS retrieval_traces (
  id TEXT PRIMARY KEY,
  answer_id TEXT,
  question TEXT NOT NULL,
  normalized_query TEXT,
  language TEXT,
  retrieval_count INTEGER,
  page_ids TEXT,
  chunk_ids TEXT,
  rerank_json TEXT,
  status TEXT,
  latency_ms INTEGER,
  error TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS failed_retrievals (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  reason TEXT,
  answer_id TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluation_results (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  question_id TEXT,
  question TEXT NOT NULL,
  expected TEXT,
  actual_status TEXT,
  passed INTEGER NOT NULL,
  detail TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingest_jobs (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  detail TEXT,
  created_at TEXT NOT NULL,
  finished_at TEXT
);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  chunk_id UNINDEXED,
  page_number UNINDEXED,
  chapter UNINDEXED,
  text,
  tokenize = 'unicode61 remove_diacritics 0'
);
"""


def db_path() -> Path:
    url = settings.database_url
    if url.startswith("sqlite:///"):
        raw = url[len("sqlite:///") :]
        path = Path(raw)
        if not path.is_absolute():
            path = (DATA_DIR.parent.parent / raw).resolve() if raw.startswith("backend/") else (DATA_DIR / Path(raw).name)
            # settings default is sqlite:///./backend/data/aadhyatmik.db relative to repo
            if "aadhyatmik.db" in raw:
                path = DATA_DIR / "aadhyatmik.db"
        return path
    return DATA_DIR / "aadhyatmik.db"


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_conn():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate() -> None:
    global _ready
    with _lock:
        with get_conn() as conn:
            conn.executescript(SCHEMA)
            conn.executescript(FTS_SCHEMA)
            row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO schema_version(version, applied_at) VALUES (1, datetime('now'))"
                )
        _ready = True


def reset_corpus(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM chunks")
    conn.execute("DELETE FROM pages")
    conn.execute("DELETE FROM books")
    conn.execute("DELETE FROM chunks_fts")
