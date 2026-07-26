from __future__ import annotations

"""
build_locale_homes.py — Feedsmith localized home generator.

The ENGLISH home (index.html) is the single source of truth for STRUCTURE.
This script clones it into de/, fr/ and it/ by applying exact text
substitutions, so every language version has the same sections, the same
machine, the same motion, translated.

Rules encoded here:
  - nav / footer anchors become LOCAL (#offers, #contact, ...) so a visitor
    never gets bounced to the English home by switching language;
  - brand + footer "Home" link point at the local home (/de/, /fr/, /it/);
  - head metadata (title, description, OG, canonical, og:url, lang) is
    fully localized; the hreflang cluster stays identical on every page;
  - offer cards / guide cards link to the (English) detail pages, the only
    versions that exist;
  - REAL MACHINE OUTPUT IS NEVER TRANSLATED. The sample CSV rows, the CSV
    column names, the YAML config, the HTTP status codes and the repository
    names come from an actual run. Translating them would turn evidence into
    fiction. Only our own captions around them are localized.

Every replacement is asserted: if a future edit to index.html breaks a key,
the build fails loudly instead of silently shipping a diverged page.

Usage:  python3 tools/build_locale_homes.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
LOCALES = ("fr", "de", "it")

STRUCTURAL = [
    ('href="/#offers"', 'href="#offers"'),
    ('href="/#guides"', 'href="#guides"'),
    ('href="/#portfolio"', 'href="#portfolio"'),
    ('href="/#contact"', 'href="#contact"'),
    ('href="/#data"', 'href="#data"'),
]

HEAD_EN = {
    "lang_attr": '<html lang="en">',
    "title": "<title>Feedsmith — Reliable Data Feeds from Public Sources | Web Scraping Specialist</title>",
    "desc": '<meta name="description" content="When no-code tools and AI scrapers get blocked or return empty pages, Feedsmith extracts clean public data and keeps it running. Reliable, maintained data feeds — factual, non-PII, you operate and own the data." />',
    "canonical": '<link rel="canonical" href="https://feedsmith.net/" />',
    "og_title": '<meta property="og:title" content="Feedsmith — Reliable Data Feeds from Public Sources" />',
    "og_desc": '<meta property="og:description" content="Clean, maintained data feeds from public sources — when no-code and AI scrapers fail." />',
    "og_url": '<meta property="og:url" content="https://feedsmith.net/" />',
    "brand_href": '<a class="brand" href="/">',
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
        HEAD_EN["brand_href"]: f'<a class="brand" href="/{lang}/">',
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
    # A literal calque of the English runs 5 lines at poster scale in every
    # target language. These are cut to the same beat as the original instead.
    ('<h1 data-rise class="in">Reliable data feeds from public sources, <em>kept running.</em></h1>',
     '<h1 data-rise class="in">Des flux de données publiques, <em>maintenus en vie.</em></h1>',
     '<h1 data-rise class="in">Datenfeeds aus öffentlichen Quellen, <em>die weiterlaufen.</em></h1>',
     '<h1 data-rise class="in">Feed di dati da fonti pubbliche, <em>tenuti in vita.</em></h1>'),
    ('When Apify, Octoparse or a ChatGPT script gets blocked and returns empty pages, I take over the extraction and keep it <em>alive</em>.',
     "Quand Apify, Octoparse ou un script écrit par ChatGPT se fait bloquer et renvoie des pages vides, je reprends l'extraction et je la maintiens <em>en vie</em>.",
     'Wenn Apify, Octoparse oder ein ChatGPT-Skript blockiert wird und leere Seiten liefert, übernehme ich die Extraktion und halte sie <em>am Leben</em>.',
     "Quando Apify, Octoparse o uno script scritto da ChatGPT viene bloccato e restituisce pagine vuote, prendo in mano l'estrazione e la tengo <em>viva</em>."),
    ('>Get a free feasibility check <span class="arw">&rarr;</span></a>',
     '>Étude de faisabilité gratuite <span class="arw">&rarr;</span></a>',
     '>Kostenlose Machbarkeitsprüfung <span class="arw">&rarr;</span></a>',
     '>Studio di fattibilità gratuito <span class="arw">&rarr;</span></a>'),
    ('>See a real output</a>', '>Voir une sortie réelle</a>',
     '>Echte Ausgabe ansehen</a>', '>Vedi un output reale</a>'),
    ('<b>Two minutes.</b> Send the public URL and the fields you need. I answer with what is extractable, how, and at what price.',
     "<b>Deux minutes.</b> Envoyez l'URL publique et les champs qu'il vous faut. Je réponds avec ce qui est extractible, comment, et à quel prix.",
     '<b>Zwei Minuten.</b> Schicken Sie die öffentliche URL und die Felder, die Sie brauchen. Ich antworte mit dem, was extrahierbar ist, wie, und zu welchem Preis.',
     "<b>Due minuti.</b> Mandami l'URL pubblico e i campi che ti servono. Rispondo con ciò che è estraibile, come, e a che prezzo."),

    # ---- machine chrome (the field names below stay as the feed emits them)
    ('<span>raw public web &rarr; structured feed</span>',
     '<span>web public brut &rarr; flux structuré</span>',
     '<span>rohes öffentliches web &rarr; strukturierter feed</span>',
     '<span>web pubblico grezzo &rarr; feed strutturato</span>'),
    ('<i></i> live</span>', '<i></i> en direct</span>', '<i></i> live</span>', '<i></i> in diretta</span>'),
    ('aria-label="Broken markup, 403 responses and empty pages travel through a forge gate and come out as clean rows of product data."',
     'aria-label="Du markup cassé, des réponses 403 et des pages vides traversent une porte de forge et ressortent en lignes propres de données produit."',
     'aria-label="Kaputtes Markup, 403-Antworten und leere Seiten laufen durch ein Schmiedetor und kommen als saubere Zeilen mit Produktdaten heraus."',
     'aria-label="Markup rotto, risposte 403 e pagine vuote attraversano una porta di forgia ed escono come righe pulite di dati prodotto."'),

    # ---- belt (HTTP codes stay literal, the descriptions do not)
    ('<span>JS-rendered prices</span>', '<span>Prix rendus en JS</span>',
     '<span>JS-gerenderte Preise</span>', '<span>Prezzi resi in JS</span>'),
    ('<span>Layout changed overnight</span>', '<span>Mise en page changée du jour au lendemain</span>',
     '<span>Layout über Nacht geändert</span>', '<span>Layout cambiato da un giorno all\'altro</span>'),
    ('<span>Rotating class names</span>', '<span>Noms de classes tournants</span>',
     '<span>Rotierende Klassennamen</span>', '<span>Nomi di classi rotanti</span>'),
    ('<span>Empty response body</span>', '<span>Corps de réponse vide</span>',
     '<span>Leerer Response-Body</span>', '<span>Corpo della risposta vuoto</span>'),
    ('<span>Cursor pagination</span>', '<span>Pagination par curseur</span>',
     '<span>Cursor-Pagination</span>', '<span>Paginazione a cursore</span>'),

    # ---- offers
    ('<p class="kick">Offers</p>', '<p class="kick">Offres</p>',
     '<p class="kick">Leistungen</p>', '<p class="kick">Servizi</p>'),
    ('<h2 class="section-title">Start with an audit. Scale to a maintained feed.</h2>',
     '<h2 class="section-title">Commencez par un audit. Passez à un flux maintenu.</h2>',
     '<h2 class="section-title">Mit einem Audit starten. Zum betreuten Feed ausbauen.</h2>',
     '<h2 class="section-title">Inizia con un audit. Passa a un feed mantenuto.</h2>'),
    ('<p>Four ways in, from a low-risk check to a feed I keep alive.</p>',
     "<p>Quatre portes d'entrée, d'une vérification sans risque à un flux que je maintiens en vie.</p>",
     '<p>Vier Einstiege, von der risikoarmen Prüfung bis zum Feed, den ich am Leben halte.</p>',
     '<p>Quattro modi di iniziare, dal controllo a basso rischio al feed che tengo in vita.</p>'),

    ('<h3>Hidden-API Audit</h3>', "<h3>Audit d'API cachée</h3>",
     '<h3>Hidden-API-Audit</h3>', '<h3>Audit di API nascosta</h3>'),
    ('<p>I check one public site, find the cleanest data route, and send you about 50 real sample rows. The low-risk way to start.</p>',
     "<p>J'examine un site public, j'identifie la voie d'accès la plus propre et je vous envoie une cinquantaine de lignes d'échantillon réelles. Le point de départ sans risque.</p>",
     '<p>Ich prüfe eine öffentliche Website, finde den saubersten Datenweg und sende Ihnen rund 50 echte Beispielzeilen. Der risikoarme Einstieg.</p>',
     "<p>Esamino un sito pubblico, trovo la via d'accesso più pulita e ti invio una cinquantina di righe di esempio reali. Il punto di partenza a basso rischio.</p>"),
    ('<div class="price">€150<span>fixed fee</span></div>',
     '<div class="price">150 €<span>forfait</span></div>',
     '<div class="price">150 €<span>Festpreis</span></div>',
     '<div class="price">150 €<span>forfait</span></div>'),

    ('<h3>One-off Scraper</h3>', '<h3>Scraper ponctuel</h3>',
     '<h3>Einmaliger Scraper</h3>', '<h3>Scraper una tantum</h3>'),
    ('<p>A robust scraper for one public source, delivered as tested code you own. Clean CSV, JSON or API output.</p>',
     '<p>Un scraper robuste pour une source publique, livré en code testé qui vous appartient. Sortie propre CSV, JSON ou API.</p>',
     '<p>Ein robuster Scraper für eine öffentliche Quelle, geliefert als getesteter Code, der Ihnen gehört. Saubere Ausgabe als CSV, JSON oder API.</p>',
     '<p>Uno scraper robusto per una fonte pubblica, consegnato come codice testato di tua proprietà. Output pulito CSV, JSON o API.</p>'),
    ('<div class="price">€600<span>to 1,500, one time</span></div>',
     '<div class="price">600 €<span>à 1 500, une fois</span></div>',
     '<div class="price">600 €<span>bis 1.500, einmalig</span></div>',
     '<div class="price">600 €<span>a 1.500, una tantum</span></div>'),

    ('<h3>Managed Data Feed</h3>', '<h3>Flux de données géré</h3>',
     '<h3>Betreuter Datenfeed</h3>', '<h3>Feed di dati gestito</h3>'),
    ('<p>Scraper, scheduled delivery and monitoring. The source changes, it breaks, I fix it, usually before you notice.</p>',
     '<p>Scraper, livraison planifiée et monitoring. La source change, ça casse, je répare, souvent avant que vous le remarquiez.</p>',
     '<p>Scraper, geplante Lieferung und Monitoring. Die Quelle ändert sich, etwas bricht, ich repariere, meist bevor Sie es merken.</p>',
     '<p>Scraper, consegna pianificata e monitoraggio. La fonte cambia, qualcosa si rompe, io riparo, spesso prima che tu te ne accorga.</p>'),
    ('<div class="price">€500<span>setup, then €150 to 500 / month</span></div>',
     '<div class="price">500 €<span>installation, puis 150 à 500 € / mois</span></div>',
     '<div class="price">500 €<span>Einrichtung, dann 150 bis 500 € / Monat</span></div>',
     '<div class="price">500 €<span>setup, poi 150 a 500 € / mese</span></div>'),

    ('<h3>Discord Bot</h3>', '<h3>Bot Discord</h3>', '<h3>Discord-Bot</h3>', '<h3>Bot Discord</h3>'),
    ('<p>A custom bot for your community: automation, public-data lookups, scheduled posts. Built and hosted.</p>',
     '<p>Un bot sur mesure pour votre communauté : automatisations, requêtes de données publiques, posts planifiés. Construit et hébergé.</p>',
     '<p>Ein maßgeschneiderter Bot für Ihre Community: Automatisierungen, Abfragen öffentlicher Daten, geplante Posts. Gebaut und gehostet.</p>',
     '<p>Un bot su misura per la tua community: automazioni, ricerche su dati pubblici, post programmati. Costruito e ospitato.</p>'),
    ('<div class="price">€500<span>to 2,500, plus hosting</span></div>',
     '<div class="price">500 €<span>à 2 500, plus hébergement</span></div>',
     '<div class="price">500 €<span>bis 2.500, zzgl. Hosting</span></div>',
     '<div class="price">500 €<span>a 2.500, più hosting</span></div>'),

    ('>See details <span class="arw">&rarr;</span></a>',
     '>Voir le détail <span class="arw">&rarr;</span></a>',
     '>Details ansehen <span class="arw">&rarr;</span></a>',
     '>Vedi i dettagli <span class="arw">&rarr;</span></a>'),

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

    # ---- the deliverable (captions only; the CSV below stays as it ran)
    ('<p class="kick">The deliverable</p>', '<p class="kick">Le livrable</p>',
     '<p class="kick">Das Ergebnis</p>', '<p class="kick">Il risultato</p>'),
    ('<h2 class="section-title">A dataset you can check, not a promise.</h2>',
     '<h2 class="section-title">Un jeu de données vérifiable, pas une promesse.</h2>',
     '<h2 class="section-title">Ein Datensatz, den Sie prüfen können, kein Versprechen.</h2>',
     '<h2 class="section-title">Un dataset che puoi verificare, non una promessa.</h2>'),
    ('<p><em>Real</em> output from the open-source starter behind the Managed Data Feed offer, run against a public sandbox catalogue. Same shape as what lands in your inbox or your database.</p>',
     "<p>Une sortie <em>réelle</em> du starter open source qui équipe l'offre Flux de données géré, exécuté sur un catalogue public de test. Exactement la forme de ce qui arrive dans votre boîte mail ou votre base.</p>",
     '<p><em>Echte</em> Ausgabe des Open-Source-Starters hinter dem Angebot Betreuter Datenfeed, ausgeführt auf einem öffentlichen Test-Katalog. Genau die Form, die in Ihrem Postfach oder Ihrer Datenbank landet.</p>',
     "<p>Output <em>reale</em> dello starter open source dietro l'offerta Feed di dati gestito, eseguito su un catalogo pubblico di prova. La stessa forma di ciò che arriva nella tua casella o nel tuo database.</p>"),
    ('<div class="panel-foot">Public sandbox source. Factual, non-personal fields. One row per product, one column per field, with the fetch timestamp kept.</div>',
     "<div class=\"panel-foot\">Source publique de test. Champs factuels, non personnels. Une ligne par produit, une colonne par champ, avec l'horodatage de collecte conservé.</div>",
     '<div class="panel-foot">Öffentliche Test-Quelle. Faktische, nicht personenbezogene Felder. Eine Zeile pro Produkt, eine Spalte pro Feld, mit erhaltenem Abruf-Zeitstempel.</div>',
     '<div class="panel-foot">Fonte pubblica di prova. Campi fattuali, non personali. Una riga per prodotto, una colonna per campo, con il timestamp di raccolta conservato.</div>'),
    ('<p class="micro" data-rise>Your feed carries your fields and nothing else: the columns you asked for, in the format you asked for.</p>',
     "<p class=\"micro\" data-rise>Votre flux porte vos champs et rien d'autre : les colonnes demandées, dans le format demandé.</p>",
     '<p class="micro" data-rise>Ihr Feed trägt Ihre Felder und sonst nichts: die Spalten, die Sie wollten, im Format, das Sie wollten.</p>',
     "<p class=\"micro\" data-rise>Il tuo feed porta i tuoi campi e nient'altro: le colonne che hai chiesto, nel formato che hai chiesto.</p>"),

    # ---- scope
    ('<p class="kick">Scope</p>', '<p class="kick">Périmètre</p>',
     '<p class="kick">Rahmen</p>', '<p class="kick">Perimetro</p>'),
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
    ('<p class="st">Typically in scope</p>', '<p class="st">Typiquement dans le périmètre</p>',
     '<p class="st">Typisch im Rahmen</p>', '<p class="st">Tipicamente nel perimetro</p>'),
    ('<span>Product prices, specs, stock</span><span class="lk">e-commerce</span>',
     '<span>Prix produits, specs, stocks</span><span class="lk">e-commerce</span>',
     '<span>Produktpreise, Specs, Bestände</span><span class="lk">e-commerce</span>',
     '<span>Prezzi prodotto, specifiche, stock</span><span class="lk">e-commerce</span>'),
    ('<span>Listings (price, size, location)</span><span class="lk">real estate</span>',
     '<span>Annonces (prix, surface, localisation)</span><span class="lk">immobilier</span>',
     '<span>Inserate (Preis, Fläche, Lage)</span><span class="lk">immobilien</span>',
     '<span>Annunci (prezzo, superficie, posizione)</span><span class="lk">immobiliare</span>'),
    ('<span>Catalogue and marketplace data</span><span class="lk">marketplace</span>',
     '<span>Données catalogue et marketplace</span><span class="lk">marketplace</span>',
     '<span>Katalog- und Marktplatzdaten</span><span class="lk">marktplatz</span>',
     '<span>Dati catalogo e marketplace</span><span class="lk">marketplace</span>'),
    ('<span>Market data, schedules, prices</span><span class="lk">travel · finance</span>',
     '<span>Données de marché, horaires, prix</span><span class="lk">voyage · finance</span>',
     '<span>Marktdaten, Fahrpläne, Preise</span><span class="lk">reise · finanzen</span>',
     '<span>Dati di mercato, orari, prezzi</span><span class="lk">viaggi · finanza</span>'),
    ('Feedsmith builds a <strong>tool</strong> for reading <strong>public, factual data</strong>. It is not used to access logins, paywalls or personal data. You remain the operator and owner of the data, and confirm your right to access the source.',
     "Feedsmith construit un <strong>outil</strong> de lecture de <strong>données publiques et factuelles</strong>. Il ne sert pas à accéder à des comptes, des paywalls ou des données personnelles. Vous restez l'exploitant et le propriétaire des données, et confirmez votre droit d'accès à la source.",
     'Feedsmith baut ein <strong>Werkzeug</strong> zum Lesen <strong>öffentlicher, faktischer Daten</strong>. Es dient nicht dem Zugriff auf Logins, Paywalls oder personenbezogene Daten. Sie bleiben Betreiber und Eigentümer der Daten und bestätigen Ihr Recht auf Zugriff auf die Quelle.',
     'Feedsmith costruisce uno <strong>strumento</strong> per leggere <strong>dati pubblici e fattuali</strong>. Non serve ad accedere a login, paywall o dati personali. Tu resti il gestore e il proprietario dei dati, e confermi il tuo diritto di accesso alla fonte.'),

    # ---- proof
    ('<p class="kick">Proof</p>', '<p class="kick">Preuves</p>',
     '<p class="kick">Belege</p>', '<p class="kick">Prove</p>'),
    ('<h2 class="section-title">Open source, tested, and runnable.</h2>',
     '<h2 class="section-title">Open source, testé, exécutable.</h2>',
     '<h2 class="section-title">Open Source, getestet, lauffähig.</h2>',
     '<h2 class="section-title">Open source, testato, eseguibile.</h2>'),
    ('<p>Not a slide deck. Real code you can read, clone and run: the hard 20% of scraping that no-code tools fail at.</p>',
     '<p>Pas un slide deck. Du vrai code à lire, cloner et lancer : les 20 % difficiles du scraping où les outils no-code échouent.</p>',
     '<p>Kein Foliensatz. Echter Code zum Lesen, Klonen und Ausführen: die schwierigen 20 % des Scrapings, an denen No-Code-Tools scheitern.</p>',
     '<p>Niente slide. Codice vero da leggere, clonare ed eseguire: il 20 % difficile dello scraping dove i tool no-code falliscono.</p>'),
    ('<div class="panel-foot">One feed, one file. That is the whole configuration behind the sample above.</div>',
     "<div class=\"panel-foot\">Un flux, un fichier. C'est toute la configuration derrière l'échantillon ci-dessus.</div>",
     '<div class="panel-foot">Ein Feed, eine Datei. Das ist die gesamte Konfiguration hinter dem Beispiel oben.</div>',
     '<div class="panel-foot">Un feed, un file. È tutta la configurazione dietro il campione qui sopra.</div>'),
    ('<div class="ico">starter</div>', '<div class="ico">starter</div>',
     '<div class="ico">starter</div>', '<div class="ico">starter</div>'),
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
    ('>View on GitHub <span class="arw">&rarr;</span></a>',
     '>Voir sur GitHub <span class="arw">&rarr;</span></a>',
     '>Auf GitHub ansehen <span class="arw">&rarr;</span></a>',
     '>Vedi su GitHub <span class="arw">&rarr;</span></a>'),

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
    ('<h3>What is a hidden API</h3>', "<h3>Qu'est-ce qu'une API cachée</h3>",
     '<h3>Was ist eine Hidden API</h3>', "<h3>Che cos'è una API nascosta</h3>"),
    ('<p>The internal JSON endpoints behind a page, and why calling them beats HTML parsing.</p>',
     '<p>Les endpoints JSON internes derrière une page, et pourquoi les appeler bat le parsing HTML.</p>',
     '<p>Die internen JSON-Endpunkte hinter einer Seite, und warum sie das HTML-Parsing schlagen.</p>',
     "<p>Gli endpoint JSON interni dietro una pagina, e perché chiamarli batte il parsing dell'HTML.</p>"),
    ('<h3>Cloudflare-protected public sites</h3>', '<h3>Sites publics protégés par Cloudflare</h3>',
     '<h3>Cloudflare-geschützte öffentliche Seiten</h3>', '<h3>Siti pubblici protetti da Cloudflare</h3>'),
    ('<p>Empty pages are usually a TLS fingerprint check rather than a CAPTCHA, and there is a compliant way to read them.</p>',
     "<p>Une page vide est le plus souvent un contrôle d'empreinte TLS plutôt qu'un CAPTCHA, et il existe une façon conforme de la lire.</p>",
     '<p>Leere Seiten sind meist ein TLS-Fingerprint-Check und kein CAPTCHA, und es gibt einen regelkonformen Weg, sie zu lesen.</p>',
     "<p>Le pagine vuote di solito sono un controllo dell'impronta TLS più che un CAPTCHA, e c'è un modo conforme di leggerle.</p>"),
    ('>Read the guide <span class="arw">&rarr;</span></span>',
     '>Lire le guide <span class="arw">&rarr;</span></span>',
     '>Guide lesen <span class="arw">&rarr;</span></span>',
     '>Leggi la guida <span class="arw">&rarr;</span></span>'),

    # ---- contact
    ('<h2>Get a free feasibility check</h2>',
     '<h2>Demandez une étude de faisabilité gratuite</h2>',
     '<h2>Kostenlose Machbarkeitsprüfung anfragen</h2>',
     '<h2>Richiedi uno studio di fattibilità gratuito</h2>'),
    ('<p>Tell me the public site and the data you need. I will tell you if it is <em>doable</em>, how, and in which language.</p>',
     "<p>Indiquez-moi le site public et les données dont vous avez besoin. Je vous dis si c'est <em>faisable</em>, comment, et dans quelle langue.</p>",
     '<p>Nennen Sie mir die öffentliche Website und die Daten, die Sie brauchen. Ich sage Ihnen, ob es <em>machbar</em> ist, wie, und in welcher Sprache.</p>',
     '<p>Indicami il sito pubblico e i dati che ti servono. Ti dico se è <em>fattibile</em>, come, e in quale lingua.</p>'),
    ('Or email <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Based in Switzerland · DE / FR / IT / EN.',
     'Ou par e-mail : <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Basé en Suisse · FR / DE / IT / EN.',
     'Oder per E-Mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Sitz in der Schweiz · DE / FR / IT / EN.',
     'Oppure via e-mail: <a href="mailto:hello@feedsmith.net">hello@feedsmith.net</a> · Con base in Svizzera · IT / FR / DE / EN.'),
    ('<button class="btn btn-primary" type="submit">Send <span class="arw">&rarr;</span></button>',
     '<button class="btn btn-primary" type="submit">Envoyer <span class="arw">&rarr;</span></button>',
     '<button class="btn btn-primary" type="submit">Anfrage senden <span class="arw">&rarr;</span></button>',
     '<button class="btn btn-primary" type="submit">Invia <span class="arw">&rarr;</span></button>'),

    # ---- form fields (shared by hero and contact)
    ('aria-label="The public site or URL" placeholder="The public site / URL"',
     'aria-label="Le site ou l\'URL publique" placeholder="Le site / l\'URL publique"',
     'aria-label="Die öffentliche Website oder URL" placeholder="Die öffentliche Website / URL"',
     'aria-label="Il sito o l\'URL pubblico" placeholder="Il sito / l\'URL pubblico"'),
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
