from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND / "data"
PLATES_DIR = DATA_DIR / "plates"
UPLOAD_DIR = DATA_DIR / "uploads"
FONT_PATH = BACKEND / "assets" / "fonts" / "TiroDevanagariHindi-Regular.ttf"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file(ROOT / ".env")
_load_env_file(BACKEND / ".env")


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


class Settings:
    llm_api_key: str = _env("LLM_API_KEY")
    llm_api_base: str = _env("LLM_API_BASE").rstrip("/")
    llm_model: str = _env("LLM_MODEL") or "gpt-4o-mini"
    llm_provider: str = _env("LLM_PROVIDER") or "openai_compatible"
    llm_timeout: float = float(_env("LLM_TIMEOUT_SECONDS") or "40")

    embedding_provider: str = _env("EMBEDDING_PROVIDER") or "local_hash"
    embedding_model: str = _env("EMBEDDING_MODEL") or "local-multilingual-hash-384"
    embedding_api_base: str = _env("EMBEDDING_API_BASE").rstrip("/")
    embedding_api_key: str = _env("EMBEDDING_API_KEY") or _env("LLM_API_KEY")

    database_url: str = _env("DATABASE_URL") or f"sqlite:///{DATA_DIR / 'aadhyatmik.db'}"
    vector_db_url: str = _env("VECTOR_DB_URL")
    admin_token: str = _env("ADMIN_TOKEN") or "change-me-local-admin"
    cors_origins: list[str] = [
        o.strip()
        for o in (_env("CORS_ORIGINS") or "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if o.strip()
    ]
    rate_limit_per_minute: int = int(_env("RATE_LIMIT_PER_MINUTE") or "30")
    log_level: str = _env("LOG_LEVEL") or "INFO"
    drive_folder_id: str = _env("SOURCE_DRIVE_FOLDER_ID") or "1JeudaFEZxohJkYfh-uBtYSgYBbwg5wGV"
    book_chunks_path: Path = ROOT / (_env("BOOK_CHUNKS_PATH") or "book_chunks.json")
    drive_catalog_path: Path = DATA_DIR / "drive_pages.json"

    book_title: str = "Aadhyatmik Satya"
    book_title_hi: str = "आध्यात्मिक सत्य"
    author: str = "Param Pujya Shree Shivkrupanand Swamiji"
    author_hi: str = "परम पूज्य श्री शिवकृपानंद स्वामीजी"
    product_url: str = "https://www.tattvatrends.com/product-page/calendar-2025"
    gurutattva_url: str = "https://gurutattva.org/"
    tattvatrends_url: str = "https://www.tattvatrends.com/"
    cover_drive_id: str = "1_ngnzVImWtRswOvMivCiBepXWFyAFtG4"


settings = Settings()
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLATES_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
