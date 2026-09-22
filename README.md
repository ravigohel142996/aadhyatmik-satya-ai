# Aadhyatmik Satya AI

A source-grounded guide to *Aadhyatmik Satya* by Param Pujya Shree Shivkrupanand Swamiji.

The assistant does not behave like a general chatbot. It searches the indexed granth first, shows the indexed wording, explains only from those lines, and labels any practical note as **Pure Soul Suggestion** — never as Swamiji’s voice.

Tagline: **प्रश्न आपका — संदर्भ ग्रंथ का।**

## What was actually indexed

This environment could list the public Google Drive folder and could not download the scans (TLS to Google user content is blocked here). The Colab notebook requires a Google sign-in and was not readable.

The working corpus is `book_chunks.json`, the extracted text already in this repository, aligned to the scan page numbers in that folder (`Page_001` … `Page_256`).

| Item | Verified value |
| --- | --- |
| Text pages indexed | 249 |
| Page range | 1–256 |
| Missing text pages in that range | 7, 8, 43, 45, 79, 113, 198 |
| Pages 257–270 | not present in the extracted corpus or in the Drive listing that was inspected |
| Claim that all 270 pages were processed | **no** |

Drive file links are stored for the scans whose public folder view exposed an id. Where a link is missing, the source viewer still shows an indexed text plate and says it is not a photograph of the printed page. Quotations carry the note: **OCR/source text requires verification.** OCR was not re-run here. No OCR confidence number is invented.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cp .env.example .env
cd frontend && npm install && cd ..

# terminal 1
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# terminal 2
cd frontend && npm run dev
```

Or: `sh scripts/dev.sh`

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

The first start builds the SQLite index from `book_chunks.json`. No API key is required. Without `LLM_API_KEY` and `LLM_API_BASE`, answers stay extractive: the granth’s own sentences, plus a clearly labeled suggestion.

## Docker

```bash
docker compose up --build
```

Frontend is published on port 5173, API on port 8000. The image installs Tesseract with Hindi so uploaded page images can be OCR’d. The default database is SQLite so the stack starts without a separate database.

## Ask

`POST /api/ask`

```json
{
  "question": "समर्पण क्या है?",
  "conversation_id": null
}
```

The response separates:

- `source_quote` — indexed granth text
- `explanation` — faithful to that text
- `pure_soul_suggestion` — AI, not a quotation
- `citations` — real page numbers from retrieval
- `confidence` — only when computed by `hybrid_rerank_v1`

If the granth does not support the question:

> इस विषय का स्पष्ट उत्तर उपलब्ध Aadhyatmik Satya के संदर्भ में नहीं मिला।

Requests for the entire book are refused. The guide will not imitate Swamiji.

## Admin

Set `ADMIN_TOKEN` in `.env`. Open http://localhost:5173/admin and pass the token as `X-Admin-Token`.

- `/admin` overview, pages, chunks, failed retrievals, ingest, reindex, evaluation
- `POST /api/ingest` accepts JSON (`book_chunks` or page records), a text PDF, or a page image if Tesseract is installed
- `POST /api/admin/reindex` rebuilds from `book_chunks.json`

## Evaluation

```bash
PYTHONPATH=backend .venv/bin/python evaluation/run_eval.py
PYTHONPATH=backend .venv/bin/pytest backend/tests -q
```

The suite covers Hindi, English, Gujarati, Hinglish, unsupported questions, and full-book refusal.

## Configuration

See `.env.example`.

| Variable | Purpose |
| --- | --- |
| `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` | Optional OpenAI-compatible chat model |
| `EMBEDDING_PROVIDER` | `local_hash` by default. Works offline. |
| `DATABASE_URL` | SQLite by default |
| `VECTOR_DB_URL` | Optional. Local vectors are stored in SQLite if unset. |
| `ADMIN_TOKEN` | Protects admin and ingest |

Do not commit real keys.

## Known limits

- Not a verified ingest of 270 printed pages.
- Some scan file ids were captured from the public folder view; others fall back to the text plate.
- Default embeddings are a local multilingual character/word hash, fused with BM25. They are not a downloaded transformer, because the model host was not reachable from this environment.
- The product link is the Tattvatrends reference supplied for this project. Stock is whatever that page shows.
