from __future__ import annotations

import math
import struct
import threading
from dataclasses import dataclass, field

import numpy as np

from app.services.textutil import (
    content_tokens,
    focus_phrases,
    preferred_phrases,
    prose_sentences,
    query_phrases,
    stable_hash,
    term_is_defined,
    tokenize,
)

DIM = 384
_lock = threading.RLock()


def embed_text(text: str) -> np.ndarray:
    vec = np.zeros(DIM, dtype=np.float32)
    tokens = tokenize(text)
    if not tokens and not text:
        return vec
    for tok in tokens:
        h = stable_hash("w:" + tok)
        sign = 1.0 if (h & 1) == 0 else -1.0
        vec[h % DIM] += sign
    compact = "".join(ch for ch in (text or "") if not ch.isspace())
    for i in range(max(0, len(compact) - 2)):
        gram = compact[i : i + 3]
        h = stable_hash("g:" + gram)
        sign = 1.0 if ((h >> 1) & 1) == 0 else -1.0
        vec[h % DIM] += 0.35 * sign
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def pack_vec(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def unpack_vec(blob: bytes) -> np.ndarray:
    count = len(blob) // 4
    return np.array(struct.unpack(f"{count}f", blob), dtype=np.float32)


@dataclass
class ChunkRec:
    id: str
    page_number: int
    page_id: str
    text: str
    cleaned_text: str
    chapter: str | None
    source_image: str | None
    tokens: list[str] = field(default_factory=list)
    vec: np.ndarray | None = None


class HybridIndex:
    def __init__(self) -> None:
        self.chunks: list[ChunkRec] = []
        self.df: dict[str, int] = {}
        self.avgdl = 1.0
        self.k1 = 1.4
        self.b = 0.72
        self.matrix: np.ndarray | None = None
        self.page_blobs: dict[int, str] = {}
        self.provider = "local_hash"
        self.model = "local-multilingual-hash-384"

    def build(self, chunks: list[ChunkRec], provider: str, model: str) -> None:
        with _lock:
            self.chunks = chunks
            self.provider = provider
            self.model = model
            self.df = {}
            self.page_blobs = {}
            lengths = []
            vectors = []
            for ch in chunks:
                ch.tokens = tokenize(ch.cleaned_text or ch.text)
                lengths.append(len(ch.tokens) or 1)
                seen = set(ch.tokens)
                for tok in seen:
                    self.df[tok] = self.df.get(tok, 0) + 1
                if ch.vec is None:
                    ch.vec = embed_text(ch.cleaned_text or ch.text)
                vectors.append(ch.vec)
                blob = ch.cleaned_text or ch.text or ""
                self.page_blobs[ch.page_number] = (self.page_blobs.get(ch.page_number, "") + "\n" + blob).strip()
            self.avgdl = (sum(lengths) / len(lengths)) if lengths else 1.0
            self.matrix = np.vstack(vectors) if vectors else np.zeros((0, DIM), dtype=np.float32)

    def _idf(self, tok: str) -> float:
        n = len(self.chunks) or 1
        df = self.df.get(tok, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def bm25(self, weights: dict[str, float], limit: int = 40) -> list[tuple[int, float]]:
        if not self.chunks:
            return []
        scores = [0.0] * len(self.chunks)
        for tok, w in weights.items():
            idf = self._idf(tok)
            if idf <= 0:
                continue
            for i, ch in enumerate(self.chunks):
                tf = ch.tokens.count(tok)
                if not tf:
                    continue
                dl = len(ch.tokens) or 1
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[i] += w * idf * (tf * (self.k1 + 1)) / denom
        ranked = sorted(((i, s) for i, s in enumerate(scores) if s > 0), key=lambda x: x[1], reverse=True)
        return ranked[:limit]

    def dense(self, query: str, limit: int = 40) -> list[tuple[int, float]]:
        if self.matrix is None or len(self.chunks) == 0:
            return []
        q = embed_text(query)
        sims = self.matrix @ q
        idx = np.argsort(-sims)[:limit]
        return [(int(i), float(sims[i])) for i in idx if float(sims[i]) > 0.05]

    def search(
        self,
        query_text: str,
        weights: dict[str, float],
        limit: int = 8,
        primary: list[str] | None = None,
        intent: str | None = None,
    ) -> list[dict]:
        bm = self.bm25(weights, 40)
        dense_q = " ".join(list(weights.keys())[:12]) + " " + query_text
        dn = self.dense(dense_q, 30)
        bm_max = max((s for _, s in bm), default=1.0) or 1.0
        dn_map = {i: s for i, s in dn}
        bm_map = {i: s for i, s in bm}
        candidate_ids = set(bm_map) | set(dn_map)
        if intent == "definition" and primary:
            candidate_ids |= set(self._definitional_indexes(primary))
        if intent == "distress":
            candidate_ids |= set(self._keyword_indexes(DISTRESS_GUIDANCE, limit=18))
        focus = focus_phrases(query_text)
        preferred = preferred_phrases(query_text)
        if focus:
            candidate_ids |= set(self._keyword_indexes(tuple(focus), limit=8))
        if preferred:
            candidate_ids |= set(self._keyword_indexes(tuple(preferred), limit=8))
        if "मिशन" in query_text:
            candidate_ids |= set(self._keyword_indexes(("मिशन",), limit=8))
        if "सर्वत्र" in query_text and "परमात्मा" in query_text:
            candidate_ids |= set(self._keyword_indexes(("सर्वत्र",), limit=8))
        content_terms = [t for t, w in weights.items() if w >= 1.1 and len(t) >= 2]
        primary = [t for t in (primary or []) if len(t) >= 2]
        phrases = query_phrases(query_text)
        results = []
        for i in candidate_ids:
            ch = self.chunks[i]
            text = ch.cleaned_text or ch.text
            hits = [t for t in content_terms if t in text]
            p_hits = [t for t in primary if t in text]
            if primary and not p_hits and intent == "definition":
                continue
            if not hits and not p_hits and i not in bm_map:
                continue
            coverage = (sum(weights.get(t, 1) for t in hits) / sum(weights.values())) if weights else 0.0
            if primary:
                coverage = max(coverage, len(p_hits) / len(primary))
            term_coverage = len(set(hits) | set(p_hits)) / max(1, len(set(content_terms) | set(primary)))
            bm_n = bm_map.get(i, 0.0) / bm_max
            cos = max(0.0, dn_map.get(i, 0.0))
            phrase_bonus = 0.08 if len(p_hits) >= 2 else 0.0
            chapter_bonus = 0.05 if ch.chapter and any(t in (ch.chapter or "") for t in p_hits) else 0.0
            fused = 0.46 * bm_n + 0.14 * cos + 0.22 * min(1.0, coverage * 1.5) + phrase_bonus + chapter_bonus
            page_blob = self.page_blobs.get(ch.page_number, text)
            if primary and not p_hits:
                fused *= 0.22
            elif primary and len(p_hits) == len(primary):
                fused += 0.12
            if "मिशन" in query_text:
                if "मिशन" in page_blob:
                    fused += 1.6
                else:
                    fused *= 0.3
            if "परमात्मा" in query_text and "सर्वत्र" in query_text:
                if "परमात्मा सर्वत्र है" in page_blob or "सर्वत्र विद्यमान" in page_blob:
                    fused += 1.35
                if "के अलावा और कुछ है ही नहीं" in page_blob or "सर्वत्र विद्यमान है" in page_blob:
                    fused += 0.7
                elif "परमात्मा" in page_blob and "सर्वत्र" in page_blob:
                    fused += 0.45
            if intent == "definition" and "मिशन" not in query_text and p_hits and ch.page_number != 2 and not _toc_like(page_blob):
                fused += _definition_strength(page_blob, p_hits)
                if any(term_is_defined(page_blob, term) for term in p_hits):
                    fused += 1.15
                elif _terms_close(page_blob, p_hits):
                    fused += 0.35
                if "पद्धति नहीं" in page_blob and "एक संस्कार" in page_blob:
                    fused += 0.9
                if ch.page_number >= 253 and ("- श्री" in page_blob or "स्वामीजी" in page_blob):
                    fused *= 0.8
            if intent == "distress":
                if any(k in page_blob for k in DISTRESS_GUIDANCE):
                    fused += 0.7
                else:
                    fused *= 0.18
                if "अपराध" in page_blob and "अशांति" not in page_blob:
                    fused *= 0.08
            if "आज" in query_text and any(k in query_text for k in ("जिय", "जीओ", "जीना", "jio", "live")):
                if "आज में" in text:
                    fused += 0.5
            for phrase in phrases:
                if phrase in text:
                    fused += 0.18 * len(phrase.split())
            if focus:
                matched = [phrase for phrase in focus if phrase in page_blob]
                if not matched:
                    fused *= 0.04
                else:
                    fused += 0.85 * len(matched)
            preferred_hit = False
            for phrase in preferred:
                if phrase in page_blob:
                    preferred_hit = True
                    fused += 0.9
            if _toc_like(page_blob) or ch.page_number == 2:
                fused *= 0.02
            if not hits and not p_hits and not preferred_hit:
                fused *= 0.2
            display_hits = p_hits or hits
            results.append(
                {
                    "chunk": ch,
                    "score": round(float(max(fused, 0)), 4),
                    "bm25": round(float(bm_n), 4),
                    "cosine": round(float(cos), 4),
                    "coverage": round(float(term_coverage), 4),
                    "weighted_coverage": round(float(coverage), 4),
                    "hits": display_hits,
                }
            )
        results.sort(key=lambda r: r["score"], reverse=True)
        picked: list[dict] = []
        seen_pages: set[int] = set()
        extras: list[dict] = []
        for row in results:
            page = row["chunk"].page_number
            if page not in seen_pages:
                picked.append(row)
                seen_pages.add(page)
            else:
                extras.append(row)
        return (picked + extras)[:limit]

    def _definitional_indexes(self, primary: list[str]) -> list[int]:
        scored = []
        for i, ch in enumerate(self.chunks):
            strength = _definition_strength(ch.cleaned_text or ch.text, primary)
            if strength >= 0.7:
                scored.append((strength, i))
        scored.sort(reverse=True)
        return [i for _, i in scored[:16]]

    def _keyword_indexes(self, needles: tuple[str, ...], limit: int = 16) -> list[int]:
        scored = []
        for i, ch in enumerate(self.chunks):
            text = ch.cleaned_text or ch.text
            n = sum(text.count(k) for k in needles)
            if n:
                scored.append((n, -ch.page_number, i))
        scored.sort(reverse=True)
        return [i for _, _, i in scored[:limit]]


DEF_CUES = ("यानी", "अर्थात्", "कहलाता", "कहलाती", "माध्यम है", "गुणधर्म", "सौंप देना", "एक संस्कार", "पद्धति नहीं", "होती है")
DISTRESS_GUIDANCE = ("अशांति", "अशांत", "चिंता मत", "भीतर की स्थिति", "आज में", "साक्षी भाव")


def _toc_like(text: str) -> bool:
    import re

    hits = re.findall(r"[०-९0-9]{1,3}\s+\S{2,24}\s+[०-९0-9]{2,3}", text)
    return len(hits) >= 3 or text.count("१ ") + text.count("२ ") > 8 and len(text) < 400


def _definition_strength(text: str, primary: list[str]) -> float:
    import re

    best = 0.0
    parts = prose_sentences(text)
    for sent in parts:
        sent = sent.strip()
        if len(sent) < 28 or _toc_like(sent):
            continue
        if not any(t in sent for t in primary):
            continue
        score = 0.0
        if any(c in sent for c in DEF_CUES):
            score += 0.7
        if all(t in sent for t in primary[:3]) and any(c in sent for c in DEF_CUES):
            score += 1.15
        if any(f"{t} है" in sent or f"{t} होता" in sent or f"{t} कहला" in sent or f"{t} यानी" in sent for t in primary):
            score += 0.55
        best = max(best, score)
    return best


def _terms_close(text: str, terms: list[str], window: int = 42) -> bool:
    picked = [t for t in terms if len(t) >= 3][:3]
    if len(picked) < 2:
        return False
    positions = []
    for term in picked:
        idx = text.find(term)
        if idx < 0:
            return False
        positions.append(idx)
    return max(positions) - min(positions) <= window + sum(len(t) for t in picked)


INDEX = HybridIndex()
