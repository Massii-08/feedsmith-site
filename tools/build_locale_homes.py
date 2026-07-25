from __future__ import annotations

"""
build_locale_homes.py — Feedsmith localized home generator.

The ENGLISH home (index.html) is the single source of truth for STRUCTURE.
This script clones it into de/, fr/ and it/ by applying exact text
substitutions, so every language version has the same sections, the same
working buttons and the same instrument panels, translated.

Rules encoded here:
  - nav / footer anchors become LOCAL (#offers, #contact, ...) so a visitor
    never gets bounced to the English home by switching language;
  - brand + footer "Home" link point at the local home (/de/, /fr/, /it/);
  - head metadata (title, description, OG, canonical, og:url, lang) is
    fully localized; the hreflang cluster stays identical on every page;
  - offer cards / guide cards link to the (English) detail pages, the only
    versions that exist;
  - REAL MACHINE OUTPUT IS NEVER TRANSLATED. The sample CSV rows, the CSV
    column names and the YAML config come from an actual run of
    managed-data-feed-starter. Translating them would turn evidence into
    fiction. Only our own captions around them are localized.

Every replacement is asserted: if a future edit to index.html breaks a key,
the build fails loudly instead of silently shipping a diverged page.

Usage:  python3 tools/build_locale_homes.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
LOCALES = ("fr", "de", "it")

# ---------------------------------------------------------------- shared --

# /#anchor -> #anchor  (stay on the local page)
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
    "brand": '<a class="brand" href="/">Feedsmith</a>',
}

HEAD = {
    "fr": dict(
        title="Feedsmith — Flux de données fiables issus de sources publiques | Spécialiste web scraping",
        desc="Quand les outils no-code et les scrapers IA se font bloquer ou renvoient des pages vides, Feedsmith extrait des données publiques propres et les maintient. Des flux fiables et maintenus : factuels, non personnels, vous exploitez et possédez les données.",
        og_title="Feedsmith — Flux de données fiables issus de sources publiques",
        og_desc="Des flux de données propres et maintenus, issus de sources publiques, quand les outils no-code et IA échouent.",
    ),
    "de": dict(
        title="Feedsmith — Verlässliche Datenfeeds aus öffentlichen Quellen | Web-Scraping-Spezialist",
        desc="Wenn No-Code-Tools und KI-Scraper blockiert werden oder leere Seiten liefern, extrahiert Feedsmith saubere öffentliche Daten und hält den Feed am Laufen. Verlässliche, betreute Datenfeeds: faktisch, nicht personenbezogen, Sie betreiben und besitzen die Daten.",
        og_title="Feedsmith — Verlässliche Datenfeeds aus öffentlichen Quellen",
        og_desc="Saubere, betreute Datenfeeds aus öffentlichen Quellen, wenn No-Code- und KI-Scraper scheitern.",
    ),
    "it": dict(
        title="Feedsmith — Feed di dati affidabili da fonti pubbliche | Specialista web scraping",
        desc="Quando i tool no-code e gli scraper IA vengono bloccati o restituiscono pagine vuote, Feedsmith estrae dati pubblici puliti e li tiene in funzione. Feed affidabili e mantenuti: fattuali, non personali, tu gestisci e possiedi i dati.",
        og_title="Feedsmith — Feed di dati affidabili da fonti pubbliche",
        og_desc="Feed di dati puliti e mantenuti, da fonti pubbliche, quando i tool no-code e IA falliscono.",
    ),
}


def head_block(lang: str) -> dict:
    base = f"https://feedsmith.net/{lang}/"
    h = HEAD[lang]
    return {
        HEAD_EN["lang_attr"]: f'<html lang="{lang}">',
        HEAD_EN["title"]: f'<title>{h["title"]}</title>',
        HEAD_EN["desc"]: f'<meta name="description" content="{h["desc"]}" />',
        HEAD_EN["canonical"]: f'<link rel="canonical" href="{base}" />',
        HEAD_EN["og_title"]: f'<meta property="og:title" content="{h["og_title"]}" />',
        HEAD_EN["og_desc"]: f'<meta property="og:description" content="{h["og_desc"]}" />',
        HEAD_EN["og_url"]: f'<meta property="og:url" content="{base}" />',
        HEAD_EN["brand"]: f'<a class="brand" href="/{lang}/">Feedsmith</a>',
    }


# ------------------------------------------------------------ dictionary --
# (english, fr, de, it). The english entry must appear in index.html.

T = [
    # ---- nav
    ('<a href="#offers">Offers</a>',
     '<a href="#offers">Offres</a>',
     '<a href="#offers">Leistungen</a>',
     '<a href="#offers">Servizi</a>'),
    ('<a href="#guides">Guides</a>',
     '<a href="#guides">Guides</a>',
     '<a href="#guides">Guides</a>',
     '<a href="#guides">Guide</a>'),
    ('>Free feasibility check</a>\n  </nav>',
     '>Étude de faisabilité gratuite</a>\n  </nav>',
     '>Kostenlose Machbarkeitsprüfung</a>\n  </nav>',
     '>Studio di fattibilità gratuito</a>\n  </nav>'),

    # ---- hero
    ('<h1>Reliable data feeds from public sources.</h1>',
     '<h1>Des flux de données fiables issus de sources publiques.</h1>',
     '<h1>Verlässliche Datenfeeds aus öffentlichen Quellen.</h1>',
     '<h1>Feed di dati affidabili da fonti pubbliche.</h1>'),
    ('When no-code tools and AI-written scripts get blocked or return empty pages, I extract the data and keep it running.',
     "Quand les outils no-code et les scripts écrits par une IA se font bloquer ou renvoient des pages vides, j'extrais les données et je les maintiens.",
     'Wenn No-Code-Tools und KI-geschriebene Skripte blockiert werden oder leere Seiten liefern, extrahiere ich die Daten und halte den Feed am Laufen.',
     "Quando i tool no-code e gli script scritti da un'IA vengono bloccati o restituiscono pagine vuote, estraggo i dati e li tengo in funzione."),
    ('aria-label="The public site or URL you need data from" placeholder="The public site / URL"',
     'aria-label="Le site ou l\'URL publique dont vous avez besoin" placeholder="Le site / l\'URL publique"',
     'aria-label="Die öffentliche Website oder URL, aus der Sie Daten brauchen" placeholder="Die öffentliche Website / URL"',
     'aria-label="Il sito o l\'URL pubblico da cui ti servono dati" placeholder="Il sito / l\'URL pubblico"'),
    ('<button class="btn btn-primary" type="submit">Get a free feasibility check</button>',
     '<button class="btn btn-primary" type="submit">Étude de faisabilité gratuite</button>',
     '<button class="btn btn-primary" type="submit">Kostenlose Machbarkeitsprüfung</button>',
     '<button class="btn btn-primary" type="submit">Studio di fattibilità gratuito</button>'),
    ('<p class="micro">Public sources only. No logins, no personal data. You operate and own the feed.</p>',
     '<p class="micro">Sources publiques uniquement. Pas de comptes, pas de données personnelles. Vous exploitez et possédez le flux.</p>',
     '<p class="micro">Nur öffentliche Quellen. Keine Logins, keine personenbezogenen Daten. Sie betreiben und besitzen den Feed.</p>',
     '<p class="micro">Solo fonti pubbliche. Niente login, niente dati personali. Tu gestisci e possiedi il feed.</p>'),

    # ---- hero register
    ('<p class="st">What a feed contains</p>',
     '<p class="st">Ce que contient un flux</p>',
     '<p class="st">Was ein Feed enthält</p>',
     '<p class="st">Cosa contiene un feed</p>'),
    ('<dt>Output</dt><dd>CSV · JSON · webhook</dd>',
     '<dt>Sortie</dt><dd>CSV · JSON · webhook</dd>',
     '<dt>Ausgabe</dt><dd>CSV · JSON · Webhook</dd>',
     '<dt>Output</dt><dd>CSV · JSON · webhook</dd>'),
    ('<dt>Cadence</dt><dd>hourly to weekly</dd>',
     "<dt>Cadence</dt><dd>de l'heure à la semaine</dd>",
     '<dt>Rhythmus</dt><dd>stündlich bis wöchentlich</dd>',
     '<dt>Cadenza</dt><dd>da oraria a settimanale</dd>'),
    ('<dt>Monitoring</dt><dd>on every run</dd>',
     '<dt>Monitoring</dt><dd>à chaque exécution</dd>',
     '<dt>Monitoring</dt><dd>bei jedem Lauf</dd>',
     '<dt>Monitoraggio</dt><dd>a ogni esecuzione</dd>'),
    ('<dt>Repair when the source changes</dt><dd>included</dd>',
     '<dt>Réparation quand la source change</dt><dd>inclus</dd>',
     '<dt>Reparatur, wenn sich die Quelle ändert</dt><dd>inklusive</dd>',
     '<dt>Riparazione quando la fonte cambia</dt><dd>inclusa</dd>'),
    ('<dt>Source data</dt><dd>public, factual, non-personal</dd>',
     '<dt>Données source</dt><dd>publiques, factuelles, non personnelles</dd>',
     '<dt>Quelldaten</dt><dd>öffentlich, faktisch, nicht personenbezogen</dd>',
     '<dt>Dati di origine</dt><dd>pubblici, fattuali, non personali</dd>'),
    ('<dt>Ownership</dt><dd>yours, with the code</dd>',
     '<dt>Propriété</dt><dd>à vous, avec le code</dd>',
     '<dt>Eigentum</dt><dd>Ihres, samt Code</dd>',
     '<dt>Proprietà</dt><dd>tuoi, con il codice</dd>'),
    ('<p class="micro">Pages are read the way a normal visitor reads them, at a respectful rate, with robots.txt honoured.</p>',
     '<p class="micro">Les pages sont lues comme le ferait un visiteur normal, à un rythme respectueux, et robots.txt est respecté.</p>',
     '<p class="micro">Seiten werden gelesen wie von einem normalen Besucher, in respektvollem Tempo, robots.txt wird respektiert.</p>',
     '<p class="micro">Le pagine vengono lette come farebbe un normale visitatore, a un ritmo rispettoso, e robots.txt è rispettato.</p>'),

    # ---- sample output (captions only: the CSV itself stays as it ran)
    ('<h2 class="section-title">A dataset you can check, not a promise.</h2>',
     '<h2 class="section-title">Un jeu de données vérifiable, pas une promesse.</h2>',
     '<h2 class="section-title">Ein Datensatz, den Sie prüfen können, kein Versprechen.</h2>',
     '<h2 class="section-title">Un dataset che puoi verificare, non una promessa.</h2>'),
    ('Below is real output from the open-source starter behind the Managed Data Feed offer, run against a public sandbox catalogue. Same shape as what lands in your inbox or your database.',
     "Ci-dessous, une sortie réelle du starter open source qui équipe l'offre Flux de données géré, exécuté sur un catalogue public de test. C'est exactement la forme de ce qui arrive dans votre boîte mail ou votre base.",
     'Unten sehen Sie echte Ausgabe des Open-Source-Starters hinter dem Angebot Betreuter Datenfeed, ausgeführt auf einem öffentlichen Test-Katalog. Genau die Form, die in Ihrem Postfach oder Ihrer Datenbank landet.',
     "Qui sotto c'è output reale dello starter open source dietro l'offerta Feed di dati gestito, eseguito su un catalogo pubblico di prova. La stessa forma di ciò che arriva nella tua casella o nel tuo database."),
    ('<div class="panel-foot">Public sandbox source. Factual, non-personal fields. One row per product, one column per field, with the fetch timestamp kept.</div>',
     "<div class=\"panel-foot\">Source publique de test. Champs factuels, non personnels. Une ligne par produit, une colonne par champ, avec l'horodatage de collecte conservé.</div>",
     '<div class="panel-foot">Öffentliche Test-Quelle. Faktische, nicht personenbezogene Felder. Eine Zeile pro Produkt, eine Spalte pro Feld, mit erhaltenem Abruf-Zeitstempel.</div>',
     '<div class="panel-foot">Fonte pubblica di prova. Campi fattuali, non personali. Una riga per prodotto, una colonna per campo, con il timestamp di raccolta conservato.</div>'),
    ('<p class="micro">Your feed carries your fields and nothing else: the columns you asked for, in the format you asked for.</p>',
     "<p class=\"micro\">Votre flux porte vos champs et rien d'autre : les colonnes demandées, dans le format demandé.</p>",
     '<p class="micro">Ihr Feed trägt Ihre Felder und sonst nichts: die Spalten, die Sie wollten, im Format, das Sie wollten.</p>',
     "<p class=\"micro\">Il tuo feed porta i tuoi campi e nient'altro: le colonne che hai chiesto, nel formato che hai chiesto.</p>"),

    # ---- offers
    ('<p class="kick">Offers</p>',
     '<p class="kick">Offres</p>',
     '<p class="kick">Leistungen</p>',
     '<p class="kick">Servizi</p>'),
    ('<h2 class="section-title">Start with an audit. Scale to a maintained feed.</h2>',
     '<h2 class="section-title">Commencez par un audit. Passez à un flux maintenu.</h2>',
     '<h2 class="section-title">Mit einem Audit starten. Zum betreuten Feed ausbauen.</h2>',
     '<h2 class="section-title">Inizia con un audit. Passa a un feed mantenuto.</h2>'),
    ('<p class="lead">Four ways in, from a low-risk check to a feed I keep alive.</p>',
     "<p class=\"lead\">Quatre portes d'entrée, d'une vérification sans risque à un flux que je maintiens en vie.</p>",
     '<p class="lead">Vier Einstiege, von der risikoarmen Prüfung bis zum Feed, den ich am Leben halte.</p>',
     '<p class="lead">Quattro modi di iniziare, dal controllo a basso rischio al feed che tengo in vita.</p>'),

    ('<h3>Hidden-API Audit</h3>',
     "<h3>Audit d'API cachée</h3>",
     '<h3>Hidden-API-Audit</h3>',
     '<h3>Audit di API nascosta</h3>'),
    ('<p>I check one public site, find the cleanest data route, and send you about 50 real sample rows. The low-risk way to start.</p>',
     "<p>J'examine un site public, j'identifie la voie d'accès la plus propre et je vous envoie une cinquantaine de lignes d'échantillon réelles. Le point de départ sans risque.</p>",
     '<p>Ich prüfe eine öffentliche Website, finde den saubersten Datenweg und sende Ihnen rund 50 echte Beispielzeilen. Der risikoarme Einstieg.</p>',
     "<p>Esamino un sito pubblico, trovo la via d'accesso più pulita e ti invio una cinquantina di righe di esempio reali. Il punto di partenza a basso rischio.</p>"),
    ('<div class="price">from €150<span>fixed fee</span></div>',
     '<div class="price">dès 150 €<span>forfait</span></div>',
     '<div class="price">ab 150 €<span>Festpreis</span></div>',
     '<div class="price">da 150 €<span>forfait</span></div>'),

    ('<h3>One-off Scraper</h3>',
     '<h3>Scraper ponctuel</h3>',
     '<h3>Einmaliger Scraper</h3>',
     '<h3>Scraper una tantum</h3>'),
    ('<p>A robust scraper for one public source, delivered as tested code you own. Clean CSV, JSON or API output.</p>',
     '<p>Un scraper robuste pour une source publique, livré en code testé qui vous appartient. Sortie propre CSV, JSON ou API.</p>',
     '<p>Ein robuster Scraper für eine öffentliche Quelle, geliefert als getesteter Code, der Ihnen gehört. Saubere Ausgabe als CSV, JSON oder API.</p>',
     '<p>Uno scraper robusto per una fonte pubblica, consegnato come codice testato di tua proprietà. Output pulito CSV, JSON o API.</p>'),
    ('<div class="price">€600 to 1,500<span>one time</span></div>',
     '<div class="price">600 à 1 500 €<span>une fois</span></div>',
     '<div class="price">600 bis 1.500 €<span>einmalig</span></div>',
     '<div class="price">600 a 1.500 €<span>una tantum</span></div>'),

    ('<h3>Managed Data Feed</h3>',
     '<h3>Flux de données géré</h3>',
     '<h3>Betreuter Datenfeed</h3>',
     '<h3>Feed di dati gestito</h3>'),
    ('<p>Scraper, scheduled delivery and monitoring. The source changes, it breaks, I fix it, usually before you notice.</p>',
     '<p>Scraper, livraison planifiée et monitoring. La source change, ça casse, je répare, souvent avant que vous le remarquiez.</p>',
     '<p>Scraper, geplante Lieferung und Monitoring. Die Quelle ändert sich, etwas bricht, ich repariere, meist bevor Sie es merken.</p>',
     '<p>Scraper, consegna pianificata e monitoraggio. La fonte cambia, qualcosa si rompe, io riparo, spesso prima che tu te ne accorga.</p>'),
    ('<div class="price">€500 to 1,000<span>then €150 to 500 / month</span></div>',
     '<div class="price">500 à 1 000 €<span>puis 150 à 500 € / mois</span></div>',
     '<div class="price">500 bis 1.000 €<span>dann 150 bis 500 € / Monat</span></div>',
     '<div class="price">500 a 1.000 €<span>poi 150 a 500 € / mese</span></div>'),

    ('<h3>Discord Bot</h3>',
     '<h3>Bot Discord</h3>',
     '<h3>Discord-Bot</h3>',
     '<h3>Bot Discord</h3>'),
    ('<p>A custom bot for your community: automation, public-data lookups, scheduled posts. Built and hosted.</p>',
     '<p>Un bot sur mesure pour votre communauté : automatisations, requêtes de données publiques, posts planifiés. Construit et hébergé.</p>',
     '<p>Ein maßgeschneiderter Bot für Ihre Community: Automatisierungen, Abfragen öffentlicher Daten, geplante Posts. Gebaut und gehostet.</p>',
     '<p>Un bot su misura per la tua community: automazioni, ricerche su dati pubblici, post programmati. Costruito e ospitato.</p>'),
    ('<div class="price">€500 to 2,500<span>plus hosting</span></div>',
     '<div class="price">500 à 2 500 €<span>plus hébergement</span></div>',
     '<div class="price">500 bis 2.500 €<span>zzgl. Hosting</span></div>',
     '<div class="price">500 a 2.500 €<span>più hosting</span></div>'),

    ('>See details</a>', '>Voir le détail</a>', '>Details ansehen</a>', '>Vedi i dettagli</a>'),

    # ---- how it works
    ('<h2 class="section-title">From a blocked scraper to a feed you can rely on.</h2>',
     "<h2 class=\"section-title\">D'un scraper bloqué à un flux sur lequel compter.</h2>",
     '<h2 class="section-title">Vom blockierten Scraper zum Feed, auf den Verlass ist.</h2>',
     '<h2 class="section-title">Da uno scraper bloccato a un feed su cui contare.</h2>'),
    ('<h3>Audit</h3><p>I check the public source and find the most reliable extraction route, a hidden API where one exists.</p>',
     "<h3>Audit</h3><p>J'examine la source publique et j'identifie la voie d'extraction la plus fiable, une API cachée quand elle existe.</p>",
     '<h3>Audit</h3><p>Ich prüfe die öffentliche Quelle und finde den verlässlichsten Extraktionsweg, eine Hidden API, wo es sie gibt.</p>',
     "<h3>Audit</h3><p>Esamino la fonte pubblica e individuo la via di estrazione più affidabile, un'API nascosta quando esiste.</p>"),
    ('<h3>Build</h3><p>A tested scraper that handles JS-heavy and Cloudflare-protected public pages, outputting clean data.</p>',
     '<h3>Construction</h3><p>Un scraper testé qui gère les pages publiques riches en JavaScript ou protégées par Cloudflare, avec une sortie propre.</p>',
     '<h3>Bauen</h3><p>Ein getesteter Scraper, der JS-lastige und Cloudflare-geschützte öffentliche Seiten beherrscht und saubere Daten liefert.</p>',
     '<h3>Costruzione</h3><p>Uno scraper testato che gestisce pagine pubbliche piene di JavaScript o protette da Cloudflare, con output pulito.</p>'),
    ('<h3>Schedule &amp; monitor</h3><p>Delivery on your cadence, with monitoring. When the source changes and it breaks, I repair it.</p>',
     '<h3>Planification &amp; monitoring</h3><p>Livraison à votre cadence, avec surveillance. Quand la source change et que ça casse, je répare.</p>',
     '<h3>Planen &amp; überwachen</h3><p>Lieferung in Ihrem Rhythmus, mit Monitoring. Ändert sich die Quelle und etwas bricht, repariere ich.</p>',
     '<h3>Pianifica &amp; monitora</h3><p>Consegna alla cadenza che vuoi, con monitoraggio. Quando la fonte cambia e qualcosa si rompe, riparo.</p>'),
    ('<h3>You operate &amp; own</h3><p>You run the tool and own the data. I build and maintain it: a tool, not an operating service.</p>',
     "<h3>Vous exploitez &amp; possédez</h3><p>Vous faites tourner l'outil et possédez les données. Je le construis et je le maintiens : un outil, pas un service d'exploitation.</p>",
     '<h3>Sie betreiben &amp; besitzen</h3><p>Sie betreiben das Tool und besitzen die Daten. Ich baue und warte es: ein Werkzeug, kein Betreiberdienst.</p>',
     '<h3>Tu gestisci &amp; possiedi</h3><p>Tu fai girare lo strumento e possiedi i dati. Io lo costruisco e lo mantengo: uno strumento, non un servizio di gestione.</p>'),

    # ---- scope
    ('<h2 class="section-title">Reliability, not circumvention.</h2>',
     '<h2 class="section-title">De la fiabilité, pas du contournement.</h2>',
     '<h2 class="section-title">Verlässlichkeit statt Umgehung.</h2>',
     '<h2 class="section-title">Affidabilità, non aggiramento.</h2>'),
    ('<li><strong>Public, logged-out pages only.</strong> Factual and business data: prices, specs, stock, listings, market data, schedules. No logins, no paywalls, no accounts.</li>',
     '<li><strong>Pages publiques, hors connexion uniquement.</strong> Données factuelles et business : prix, specs, stocks, annonces, données de marché, horaires. Pas de comptes, pas de paywalls.</li>',
     '<li><strong>Nur öffentliche Seiten, ohne Login.</strong> Faktische und geschäftliche Daten: Preise, Spezifikationen, Bestände, Inserate, Marktdaten, Fahrpläne. Keine Logins, keine Paywalls, keine Konten.</li>',
     '<li><strong>Solo pagine pubbliche, senza login.</strong> Dati fattuali e business: prezzi, specifiche, disponibilità, annunci, dati di mercato, orari. Niente login, niente paywall, niente account.</li>'),
    ('<li><strong>No personal data.</strong> Strictly non-PII. No names with contacts, profiles or photos. B2B and factual data only.</li>',
     '<li><strong>Aucune donnée personnelle.</strong> Strictement non-PII. Pas de noms avec contacts, de profils ou de photos. Données B2B et factuelles uniquement.</li>',
     '<li><strong>Keine personenbezogenen Daten.</strong> Strikt ohne PII. Keine Namen mit Kontaktdaten, keine Profile, keine Fotos. Nur B2B- und Sachdaten.</li>',
     '<li><strong>Nessun dato personale.</strong> Rigorosamente senza PII. Niente nomi con contatti, profili o foto. Solo dati B2B e fattuali.</li>'),
    ('<li><strong>robots.txt and rate limits respected.</strong> Pages are read like a normal visitor would, at a respectful rate. Output is structured and transformed.</li>',
     '<li><strong>robots.txt et limites de débit respectés.</strong> Les pages sont lues comme le ferait un visiteur normal, à un rythme respectueux. La sortie est structurée et transformée.</li>',
     '<li><strong>robots.txt und Rate-Limits respektiert.</strong> Seiten werden gelesen wie von einem normalen Besucher, in respektvollem Tempo. Die Ausgabe ist strukturiert und transformiert.</li>',
     "<li><strong>robots.txt e limiti di frequenza rispettati.</strong> Le pagine vengono lette come farebbe un normale visitatore, a un ritmo rispettoso. L'output è strutturato e trasformato.</li>"),
    ('<li><strong>You operate and own the data.</strong> I build and maintain the tool, you run it and control the data. A clean, documented handover every time.</li>',
     "<li><strong>Vous exploitez et possédez les données.</strong> Je construis et maintiens l'outil, vous l'exploitez et contrôlez les données. Une passation propre et documentée, à chaque fois.</li>",
     '<li><strong>Sie betreiben und besitzen die Daten.</strong> Ich baue und warte das Tool, Sie betreiben es und kontrollieren die Daten. Eine saubere, dokumentierte Übergabe, jedes Mal.</li>',
     '<li><strong>Tu gestisci e possiedi i dati.</strong> Io costruisco e mantengo lo strumento, tu lo gestisci e controlli i dati. Una consegna pulita e documentata, ogni volta.</li>'),
    ('<p class="st">Typically in scope</p>',
     '<p class="st">Typiquement dans le périmètre</p>',
     '<p class="st">Typisch im Rahmen</p>',
     '<p class="st">Tipicamente nel perimetro</p>'),
    ('<span>Product prices, specs, stock</span><span class="lk">e-commerce</span>',
     '<span>Prix produits, specs, stocks</span><span class="lk">e-commerce</span>',
     '<span>Produktpreise, Specs, Bestände</span><span class="lk">E-Commerce</span>',
     '<span>Prezzi prodotto, specifiche, stock</span><span class="lk">e-commerce</span>'),
    ('<span>Listings (price, size, location)</span><span class="lk">real estate</span>',
     '<span>Annonces (prix, surface, localisation)</span><span class="lk">immobilier</span>',
     '<span>Inserate (Preis, Fläche, Lage)</span><span class="lk">Immobilien</span>',
     '<span>Annunci (prezzo, superficie, posizione)</span><span class="lk">immobiliare</span>'),
    ('<span>Catalogue and marketplace data</span><span class="lk">marketplace</span>',
     '<span>Données catalogue et marketplace</span><span class="lk">marketplace</span>',
     '<span>Katalog- und Marktplatzdaten</span><span class="lk">Marktplatz</span>',
     '<span>Dati catalogo e marketplace</span><span class="lk">marketplace</span>'),
    ('<span>Market data, schedules, prices</span><span class="lk">travel · finance</span>',
     '<span>Données de marché, horaires, prix</span><span class="lk">voyage · finance</span>',
     '<span>Marktdaten, Fahrpläne, Preise</span><span class="lk">Reise · Finanzen</span>',
     '<span>Dati di mercato, orari, prezzi</span><span class="lk">viaggi · finanza</span>'),
    ('Feedsmith builds a <strong>tool</strong> for reading <strong>public, factual data</strong>. It is not used to access logins, paywalls or personal data. You remain the operator and owner of the data, and confirm your right to access the source.',
     "Feedsmith construit un <strong>outil</strong> de lecture de <strong>données publiques et factuelles</strong>. Il ne sert pas à accéder à des comptes, des paywalls ou des données personnelles. Vous restez l'exploitant et le propriétaire des données, et confirmez votre droit d'accès à la source.",
     'Feedsmith baut ein <strong>Werkzeug</strong> zum Lesen <strong>öffentlicher, faktischer Daten</strong>. Es dient nicht dem Zugriff auf Logins, Paywalls oder personenbezogene Daten. Sie bleiben Betreiber und Eigentümer der Daten und bestätigen Ihr Recht auf Zugriff auf die Quelle.',
     'Feedsmith costruisce uno <strong>strumento</strong> per leggere <strong>dati pubblici e fattuali</strong>. Non serve ad accedere a login, paywall o dati personali. Tu resti il gestore e il proprietario dei dati, e confermi il tuo diritto di accesso alla fonte.'),

    # ---- proof
    ('<p class="kick">Proof</p>',
     '<p class="kick">Preuves</p>',
     '<p class="kick">Belege</p>',
     '<p class="kick">Prove</p>'),
    ('<h2 class="section-title">Open source, tested, and runnable.</h2>',
     '<h2 class="section-title">Open source, testé, exécutable.</h2>',
     '<h2 class="section-title">Open Source, getestet, lauffähig.</h2>',
     '<h2 class="section-title">Open source, testato, eseguibile.</h2>'),
    ('<p class="lead">Not a slide deck. Real code you can read, clone and run: the hard 20% of scraping that no-code tools fail at.</p>',
     '<p class="lead">Pas un slide deck. Du vrai code à lire, cloner et lancer : les 20 % difficiles du scraping où les outils no-code échouent.</p>',
     '<p class="lead">Kein Foliensatz. Echter Code zum Lesen, Klonen und Ausführen: die schwierigen 20 % des Scrapings, an denen No-Code-Tools scheitern.</p>',
     '<p class="lead">Niente slide. Codice vero da leggere, clonare ed eseguire: il 20 % difficile dello scraping dove i tool no-code falliscono.</p>'),
    ('<div class="panel-foot">One feed, one file. That is the whole configuration behind the sample above.</div>',
     "<div class=\"panel-foot\">Un flux, un fichier. C'est toute la configuration derrière l'échantillon ci-dessus.</div>",
     '<div class="panel-foot">Ein Feed, eine Datei. Das ist die gesamte Konfiguration hinter dem Beispiel oben.</div>',
     '<div class="panel-foot">Un feed, un file. È tutta la configurazione dietro il campione qui sopra.</div>'),
    ('<p>The Managed Data Feed offer in code: resilient fetch, no-PII policy, schedule, self-healing monitor, CSV / JSON / webhook output.</p>',
     "<p>L'offre Flux de données géré, en code : fetch résilient, politique no-PII, planification, monitoring auto-réparant, sortie CSV / JSON / webhook.</p>",
     '<p>Das Angebot Betreuter Datenfeed als Code: robustes Fetching, No-PII-Policy, Zeitplan, selbstheilendes Monitoring, Ausgabe als CSV / JSON / Webhook.</p>',
     "<p>L'offerta Feed di dati gestito, in codice: fetch resiliente, policy no-PII, pianificazione, monitoraggio auto-riparante, output CSV / JSON / webhook.</p>"),
    ("<p>Read a site's internal JSON API directly instead of parsing fragile HTML: faster, and far more stable.</p>",
     "<p>Lire directement l'API JSON interne d'un site au lieu de parser un HTML fragile : plus rapide, et bien plus stable.</p>",
     '<p>Die interne JSON-API einer Website direkt lesen statt fragiles HTML zu parsen: schneller und deutlich stabiler.</p>',
     "<p>Leggere direttamente l'API JSON interna di un sito invece di fare parsing di HTML fragile: più veloce, e molto più stabile.</p>"),
    ('<p>Why a public page returns empty: a TLS fingerprint check before render. How to read it like a normal browser, compliantly.</p>',
     "<p>Pourquoi une page publique revient vide : un contrôle d'empreinte TLS avant le rendu. Comment la lire comme un navigateur normal, en conformité.</p>",
     '<p>Warum eine öffentliche Seite leer zurückkommt: ein TLS-Fingerprint-Check vor dem Rendern. Wie man sie wie ein normaler Browser liest, regelkonform.</p>',
     "<p>Perché una pagina pubblica torna vuota: un controllo dell'impronta TLS prima del rendering. Come leggerla come un browser normale, in modo conforme.</p>"),
    ('>View on GitHub</a>', '>Voir sur GitHub</a>', '>Auf GitHub ansehen</a>', '>Vedi su GitHub</a>'),

    # ---- guides
    ('<h2 class="section-title">The why behind the work.</h2>',
     '<h2 class="section-title">Le pourquoi derrière le travail.</h2>',
     '<h2 class="section-title">Das Warum hinter der Arbeit.</h2>',
     '<h2 class="section-title">Il perché dietro il lavoro.</h2>'),
    ('<h3>Why your no-code scraper keeps breaking</h3>',
     '<h3>Pourquoi votre scraper no-code casse en boucle</h3>',
     '<h3>Warum Ihr No-Code-Scraper immer wieder bricht</h3>',
     '<h3>Perché il tuo scraper no-code continua a rompersi</h3>'),
    ('<p>Layout changes, JS-rendered data, fingerprint checks, and what actually fixes them.</p>',
     "<p>Changements de layout, données rendues en JS, contrôles d'empreinte, et ce qui les corrige vraiment.</p>",
     '<p>Layout-Änderungen, JS-gerenderte Daten, Fingerprint-Checks, und was wirklich hilft.</p>',
     '<p>Cambi di layout, dati renderizzati in JS, controlli di fingerprint, e cosa li risolve davvero.</p>'),
    ('<h3>What is a hidden API</h3>',
     "<h3>Qu'est-ce qu'une API cachée</h3>",
     '<h3>Was ist eine Hidden API</h3>',
     "<h3>Che cos'è una API nascosta</h3>"),
    ('<p>The internal JSON endpoints behind a page, and why calling them beats HTML parsing.</p>',
     '<p>Les endpoints JSON internes derrière une page, et pourquoi les appeler bat le parsing HTML.</p>',
     '<p>Die internen JSON-Endpunkte hinter einer Seite, und warum sie das HTML-Parsing schlagen.</p>',
     "<p>Gli endpoint JSON interni dietro una pagina, e perché chiamarli batte il parsing dell'HTML.</p>"),
    ('<h3>Cloudflare-protected public sites</h3>',
     '<h3>Sites publics protégés par Cloudflare</h3>',
     '<h3>Cloudflare-geschützte öffentliche Seiten</h3>',
     '<h3>Siti pubblici protetti da Cloudflare</h3>'),
    ('<p>Empty pages are usually a TLS fingerprint check rather than a CAPTCHA, and there is a compliant way to read them.</p>',
     "<p>Une page vide est le plus souvent un contrôle d'empreinte TLS plutôt qu'un CAPTCHA, et il existe une façon conforme de la lire.</p>",
     '<p>Leere Seiten sind meist ein TLS-Fingerprint-Check und kein CAPTCHA, und es gibt einen regelkonformen Weg, sie zu lesen.</p>',
     "<p>Le pagine vuote di solito sono un controllo dell'impronta TLS più che un CAPTCHA, e c'è un modo conforme di leggerle.</p>"),
    ('>Read the guide</a>', '>Lire le guide</a>', '>Guide lesen</a>', '>Leggi la guida</a>'),

    # ---- contact
    ('<h2>Get a free feasibility check</h2>',
     '<h2>Demandez une étude de faisabilité gratuite</h2>',
     '<h2>Kostenlose Machbarkeitsprüfung anfragen</h2>',
     '<h2>Richiedi uno studio di fattibilità gratuito</h2>'),
    ('<p>Tell me the public site and the data you need. I will tell you if it is doable, how, and in which language.</p>',
     "<p>Indiquez-moi le site public et les données dont vous avez besoin. Je vous dis si c'est faisable, comment, et dans quelle langue.</p>",
     '<p>Nennen Sie mir die öffentliche Website und die Daten, die Sie brauchen. Ich sage Ihnen, ob es machbar ist, wie, und in welcher Sprache.</p>',
     '<p>Indicami il sito pubblico e i dati che ti servono. Ti dico se è fattibile, come, e in quale lingua.</p>'),
    ('aria-label="The public site or URL" placeholder="The public site / URL"',
     'aria-label="Le site ou l\'URL publique" placeholder="Le site / l\'URL publique"',
     'aria-label="Die öffentliche Website oder URL" placeholder="Die öffentliche Website / URL"',
     'aria-label="Il sito o l\'URL pubblico" placeholder="Il sito / l\'URL pubblico"'),
    ('<button class="btn btn-primary" type="submit">Send</button>',
     '<button class="btn btn-primary" type="submit">Envoyer</button>',
     '<button class="btn btn-primary" type="submit">Anfrage senden</button>',
     '<button class="btn btn-primary" type="submit">Invia</button>'),
    ('Or email <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Based in Switzerland · DE / FR / IT / EN.',
     'Ou par e-mail : <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Basé en Suisse · FR / DE / IT / EN.',
     'Oder per E-Mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Sitz in der Schweiz · DE / FR / IT / EN.',
     'Oppure via e-mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Con base in Svizzera · IT / FR / DE / EN.'),

    # ---- shared form placeholders (hero + contact)
    ('aria-label="Your email" placeholder="Your email"',
     'aria-label="Votre e-mail" placeholder="Votre e-mail"',
     'aria-label="Ihre E-Mail" placeholder="Ihre E-Mail"',
     'aria-label="La tua e-mail" placeholder="La tua e-mail"'),
    ('aria-label="What data do you need, and in which language" placeholder="What data do you need? Which language (DE / FR / IT / EN)?"',
     'aria-label="Quelles données vous faut-il, et dans quelle langue" placeholder="Quelles données vous faut-il ? Quelle langue (FR / DE / IT / EN) ?"',
     'aria-label="Welche Daten brauchen Sie, und in welcher Sprache" placeholder="Welche Daten brauchen Sie? Welche Sprache (DE / FR / IT / EN)?"',
     'aria-label="Quali dati ti servono, e in quale lingua" placeholder="Quali dati ti servono? Quale lingua (IT / FR / DE / EN)?"'),

    # ---- footer
    ('Public sources only · factual, non-personal data · robots.txt and rate limits respected · you operate and own the data.',
     'Sources publiques uniquement · données factuelles, non personnelles · robots.txt et limites de débit respectés · vous exploitez et possédez les données.',
     'Nur öffentliche Quellen · faktische, nicht personenbezogene Daten · robots.txt und Rate-Limits respektiert · Sie betreiben und besitzen die Daten.',
     'Solo fonti pubbliche · dati fattuali, non personali · robots.txt e limiti di frequenza rispettati · tu gestisci e possiedi i dati.'),
    ('<a href="/">Home</a>', '<a href="/fr/">Accueil</a>', '<a href="/de/">Start</a>', '<a href="/it/">Home</a>'),
]

IDX = {"fr": 1, "de": 2, "it": 3}


def build(lang: str) -> str:
    html = SRC.read_text(encoding="utf-8")

    for old, new in STRUCTURAL:
        html = html.replace(old, new)

    for old, new in head_block(lang).items():
        assert old in html, f"[{lang}] head key missing from index.html: {old[:70]}"
        html = html.replace(old, new)

    i = IDX[lang]
    for row in T:
        en, trans = row[0], row[i]
        assert en in html, f"[{lang}] key missing from index.html: {en[:70]}"
        html = html.replace(en, trans)

    return html


def main() -> None:
    for lang in LOCALES:
        out = ROOT / lang / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(lang), encoding="utf-8")
        print(f"  wrote {out.relative_to(ROOT)}")
    print("done")


if __name__ == "__main__":
    main()
