from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import FONT_PATH, PLATES_DIR

PAGE_W, PAGE_H = 1100, 1560


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    return ImageFont.load_default()


def render_text_plate(page_number: int, text: str, highlight: str | None = None) -> Path:
    """Render an indexed-text plate. This is not a photograph of the printed page."""
    PLATES_DIR.mkdir(parents=True, exist_ok=True)
    out = PLATES_DIR / f"page_{page_number:03d}.png"
    img = Image.new("RGB", (PAGE_W, PAGE_H), "#F7F1E6")
    draw = ImageDraw.Draw(img)
    draw.rectangle((36, 36, PAGE_W - 36, PAGE_H - 36), outline="#C4B49A", width=2)
    draw.rectangle((48, 48, PAGE_W - 48, PAGE_H - 48), outline="#E4D3AE", width=1)
    title_font = _font(28)
    body_font = _font(26)
    small = _font(18)
    draw.text((72, 68), "आध्यात्मिक सत्य", font=title_font, fill="#6E2A38")
    draw.text((72, 108), f"स्रोत पृष्ठ {page_number}", font=small, fill="#A68445")
    draw.line((72, 142, PAGE_W - 72, 142), fill="#E4D3AE", width=1)
    note = "Indexed text plate — not a scan. Verify wording on the source image."
    draw.text((72, PAGE_H - 78), note, font=small, fill="#8A7564")

    highlight_key = (highlight or "").strip()[:80]
    y = 168
    max_w = PAGE_W - 150
    for paragraph in (text or "").split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            y += 16
            continue
        # wrap by measured width
        words = paragraph.split(" ")
        line = ""
        lines = []
        for word in words:
            trial = word if not line else line + " " + word
            bbox = draw.textbbox((0, 0), trial, font=body_font)
            if bbox[2] > max_w and line:
                lines.append(line)
                line = word
            else:
                line = trial
        if line:
            lines.append(line)
        for line in lines:
            if y > PAGE_H - 120:
                draw.text((72, y), "…", font=body_font, fill="#3A2418")
                img.save(out, "PNG")
                return out
            color = "#6E2A38" if highlight_key and highlight_key[:18] in line else "#2A211C"
            draw.text((72, y), line, font=body_font, fill=color)
            y += 40
    img.save(out, "PNG")
    return out
