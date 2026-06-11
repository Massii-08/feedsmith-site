from __future__ import annotations

"""
generate_scrape_pages.py — Feedsmith pSEO page generator (multilingual).

Reads tools/targets.json (EN data) plus tools/targets-i18n-<lang>.json
(translated data) and the per-language templates scrape/_template.html /
scrape/_template_<lang>.html, then writes one landing page per target and
per language:

    scrape/<slug>.html            (EN)
    <lang>/scrape/<slug>.html     (de / fr / it)

Every page carries the full hreflang cluster and a language switch that
points at its own equivalents, so visitors never lose their place by
switching language. Pure Python 3 standard library.

pSEO discipline
---------------
Programmatic SEO multiplies pages cheaply, so the only safeguard is the
INPUT. tools/targets.json must contain SAFE VERTICALS ONLY:

  - public, factual, non-PII data (e-commerce catalogs, real-estate
    LISTINGS, marketplaces, B2B directories, travel prices, sandboxes);
  - sources whose data any visitor sees without logging in.

NEVER add social networks, user profiles, login-gated sites, or anything
that touches personal data. Every generated page is framed around
reliability on public data, respect for Terms of Service / robots.txt /
rate limits, and the client operating and owning the resulting feed.

The script is idempotent: running it again overwrites the generated
pages with the same content for the same inputs.
"""

import json
from pathlib import Path

BASE_URL = "https://feedsmith.net"

ROOT = Path(__file__).resolve().parent.parent
TARGETS_PATH = ROOT / "tools" / "targets.json"
LANGS = ("de", "fr", "it")

REQUIRED_KEYS = ("slug", "site", "vertical", "what_data", "intro")
I18N_KEYS = ("site", "vertical", "what_data", "intro")

# Per-language SEO strings. {site}/{vertical}/{what_data} are filled per target.
SEO = {
    "en": {
        "title": "Scrape {site} the compliant way — {vertical} data feed | Feedsmith",
        "description": (
            "Reliable, maintained feed of public {vertical_lc} data from "
            "{site}: {what_data}. Public sources only, within ToS and rate limits."
        ),
        "h1": "A reliable data feed from {site}",
    },
    "de": {
        "title": "{site} regelkonform auslesen — {vertical}-Datenfeed | Feedsmith",
        "description": (
            "Verlässlicher, betreuter Feed öffentlicher Daten ({vertical_lc}) aus "
            "{site}: {what_data}. Nur öffentliche Quellen, im Rahmen von AGB und Rate-Limits."
        ),
        "h1": "Ein verlässlicher Datenfeed aus {site}",
    },
    "fr": {
        "title": "Extraire {site} en conformité — flux de données {vertical_lc} | Feedsmith",
        "description": (
            "Flux fiable et maintenu de données publiques ({vertical_lc}) depuis "
            "{site} : {what_data}. Sources publiques uniquement, dans le respect des CGU et des limites de débit."
        ),
        "h1": "Un flux de données fiable depuis {site}",
    },
    "it": {
        "title": "Estrarre dati da {site} in conformità — feed {vertical_lc} | Feedsmith",
        "description": (
            "Feed affidabile e mantenuto di dati pubblici ({vertical_lc}) da "
            "{site}: {what_data}. Solo fonti pubbliche, nel rispetto dei ToS e dei limiti di frequenza."
        ),
        "h1": "Un feed di dati affidabile da {site}",
    },
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def page_url(lang: str, slug: str) -> str:
    prefix = "" if lang == "en" else f"{lang}/"
    return f"{BASE_URL}/{prefix}scrape/{slug}.html"


def alternates(slug: str) -> str:
    lines = [
        f'  <link rel="alternate" hreflang="{l}" href="{page_url(l, slug)}">'
        for l in ("en", "de", "fr", "it")
    ]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{page_url("en", slug)}">')
    return "\n".join(lines)


def langswitch(slug: str) -> str:
    parts = [
        f'<a href="{page_url(l, slug).replace(BASE_URL, "")}">{l.upper()}</a>'
        for l in ("en", "de", "fr", "it")
    ]
    return " · ".join(parts)


def build_page(template: str, lang: str, target: dict, data: dict) -> str:
    slug = target["slug"]
    seo = SEO[lang]
    fmt = dict(
        site=data["site"],
        vertical=data["vertical"],
        vertical_lc=data["vertical"].lower() if lang == "en" or lang == "fr" or lang == "it" else data["vertical"],
        what_data=data["what_data"],
    )
    title = seo["title"].format(**fmt)
    description = seo["description"].format(**fmt)
    h1 = seo["h1"].format(**fmt)

    replacements = {
        "{{TITLE}}": esc(title),
        "{{DESCRIPTION}}": esc(description),
        "{{CANONICAL}}": esc(page_url(lang, slug)),
        "{{ALTERNATES}}": alternates(slug),
        "{{H1}}": esc(h1),
        "{{SITE}}": esc(data["site"]),
        "{{VERTICAL}}": esc(data["vertical"]),
        "{{WHAT_DATA}}": esc(data["what_data"]),
        "{{BODY_INTRO}}": esc(data["intro"]),
        "{{LANGSWITCH}}": langswitch(slug),
    }
    page = template
    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)
    return page


def main() -> None:
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    if not isinstance(targets, list):
        raise SystemExit("targets.json must be a JSON array of target objects.")
    for target in targets:
        missing = [k for k in REQUIRED_KEYS if not target.get(k)]
        if missing:
            raise SystemExit(
                f"Target {target.get('slug', '<no slug>')} is missing keys: {', '.join(missing)}"
            )

    templates = {"en": (ROOT / "scrape" / "_template.html").read_text(encoding="utf-8")}
    i18n: dict[str, dict] = {}
    for lang in LANGS:
        tpl = ROOT / "scrape" / f"_template_{lang}.html"
        data = ROOT / "tools" / f"targets-i18n-{lang}.json"
        if not tpl.exists() or not data.exists():
            print(f"note: skipping '{lang}' (missing {tpl.name} or {data.name})")
            continue
        templates[lang] = tpl.read_text(encoding="utf-8")
        i18n[lang] = json.loads(data.read_text(encoding="utf-8"))
        for target in targets:
            entry = i18n[lang].get(target["slug"])
            if not entry or any(not entry.get(k) for k in I18N_KEYS):
                raise SystemExit(f"targets-i18n-{lang}.json: missing/incomplete entry '{target['slug']}'")

    written = []
    for lang, template in templates.items():
        out_dir = ROOT / "scrape" if lang == "en" else ROOT / lang / "scrape"
        out_dir.mkdir(parents=True, exist_ok=True)
        for target in targets:
            data = target if lang == "en" else i18n[lang][target["slug"]]
            out_path = out_dir / f"{target['slug']}.html"
            out_path.write_text(build_page(template, lang, target, data), encoding="utf-8")
            written.append(out_path)

    print(f"Generated {len(written)} scrape page(s):")
    for path in written:
        print(f"  - {path.relative_to(ROOT)}")
    print(
        "Reminder: targets must be public / factual / non-PII verticals "
        "(exclude social networks, PII, and login-gated sites)."
    )


if __name__ == "__main__":
    main()
