from __future__ import annotations

"""
check_locales.py — structural + safety validator for localized pages.

For every localized offer/guide page, verifies against its English source:
  1. identical tag sequence (tag names + class attributes) — catches broken
     markup, dropped sections, reformatting;
  2. internal links carry the language prefix; hreflang cluster untouched;
  3. legal-safe wording (no affirmative circumvention verbs);
  4. no leftover long English sentences (heuristic).

Exit code 1 on any finding. Run: python3 tools/check_locales.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("de", "fr", "it")
PAGES = [
    "offers/scraper.html",
    "offers/managed-data-feed.html",
    "offers/discord-bot.html",
    "offers/hidden-api-audit.html",
    "guides/what-is-a-hidden-api.html",
    "guides/no-code-scraper-keeps-breaking.html",
    "guides/cloudflare-protected-public-sites.html",
]

TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9-]+)((?:\s+[^<>]*?)?)(/?)>", re.S)
CLASS_RE = re.compile(r'class="([^"]*)"')

# Affirmative circumvention verbs (legal guard). Negated framings used on the
# site ("statt Umgehung", "pas du contournement", "non aggiramento") are fine.
FORBIDDEN = re.compile(
    r"\b(bypass\w*|umgeh\w+|aushebel\w+|contourn\w+|déjou\w+|aggir\w+|elud\w+)\b",
    re.I,
)
ALLOWED_NEGATIONS = (
    "statt umgehung",
    "keine umgehung",
    "niemals",
    "pas du contournement",
    "pas de contournement",
    "jamais de contourner",
    "jamais à contourner",
    "jamais comme",
    "ne s'agit jamais",
    "ni un",
    "non aggiramento",
    "mai di aggirare",
    "mai come",
    "non si tratta mai",
    "not circumvention",
)

# Heuristic: English function-word runs that should not survive translation.
ENGLISH_RE = re.compile(
    r"\b(the|and|with|you|your|from|that|this|when|what)\b(?:[^<>]*?\b(the|and|with|you|your|from|that|this|when|what)\b){2}",
    re.I,
)
# Tags whose text content legitimately stays English (code, brand, repo names).
SKIP_TEXT_PARENTS = {"code", "script", "style", "svg", "title", "desc"}


def tag_signature(html: str) -> list[str]:
    sig = []
    for m in TAG_RE.finditer(html):
        closing, name, attrs, selfclose = m.groups()
        cls = CLASS_RE.search(attrs or "")
        sig.append(f"{closing}{name}" + (f".{cls.group(1)}" if cls else ""))
    return sig


def text_chunks(html: str):
    """Visible text chunks with a rough parent-tag context."""
    chunks = []
    stack: list[str] = []
    pos = 0
    for m in TAG_RE.finditer(html):
        text = html[pos:m.start()]
        if text.strip():
            chunks.append((stack[-1] if stack else "", text))
        closing, name, _attrs, selfclose = m.groups()
        lname = name.lower()
        if closing:
            while stack and stack[-1] != lname:
                stack.pop()
            if stack:
                stack.pop()
        elif not selfclose and lname not in {"meta", "link", "br", "img", "input", "hr"}:
            stack.append(lname)
        pos = m.end()
    return chunks


def main() -> int:
    problems: list[str] = []
    for lang in LANGS:
        for rel in PAGES:
            src = ROOT / rel
            loc = ROOT / lang / rel
            tag = f"{lang}/{rel}"
            if not loc.exists():
                problems.append(f"{tag}: MISSING")
                continue
            s, t = src.read_text(encoding="utf-8"), loc.read_text(encoding="utf-8")

            sig_s, sig_t = tag_signature(s), tag_signature(t)
            if sig_s != sig_t:
                # report first divergence point
                i = next((i for i, (a, b) in enumerate(zip(sig_s, sig_t)) if a != b), min(len(sig_s), len(sig_t)))
                a = sig_s[i] if i < len(sig_s) else "<end>"
                b = sig_t[i] if i < len(sig_t) else "<end>"
                problems.append(f"{tag}: tag structure diverges at #{i}: EN={a!r} vs {lang.upper()}={b!r}")

            if f'<html lang="{lang}">' not in t:
                problems.append(f"{tag}: missing <html lang=\"{lang}\">")
            if f"https://feedsmith.net/{lang}/{rel}" not in t:
                problems.append(f"{tag}: canonical not localized")
            for line in re.findall(r'<link rel="alternate"[^>]*>', s):
                if line not in t:
                    problems.append(f"{tag}: hreflang line altered: {line[:80]}")
            # the footer lang-switch legitimately links to the EN equivalent —
            # strip it before scanning for unprefixed internal links
            t_no_switch = re.sub(r'<span class="lang-switch">.*?</span>', "", t, flags=re.S)
            for href in re.findall(r'href="(/(?:offers|guides)/[^"]+|/#[a-z]+)"', t_no_switch):
                problems.append(f"{tag}: unprefixed internal link {href}")

            lower = t.lower()
            for m in FORBIDDEN.finditer(lower):
                ctx = lower[max(0, m.start() - 40):m.end() + 20]
                if not any(n in ctx for n in ALLOWED_NEGATIONS):
                    problems.append(f"{tag}: forbidden wording '{m.group(0)}' (ctx: …{ctx.strip()}…)")

            for parent, text in text_chunks(t):
                if parent in SKIP_TEXT_PARENTS:
                    continue
                if ENGLISH_RE.search(text) and len(text.strip()) > 40:
                    problems.append(f"{tag}: possible untranslated text: {text.strip()[:80]!r}")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK — {len(LANGS) * len(PAGES)} localized pages structurally identical, links prefixed, wording safe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
