from __future__ import annotations

"""
build_locale_homes.py — Feedsmith localized home generator.

The ENGLISH home (index.html) is the single source of truth for structure.
This script clones it into de/, fr/ and it/ by applying exact text
substitutions, so every language version has the SAME sections, the SAME
working buttons and the SAME signature hero motif — translated.

Rules encoded here:
  - nav / footer anchors become LOCAL (#offers, #contact, ...) so a visitor
    never gets bounced to the English home by switching language;
  - brand + footer "Home" link point at the local home (/de/, /fr/, /it/);
  - head metadata (title, description, OG, canonical, og:url, lang) is
    fully localized; hreflang cluster stays identical on every page;
  - offer cards / guide cards link to the (English) detail pages — the only
    versions that exist — and the section intro says so.

Every replacement is asserted: if a future edit to index.html breaks a key,
the build fails loudly instead of silently shipping a diverged page.

Usage:  python3 tools/build_locale_homes.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

# ---------------------------------------------------------------- shared --

# Structural swaps applied to every locale BEFORE the text dictionary.
# /#anchor  ->  #anchor  (stay on the local page)
STRUCTURAL = [
    ('href="/#offers"', 'href="#offers"'),
    ('href="/#guides"', 'href="#guides"'),
    ('href="/#portfolio"', 'href="#portfolio"'),
    ('href="/#contact"', 'href="#contact"'),
]

HEAD_EN = {
    "lang_attr": '<html lang="en">',
    "title": "<title>Feedsmith — Reliable Data Feeds from Public Sources | Web Scraping Specialist</title>",
    "desc": '<meta name="description" content="When no-code tools and AI scrapers get blocked or return empty pages, Feedsmith extracts clean public data and keeps it running. Reliable, maintained data feeds — factual, non-PII, you operate and own the data." />',
    "canonical": '<link rel="canonical" href="https://feedsmith.net/" />',
    "og_title": '<meta property="og:title" content="Feedsmith — Reliable Data Feeds from Public Sources" />',
    "og_desc": '<meta property="og:description" content="Clean, maintained data feeds from public sources — when no-code and AI scrapers fail." />',
    "og_url": '<meta property="og:url" content="https://feedsmith.net/" />',
    "brand": '<a class="brand" href="/"><span class="brand-mark">◆</span> Feedsmith</a>',
}


def head_block(lang: str, title: str, desc: str, og_title: str, og_desc: str) -> dict:
    base = f"https://feedsmith.net/{lang}/"
    return {
        HEAD_EN["lang_attr"]: f'<html lang="{lang}">',
        HEAD_EN["title"]: f"<title>{title}</title>",
        HEAD_EN["desc"]: f'<meta name="description" content="{desc}" />',
        HEAD_EN["canonical"]: f'<link rel="canonical" href="{base}" />',
        HEAD_EN["og_title"]: f'<meta property="og:title" content="{og_title}" />',
        HEAD_EN["og_desc"]: f'<meta property="og:description" content="{og_desc}" />',
        HEAD_EN["og_url"]: f'<meta property="og:url" content="{base}" />',
        HEAD_EN["brand"]: f'<a class="brand" href="/{lang}/"><span class="brand-mark">◆</span> Feedsmith</a>',
    }


# ------------------------------------------------------------------- FR ---

FR = {
    # nav
    '<a href="#offers">Offers</a>': '<a href="#offers">Offres</a>',
    '<a href="#guides">Guides</a>': '<a href="#guides">Guides</a>',
    '<a href="#portfolio">Portfolio</a>': '<a href="#portfolio">Portfolio</a>',
    '>Free feasibility check</a>\n  </nav>': '>Étude de faisabilité gratuite</a>\n  </nav>',
    # hero
    '<span class="eyebrow">Web scraping &amp; maintained data feeds</span>': '<span class="eyebrow">Web scraping &amp; flux de données maintenus</span>',
    '<h1>Reliable data feeds<br class="lb"> <span class="hl">from public sources</span>.</h1>': '<h1>Des flux de données fiables<br class="lb"> <span class="hl">issus de sources publiques</span>.</h1>',
    'When Apify, Octoparse or a ChatGPT-written script gets blocked, returns empty pages, or breaks every time the site changes — I extract clean public data, and keep it running.': "Quand Apify, Octoparse ou un script écrit par ChatGPT se fait bloquer, renvoie des pages vides ou casse à chaque changement du site — j'extrais des données publiques propres, et je les maintiens dans la durée.",
    'aria-label="The public site or URL you need data from" placeholder="The public site / URL"': 'aria-label="Le site ou l\'URL publique dont vous avez besoin" placeholder="Le site / l\'URL publique"',
    '<button class="btn btn-primary" type="submit">Get a free feasibility check</button>': '<button class="btn btn-primary" type="submit">Étude de faisabilité gratuite</button>',
    'Public sources only · no logins, no personal data · you operate and own the data.': "Sources publiques uniquement · pas de comptes, pas de données personnelles · vous exploitez et possédez les données.",
    # hero motif a11y
    'Raw public web pages, forged into a clean structured data feed': "Des pages web publiques brutes, forgées en un flux de données propre et structuré",
    'Messy website windows flow through a forge spark and come out as a tidy live data table with CSV and JSON output.': "Des fenêtres de sites désordonnées traversent une étincelle de forge et ressortent en table de données propre, avec export CSV et JSON.",
    # screener
    '<div class="kick">The deliverable</div>': '<div class="kick">Le livrable</div>',
    '<h2 class="section-title">A clean dataset, not a promise.</h2>': '<h2 class="section-title">Un jeu de données propre, pas une promesse.</h2>',
    "You get structured public data — CSV, JSON, or an API — with the fields you need and nothing you don't. Factual, non-personal, and verifiable against the source.": "Vous recevez des données publiques structurées — CSV, JSON ou API — avec les champs dont vous avez besoin et rien d'autre. Factuelles, non personnelles et vérifiables à la source.",
    '<span class="lab">Currency</span>': '<span class="lab">Devise</span>',
    '<span class="lab" style="margin-left:8px">Availability</span>': '<span class="lab" style="margin-left:8px">Disponibilité</span>',
    '<span class="lab" style="margin-left:8px">Rating</span>': '<span class="lab" style="margin-left:8px">Note</span>',
    '<button class="chip on" type="button">In stock</button>': '<button class="chip on" type="button">En stock</button>',
    '<span class="count"><b>6</b> of <b>2,480</b> products</span>': '<span class="count"><b>6</b> sur <b>2 480</b> produits</span>',
    '<th scope="col">Product</th>': '<th scope="col">Produit</th>',
    '<th scope="col">Category</th>': '<th scope="col">Catégorie</th>',
    '<th scope="col" class="r">Price</th>': '<th scope="col" class="r">Prix</th>',
    '<th scope="col" class="r">Availability</th>': '<th scope="col" class="r">Disponibilité</th>',
    '<th scope="col" class="r">Rating</th>': '<th scope="col" class="r">Note</th>',
    '<th scope="col">Source</th>': '<th scope="col">Source</th>',
    '<td>Peripherals</td>': '<td>Périphériques</td>',
    '<td>Accessories</td>': '<td>Accessoires</td>',
    '<td>Displays</td>': '<td>Écrans</td>',
    '<td>Audio</td>': '<td>Audio</td>',
    '<td class="r">In stock</td>': '<td class="r">En stock</td>',
    '<td class="r">3 left</td>': '<td class="r">3 restants</td>',
    '<td class="r">Out of stock</td>': '<td class="r">Rupture</td>',
    'public catalog ↗': 'catalogue public ↗',
    'Sample data, public sources only. Factual / non-personal fields. robots.txt and sensible rate limits respected. You operate and own the feed.': "Données d'exemple, sources publiques uniquement. Champs factuels / non personnels. robots.txt et limites de débit respectés. Vous exploitez et possédez le flux.",
    # offers
    '<div class="kick">Offers</div>': '<div class="kick">Offres</div>',
    '<h2 class="section-title">Start small. Scale to a maintained feed.</h2>': '<h2 class="section-title">Commencez petit. Passez à un flux maintenu.</h2>',
    'Begin with a low-risk audit, get a one-off dataset, or hand the upkeep to me with a managed feed.': "Démarrez par un audit sans risque, recevez un export ponctuel, ou confiez-moi la maintenance avec un flux géré. Pages de détail en anglais.",
    '<h3>Hidden-API Audit</h3>': "<h3>Audit d'API cachée</h3>",
    'I check one public site, find the cleanest data route, and send you ~50 real sample rows. A low-risk way to start.': "J'examine un site public, j'identifie la voie d'accès la plus propre et je vous envoie ~50 lignes d'échantillon réelles. Le point de départ sans risque.",
    '<div class="price">From €150<small> &nbsp;fixed</small></div>': '<div class="price">Dès 150 €<small> &nbsp;fixe</small></div>',
    '<h3>One-off Scraper</h3>': '<h3>Scraper ponctuel</h3>',
    'A robust scraper for one public source, delivered as tested code you own. Clean CSV / JSON / API output.': "Un scraper robuste pour une source publique, livré en code testé qui vous appartient. Sortie propre CSV / JSON / API.",
    '<span class="pill">Core</span>': '<span class="pill">Cœur</span>',
    '<h3>Managed Data Feed</h3>': '<h3>Flux de données géré</h3>',
    "Scraper + scheduled delivery + monitoring. The source changes, it breaks, I fix it — usually before you notice.": "Scraper + livraison planifiée + monitoring. La source change, ça casse, je répare — souvent avant que vous le remarquiez.",
    '<small> + €150–500/mo</small>': '<small> + 150–500 €/mois</small>',
    '<h3>Discord Bot</h3>': '<h3>Bot Discord</h3>',
    'A custom bot for your community: automation, public-data lookups, scheduled posts. Built and hosted.': "Un bot sur mesure pour votre communauté : automatisations, requêtes de données publiques, posts planifiés. Construit et hébergé.",
    '<small> + hosting</small>': '<small> + hébergement</small>',
    '<span class="more">See details →</span>': '<span class="more">Voir le détail →</span>',
    # how it works
    '<div class="kick">How it works</div>': '<div class="kick">Comment ça marche</div>',
    '<h2 class="section-title">From a blocked scraper to a feed you can rely on.</h2>': '<h2 class="section-title">D\'un scraper bloqué à un flux sur lequel compter.</h2>',
    '<h3>Audit</h3><p>I check the public source and find the most reliable extraction route — a hidden API where one exists.</p>': "<h3>Audit</h3><p>J'examine la source publique et j'identifie la voie d'extraction la plus fiable — une API cachée quand elle existe.</p>",
    '<h3>Build</h3><p>A tested scraper that handles JS-heavy and Cloudflare-protected public pages, outputting clean data.</p>': "<h3>Construction</h3><p>Un scraper testé qui gère les pages publiques riches en JavaScript ou protégées par Cloudflare, avec une sortie propre.</p>",
    '<h3>Schedule &amp; monitor</h3><p>Delivery on your cadence, with monitoring. When the source changes and it breaks, I repair it.</p>': "<h3>Planification &amp; monitoring</h3><p>Livraison à votre cadence, avec surveillance. Quand la source change et que ça casse, je répare.</p>",
    '<h3>You operate &amp; own</h3><p>You run the tool and own the data. I build and maintain it — a tool, not an operating service.</p>': "<h3>Vous exploitez &amp; possédez</h3><p>Vous faites tourner l'outil et possédez les données. Je construis et je maintiens — un outil, pas un service d'exploitation.</p>",
    # trust
    '<div class="kick">Scope &amp; trust</div>': '<div class="kick">Cadre &amp; confiance</div>',
    '<h2 class="section-title">Reliability, not circumvention.</h2>': '<h2 class="section-title">De la fiabilité, pas du contournement.</h2>',
    '<h4>Public, logged-out pages only</h4><p>Factual / business data: prices, specs, stock, listings, market data, schedules. No logins, no paywalls, no accounts.</p>': "<h4>Pages publiques, hors connexion uniquement</h4><p>Données factuelles / business : prix, specs, stocks, annonces, données de marché, horaires. Pas de comptes, pas de paywalls.</p>",
    '<h4>No personal data</h4><p>Strictly non-PII. No names with contacts, profiles, or photos — B2B and factual data only.</p>': "<h4>Aucune donnée personnelle</h4><p>Strictement non-PII. Pas de noms avec contacts, de profils ou de photos — données B2B et factuelles uniquement.</p>",
    '<h4>robots.txt &amp; rate limits respected</h4><p>Pages are read like a normal visitor would, at a respectful rate. Output is structured and transformed.</p>': "<h4>robots.txt &amp; limites de débit respectés</h4><p>Les pages sont lues comme le ferait un visiteur normal, à un rythme respectueux. La sortie est structurée et transformée.</p>",
    '<h4>You operate and own the data</h4><p>I build and maintain the tool; you run it and control the data. A clean, documented handover every time.</p>': "<h4>Vous exploitez et possédez les données</h4><p>Je construis et maintiens l'outil ; vous l'exploitez et contrôlez les données. Une passation propre et documentée, à chaque fois.</p>",
    '<div class="st">Typically in scope</div>': '<div class="st">Typiquement dans le périmètre</div>',
    '<div class="source-row"><span>Product prices, specs, stock</span><span class="lk">e-commerce</span></div>': '<div class="source-row"><span>Prix produits, specs, stocks</span><span class="lk">e-commerce</span></div>',
    '<div class="source-row"><span>Listings (price, size, location)</span><span class="lk">real estate</span></div>': '<div class="source-row"><span>Annonces (prix, surface, localisation)</span><span class="lk">immobilier</span></div>',
    '<div class="source-row"><span>Catalogue / marketplace data</span><span class="lk">marketplace</span></div>': '<div class="source-row"><span>Données catalogue / marketplace</span><span class="lk">marketplace</span></div>',
    '<div class="source-row"><span>Market data, schedules, prices</span><span class="lk">travel · finance</span></div>': '<div class="source-row"><span>Données de marché, horaires, prix</span><span class="lk">voyage · finance</span></div>',
    'Feedsmith builds a <strong>tool</strong> for reading <strong>public, factual data</strong>. It is not used to access logins, paywalls, or personal data. You remain the operator and owner of the data and confirm your right to access the source.': "Feedsmith construit un <strong>outil</strong> de lecture de <strong>données publiques et factuelles</strong>. Il ne sert pas à accéder à des comptes, des paywalls ou des données personnelles. Vous restez l'exploitant et le propriétaire des données et confirmez votre droit d'accès à la source.",
    # portfolio
    '<div class="kick">Proof</div>': '<div class="kick">Preuves</div>',
    '<h2 class="section-title">Open-source, tested, and runnable.</h2>': '<h2 class="section-title">Open source, testé, exécutable.</h2>',
    'Not a slide deck — real code you can read, clone, and run. The hard 20% of scraping that no-code tools fail at.': "Pas un slide deck — du vrai code à lire, cloner et lancer. Les 20 % difficiles du scraping où les outils no-code échouent.",
    'The Managed Data Feed offer in code: resilient fetch → no-PII policy → schedule → self-healing monitor → CSV/JSON/webhook, in FastAPI.': "L'offre Flux de données géré, en code : fetch résilient → politique no-PII → planification → monitoring auto-réparant → CSV/JSON/webhook, en FastAPI.",
    "Read a site's internal JSON API directly instead of parsing fragile HTML — faster and far more stable.": "Lire directement l'API JSON interne d'un site au lieu de parser un HTML fragile — plus rapide et bien plus stable.",
    'Why a public page returns empty: a TLS fingerprint check before render. Read it like a normal browser, compliantly.': "Pourquoi une page publique revient vide : un contrôle d'empreinte TLS avant le rendu. La lire comme un navigateur normal, en conformité.",
    '<span class="more">View on GitHub ↗</span>': '<span class="more">Voir sur GitHub ↗</span>',
    # guides
    '<div class="kick">Guides</div>': '<div class="kick">Guides</div>',
    '<h2 class="section-title">The why behind the work.</h2>': '<h2 class="section-title">Le pourquoi derrière le travail.</h2>',
    '<h3>Why your no-code scraper keeps breaking</h3>': '<h3>Pourquoi votre scraper no-code casse en boucle</h3>',
    'Layout changes, JS-rendered data, fingerprint checks — and what actually fixes them.': "Changements de layout, données rendues en JS, contrôles d'empreinte — et ce qui les corrige vraiment. (Guide en anglais.)",
    '<h3>What is a hidden API</h3>': '<h3>Qu\'est-ce qu\'une API cachée</h3>',
    'The internal JSON endpoints behind a page — and why calling them beats HTML parsing.': "Les endpoints JSON internes derrière une page — et pourquoi les appeler bat le parsing HTML. (Guide en anglais.)",
    '<h3>Cloudflare-protected public sites</h3>': '<h3>Sites publics protégés par Cloudflare</h3>',
    'Empty pages are usually a TLS fingerprint check, not a CAPTCHA — the compliant way to read them.': "Une page vide est souvent un contrôle d'empreinte TLS, pas un CAPTCHA — la façon conforme de les lire. (Guide en anglais.)",
    '<span class="more">Read the guide →</span>': '<span class="more">Lire le guide →</span>',
    # contact CTA
    '<h2>Get a free feasibility check</h2>': '<h2>Demandez une étude de faisabilité gratuite</h2>',
    "Tell me the public site and the data you need. I'll tell you if it's doable, how, and in which language.": "Indiquez-moi le site public et les données dont vous avez besoin. Je vous dis si c'est faisable, comment, et dans quelle langue.",
    'aria-label="The public site or URL" placeholder="The public site / URL"': 'aria-label="Le site ou l\'URL publique" placeholder="Le site / l\'URL publique"',
    'aria-label="Your email" placeholder="Your email"': 'aria-label="Votre e-mail" placeholder="Votre e-mail"',
    'aria-label="What data do you need, and in which language" placeholder="What data do you need? Which language (DE / FR / IT / EN)?"': 'aria-label="Quelles données vous faut-il, et dans quelle langue" placeholder="Quelles données vous faut-il ? Quelle langue (FR / DE / IT / EN) ?"',
    '<button class="btn btn-primary" type="submit">Send</button>': '<button class="btn btn-primary" type="submit">Envoyer</button>',
    'Or email <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Based in Switzerland · DE / FR / IT / EN.': 'Ou par e-mail : <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Basé en Suisse · FR / DE / IT / EN.',
    # footer
    '<div><strong>Feedsmith</strong> — reliable data feeds from public sources.': '<div><strong>Feedsmith</strong> — des flux de données fiables issus de sources publiques.',
    'Public sources only · factual / non-PII data · robots.txt &amp; rate limits respected · you operate and own the data.': "Sources publiques uniquement · données factuelles / non-PII · robots.txt &amp; limites de débit respectés · vous exploitez et possédez les données.",
    '<a href="/">Home</a>': '<a href="/fr/">Accueil</a>',
}

# ------------------------------------------------------------------- DE ---

DE = {
    '<a href="#offers">Offers</a>': '<a href="#offers">Leistungen</a>',
    '<a href="#guides">Guides</a>': '<a href="#guides">Guides</a>',
    '<a href="#portfolio">Portfolio</a>': '<a href="#portfolio">Portfolio</a>',
    '>Free feasibility check</a>\n  </nav>': '>Kostenlose Machbarkeitsprüfung</a>\n  </nav>',
    '<span class="eyebrow">Web scraping &amp; maintained data feeds</span>': '<span class="eyebrow">Web Scraping &amp; betreute Datenfeeds</span>',
    '<h1>Reliable data feeds<br class="lb"> <span class="hl">from public sources</span>.</h1>': '<h1>Verlässliche Datenfeeds<br class="lb"> <span class="hl">aus öffentlichen Quellen</span>.</h1>',
    'When Apify, Octoparse or a ChatGPT-written script gets blocked, returns empty pages, or breaks every time the site changes — I extract clean public data, and keep it running.': "Wenn Apify, Octoparse oder ein ChatGPT-Skript blockiert wird, leere Seiten liefert oder bei jeder Änderung der Website bricht — ich extrahiere saubere öffentliche Daten und halte den Feed am Laufen.",
    'aria-label="The public site or URL you need data from" placeholder="The public site / URL"': 'aria-label="Die öffentliche Website oder URL, aus der Sie Daten brauchen" placeholder="Die öffentliche Website / URL"',
    '<button class="btn btn-primary" type="submit">Get a free feasibility check</button>': '<button class="btn btn-primary" type="submit">Kostenlose Machbarkeitsprüfung</button>',
    'Public sources only · no logins, no personal data · you operate and own the data.': "Nur öffentliche Quellen · keine Logins, keine personenbezogenen Daten · Sie betreiben und besitzen die Daten.",
    'Raw public web pages, forged into a clean structured data feed': "Rohe öffentliche Webseiten, geschmiedet zu einem sauberen, strukturierten Datenfeed",
    'Messy website windows flow through a forge spark and come out as a tidy live data table with CSV and JSON output.': "Unordentliche Website-Fenster fließen durch einen Schmiedefunken und kommen als saubere Live-Datentabelle mit CSV- und JSON-Ausgabe heraus.",
    '<div class="kick">The deliverable</div>': '<div class="kick">Das Ergebnis</div>',
    '<h2 class="section-title">A clean dataset, not a promise.</h2>': '<h2 class="section-title">Ein sauberer Datensatz, kein Versprechen.</h2>',
    "You get structured public data — CSV, JSON, or an API — with the fields you need and nothing you don't. Factual, non-personal, and verifiable against the source.": "Sie erhalten strukturierte öffentliche Daten — CSV, JSON oder API — mit genau den Feldern, die Sie brauchen, und nichts darüber hinaus. Faktisch, nicht personenbezogen und an der Quelle überprüfbar.",
    '<span class="lab">Currency</span>': '<span class="lab">Währung</span>',
    '<span class="lab" style="margin-left:8px">Availability</span>': '<span class="lab" style="margin-left:8px">Verfügbarkeit</span>',
    '<span class="lab" style="margin-left:8px">Rating</span>': '<span class="lab" style="margin-left:8px">Bewertung</span>',
    '<button class="chip on" type="button">In stock</button>': '<button class="chip on" type="button">Auf Lager</button>',
    '<span class="count"><b>6</b> of <b>2,480</b> products</span>': '<span class="count"><b>6</b> von <b>2.480</b> Produkten</span>',
    '<th scope="col">Product</th>': '<th scope="col">Produkt</th>',
    '<th scope="col">Category</th>': '<th scope="col">Kategorie</th>',
    '<th scope="col" class="r">Price</th>': '<th scope="col" class="r">Preis</th>',
    '<th scope="col" class="r">Availability</th>': '<th scope="col" class="r">Verfügbarkeit</th>',
    '<th scope="col" class="r">Rating</th>': '<th scope="col" class="r">Bewertung</th>',
    '<th scope="col">Source</th>': '<th scope="col">Quelle</th>',
    '<td>Peripherals</td>': '<td>Peripherie</td>',
    '<td>Accessories</td>': '<td>Zubehör</td>',
    '<td>Displays</td>': '<td>Displays</td>',
    '<td>Audio</td>': '<td>Audio</td>',
    '<td class="r">In stock</td>': '<td class="r">Auf Lager</td>',
    '<td class="r">3 left</td>': '<td class="r">3 übrig</td>',
    '<td class="r">Out of stock</td>': '<td class="r">Ausverkauft</td>',
    'public catalog ↗': 'öffentlicher Katalog ↗',
    'Sample data, public sources only. Factual / non-personal fields. robots.txt and sensible rate limits respected. You operate and own the feed.': "Beispieldaten, nur öffentliche Quellen. Faktische / nicht personenbezogene Felder. robots.txt und Rate-Limits respektiert. Sie betreiben und besitzen den Feed.",
    '<div class="kick">Offers</div>': '<div class="kick">Leistungen</div>',
    '<h2 class="section-title">Start small. Scale to a maintained feed.</h2>': '<h2 class="section-title">Klein starten. Zum betreuten Feed ausbauen.</h2>',
    'Begin with a low-risk audit, get a one-off dataset, or hand the upkeep to me with a managed feed.': "Beginnen Sie mit einem risikoarmen Audit, holen Sie sich einen einmaligen Datensatz — oder geben Sie die Wartung mit einem betreuten Feed an mich ab. Detailseiten auf Englisch.",
    '<h3>Hidden-API Audit</h3>': '<h3>Hidden-API-Audit</h3>',
    'I check one public site, find the cleanest data route, and send you ~50 real sample rows. A low-risk way to start.': "Ich prüfe eine öffentliche Website, finde den saubersten Datenweg und sende Ihnen ~50 echte Beispielzeilen. Der risikoarme Einstieg.",
    '<div class="price">From €150<small> &nbsp;fixed</small></div>': '<div class="price">Ab 150 €<small> &nbsp;fix</small></div>',
    '<h3>One-off Scraper</h3>': '<h3>Einmaliger Scraper</h3>',
    'A robust scraper for one public source, delivered as tested code you own. Clean CSV / JSON / API output.': "Ein robuster Scraper für eine öffentliche Quelle, geliefert als getesteter Code, der Ihnen gehört. Saubere Ausgabe als CSV / JSON / API.",
    '<span class="pill">Core</span>': '<span class="pill">Kern</span>',
    '<h3>Managed Data Feed</h3>': '<h3>Betreuter Datenfeed</h3>',
    "Scraper + scheduled delivery + monitoring. The source changes, it breaks, I fix it — usually before you notice.": "Scraper + geplante Lieferung + Monitoring. Die Quelle ändert sich, etwas bricht, ich repariere — meist bevor Sie es merken.",
    '<small> + €150–500/mo</small>': '<small> + 150–500 €/Monat</small>',
    '<h3>Discord Bot</h3>': '<h3>Discord-Bot</h3>',
    'A custom bot for your community: automation, public-data lookups, scheduled posts. Built and hosted.': "Ein maßgeschneiderter Bot für Ihre Community: Automatisierungen, Abfragen öffentlicher Daten, geplante Posts. Gebaut und gehostet.",
    '<small> + hosting</small>': '<small> + Hosting</small>',
    '<span class="more">See details →</span>': '<span class="more">Details ansehen →</span>',
    '<div class="kick">How it works</div>': '<div class="kick">So läuft es ab</div>',
    '<h2 class="section-title">From a blocked scraper to a feed you can rely on.</h2>': '<h2 class="section-title">Vom blockierten Scraper zum Feed, auf den Verlass ist.</h2>',
    '<h3>Audit</h3><p>I check the public source and find the most reliable extraction route — a hidden API where one exists.</p>': "<h3>Audit</h3><p>Ich prüfe die öffentliche Quelle und finde den verlässlichsten Extraktionsweg — eine Hidden API, wo es sie gibt.</p>",
    '<h3>Build</h3><p>A tested scraper that handles JS-heavy and Cloudflare-protected public pages, outputting clean data.</p>': "<h3>Bauen</h3><p>Ein getesteter Scraper, der JS-lastige und Cloudflare-geschützte öffentliche Seiten beherrscht und saubere Daten liefert.</p>",
    '<h3>Schedule &amp; monitor</h3><p>Delivery on your cadence, with monitoring. When the source changes and it breaks, I repair it.</p>': "<h3>Planen &amp; überwachen</h3><p>Lieferung in Ihrem Rhythmus, mit Monitoring. Ändert sich die Quelle und etwas bricht, repariere ich.</p>",
    '<h3>You operate &amp; own</h3><p>You run the tool and own the data. I build and maintain it — a tool, not an operating service.</p>': "<h3>Sie betreiben &amp; besitzen</h3><p>Sie betreiben das Tool und besitzen die Daten. Ich baue und warte — ein Werkzeug, kein Betreiberdienst.</p>",
    '<div class="kick">Scope &amp; trust</div>': '<div class="kick">Rahmen &amp; Vertrauen</div>',
    '<h2 class="section-title">Reliability, not circumvention.</h2>': '<h2 class="section-title">Verlässlichkeit statt Umgehung.</h2>',
    '<h4>Public, logged-out pages only</h4><p>Factual / business data: prices, specs, stock, listings, market data, schedules. No logins, no paywalls, no accounts.</p>': "<h4>Nur öffentliche Seiten, ohne Login</h4><p>Faktische / geschäftliche Daten: Preise, Spezifikationen, Bestände, Inserate, Marktdaten, Fahrpläne. Keine Logins, keine Paywalls, keine Konten.</p>",
    '<h4>No personal data</h4><p>Strictly non-PII. No names with contacts, profiles, or photos — B2B and factual data only.</p>': "<h4>Keine personenbezogenen Daten</h4><p>Strikt ohne PII. Keine Namen mit Kontaktdaten, keine Profile, keine Fotos — nur B2B- und Sachdaten.</p>",
    '<h4>robots.txt &amp; rate limits respected</h4><p>Pages are read like a normal visitor would, at a respectful rate. Output is structured and transformed.</p>': "<h4>robots.txt &amp; Rate-Limits respektiert</h4><p>Seiten werden gelesen wie von einem normalen Besucher, in respektvollem Tempo. Die Ausgabe ist strukturiert und transformiert.</p>",
    '<h4>You operate and own the data</h4><p>I build and maintain the tool; you run it and control the data. A clean, documented handover every time.</p>': "<h4>Sie betreiben und besitzen die Daten</h4><p>Ich baue und warte das Tool; Sie betreiben es und kontrollieren die Daten. Eine saubere, dokumentierte Übergabe — jedes Mal.</p>",
    '<div class="st">Typically in scope</div>': '<div class="st">Typisch im Rahmen</div>',
    '<div class="source-row"><span>Product prices, specs, stock</span><span class="lk">e-commerce</span></div>': '<div class="source-row"><span>Produktpreise, Specs, Bestände</span><span class="lk">E-Commerce</span></div>',
    '<div class="source-row"><span>Listings (price, size, location)</span><span class="lk">real estate</span></div>': '<div class="source-row"><span>Inserate (Preis, Fläche, Lage)</span><span class="lk">Immobilien</span></div>',
    '<div class="source-row"><span>Catalogue / marketplace data</span><span class="lk">marketplace</span></div>': '<div class="source-row"><span>Katalog- / Marktplatzdaten</span><span class="lk">Marktplatz</span></div>',
    '<div class="source-row"><span>Market data, schedules, prices</span><span class="lk">travel · finance</span></div>': '<div class="source-row"><span>Marktdaten, Fahrpläne, Preise</span><span class="lk">Reise · Finanzen</span></div>',
    'Feedsmith builds a <strong>tool</strong> for reading <strong>public, factual data</strong>. It is not used to access logins, paywalls, or personal data. You remain the operator and owner of the data and confirm your right to access the source.': "Feedsmith baut ein <strong>Werkzeug</strong> zum Lesen <strong>öffentlicher, faktischer Daten</strong>. Es dient nicht dem Zugriff auf Logins, Paywalls oder personenbezogene Daten. Sie bleiben Betreiber und Eigentümer der Daten und bestätigen Ihr Recht auf Zugriff auf die Quelle.",
    '<div class="kick">Proof</div>': '<div class="kick">Belege</div>',
    '<h2 class="section-title">Open-source, tested, and runnable.</h2>': '<h2 class="section-title">Open Source, getestet, lauffähig.</h2>',
    'Not a slide deck — real code you can read, clone, and run. The hard 20% of scraping that no-code tools fail at.': "Kein Foliensatz — echter Code zum Lesen, Klonen und Ausführen. Die schwierigen 20 % des Scrapings, an denen No-Code-Tools scheitern.",
    'The Managed Data Feed offer in code: resilient fetch → no-PII policy → schedule → self-healing monitor → CSV/JSON/webhook, in FastAPI.': "Das Angebot Betreuter Datenfeed als Code: robustes Fetching → No-PII-Policy → Zeitplan → selbstheilendes Monitoring → CSV/JSON/Webhook, in FastAPI.",
    "Read a site's internal JSON API directly instead of parsing fragile HTML — faster and far more stable.": "Die interne JSON-API einer Website direkt lesen statt fragiles HTML zu parsen — schneller und deutlich stabiler.",
    'Why a public page returns empty: a TLS fingerprint check before render. Read it like a normal browser, compliantly.': "Warum eine öffentliche Seite leer zurückkommt: ein TLS-Fingerprint-Check vor dem Rendern. Lesen wie ein normaler Browser, regelkonform.",
    '<span class="more">View on GitHub ↗</span>': '<span class="more">Auf GitHub ansehen ↗</span>',
    '<h2 class="section-title">The why behind the work.</h2>': '<h2 class="section-title">Das Warum hinter der Arbeit.</h2>',
    '<h3>Why your no-code scraper keeps breaking</h3>': '<h3>Warum Ihr No-Code-Scraper immer wieder bricht</h3>',
    'Layout changes, JS-rendered data, fingerprint checks — and what actually fixes them.': "Layout-Änderungen, JS-gerenderte Daten, Fingerprint-Checks — und was wirklich hilft. (Guide auf Englisch.)",
    '<h3>What is a hidden API</h3>': '<h3>Was ist eine Hidden API</h3>',
    'The internal JSON endpoints behind a page — and why calling them beats HTML parsing.': "Die internen JSON-Endpunkte hinter einer Seite — und warum sie das HTML-Parsing schlagen. (Guide auf Englisch.)",
    '<h3>Cloudflare-protected public sites</h3>': '<h3>Cloudflare-geschützte öffentliche Seiten</h3>',
    'Empty pages are usually a TLS fingerprint check, not a CAPTCHA — the compliant way to read them.': "Leere Seiten sind meist ein TLS-Fingerprint-Check, kein CAPTCHA — der regelkonforme Weg, sie zu lesen. (Guide auf Englisch.)",
    '<span class="more">Read the guide →</span>': '<span class="more">Guide lesen →</span>',
    '<h2>Get a free feasibility check</h2>': '<h2>Kostenlose Machbarkeitsprüfung anfragen</h2>',
    "Tell me the public site and the data you need. I'll tell you if it's doable, how, and in which language.": "Nennen Sie mir die öffentliche Website und die Daten, die Sie brauchen. Ich sage Ihnen, ob es machbar ist, wie — und in welcher Sprache.",
    'aria-label="The public site or URL" placeholder="The public site / URL"': 'aria-label="Die öffentliche Website oder URL" placeholder="Die öffentliche Website / URL"',
    'aria-label="Your email" placeholder="Your email"': 'aria-label="Ihre E-Mail" placeholder="Ihre E-Mail"',
    'aria-label="What data do you need, and in which language" placeholder="What data do you need? Which language (DE / FR / IT / EN)?"': 'aria-label="Welche Daten brauchen Sie, und in welcher Sprache" placeholder="Welche Daten brauchen Sie? Welche Sprache (DE / FR / IT / EN)?"',
    '<button class="btn btn-primary" type="submit">Send</button>': '<button class="btn btn-primary" type="submit">Anfrage senden</button>',
    'Or email <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Based in Switzerland · DE / FR / IT / EN.': 'Oder per E-Mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Sitz in der Schweiz · DE / FR / IT / EN.',
    '<div><strong>Feedsmith</strong> — reliable data feeds from public sources.': '<div><strong>Feedsmith</strong> — verlässliche Datenfeeds aus öffentlichen Quellen.',
    'Public sources only · factual / non-PII data · robots.txt &amp; rate limits respected · you operate and own the data.': "Nur öffentliche Quellen · faktische / nicht personenbezogene Daten · robots.txt &amp; Rate-Limits respektiert · Sie betreiben und besitzen die Daten.",
    '<a href="/">Home</a>': '<a href="/de/">Start</a>',
}

# ------------------------------------------------------------------- IT ---

IT = {
    '<a href="#offers">Offers</a>': '<a href="#offers">Servizi</a>',
    '<a href="#guides">Guides</a>': '<a href="#guides">Guide</a>',
    '<a href="#portfolio">Portfolio</a>': '<a href="#portfolio">Portfolio</a>',
    '>Free feasibility check</a>\n  </nav>': '>Studio di fattibilità gratuito</a>\n  </nav>',
    '<span class="eyebrow">Web scraping &amp; maintained data feeds</span>': '<span class="eyebrow">Web scraping &amp; feed di dati mantenuti</span>',
    '<h1>Reliable data feeds<br class="lb"> <span class="hl">from public sources</span>.</h1>': '<h1>Feed di dati affidabili<br class="lb"> <span class="hl">da fonti pubbliche</span>.</h1>',
    'When Apify, Octoparse or a ChatGPT-written script gets blocked, returns empty pages, or breaks every time the site changes — I extract clean public data, and keep it running.': "Quando Apify, Octoparse o uno script scritto da ChatGPT viene bloccato, restituisce pagine vuote o si rompe a ogni modifica del sito — estraggo dati pubblici puliti e li tengo in funzione.",
    'aria-label="The public site or URL you need data from" placeholder="The public site / URL"': 'aria-label="Il sito o l\'URL pubblico da cui ti servono i dati" placeholder="Il sito / l\'URL pubblico"',
    '<button class="btn btn-primary" type="submit">Get a free feasibility check</button>': '<button class="btn btn-primary" type="submit">Studio di fattibilità gratuito</button>',
    'Public sources only · no logins, no personal data · you operate and own the data.': "Solo fonti pubbliche · niente login, niente dati personali · tu gestisci e possiedi i dati.",
    'Raw public web pages, forged into a clean structured data feed': "Pagine web pubbliche grezze, forgiate in un feed di dati pulito e strutturato",
    'Messy website windows flow through a forge spark and come out as a tidy live data table with CSV and JSON output.': "Finestre di siti disordinate attraversano una scintilla di forgia ed escono come una tabella di dati pulita, con output CSV e JSON.",
    '<div class="kick">The deliverable</div>': '<div class="kick">Il risultato</div>',
    '<h2 class="section-title">A clean dataset, not a promise.</h2>': '<h2 class="section-title">Un dataset pulito, non una promessa.</h2>',
    "You get structured public data — CSV, JSON, or an API — with the fields you need and nothing you don't. Factual, non-personal, and verifiable against the source.": "Ricevi dati pubblici strutturati — CSV, JSON o API — con i campi che ti servono e nient'altro. Fattuali, non personali e verificabili alla fonte.",
    '<span class="lab">Currency</span>': '<span class="lab">Valuta</span>',
    '<span class="lab" style="margin-left:8px">Availability</span>': '<span class="lab" style="margin-left:8px">Disponibilità</span>',
    '<span class="lab" style="margin-left:8px">Rating</span>': '<span class="lab" style="margin-left:8px">Valutazione</span>',
    '<button class="chip on" type="button">In stock</button>': '<button class="chip on" type="button">Disponibile</button>',
    '<span class="count"><b>6</b> of <b>2,480</b> products</span>': '<span class="count"><b>6</b> di <b>2.480</b> prodotti</span>',
    '<th scope="col">Product</th>': '<th scope="col">Prodotto</th>',
    '<th scope="col">Category</th>': '<th scope="col">Categoria</th>',
    '<th scope="col" class="r">Price</th>': '<th scope="col" class="r">Prezzo</th>',
    '<th scope="col" class="r">Availability</th>': '<th scope="col" class="r">Disponibilità</th>',
    '<th scope="col" class="r">Rating</th>': '<th scope="col" class="r">Valutazione</th>',
    '<th scope="col">Source</th>': '<th scope="col">Fonte</th>',
    '<td>Peripherals</td>': '<td>Periferiche</td>',
    '<td>Accessories</td>': '<td>Accessori</td>',
    '<td>Displays</td>': '<td>Display</td>',
    '<td>Audio</td>': '<td>Audio</td>',
    '<td class="r">In stock</td>': '<td class="r">Disponibile</td>',
    '<td class="r">3 left</td>': '<td class="r">3 rimasti</td>',
    '<td class="r">Out of stock</td>': '<td class="r">Esaurito</td>',
    'public catalog ↗': 'catalogo pubblico ↗',
    'Sample data, public sources only. Factual / non-personal fields. robots.txt and sensible rate limits respected. You operate and own the feed.': "Dati di esempio, solo fonti pubbliche. Campi fattuali / non personali. robots.txt e limiti di frequenza rispettati. Tu gestisci e possiedi il feed.",
    '<div class="kick">Offers</div>': '<div class="kick">Servizi</div>',
    '<h2 class="section-title">Start small. Scale to a maintained feed.</h2>': '<h2 class="section-title">Parti in piccolo. Passa a un feed mantenuto.</h2>',
    'Begin with a low-risk audit, get a one-off dataset, or hand the upkeep to me with a managed feed.': "Inizia con un audit a basso rischio, ottieni un'estrazione una tantum, oppure affidami la manutenzione con un feed gestito. Pagine di dettaglio in inglese.",
    '<h3>Hidden-API Audit</h3>': '<h3>Audit di API nascosta</h3>',
    'I check one public site, find the cleanest data route, and send you ~50 real sample rows. A low-risk way to start.': "Esamino un sito pubblico, trovo la via d'accesso più pulita e ti invio ~50 righe di esempio reali. Il punto di partenza a basso rischio.",
    '<div class="price">From €150<small> &nbsp;fixed</small></div>': '<div class="price">Da 150 €<small> &nbsp;fisso</small></div>',
    '<h3>One-off Scraper</h3>': '<h3>Scraper una tantum</h3>',
    'A robust scraper for one public source, delivered as tested code you own. Clean CSV / JSON / API output.': "Uno scraper robusto per una fonte pubblica, consegnato come codice testato di tua proprietà. Output pulito CSV / JSON / API.",
    '<span class="pill">Core</span>': '<span class="pill">Core</span>',
    '<h3>Managed Data Feed</h3>': '<h3>Feed di dati gestito</h3>',
    "Scraper + scheduled delivery + monitoring. The source changes, it breaks, I fix it — usually before you notice.": "Scraper + consegna pianificata + monitoraggio. La fonte cambia, qualcosa si rompe, io riparo — spesso prima che tu te ne accorga.",
    '<small> + €150–500/mo</small>': '<small> + 150–500 €/mese</small>',
    '<h3>Discord Bot</h3>': '<h3>Bot Discord</h3>',
    'A custom bot for your community: automation, public-data lookups, scheduled posts. Built and hosted.': "Un bot su misura per la tua community: automazioni, ricerche su dati pubblici, post programmati. Costruito e ospitato.",
    '<small> + hosting</small>': '<small> + hosting</small>',
    '<span class="more">See details →</span>': '<span class="more">Vedi i dettagli →</span>',
    '<div class="kick">How it works</div>': '<div class="kick">Come funziona</div>',
    '<h2 class="section-title">From a blocked scraper to a feed you can rely on.</h2>': '<h2 class="section-title">Da uno scraper bloccato a un feed su cui contare.</h2>',
    '<h3>Audit</h3><p>I check the public source and find the most reliable extraction route — a hidden API where one exists.</p>': "<h3>Audit</h3><p>Esamino la fonte pubblica e individuo la via di estrazione più affidabile — un'API nascosta quando esiste.</p>",
    '<h3>Build</h3><p>A tested scraper that handles JS-heavy and Cloudflare-protected public pages, outputting clean data.</p>': "<h3>Costruzione</h3><p>Uno scraper testato che gestisce pagine pubbliche piene di JavaScript o protette da Cloudflare, con output pulito.</p>",
    '<h3>Schedule &amp; monitor</h3><p>Delivery on your cadence, with monitoring. When the source changes and it breaks, I repair it.</p>': "<h3>Pianifica &amp; monitora</h3><p>Consegna alla cadenza che vuoi, con monitoraggio. Quando la fonte cambia e qualcosa si rompe, riparo.</p>",
    '<h3>You operate &amp; own</h3><p>You run the tool and own the data. I build and maintain it — a tool, not an operating service.</p>': "<h3>Tu gestisci &amp; possiedi</h3><p>Tu fai girare lo strumento e possiedi i dati. Io lo costruisco e lo mantengo — uno strumento, non un servizio di gestione.</p>",
    '<div class="kick">Scope &amp; trust</div>': '<div class="kick">Perimetro &amp; fiducia</div>',
    '<h2 class="section-title">Reliability, not circumvention.</h2>': '<h2 class="section-title">Affidabilità, non aggiramento.</h2>',
    '<h4>Public, logged-out pages only</h4><p>Factual / business data: prices, specs, stock, listings, market data, schedules. No logins, no paywalls, no accounts.</p>': "<h4>Solo pagine pubbliche, senza login</h4><p>Dati fattuali / business: prezzi, specifiche, disponibilità, annunci, dati di mercato, orari. Niente login, niente paywall, niente account.</p>",
    '<h4>No personal data</h4><p>Strictly non-PII. No names with contacts, profiles, or photos — B2B and factual data only.</p>': "<h4>Nessun dato personale</h4><p>Rigorosamente senza PII. Niente nomi con contatti, profili o foto — solo dati B2B e fattuali.</p>",
    '<h4>robots.txt &amp; rate limits respected</h4><p>Pages are read like a normal visitor would, at a respectful rate. Output is structured and transformed.</p>': "<h4>robots.txt &amp; limiti di frequenza rispettati</h4><p>Le pagine vengono lette come farebbe un normale visitatore, a un ritmo rispettoso. L'output è strutturato e trasformato.</p>",
    '<h4>You operate and own the data</h4><p>I build and maintain the tool; you run it and control the data. A clean, documented handover every time.</p>': "<h4>Tu gestisci e possiedi i dati</h4><p>Io costruisco e mantengo lo strumento; tu lo gestisci e controlli i dati. Una consegna pulita e documentata, ogni volta.</p>",
    '<div class="st">Typically in scope</div>': '<div class="st">Tipicamente nel perimetro</div>',
    '<div class="source-row"><span>Product prices, specs, stock</span><span class="lk">e-commerce</span></div>': '<div class="source-row"><span>Prezzi prodotto, specifiche, stock</span><span class="lk">e-commerce</span></div>',
    '<div class="source-row"><span>Listings (price, size, location)</span><span class="lk">real estate</span></div>': '<div class="source-row"><span>Annunci (prezzo, superficie, posizione)</span><span class="lk">immobiliare</span></div>',
    '<div class="source-row"><span>Catalogue / marketplace data</span><span class="lk">marketplace</span></div>': '<div class="source-row"><span>Dati catalogo / marketplace</span><span class="lk">marketplace</span></div>',
    '<div class="source-row"><span>Market data, schedules, prices</span><span class="lk">travel · finance</span></div>': '<div class="source-row"><span>Dati di mercato, orari, prezzi</span><span class="lk">viaggi · finanza</span></div>',
    'Feedsmith builds a <strong>tool</strong> for reading <strong>public, factual data</strong>. It is not used to access logins, paywalls, or personal data. You remain the operator and owner of the data and confirm your right to access the source.': "Feedsmith costruisce uno <strong>strumento</strong> per leggere <strong>dati pubblici e fattuali</strong>. Non serve ad accedere a login, paywall o dati personali. Tu resti il gestore e il proprietario dei dati e confermi il tuo diritto di accesso alla fonte.",
    '<div class="kick">Proof</div>': '<div class="kick">Prove</div>',
    '<h2 class="section-title">Open-source, tested, and runnable.</h2>': '<h2 class="section-title">Open source, testato, eseguibile.</h2>',
    'Not a slide deck — real code you can read, clone, and run. The hard 20% of scraping that no-code tools fail at.': "Niente slide — codice vero da leggere, clonare ed eseguire. Il 20 % difficile dello scraping dove i tool no-code falliscono.",
    'The Managed Data Feed offer in code: resilient fetch → no-PII policy → schedule → self-healing monitor → CSV/JSON/webhook, in FastAPI.': "L'offerta Feed di dati gestito, in codice: fetch resiliente → policy no-PII → pianificazione → monitoraggio auto-riparante → CSV/JSON/webhook, in FastAPI.",
    "Read a site's internal JSON API directly instead of parsing fragile HTML — faster and far more stable.": "Leggere direttamente l'API JSON interna di un sito invece di fare parsing di HTML fragile — più veloce e molto più stabile.",
    'Why a public page returns empty: a TLS fingerprint check before render. Read it like a normal browser, compliantly.': "Perché una pagina pubblica torna vuota: un controllo dell'impronta TLS prima del rendering. Leggerla come un browser normale, in modo conforme.",
    '<span class="more">View on GitHub ↗</span>': '<span class="more">Vedi su GitHub ↗</span>',
    '<div class="kick">Guides</div>': '<div class="kick">Guide</div>',
    '<h2 class="section-title">The why behind the work.</h2>': '<h2 class="section-title">Il perché dietro il lavoro.</h2>',
    '<h3>Why your no-code scraper keeps breaking</h3>': '<h3>Perché il tuo scraper no-code continua a rompersi</h3>',
    'Layout changes, JS-rendered data, fingerprint checks — and what actually fixes them.': "Cambi di layout, dati renderizzati in JS, controlli di fingerprint — e cosa li risolve davvero. (Guida in inglese.)",
    '<h3>What is a hidden API</h3>': '<h3>Che cos\'è una API nascosta</h3>',
    'The internal JSON endpoints behind a page — and why calling them beats HTML parsing.': "Gli endpoint JSON interni dietro una pagina — e perché chiamarli batte il parsing dell'HTML. (Guida in inglese.)",
    '<h3>Cloudflare-protected public sites</h3>': '<h3>Siti pubblici protetti da Cloudflare</h3>',
    'Empty pages are usually a TLS fingerprint check, not a CAPTCHA — the compliant way to read them.': "Le pagine vuote di solito sono un controllo dell'impronta TLS, non un CAPTCHA — il modo conforme di leggerle. (Guida in inglese.)",
    '<span class="more">Read the guide →</span>': '<span class="more">Leggi la guida →</span>',
    '<h2>Get a free feasibility check</h2>': '<h2>Richiedi uno studio di fattibilità gratuito</h2>',
    "Tell me the public site and the data you need. I'll tell you if it's doable, how, and in which language.": "Indicami il sito pubblico e i dati che ti servono. Ti dico se è fattibile, come, e in quale lingua.",
    'aria-label="The public site or URL" placeholder="The public site / URL"': 'aria-label="Il sito o l\'URL pubblico" placeholder="Il sito / l\'URL pubblico"',
    'aria-label="Your email" placeholder="Your email"': 'aria-label="La tua e-mail" placeholder="La tua e-mail"',
    'aria-label="What data do you need, and in which language" placeholder="What data do you need? Which language (DE / FR / IT / EN)?"': 'aria-label="Quali dati ti servono, e in quale lingua" placeholder="Quali dati ti servono? Quale lingua (IT / FR / DE / EN)?"',
    '<button class="btn btn-primary" type="submit">Send</button>': '<button class="btn btn-primary" type="submit">Invia</button>',
    'Or email <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Based in Switzerland · DE / FR / IT / EN.': 'Oppure via e-mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Con base in Svizzera · IT / FR / DE / EN.',
    '<div><strong>Feedsmith</strong> — reliable data feeds from public sources.': '<div><strong>Feedsmith</strong> — feed di dati affidabili da fonti pubbliche.',
    'Public sources only · factual / non-PII data · robots.txt &amp; rate limits respected · you operate and own the data.': "Solo fonti pubbliche · dati fattuali / non-PII · robots.txt &amp; limiti di frequenza rispettati · tu gestisci e possiedi i dati.",
    '<a href="/">Home</a>': '<a href="/it/">Home</a>',
}

LOCALES = {
    "fr": (FR, head_block(
        "fr",
        "Feedsmith — Flux de données fiables issus de sources publiques",
        "Quand les outils no-code et les scrapers IA sont bloqués ou renvoient des pages vides, Feedsmith extrait des données publiques propres et les maintient dans la durée. Données factuelles, non personnelles — vous exploitez et possédez les données.",
        "Feedsmith — Flux de données fiables issus de sources publiques",
        "Des flux de données propres et maintenus, issus de sources publiques — quand les scrapers no-code et IA échouent.",
    )),
    "de": (DE, head_block(
        "de",
        "Feedsmith — Verlässliche Datenfeeds aus öffentlichen Quellen",
        "Wenn No-Code-Tools und KI-Scraper blockiert werden oder leere Seiten liefern, extrahiert Feedsmith saubere öffentliche Daten und hält den Feed am Laufen. Faktische, nicht personenbezogene Daten — Sie betreiben und besitzen die Daten.",
        "Feedsmith — Verlässliche Datenfeeds aus öffentlichen Quellen",
        "Saubere, betreute Datenfeeds aus öffentlichen Quellen — wenn No-Code- und KI-Scraper scheitern.",
    )),
    "it": (IT, head_block(
        "it",
        "Feedsmith — Feed di dati affidabili da fonti pubbliche",
        "Quando i tool no-code e gli scraper IA vengono bloccati o restituiscono pagine vuote, Feedsmith estrae dati pubblici puliti e li tiene in funzione. Dati fattuali, non personali — tu gestisci e possiedi i dati.",
        "Feedsmith — Feed di dati affidabili da fonti pubbliche",
        "Feed di dati puliti e mantenuti, da fonti pubbliche — quando gli scraper no-code e IA falliscono.",
    )),
}


def build(lang: str, texts: dict, head: dict) -> None:
    src = SRC.read_text(encoding="utf-8")
    missing = [old for old in list(head) + STRUCTURAL_KEYS if old not in src]
    out = src
    for old, new in head.items():
        out = out.replace(old, new)
    for old, new in STRUCTURAL:
        out = out.replace(old, new)
    # text keys are validated against the structurally-rewritten document
    missing += [old for old in texts if old not in out]
    if missing:
        raise SystemExit(
            f"[{lang}] {len(missing)} key(s) no longer match index.html:\n  - "
            + "\n  - ".join(m[:90] for m in missing)
        )
    for old, new in texts.items():
        out = out.replace(old, new)
    dest = ROOT / lang / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print(f"built {dest.relative_to(ROOT)}")


STRUCTURAL_KEYS = [old for old, _ in STRUCTURAL]

if __name__ == "__main__":
    for lang, (texts, head) in LOCALES.items():
        build(lang, texts, head)
    print("Done. EN home is the source of truth; re-run after editing index.html.")
