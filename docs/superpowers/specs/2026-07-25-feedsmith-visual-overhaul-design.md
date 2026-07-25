# Feedsmith - refonte visuelle complete ("Bureau technique")

Date: 2026-07-25
Statut: valide par Massii (direction A + panneaux instrument, vraies captures de livrables)

---

## 1. Pourquoi

Le site en production coche presque toute la liste des signatures "genere par IA":
palette dark-SaaS vert/menthe neon, Inter Bold partout, eyebrow `diamant + CAPS espacees`
repetee 6 fois, mot colore dans le H1, petit trait accent sous chaque H2, tout le contenu
enferme dans des cartes a coins arrondis avec halo, grilles 4 colonnes identiques, nav
glassmorphism, halos radiaux et grille de points en fond.

Le contenu, lui, est bon: prix affiches, perimetre legal explicite, preuves GitHub, 4 langues.
C'est la peau qu'il faut refaire, et la repetition structurelle qu'il faut casser.

## 2. Lecture du brief

Refonte-overhaul d'une landing de prestataire B2B solo (ingenierie de donnees) pour des PME
DACH/Suisse et des acheteurs techniques. Langage cible: **instrument de precision / rapport
technique**. Pas de framework, pas d'etape de build.

Reglages: variance 7, motion 4 (CSS seul), densite 5. La donnee est le produit, elle doit
etre visible sur la page plutot que decrite.

## 3. Le systeme "Bureau technique"

### 3.1 Jetons

```
--paper    #F2F2EF   fond de page (papier froid, pas de creme beige)
--paper-2  #EAEAE6   bandes de section alternees
--ink      #16181C   texte principal
--mid      #5F656C   texte secondaire
--dim      #8B9198   texte tertiaire, legendes
--rule     #D9D9D3   filet 1px
--rule-ink #16181C   filet 2px de tete de tableau
--sig      #C7351C   vermillon, accent unique
--panel    #101216   fond des panneaux instrument
--panel-tx #E8EAEC   texte sur panneau
--panel-2  #949BA3   texte secondaire sur panneau
--panel-ln #22262C   filet dans un panneau
--panel-sg #E0A33C   ambre, signal dans un panneau uniquement
```

Un seul accent sur toute la page (`--sig`). L'ambre n'existe QUE dans un panneau instrument,
comme un surlignage de sortie machine. Aucun degrade, aucun halo, aucune ombre floue.

### 3.2 Typographie

- Display et interface: **Archivo** (400/500/600/700), auto-hebergee en woff2.
- Chiffres, etiquettes techniques, sorties machine: **IBM Plex Mono** (400/500), auto-hebergee.
- Inter est retire du site.
- Tous les chiffres passent en `font-variant-numeric: tabular-nums`.
- Echelle: h1 56/1.04 (max 2 lignes), h2 34, h3 19, corps 16/1.6, mono 13.
- Les titres allemands sont testes: aucun titre ne doit depasser 2 lignes en DE.

### 3.3 Structure et formes

- Rayon **0** partout. Pas de coins arrondis, pas de pilules. C'est la regle de forme unique.
- Separation par **filets** (1px `--rule`, 2px `--ink` en tete de bloc) et par blanc, pas par cartes.
- Grilles asymetriques (7/5, 1fr/2.2fr/auto), jamais 4 colonnes egales.
- Maximum **2 eyebrows sur toute la page d'accueil** (contre 6 aujourd'hui).
- Aucun mot colore dans un titre. Aucun trait decoratif sous les titres.
- Aucun tiret cadratin dans le texte visible, dans les 4 langues.

### 3.4 Le panneau instrument

Bloc sombre insere dans la page claire, reserve a **ce qui sort d'une machine**: extrait CSV,
JSON, configuration YAML d'un flux, journal d'execution, extrait de code.

Regles: fond `--panel`, texte mono, filets `--panel-ln`, en-tete de panneau en mono 11px
espacee, une seule couleur de signal (`--panel-sg`). Ce n'est pas une inversion de theme de
section, c'est un composant, au meme titre qu'un bloc de code dans un article. Il ne porte
jamais de texte marketing.

### 3.5 Mouvement

Transitions de couleur au survol (150ms) et soulignement des liens. Aucune animation d'entree
au scroll, aucun element en boucle. `prefers-reduced-motion` respecte par construction.

## 4. Preuves visuelles

Aucune image decorative, aucune illustration SVG dessinee a la main, aucun faux ecran en `div`.
Les seuls visuels sont de **vrais artefacts** produits par les depots de Massii:

- `managed-data-feed-starter/data/books-demo.csv` (sortie reelle, source publique books.toscrape.com)
- `managed-data-feed-starter/data/prices-demo.json` (sortie reelle)
- `managed-data-feed-starter/feeds/books_demo.yaml` (configuration reelle d'un flux)
- extraits de code reels des 3 depots publics

Ils sont rendus soit en texte reel dans un panneau instrument (preferable: selectionnable,
traduisible, sans poids d'image), soit en capture PNG quand le rendu compte.

## 5. Page par page

| Page | Ce qui change |
|---|---|
| Accueil (x4 langues) | Restructuration complete: hero 7/5 avec registre de flux, offres en registre a filets, perimetre en 2 colonnes, preuves en panneau instrument, contact en pied de page |
| 4 offres (x4 langues) | Meme systeme, en-tete d'offre + prix en mono, etapes en liste numerotee a filets, plus de cartes |
| 3 guides (x4 langues) | Gabarit de lecture: colonne 68ch, sommaire lateral, code en panneau instrument |
| 5 pages pSEO (x4 langues) | Gabarit resserre genere par `tools/generate_scrape_pages.py`, qui est mis a jour en meme temps |
| 404 | Aligne sur le nouveau systeme |

## 6. Ce qui ne change pas

- Les URL, les slugs, les ancres (`/#offers`, `/#guides`, `/#portfolio`, `/#contact`).
- Les balises `title`, `description`, `canonical`, `hreflang`, OG, le `sitemap.xml`, `robots.txt`.
- Les noms de champs du formulaire Formspree (`target_url`, `email`, `details`) et l'action.
- Les en-tetes `_headers` et la CSP. Les polices auto-hebergees restent couvertes par `font-src 'self'`.
- Le contrat de classes partage entre les 57 pages: un seul `css/style.css`, aucune etape de build.
- La position juridique: sources publiques, non-PII, robots.txt et limites de debit respectes.

## 7. Verification avant livraison

1. Rendu Playwright de la home dans les 4 langues, en 1440px et 390px.
2. Rendu d'une page de chaque famille (offre, guide, pSEO, 404).
3. Controle mecanique: 0 tiret cadratin visible, 0 `border-radius` non nul, 1 seul accent,
   nombre d'eyebrows conforme, aucun titre a plus de 2 lignes en DE.
4. Contraste WCAG AA verifie sur le texte, les champs de formulaire et les boutons.
5. Console sans erreur, aucune requete vers un hote externe.

## 8. Hors perimetre

Refonte du contenu editorial des guides, nouvelle offre, changement de logo ou de nom,
generation de nouvelles pages pSEO, traduction de nouvelles langues.
