from __future__ import annotations

import re

_ARABIC_TO_PERSIAN = str.maketrans({
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
    "ة": "ه",
    "ؤ": "و",
    "إ": "ا",
    "أ": "ا",
    "ٱ": "ا",
})

_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED]")
_SPACE_RE = re.compile(r"\s+")


def normalize_fa(text: str) -> str:
    text = text.translate(_ARABIC_TO_PERSIAN)
    text = text.replace("\u200c", " ").replace("‌", " ")
    text = _DIACRITICS_RE.sub("", text)
    text = _SPACE_RE.sub(" ", text)
    return text.strip().lower()
