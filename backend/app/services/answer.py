from __future__ import annotations

import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone

from app.config import settings
from app.db import get_conn
from app.services.gloss import close_reading
from app.services.practice import granth_practice
from app.services.index import INDEX
from app.services.llm import LLMError, complete_json, llm_configured
from app.services.textutil import (
    answer_language,
    clean_whitespace,
    detect_language,
    expand_query,
    is_definition_query,
    is_distress_query,
    focus_phrases,
    is_followup,
    preferred_phrases,
    primary_terms,
    question_supported,
    prose_sentences,
    split_sentences,
    term_is_defined,
)

log = logging.getLogger("aadhyatmik.answer")

FULL_BOOK = re.compile(
    r"(entire book|whole book|all pages|full book|dump (the )?book|complete book|"
    r"पूरी किताब|पूरा ग्रंथ|सारी पुस्तक|सभी पृष्ठ|सारे पेज|पूरा पाठ|entire granth|"
    r"give me all pages|सभी पेज)",
    re.I,
)
PERSONA = re.compile(
    r"(as swamiji|speak as swamiji|pretend you are swamiji|channel swamiji|"
    r"स्वामीजी बनकर|तुम स्वामीजी हो|स्वामीजी की आवाज़ में जवाब|personally told me|"
    r"स्वामीजी ने मुझसे कहा)",
    re.I,
)
ATTRIBUTION_BANNED = re.compile(
    r"(स्वामीजी कहते हैं कि आपको|स्वामीजी ने कहा कि आप|swamiji says you should|"
    r"swamiji told you|स्वामीजी ने आपको आदेश)",
    re.I,
)

LABELS = {
    "quote": "ग्रंथ में स्वामीजी के शब्द",
    "explanation": "ग्रंथ के अनुसार समझ",
    "suggestion": "Pure Soul Suggestion",
    "reference": "संदर्भ",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _insufficient_copy(lang: str) -> tuple[str, str]:
    if lang == "en":
        return (
            "A clear answer to this subject was not found in the available Aadhyatmik Satya references.",
            "You may ask again with a related word or theme from the granth.",
        )
    if lang == "gu":
        return (
            "આ વિષયનો સ્પષ્ટ ઉત્તર ઉપલબ્ધ Aadhyatmik Satya ના સંદર્ભમાં મળ્યો નથી.",
            "તમે પ્રશ્નને કોઈ સંબંધિત શબ્દ સાથે ફરી પૂછી શકો છો.",
        )
    if lang == "hinglish":
        return (
            "Is vishay ka spasht jawab uplabdh Aadhyatmik Satya ke sandarbh mein nahi mila.",
            "Aap apna prashn kisi related shabd ke saath dobara pooch sakte hain.",
        )
    return (
        "इस विषय का स्पष्ट उत्तर उपलब्ध Aadhyatmik Satya के संदर्भ में नहीं मिला।",
        "आप अपने प्रश्न को किसी संबंधित विषय या शब्द के साथ दोबारा पूछ सकते हैं।",
    )


def _history_text(conversation_id: str | None) -> str:
    if not conversation_id:
        return ""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC LIMIT 6
            """,
            (conversation_id,),
        ).fetchall()
    users = [r["content"] for r in rows if r["role"] == "user"]
    return users[0] if users else ""


def _search_query(question: str, conversation_id: str | None) -> str:
    prev = _history_text(conversation_id)
    if prev and (is_followup(question) or re.search(r"page|पृष्ठ|exactly|कहाँ लिखा|किस पृष्ठ", question, re.I)):
        return f"{prev}\n{question}"
    return question


def _page_text(page_number: int) -> tuple[str, str | None, str | None, str | None]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT original_ocr, cleaned_text, chapter, drive_file_id, ocr_note FROM pages WHERE page_number = ?",
            (page_number,),
        ).fetchone()
    if not row:
        return "", None, None, None
    return row["original_ocr"] or row["cleaned_text"] or "", row["chapter"], row["drive_file_id"], row["ocr_note"]


def _best_window(
    page_text: str,
    terms: list[str],
    limit: int = 620,
    primary: list[str] | None = None,
    focus: list[str] | None = None,
) -> str:
    text = re.sub(r"(?<![।!?])\n+", " ", page_text or "")
    text = re.sub(r"[ \t]{2,}", " ", text).strip()
    sentences = prose_sentences(text)
    if not sentences:
        return ""
    primary = primary or []
    scored = []
    for i, sent in enumerate(sentences):
        if _toc_line(sent):
            continue
        score = sum(1.2 if t in sent else 0 for t in terms)
        score += sum(6.0 if t in sent else 0 for t in primary if t not in {"जीवन"})
        if any(term_is_defined(sent, t) for t in primary):
            score += 14
        if any(c in sent for c in ("यानी", "सौंप देना", "माध्यम है", "गुणधर्म", "एक संस्कार", "अशांति", "अशांत", "पद्धति नहीं")) and any(t in sent for t in primary):
            score += 5
        if "परेशान" in primary and "जीवन" in sent and "अशांति" not in sent and "अशांत" not in sent and "चिंता" not in sent:
            score -= 3
        if any(f"{t} है" in sent for t in primary):
            score += 4
        if focus and any(phrase in sent for phrase in focus):
            score += 8 + 6 * sum(phrase in sent for phrase in focus)
        if "आज में जियो" in sent or "पद्धति नहीं" in sent or "सौंप देना" in sent:
            score += 6
        if "अपराध" in sent:
            score -= 14
        score += min(len(sent), 180) / 400
        scored.append((score, i))
    scored.sort(reverse=True)
    if not scored or scored[0][0] <= 0:
        return ""
    center = scored[0][1]
    start_at = center
    if center > 0 and (
        any(term_is_defined(sentences[center - 1], t) for t in primary)
        or sentences[center].startswith(("ठीक वैसे", "इसीलिए", "इसलिए", "बस,"))
    ):
        start_at = center - 1
    anchor = sentences[start_at]
    idx = text.find(anchor)
    if idx < 0:
        return _verbatim_span(page_text or "", anchor, anchor, limit) or anchor[:limit]
    end = idx + len(anchor)
    last = start_at
    for j in range(start_at + 1, min(len(sentences), start_at + 3)):
        nxt = sentences[j]
        if _toc_line(nxt) or _next_point(nxt, primary):
            break
        if nxt.strip().startswith(("-", "–", "श्री शिव")):
            break
        pos = text.find(nxt, end)
        if pos < 0 or pos - end > 16:
            break
        if pos + len(nxt) - idx > limit:
            break
        end = pos + len(nxt)
        last = j
    return _verbatim_span(page_text or "", sentences[start_at], sentences[last], limit)


def _verbatim_span(original: str, start_sent: str, end_sent: str, limit: int) -> str:
    """Return a substring of the stored page, so the quotation can be found on that page."""
    chars: list[str] = []
    mapping: list[int] = []
    for i, ch in enumerate(original or ""):
        if ch.isspace():
            continue
        chars.append(ch)
        mapping.append(i)
    if not mapping:
        return ""
    blob = "".join(chars)
    start_key = re.sub(r"\s+", "", start_sent)[:32]
    end_key = re.sub(r"\s+", "", end_sent)[-28:]
    start = blob.find(start_key)
    if start < 0:
        return ""
    end = blob.find(end_key, start)
    if end < 0:
        end = min(len(blob), start + len(re.sub(r"\s+", "", start_sent)))
    else:
        end = min(len(blob), end + len(end_key))
    excerpt = original[mapping[start] : mapping[end - 1] + 1].strip()
    if len(excerpt) > limit:
        excerpt = excerpt[:limit].rstrip()
    return excerpt


def _leading_clause(page_text: str) -> str:
    text = (page_text or "").strip()
    if not text:
        return ""
    cut = text.find("।")
    clause = text if cut < 0 else text[: cut + 1]
    clause = clause.strip()
    if len(clause) < 8 or len(clause) > 280:
        return ""
    return clause


def _next_point(sent: str, primary: list[str]) -> bool:
    s = sent.strip()
    if re.match(r"^[(（]?[०-९0-9]{1,3}[)）.]", s) and not any(t in s for t in primary):
        return True
    return False


def _toc_line(sent: str) -> bool:
    if len(sent) < 90 and sent.count(" ") < 8 and any(ch.isdigit() or ch in "०१२३४५६७८९" for ch in sent):
        if sent.count("१") + sent.count("२") >= 2:
            return True
    return False


def _confidence(top: dict | None) -> dict | None:
    if not top:
        return {
            "score": 0.0,
            "method": "hybrid_rerank_v1",
            "level": "insufficient",
            "coverage": 0.0,
        }
    coverage = float(top.get("weighted_coverage") or 0)
    cosine = float(top.get("cosine") or 0)
    score = 0.7 * min(1.0, coverage * 1.6) + 0.3 * cosine
    if top.get("hits") and len(top["hits"]) >= 2:
        score = min(1.0, score + 0.06)
    score = round(max(0.0, min(1.0, score)), 4)
    if not top.get("hits"):
        level = "insufficient"
    elif score >= 0.5 and coverage >= 0.22:
        level = "strong"
    elif score >= 0.28 and coverage >= 0.12 and top.get("hits"):
        level = "partial"
    else:
        level = "insufficient"
    return {
        "score": score,
        "method": "hybrid_rerank_v1",
        "level": level,
        "coverage": round(coverage, 4),
    }


def _themes(text: str) -> set[str]:
    found = set()
    pairs = {
        "ध्यान": ("ध्यान", "साधना", "संस्कार"),
        "समर्पण": ("समर्पण",),
        "अशांति": ("अशांति", "अशांत", "चिंता", "शांति"),
        "मैं": ("अहंकार", "‘मैं’", '"मैं"', "मैं"),
        "वर्तमान": ("वर्तमान", "आज में"),
        "साक्षी": ("साक्षी",),
        "गुरु": ("सद्गुरु", "गुरु", "गुरुतत्व"),
        "समस्या": ("समस्या", "मुसीबत"),
    }
    for name, needles in pairs.items():
        if any(n in text for n in needles):
            found.add(name)
    return found


def _instruction_line(text: str) -> str:
    cues = ("करो", "जियो", "रहो", "छोड़", "मत ", "कीजिए", "हो जाएँ", "समर्पित")
    for sent in split_sentences(text or ""):
        if "अपराध" in sent:
            continue
        if any(cue in sent for cue in cues) and 18 <= len(sent) <= 180:
            return sent.strip()
    return ""


def _suggestion(lang: str, text: str) -> str:
    practice = granth_practice(lang, text)
    if practice:
        return practice
    line = _instruction_line(text)
    if lang == "en":
        lead = "According to the lines above, the practice is what those words already say."
        if line:
            lead = f"According to the lines above, keep to this: {line}"
        return lead + " This is not Swamiji’s personal instruction, and no extra result has been added."
    if lang == "gu":
        lead = "ઉપરની પંક્તિઓ પ્રમાણે કરવાની વાત એ જ શબ્દોમાં છે."
        if line:
            lead = f"ઉપરની પંક્તિઓ પ્રમાણે આ રાખો: {line}"
        return lead + " આ સ્વામીજીનો અંગત આદેશ નથી."
    if lang == "hinglish":
        lead = "Upar ki panktiyon ke anusar practice wahi hai jo un shabdon mein hai."
        if line:
            lead = f"Upar ki panktiyon ke anusar aap yeh rakho: {line}"
        return lead + " Yeh Swamiji ka personal order nahi hai, aur koi extra benefit joda nahi gaya."
    lead = "ऊपर की पंक्तियों के अनुसार करने की बात उन्हीं शब्दों में है।"
    if line:
        lead = f"ऊपर की पंक्तियों के अनुसार यह रखें: {line}"
    return lead + " यह स्वामीजी का व्यक्तिगत आदेश नहीं है, और कोई अलग फल जोड़ा नहीं गया।"


def _frame(lang: str, gloss: str | None) -> str:
    if lang == "en":
        return gloss or "The answer is the quotation above, kept in the granth’s language. Nothing beyond those lines has been added."
    if lang == "gu":
        return gloss or "જવાબ ઉપરના ઉદ્ધરણમાં છે. ઉદ્ધરણ ગ્રંથની મૂળ ભાષામાં રાખ્યું છે. આ ઉપરાંત કોઈ નવી વાત ઉમેરાઈ નથી."
    if lang == "hinglish":
        return gloss or "Jawab upar diye quotation mein hai. Quotation granth ki bhasha mein hai. Uske aage koi nayi baat nahi jodi gayi."
    return gloss or "उत्तर ऊपर दिए गए उद्धरण में है। उद्धरण ग्रंथ की भाषा में है। उसके आगे कोई नई बात नहीं जोड़ी गई।"


def _explain(lang: str, sentences: list[str], excerpt: str = "") -> str:
    shown = sentences[:3]
    gloss = close_reading(lang, excerpt or " ".join(shown))
    note = {
        "en": "Original lines:",
        "gu": "મૂળ પંક્તિઓ:",
        "hinglish": "Mool panktiyan:",
        "hi": "मूल पंक्तियाँ:",
    }.get(lang, "मूल पंक्तियाँ:")
    bullets = "\n".join(f"• {s}" for s in shown)
    return _frame(lang, gloss) + "\n\n" + note + "\n" + bullets


def _quote_label(page: int, excerpt: str) -> tuple[str, str]:
    if page == 3:
        return "ग्रंथ का अंश", "यह पृष्ठ अनुरोध है, गुरुमाँ के हस्ताक्षर के साथ। इसे स्वामीजी का कथन नहीं माना गया।"
    if page >= 253:
        return (
            "ग्रंथ का अंश",
            "This later page mixes editorial lines and named quotations. Indexed text — verify on the source page.",
        )
    return LABELS["quote"], "Indexed text — verify on the source page."


def _public_trace(hits: list[dict]) -> list[dict]:
    out = []
    for h in hits[:4]:
        ch = h["chunk"]
        out.append(
            {
                "page": ch.page_number,
                "chunk_id": ch.id,
                "chapter": ch.chapter,
                "score": h["score"],
                "coverage": h["coverage"],
            }
        )
    return out


async def _maybe_llm(question: str, lang: str, context_blocks: list[dict]) -> dict | None:
    if not llm_configured():
        return None
    system = (
        "You are a source-grounded assistant for the book Aadhyatmik Satya. "
        "Use ONLY the provided context. Do not invent teachings, page numbers, or quotations. "
        "Never speak as Swamiji. Never say Swamiji personally answered the user. "
        "Return JSON with keys explanation and pure_soul_suggestion. "
        "explanation must stay faithful to the context and match the user's language "
        f"({lang}). pure_soul_suggestion must be clearly AI-generated, gentle, with no guarantees, "
        "no medical claims, and must not be attributed to Swamiji. "
        "If the context is insufficient, set explanation to an insufficiency statement and pure_soul_suggestion to null."
    )
    user = json.dumps({"question": question, "context": context_blocks}, ensure_ascii=False)
    try:
        data = await complete_json(system, user)
    except LLMError:
        log.exception("llm_failed_fallback")
        return None
    if not isinstance(data, dict):
        return None
    explanation = (data.get("explanation") or "").strip()
    suggestion = data.get("pure_soul_suggestion")
    if suggestion:
        suggestion = str(suggestion).strip()
    if ATTRIBUTION_BANNED.search(explanation or "") or ATTRIBUTION_BANNED.search(suggestion or ""):
        log.warning("llm_attribution_rejected")
        return None
    return {"explanation": explanation, "pure_soul_suggestion": suggestion}


async def answer_question(question: str, conversation_id: str | None = None) -> dict:
    started = time.perf_counter()
    question = (question or "").strip()
    detected = detect_language(question)
    lang = answer_language(detected)
    answer_id = str(uuid.uuid4())
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO conversations(id, created_at, updated_at) VALUES (?, ?, ?)",
                (conversation_id, _now(), _now()),
            )
    else:
        with get_conn() as conn:
            exists = conn.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO conversations(id, created_at, updated_at) VALUES (?, ?, ?)",
                    (conversation_id, _now(), _now()),
                )

    if PERSONA.search(question):
        payload = _refuse_persona(lang, answer_id, conversation_id, question, started)
        return payload
    if FULL_BOOK.search(question):
        return _refuse_full(lang, answer_id, conversation_id, question, started)

    search_text = _search_query(question, conversation_id)
    if not question_supported(question, INDEX.df):
        return _insufficient(lang, answer_id, conversation_id, question, [], _confidence(None), started, detected)
    tokens, weights = expand_query(search_text)
    primary = primary_terms(question) or primary_terms(search_text)
    if not weights:
        weights = {t: 1.0 for t in (primary or question.split()[:6] or ["आध्यात्मिक"])}
    intent = "definition" if is_definition_query(question) else "distress" if is_distress_query(question) else None
    if intent == "distress":
        primary = [t for t in primary if t not in {"जीवन", "समझ", "करना"}]
        if "जीवन" in weights:
            weights["जीवन"] = min(weights["जीवन"], 0.45)
    focus = focus_phrases(question)
    hits = INDEX.search(search_text, weights, limit=6, primary=primary, intent=intent)
    if focus:
        focused = [
            hit
            for hit in hits
            if any(phrase in ((hit["chunk"].cleaned_text or "") + (hit["chunk"].text or "")) for phrase in focus)
        ]
        if not focused:
            return _insufficient(lang, answer_id, conversation_id, question, hits, _confidence(None), started, detected)
        hits = focused
    if intent == "distress":
        guided = []
        for hit in hits:
            blob = (hit["chunk"].cleaned_text or "") + (hit["chunk"].text or "")
            if "अपराध" in blob and "अशांति" not in blob:
                continue
            if any(k in blob for k in ("अशांति", "अशांत", "चिंता", "आज में", "साक्षी")):
                guided.append(hit)
        if not guided:
            return _insufficient(lang, answer_id, conversation_id, question, hits, _confidence(None), started, detected)
        hits = guided
    conf = _confidence(hits[0] if hits else None)
    level = conf["level"] if conf else "insufficient"
    grounded = level in {"strong", "partial"} and bool(hits and hits[0].get("hits"))

    if not grounded:
        return _insufficient(lang, answer_id, conversation_id, question, hits, conf, started, detected)

    top_pages = []
    for h in hits:
        if h["chunk"].page_number not in top_pages:
            top_pages.append(h["chunk"].page_number)
        if len(top_pages) == 2:
            break
    passages = []
    citations = []
    terms = list(weights.keys())
    for page in top_pages:
        original, chapter, drive_id, ocr_note = _page_text(page)
        excerpt = _best_window(original or "", terms, primary=primary, focus=focus)
        if not excerpt:
            continue
        wanted = preferred_phrases(question)
        if passages and wanted and not any(phrase in excerpt for phrase in wanted):
            continue
        label, verify = _quote_label(page, excerpt)
        passages.append(
            {
                "page": page,
                "chapter": chapter,
                "excerpt": excerpt,
                "label": label,
                "verification": verify,
                "drive_file_id": drive_id,
                "ocr_note": ocr_note,
            }
        )
        citations.append(
            {
                "page": page,
                "book": settings.book_title,
                "chapter": chapter,
                "chunk_id": next(h["chunk"].id for h in hits if h["chunk"].page_number == page),
                "drive_file_id": drive_id,
            }
        )
        page_ends = (original or "").rstrip()
        cut_off = excerpt and page_ends.endswith(excerpt[-12:]) and not excerpt.rstrip().endswith(("।", "?", "!", "॥", "”", '"'))
        if cut_off and page + 1 not in {c["page"] for c in citations}:
            nxt, nxt_chapter, nxt_drive, nxt_note = _page_text(page + 1)
            extra = _leading_clause(nxt)
            if extra and extra in (nxt or ""):
                passages.append(
                    {
                        "page": page + 1,
                        "chapter": nxt_chapter,
                        "excerpt": extra,
                        "label": _quote_label(page + 1, extra)[0],
                        "verification": "Indexed text — verify on the source page. Continues the previous page.",
                        "drive_file_id": nxt_drive,
                        "ocr_note": nxt_note,
                    }
                )
                citations.append(
                    {
                        "page": page + 1,
                        "book": settings.book_title,
                        "chapter": nxt_chapter,
                        "chunk_id": None,
                        "drive_file_id": nxt_drive,
                    }
                )
    if not passages:
        return _insufficient(lang, answer_id, conversation_id, question, hits, conf, started, detected)

    quote = "\n\n".join(p["excerpt"] for p in passages)
    sentences = []
    for p in passages:
        sentences.extend(split_sentences(p["excerpt"])[:2])
    lead = split_sentences(passages[0]["excerpt"]) or sentences
    explanation = _explain(lang, lead, passages[0]["excerpt"])
    suggestion = _suggestion(lang, quote)
    llm = await _maybe_llm(
        question,
        lang,
        [{"page": p["page"], "text": p["excerpt"]} for p in passages],
    )
    if llm and llm.get("explanation"):
        explanation = llm["explanation"]
    if llm and llm.get("pure_soul_suggestion"):
        suggestion = llm["pure_soul_suggestion"]
        if "स्वामीजी" in suggestion and "नहीं" not in suggestion:
            suggestion = _suggestion(lang, quote)

    payload = {
        "answer_id": answer_id,
        "conversation_id": conversation_id,
        "language": lang,
        "detected_language": detected,
        "status": "grounded" if level == "strong" else "partial",
        "labels": {
            **LABELS,
            "quote": passages[0]["label"],
        },
        "source_quote": passages[0]["excerpt"],
        "source_passages": passages,
        "quote_verification": passages[0]["verification"],
        "explanation": explanation,
        "pure_soul_suggestion": suggestion,
        "citations": citations,
        "confidence": conf,
        "llm_used": bool(llm),
        "retrieval": _public_trace(hits),
    }
    _persist(question, payload, hits, started, status=payload["status"])
    return payload


def _refuse_full(lang, answer_id, conversation_id, question, started) -> dict:
    if lang == "en":
        msg = "This guide can answer questions and show relevant excerpts with page references. It does not reproduce the full book."
    elif lang == "gu":
        msg = "આ માર્ગદર્શક પ્રશ્નોના સંદર્ભિત અંશો બતાવે છે. આખું પુસ્તક અહીં નથી આપવામાં આવતું."
    elif lang == "hinglish":
        msg = "Yeh guide prashn ka relevant ansh aur page reference de sakta hai. Poori kitab yahan reproduce nahi ki jaati."
    else:
        msg = "यह मार्गदर्शक प्रश्न का उत्तर और आवश्यक अंश दिखा सकता है। पूरा ग्रंथ यहाँ पुनर्मुद्रित नहीं किया जाता।"
    payload = {
        "answer_id": answer_id,
        "conversation_id": conversation_id,
        "language": lang,
        "status": "refused_full_text",
        "labels": LABELS,
        "source_quote": None,
        "explanation": msg,
        "pure_soul_suggestion": None,
        "citations": [],
        "confidence": None,
        "llm_used": False,
    }
    _persist(question, payload, [], started, status="refused_full_text")
    return payload


def _refuse_persona(lang, answer_id, conversation_id, question, started) -> dict:
    if lang == "en":
        msg = "This guide does not imitate Swamiji or claim a personal message from him. Ask a question about the granth, and the answer will stay with the indexed pages."
    else:
        msg = "यह मार्गदर्शक स्वामीजी की जीवित वाणी का अभिनय नहीं करता और उनसे व्यक्तिगत संदेश का दावा नहीं करता। ग्रंथ से जुड़ा प्रश्न पूछें — उत्तर केवल अनुक्रमित पृष्ठों पर टिका रहेगा।"
    payload = {
        "answer_id": answer_id,
        "conversation_id": conversation_id,
        "language": lang,
        "status": "refused_persona",
        "labels": LABELS,
        "source_quote": None,
        "explanation": msg,
        "pure_soul_suggestion": None,
        "citations": [],
        "confidence": None,
        "llm_used": False,
    }
    _persist(question, payload, [], started, status="refused_persona")
    return payload


def _insufficient(lang, answer_id, conversation_id, question, hits, conf, started, detected) -> dict:
    primary, secondary = _insufficient_copy(lang)
    payload = {
        "answer_id": answer_id,
        "conversation_id": conversation_id,
        "language": lang,
        "detected_language": detected,
        "status": "insufficient",
        "labels": LABELS,
        "source_quote": None,
        "source_passages": [],
        "explanation": primary,
        "follow_up_hint": secondary,
        "pure_soul_suggestion": None,
        "citations": [],
        "confidence": conf,
        "llm_used": False,
        "retrieval": _public_trace(hits),
    }
    _persist(question, payload, hits, started, status="insufficient", failed=True)
    return payload


def _persist(question, payload, hits, started, status: str, failed: bool = False) -> None:
    latency = int((time.perf_counter() - started) * 1000)
    answer_id = payload["answer_id"]
    conversation_id = payload["conversation_id"]
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages(id, conversation_id, role, content, answer_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), conversation_id, "user", question, None, _now()),
        )
        conn.execute(
            "INSERT INTO messages(id, conversation_id, role, content, answer_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                conversation_id,
                "assistant",
                payload.get("explanation") or "",
                json.dumps(payload, ensure_ascii=False),
                _now(),
            ),
        )
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (_now(), conversation_id),
        )
        for c in payload.get("citations") or []:
            conn.execute(
                """
                INSERT INTO citations(id, answer_id, page_number, chunk_id, book_title, chapter, excerpt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    answer_id,
                    c["page"],
                    c.get("chunk_id"),
                    c.get("book") or settings.book_title,
                    c.get("chapter"),
                    (payload.get("source_quote") or "")[:500],
                ),
            )
        conn.execute(
            """
            INSERT INTO retrieval_traces(id, answer_id, question, normalized_query, language, retrieval_count,
              page_ids, chunk_ids, rerank_json, status, latency_ms, error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                answer_id,
                question,
                " ".join((hits[0].get("hits") if hits else []) or []),
                payload.get("language"),
                len(hits),
                json.dumps([h["chunk"].page_number for h in hits]),
                json.dumps([h["chunk"].id for h in hits]),
                json.dumps(
                    [
                        {
                            "page": h["chunk"].page_number,
                            "score": h["score"],
                            "coverage": h["coverage"],
                            "hits": h["hits"],
                        }
                        for h in hits
                    ],
                    ensure_ascii=False,
                ),
                status,
                latency,
                None,
                _now(),
            ),
        )
        if failed:
            conn.execute(
                "INSERT INTO failed_retrievals(id, question, reason, answer_id, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), question, status, answer_id, _now()),
            )
    log.info(
        "ask status=%s pages=%s latency_ms=%s llm=%s",
        status,
        [c.get("page") for c in payload.get("citations") or []],
        latency,
        payload.get("llm_used"),
    )
