from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
GUJARATI = re.compile(r"[\u0A80-\u0AFF]")
LATIN = re.compile(r"[A-Za-z]")
DANDA = "।|"
ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00ad"), None)

HI_STOP = {
    "का", "के", "की", "है", "हैं", "में", "से", "को", "एक", "यह", "वह", "और", "या", "तो", "भी",
    "ही", "ने", "पर", "लिए", "क्या", "कैसे", "क्यों", "कौन", "मुझे", "मैं", "मेरा", "मेरी", "बहुत",
    "नहीं", "हो", "होता", "होती", "करने", "करना", "चाहिए", "अपना", "अपने", "आप", "था", "थी", "थे",
    "जो", "कि", "इस", "उस", "तक", "न", "मत", "हूं", "हूँ", "है।", "का।", "कर", "रहा", "रही", "रहे",
    "आ", "गया", "गई", "कुछ", "सब", "कोई", "जब", "तब", "अगर", "यदि", "तो", "ये", "वो", "उसका",
    "इसका", "इसे", "उसे", "हम", "हमारा", "तुम", "आपका", "लिए।", "बाद", "पहले", "साथ", "बारे",
    "मतलब", "बताओ", "बताएं", "बताइए", "समझ", "समझाओ", "सरल", "daily", "life",
    "लिखा", "लिखी", "लिखे", "कहता", "कहते", "कहती", "अनुसार", "ग्रंथ", "पुस्तक",
    "शुरुआत", "होने", "दिया", "दिए", "किया", "किए",
}
EN_STOP = {
    "the", "a", "an", "is", "are", "was", "were", "what", "why", "how", "should", "i", "my", "me",
    "do", "to", "of", "in", "and", "or", "for", "with", "on", "at", "from", "this", "that", "it",
    "be", "can", "could", "would", "please", "tell", "about", "according", "book", "page", "does",
    "did", "not", "no", "yes", "we", "our", "you", "your", "am", "been", "being", "as", "by",
    "if", "when", "where", "who", "whom", "which", "into", "than", "then", "so", "just", "very",
}
ROMAN_CONTENT = {
    "samarpan": ["समर्पण"],
    "surrender": ["समर्पण"],
    "dhyan": ["ध्यान"],
    "dhyaan": ["ध्यान"],
    "dhyana": ["ध्यान"],
    "meditation": ["ध्यान", "समर्पण"],
    "meditate": ["ध्यान", "समर्पण"],
    "guru": ["गुरु", "सद्गुरु"],
    "sadguru": ["सद्गुरु", "गुरु"],
    "tattva": ["तत्त्व", "तत्व", "गुरुतत्व"],
    "tattwa": ["तत्त्व", "तत्व", "गुरुतत्व"],
    "tattv": ["तत्त्व", "तत्व"],
    "gurutattva": ["गुरुतत्व", "गुरु", "माध्यम"],
    "gurutattwa": ["गुरुतत्व", "गुरु"],
    "sadhak": ["साधक"],
    "sadhaks": ["साधक"],
    "sadhna": ["साधना"],
    "sadhana": ["साधना"],
    "ahamkar": ["अहंकार"],
    "ahankar": ["अहंकार"],
    "ahankaar": ["अहंकार"],
    "ego": ["अहंकार"],
    "parmatma": ["परमात्मा"],
    "paramatma": ["परमात्मा"],
    "parmeshwar": ["परमात्मा"],
    "chitta": ["चित्त"],
    "chit": ["चित्त"],
    "samadhi": ["समाधि"],
    "moksha": ["मोक्ष"],
    "moksh": ["मोक्ष"],
    "atma": ["आत्मा"],
    "aatma": ["आत्मा"],
    "ashram": ["आश्रम"],
    "abhamandal": ["आभामण्डल", "आभामंडल"],
    "aura": ["आभामण्डल"],
    "dharma": ["धर्म"],
    "manushya": ["मनुष्य"],
    "shanti": ["शांति"],
    "peace": ["शांति", "अशांति"],
    "pareshan": ["परेशान", "अशांति", "चिंता"],
    "pareshani": ["अशांति", "चिंता", "समस्या"],
    "restless": ["अशांत", "चंचल", "चित्त"],
    "anxiety": ["चिंता", "अशांति"],
    "anxious": ["चिंता", "अशांति"],
    "tension": ["चिंता", "अशांति"],
    "chinta": ["चिंता"],
    "worry": ["चिंता"],
    "worried": ["चिंता", "परेशान", "अशांति"],
    "mind": ["मन", "चित्त"],
    "mann": ["मन"],
    "jeevan": ["जीवन"],
    "jivan": ["जीवन"],
    "life": ["जीवन"],
    "seva": ["गुरुसेवा", "सेवा"],
    "bhakti": ["भक्ति"],
    "prem": ["प्रेम"],
    "love": ["प्रेम"],
    "ahimsa": ["अहिंसा"],
    "vartaman": ["वर्तमान"],
    "present": ["वर्तमान"],
    "gurushakti": ["गुरुशक्ति"],
    "dham": ["धाम", "गुरुशक्ति"],
    "sanskar": ["संस्कार"],
    "samskar": ["संस्कार"],
    "mission": ["मिशन"],
    "sakshi": ["साक्षी"],
    "witness": ["साक्षी"],
    "problem": ["समस्या"],
    "samasya": ["समस्या"],
    "dukh": ["दुःख", "दुख"],
    "dukh": ["दुःख"],
    "suffering": ["दुःख", "समस्या", "अशांति"],
    "purpose": ["उद्देश्य", "जीवन"],
    "uddeshya": ["उद्देश्य"],
    "balance": ["संतुलन"],
    "santulan": ["संतुलन"],
    "minute": ["मिनट"],
    "minutes": ["मिनट"],
    "chaitanya": ["चैतन्य"],
    "consciousness": ["चैतन्य", "आत्मा"],
    "inner": ["भीतर", "आत्मा"],
    "journey": ["यात्रा", "अंतर्यात्रा"],
    "antar": ["अंतर"],
    "difference": ["अंतर"],
    "farq": ["अंतर"],
    "bhed": ["अंतर"],
}
GU_TO_HI = {
    "ગુરુ": "गुरु",
    "સદ્ગુરુ": "सद्गुरु",
    "સમર્પણ": "समर्पण",
    "ધ્યાન": "ध्यान",
    "સાધક": "साधक",
    "સાધના": "साधना",
    "અહંકાર": "अहंकार",
    "પરમાત્મા": "परमात्मा",
    "ચિત્ત": "चित्त",
    "મોક્ષ": "मोक्ष",
    "આત્મા": "आत्मा",
    "શાંતિ": "शांति",
    "ચિંતા": "चिंता",
    "જીવન": "जीवन",
    "ધર્મ": "धर्म",
    "પ્રેમ": "प्रेम",
    "મન": "मन",
}
DISTRESS_MARKERS = {
    "परेशान", "अशांत", "अशांति", "चिंता", "दुखी", "दुःख", "व्याकुल", "बेचैन", "tension",
    "restless", "anxious", "worried", "pareshan", "pareshani", "चंचल", "समस्या", "मुसीबत",
    "नहीं समझ", "what should i do", "क्या करूँ", "क्या करूं", "क्या करना",
}
FOLLOWUP_MARKERS = (
    "इसे", "इसका", "इसको", "यह", "ये", "और बताओ", "सरल", "aur", "iska", "ise", "this",
    "that", "apply", "daily", "आगे", "उसी", "वही", "page", "पृष्ठ", "exactly", "बिल्कुल",
)


def strip_invisibles(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    return text.translate(ZERO_WIDTH)


def clean_whitespace(text: str) -> str:
    text = strip_invisibles(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    text = strip_invisibles(text).lower()
    text = text.replace("।", " ").replace("|", " ").replace("॥", " ")
    parts = re.findall(r"[\u0900-\u097F\u0A80-\u0AFFA-Za-z0-9०-९]{2,}", text)
    return parts


def content_tokens(text: str) -> list[str]:
    out = []
    for tok in tokenize(text):
        if tok in HI_STOP or tok in EN_STOP:
            continue
        if tok.isdigit():
            continue
        out.append(tok)
    return out


def detect_language(text: str) -> str:
    t = text or ""
    dev = len(DEVANAGARI.findall(t))
    gu = len(GUJARATI.findall(t))
    lat = len(LATIN.findall(t))
    if gu > 2 and gu >= dev:
        return "gu"
    if dev > 2 and dev >= lat * 0.4:
        return "hi"
    low = t.lower()
    roman_gu = any(m in low for m in (" shu ", "shu che", "chhe", " nathi", " tame ", " mane ", " kem "))
    if roman_gu or low.strip().endswith("che?") or " shu che" in f" {low}":
        return "gu-roman"
    hinglish_markers = ("kya", "hai", "hota", "hoti", "mera", "meri", "kyun", "kyu", "kaise", "nahi", "nahin", "bahut", "mein", "main ", "karu", "karun")
    if lat > 0 and any(m in f" {low} " for m in hinglish_markers):
        return "hinglish"
    if lat > 0:
        return "en"
    return "hi"


def is_followup(text: str) -> bool:
    low = (text or "").lower().strip()
    if len(low) < 48 and any(m in low for m in FOLLOWUP_MARKERS):
        return True
    if len(content_tokens(text)) <= 3 and len(low) < 40:
        return True
    return False


def is_definition_query(text: str) -> bool:
    low = (text or "").lower()
    return any(
        m in low
        for m in (
            "क्या है", "क्या होता", "क्या होती", "किसे कहते", "किसे कह", "what is", "who is",
            "shu che", "એટલે", "meaning", "define", "परिभाषा", "अर्थ क्या", "kya hai", "kya hota",
        )
    )


def is_distress_query(text: str) -> bool:
    return _looks_distressed(text)


GENERIC_QUERY = {
    "विधि", "उपाय", "तरीका", "नुस्खा", "बात", "बातें", "solution", "method", "recipe",
    "stock", "buy", "investment", "invest", "cryptocurrency", "crypto", "bitcoin",
    "baking", "quantum", "according",
}


def question_supported(text: str, df: dict[str, int]) -> bool:
    """False when the question's distinctive words are absent from the indexed corpus."""
    originals = content_tokens(text)
    if not originals:
        return True

    def known(tok: str) -> bool:
        if df.get(tok, 0) > 0:
            return True
        mapped = list(ROMAN_CONTENT.get(tok, []))
        if tok in GU_TO_HI:
            mapped.append(GU_TO_HI[tok])
        return any(df.get(item, 0) > 0 for item in mapped)

    present = [tok for tok in originals if known(tok)]
    absent = [tok for tok in originals if tok not in present]
    if not present:
        return False
    distinctive_present = [tok for tok in present if tok not in GENERIC_QUERY and len(tok) >= 2]
    distinctive_absent = [tok for tok in absent if tok not in GENERIC_QUERY and len(tok) >= 4]
    if distinctive_absent and not distinctive_present:
        return False
    return True


def query_phrases(text: str) -> list[str]:
    tokens = tokenize(text)
    phrases = []
    for size in (4, 3, 2):
        if len(tokens) < size:
            continue
        for i in range(len(tokens) - size + 1):
            window = tokens[i : i + size]
            content = [tok for tok in window if tok not in HI_STOP and tok not in EN_STOP and not tok.isdigit()]
            if len(content) < 2:
                continue
            phrase = " ".join(window)
            if phrase not in phrases and len(phrase) >= 6:
                phrases.append(phrase)
    return phrases[:8]


def primary_terms(text: str) -> list[str]:
    """Content terms taken from the question itself, plus direct script mappings — not broad expansions."""
    terms = []
    for tok in content_tokens(text):
        if tok not in terms:
            terms.append(tok)
        for mapped in ROMAN_CONTENT.get(tok, []):
            if mapped not in terms:
                terms.append(mapped)
    for gu, hi in GU_TO_HI.items():
        if gu in (text or "") and hi not in terms:
            terms.append(hi)
    blob = text or ""
    if "गुरु" in blob and ("तत्त्व" in blob or "तत्व" in blob or "tattva" in blob.lower()):
        for extra in ("गुरुतत्व", "गुरु", "माध्यम"):
            if extra not in terms:
                terms.append(extra)
    if "तत्त्व" in terms and "तत्व" not in terms:
        terms.append("तत्व")
    if "तत्व" in terms and "तत्त्व" not in terms:
        terms.append("तत्त्व")
    return [t for t in terms if t not in HI_STOP and t not in EN_STOP and len(t) >= 2]


def expand_query(text: str) -> tuple[list[str], dict[str, float]]:
    """Return search tokens and weights. Original content terms weigh more than expansions."""
    weights: dict[str, float] = {}
    original = content_tokens(text)
    for tok in original:
        weights[tok] = max(weights.get(tok, 0), 3.0)
        mapped = ROMAN_CONTENT.get(tok)
        if mapped:
            for m in mapped:
                weights[m] = max(weights.get(m, 0), 2.4)
    for gu, hi in GU_TO_HI.items():
        if gu in (text or ""):
            weights[hi] = max(weights.get(hi, 0), 2.6)
    low = (text or "").lower()
    if any(k in low for k in ("30", "तीस", "minute", "मिनट")) and any(
        k in low for k in ("dhyan", "ध्यान", "meditation", "minute", "मिनट")
    ):
        weights["मिनट"] = max(weights.get("मिनट", 0), 2.2)
        weights["30"] = 1.5
        weights["ध्यान"] = max(weights.get("ध्यान", 0), 2.0)
    if _looks_distressed(text):
        for extra in ("अशांति", "अशांत", "चिंता", "शांति", "समस्या", "वर्तमान", "साक्षी", "चित्त", "मुसीबत"):
            weights[extra] = max(weights.get(extra, 0), 1.15)
        weights["जीवन"] = max(weights.get("जीवन", 0), 1.4)
    if any(k in low for k in ("अंतर", "difference", " farq", "versus", " vs ")):
        weights["अंतर"] = max(weights.get("अंतर", 0), 1.2)
    tokens = [t for t, w in weights.items() if w > 0 and t not in HI_STOP and t not in EN_STOP]
    return tokens, weights


def _looks_distressed(text: str) -> bool:
    low = (text or "").lower()
    if any(m in low for m in DISTRESS_MARKERS):
        return True
    if "परेशान" in (text or "") or "अशांत" in (text or ""):
        return True
    return False


def split_sentences(text: str) -> list[str]:
    text = clean_whitespace(text)
    if not text:
        return []
    parts = re.split(r"(?<=[।!?])\s+|\n+", text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) >= 12:
            out.append(p)
    return out or [text]


def stable_hash(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


@dataclass
class LangCopy:
    code: str


def answer_language(detected: str) -> str:
    if detected in {"gu", "gu-roman"}:
        return "gu"
    if detected == "en":
        return "en"
    if detected == "hinglish":
        return "hinglish"
    return "hi"
