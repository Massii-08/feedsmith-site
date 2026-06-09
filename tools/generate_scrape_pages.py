from __future__ import annotations

"""
generate_scrape_pages.py — Feedsmith pSEO page generator.

Reads tools/targets.json and scrape/_template.html, then writes one
scrape/<slug>.html landing page per target by filling the template
placeholders. Pure Python 3 standard library (json, pathlib, html).

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
rate limits, and the client operating and owning the resulting feed —
never around getting around protections.

The script is idempotent: running it again overwrites the generated
pages with the same content for the same inputs.
"""

import html
import json
from pathlib import Path

# Swappable canonical/OG base domain (placeholder until a real domain is set).
BASE_URL = "https://feedsmith.dev"

# Repo root is the parent of this tools/ directory.
ROOT = Path(__file__).resolve().parent.parent
TARGETS_PATH = ROOT / "tools" / "targets.json"
TEMPLATE_PATH = ROOT / "scrape" / "_template.html"
OUTPUT_DIR = ROOT / "scrape"

# Required keys for every target entry.
REQUIRED_KEYS = ("slug", "site", "vertical", "what_data", "intro")


def build_page(template: str, target: dict) -> str:
    """Fill the template placeholders for one target, escaping all values."""
    site = html.escape(target["site"])
    vertical = html.escape(target["vertical"])
    what_data = html.escape(target["what_data"])
    intro = html.escape(target["intro"])
    slug = target["slug"]

    canonical = f"{BASE_URL}/scrape/{slug}.html"

    # Keyword-rich, unique title + description per page.
    title = f"Scrape {target['site']} the compliant way — {target['vertical']} data feed | Feedsmith"
    description = (
        f"Reliable, maintained feed of public {target['vertical'].lower()} data from "
        f"{target['site']}: {target['what_data']}. Public sources only, within ToS and rate limits."
    )
    h1 = f"A reliable data feed from {target['site']}"

    replacements = {
        "{{TITLE}}": html.escape(title),
        "{{DESCRIPTION}}": html.escape(description),
        "{{CANONICAL}}": html.escape(canonical),
        "{{H1}}": html.escape(h1),
        "{{SITE}}": site,
        "{{VERTICAL}}": vertical,
        "{{WHAT_DATA}}": what_data,
        "{{BODY_INTRO}}": intro,
    }

    page = template
    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)
    return page


def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))

    if not isinstance(targets, list):
        raise SystemExit("targets.json must be a JSON array of target objects.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for target in targets:
        missing = [k for k in REQUIRED_KEYS if k not in target or target[k] == ""]
        if missing:
            raise SystemExit(
                f"Target {target.get('slug', '<no slug>')} is missing keys: {', '.join(missing)}"
            )
        out_path = OUTPUT_DIR / f"{target['slug']}.html"
        out_path.write_text(build_page(template, target), encoding="utf-8")
        written.append(out_path)

    print(f"Generated {len(written)} scrape page(s) into {OUTPUT_DIR}:")
    for path in written:
        print(f"  - {path.relative_to(ROOT)}")
    print(
        "Reminder: targets must be public / factual / non-PII verticals "
        "(exclude social networks, PII, and login-gated sites)."
    )


if __name__ == "__main__":
    main()
