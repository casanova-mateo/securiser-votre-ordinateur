"""Met en page le guide Markdown FR en PDF (WeasyPrint).

Usage : python build_pdf.py [guide.md] [sortie.pdf] [--html sortie.html] [--fiche --subtitle "…"]
Par défaut : ../securiser-votre-ordinateur-personnel.md -> PDF du même nom, à côté du Markdown.
Avec --fiche : mise en page courte (bandeau-titre au lieu de la couverture et du sommaire,
sections non numérotées), utilisée par build_fiches.py.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path
from typing import NamedTuple

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from weasyprint import HTML

BUILD_DIR = Path(__file__).resolve().parent
ROOT = BUILD_DIR.parent
GUIDE_MD = ROOT / "securiser-votre-ordinateur-personnel.md"

# Réglages de la couverture et des métadonnées.
AUTHOR = "Matéo CASANOVA"
GUIDE_TITLE = "Sécuriser votre ordinateur personnel"
GUIDE_SUBTITLE = "Protéger vos données sous Windows, macOS et Linux"
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
          "août", "septembre", "octobre", "novembre", "décembre"]
# Version publiée et sa date (imprimée en mois et année) : changez les deux à chaque publication.
# La date est fixe pour que régénérer une même version donne exactement les mêmes PDF.
VERSION = "1.0"
RELEASE_DATE = datetime.date(2026, 10, 24)
EDITION = "version originale en français"
# Page de téléchargement, imprimée dans la mention finale de chaque document (vide : non imprimée).
SITE_URL = "https://casanova-mateo.github.io/securiser-votre-ordinateur/"
CONTACT = "mateo.casanova.cyber@gmail.com"
LICENSE_NOTE = (
    "Licence Creative Commons Attribution 4.0 International (CC BY 4.0) : vous pouvez copier, "
    "imprimer, distribuer et adapter {doc}, y compris à des fins commerciales, à condition "
    "de citer l’auteur, d’indiquer si des modifications ont été faites et de mentionner la "
    "licence (creativecommons.org/licenses/by/4.0/deed.fr).")
TOPICS = ("Mises à jour · Antivirus · Mots de passe · Chiffrement · Cloud · Navigateur · Réseau · "
          "Sauvegardes · Smartphone · Linux · Incidents")
KEYWORDS = ("sécurité informatique, mots de passe, chiffrement, BitLocker, FileVault, LUKS, "
            "sauvegardes, Windows, macOS, Linux")

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]")
OS_HEADING = re.compile(r"^(?:Sécuriser votre session )?(Windows|macOS|Linux)$"
                        r"|^(?:Les bons réflexes en ligne"
                        r"|Les bonnes habitudes avec vos appareils)$")
OS_KIND = {"Windows": "win", "macOS": "mac", "Linux": "linux"}
CALLOUT_KIND = {"Exemple": "example", "Pourquoi": "important", "Le kit": "important",
                "Par où commencer": "important", "Solution": "solution",
                "Pour se faire aider": "solution", "Attention": "warning"}
KEYS = re.compile(r"[A-Za-z]+(?: \+ [A-Za-z]+)+")
# Éléments qui terminent un encadré système.
CARD_END = ("h2", "h3", "h4", "blockquote")
# Fiche : pas d'en-tête courant sur la première page, qui porte le bandeau-titre.
FICHE_FIRST_PAGE = ("@page :first { background-image: none; @top-left { content: none; } "
                    "@top-right { content: none; } }")
# Options de WeasyPrint : PDF accessible (balisé).
PDF_OPTIONS = {"pdf_variant": "pdf/ua-1"}


class SourceError(ValueError):
    """Le Markdown ne respecte pas une convention dont dépend la mise en page."""


class Document(NamedTuple):
    """Le document mis en forme, commun au PDF et au site."""
    soup: BeautifulSoup
    title: str
    toc: list  # (niveau, numéro, texte, ancre) de chaque chapitre et de chaque partie
    content: Tag  # <main>, qui contient un <section> par chapitre
    chapters: list


def clean(text):
    """Texte d'un titre, sans ses emojis."""
    return EMOJI.sub("", text).strip()


def fr_typo(text):
    """Espaces insécables de la typographie française."""
    text = re.sub(r" ([:;!?»])", "\u00a0\\1", text)
    text = text.replace("« ", "«\u00a0")
    return re.sub(r"(\d) (?=[^\W\d_])", "\\1\u00a0", text)


def date_label(day):
    """Mois et année, par exemple « Octobre 2026 »."""
    return f"{MONTHS[day.month - 1].capitalize()} {day.year}"


def tag(soup, name, cls=None, text=None, **attrs):
    """Nouvel élément HTML, avec sa classe et son texte."""
    t = soup.new_tag(name, attrs=attrs)
    if cls:
        t["class"] = cls
    if text is not None:
        t.string = text
    return t


def leading_strong(el):
    """Le texte en gras qui ouvre le paragraphe `el` (libellé d'un encadré), sinon None."""
    if el is None or el.name != "p" or not el.contents:
        return None
    first = el.contents[0]
    return first if getattr(first, "name", None) == "strong" else None


def callout_kind(label):
    """Couleur d'un encadré d'après son libellé ; un libellé inconnu donne un encadré bleu."""
    return next((v for k, v in CALLOUT_KIND.items() if label.startswith(k)), "example")


def class_names(el):
    """Classes de l'élément `el`, sous forme de liste."""
    cls = el.get("class") or []
    return cls.split() if isinstance(cls, str) else cls


def is_card(el):
    """Vrai pour un encadré propre à un système (div.card)."""
    return class_names(el)[:1] == ["card"]


def parse(md_text):
    """Arbre HTML du Markdown."""
    # python-markdown attend 4 espaces pour les listes imbriquées.
    md_text = re.sub(r"(?m)^ {2,3}(?=(?:[-*]|\d+\.) )", "    ", md_text)
    return BeautifulSoup(markdown.markdown(md_text, extensions=["tables", "sane_lists"]),
                         "html.parser")


def take_title(soup):
    """Retire le titre et la ligne d'auteur, qui passent sur la couverture ; renvoie le titre."""
    h1 = soup.find("h1")
    if h1 is None:
        raise SourceError("le document doit commencer par un titre « # … »")
    # Seul un paragraphe entièrement en italique, juste sous le titre, est une ligne d'auteur.
    byline = h1.find_next_sibling()
    if byline is not None and byline.name == "p":
        parts = [c for c in byline.contents if str(c).strip()]
        if len(parts) == 1 and getattr(parts[0], "name", None) == "em":
            byline.decompose()
    title = clean(h1.get_text())
    h1.decompose()
    return title


def number_headings(soup, fiche):
    """Numérote les chapitres (« 02 ») et les parties (« 2.1 ») ; renvoie le sommaire."""
    toc, chap, sec = [], 0, 0
    for h in soup.find_all(["h2", "h3", "h4"]):
        text = clean(h.get_text())
        m = OS_HEADING.match(text)
        if m and h.name != "h2":
            h["data-kind"] = OS_KIND.get(m.group(1), "univ")
        if h.name == "h4":
            h.string = text
            continue
        if h.name == "h2":
            chap, sec = chap + 1, 0
            num, hid = f"{chap:02d}", f"ch{chap}"
        else:
            sec += 1
            num, hid = f"{chap}.{sec}", f"s{chap}-{sec}"
        h.clear()
        h["id"] = hid
        if not fiche:  # les fiches ne sont pas numérotées
            h.append(tag(soup, "span", "num", num))
            h.append(" ")  # espace pour les signets du PDF
        h.append(tag(soup, "span", "t", text))
        toc.append((h.name, num, text, hid))
    return toc


def split_chapters(soup, title):
    """Un <section> par chapitre ; un contenu placé avant le premier titre forme une introduction
    sans titre. Renvoie l'élément <main> et la liste des chapitres."""
    content = tag(soup, "main")
    current = None
    for node in list(soup.contents):
        name = getattr(node, "name", None)
        if name == "h2" or (current is None and name):
            current = tag(soup, "section", "chapter")
            # en-tête de page
            current["data-title"] = (fr_typo(node.find("span", class_="t").get_text())
                                     if name == "h2" else title)
            content.append(current)
        if current is not None:
            current.append(node.extract())
        else:
            node.extract()
    return content, content.find_all("section", recursive=False)


def mark_chapters(chapters, fiche):
    """Les chapitres s'enchaînent, sauf les annexes qui commencent sur une nouvelle page ;
    la liste de vérification n'est jamais coupée entre deux pages. Dans une fiche, le premier
    chapitre suit directement le bandeau-titre."""
    for ch in chapters if fiche else chapters[1:]:
        annex = ch["data-title"].startswith("Annexe")
        keep = ch.find("ul", class_="checklist") is not None
        ch["class"] = "chapter" if annex else "chapter flow keep" if keep else "chapter flow"
    if not fiche and chapters:
        for p in chapters[0].find_all("p", recursive=False):
            p["class"] = "lead"


def mark_tables(content):
    """Tableaux : comparatif (3 colonnes ou plus) et longs tableaux autorisés à continuer
    sur la page suivante."""
    for table in content.find_all("table"):
        classes = []
        if len(table.find_all("th")) >= 3:
            classes.append("compare")
        if len(table.select("tbody > tr")) > 12:
            classes.append("long")
        if classes:
            table["class"] = classes


def wrap_cards(soup, content):
    """Encadrés par système : le titre et son contenu jusqu'au titre suivant."""
    for h in content.find_all(["h3", "h4"], attrs={"data-kind": True}):
        card = tag(soup, "div", f"card {h['data-kind']}")
        h.insert_before(card)
        sib = h
        while sib is not None:
            nxt = sib.find_next_sibling()
            card.append(sib.extract())
            sib = nxt if nxt is not None and nxt.name not in CARD_END else None
        h["class"] = "card-title"


def split_callouts(soup, content):
    """python-markdown fusionne des citations consécutives : on les sépare à chaque libellé."""
    pending = content.find_all("blockquote")
    while pending:
        bq = pending.pop()
        for el in bq.find_all("p", recursive=False)[1:]:
            lead = leading_strong(el)
            if lead is not None and lead.get_text().startswith(tuple(CALLOUT_KIND)):
                split = tag(soup, "blockquote")
                bq.insert_after(split)
                sib = el
                while sib is not None:
                    nxt = sib.find_next_sibling()
                    split.append(sib.extract())
                    sib = nxt
                pending.append(split)  # elle peut contenir encore d'autres encadrés
                break


def style_callouts(soup, content):
    """Citations -> encadrés colorés d'après leur libellé (Exemple, Solution, Attention…).
    Une citation sans libellé en gras forme un encadré bleu sans titre."""
    for bq in content.find_all("blockquote"):
        lead = leading_strong(bq.find(True, recursive=False))
        if lead is None:
            bq["class"] = "callout example"
            continue
        label = lead.get_text().rstrip(" :\u00a0")
        bq["class"] = "callout " + callout_kind(label)
        para = lead.parent
        lead.extract()
        first = para.contents[0] if para.contents else None
        if isinstance(first, NavigableString):
            rest = first.lstrip()
            first.replace_with(rest[:1].upper() + rest[1:])
        if not para.get_text(strip=True):
            para.decompose()
        bq.insert(0, tag(soup, "div", "callout-label", label))


def style_menus_and_keys(soup, content):
    """Chemins de menus (« A > B ») et raccourcis clavier (« Ctrl + C »)."""
    for s in content.find_all("strong"):
        text = s.get_text()
        if " > " in text:
            s.clear()
            s["class"] = "path"
            for i, part in enumerate(text.split(" > ")):
                if i:
                    s.append(tag(soup, "span", "sep", "›"))
                s.append(part)
        elif KEYS.fullmatch(text):
            keys = tag(soup, "span", "keys")
            for i, k in enumerate(text.split(" + ")):
                if i:
                    keys.append(tag(soup, "span", "plus", "+"))
                keys.append(tag(soup, "kbd", text=k))
            s.replace_with(keys)


def style_lists(soup, content):
    """Liste de vérification (cases à cocher) et étapes numérotées."""
    for li in content.find_all("li"):
        first = li.contents[0] if li.contents else None
        if isinstance(first, NavigableString) and first.startswith("[ ] "):
            first.replace_with(first[4:])
            li.parent["class"] = "checklist"
    for ol in content.find_all("ol"):
        if ol.find_parent("blockquote") is None:
            # Une procédure courte ne doit pas être coupée entre deux pages.
            ol["class"] = "steps short" if len(ol.find_all("li", recursive=False)) <= 6 else "steps"
    checklist = content.find("ul", class_="checklist")
    if checklist is not None:
        stamp = tag(soup, "p", "check-date", "Date de la dernière vérification :\u00a0")
        stamp.append(tag(soup, "span", "line"))
        checklist.insert_after(stamp)


def group_blocks(soup, chapters):
    """Chaque titre forme avec son contenu (jusqu'au titre suivant) un bloc jamais coupé entre
    deux pages : chaque page commence ainsi par un titre. Un encadré système, qui porte son
    propre titre, forme aussi un bloc."""
    for ch in chapters:
        groups = []
        for el in [c for c in ch.contents if getattr(c, "name", None)]:
            if el.name in ("h2", "h3", "h4") or is_card(el) or not groups:
                groups.append([])
            groups[-1].append(el)
        for i, group in enumerate(groups):
            block = tag(soup, "div", "block")
            group[0].insert_before(block)
            for el in group:
                block.append(el.extract())
            # Titre suivi d'une courte introduction : il reste avec le bloc suivant.
            lead_in = group[0].name in ("h2", "h3") and len(block.get_text()) < 600
            if block.find("table", class_="long"):
                block["class"] = "block free"  # plus long qu'une page : il continue sur la suivante
            elif lead_in and i + 1 < len(groups):
                block["class"] = "block lead-in"


def apply_typo(content):
    """Typographie française sur tout le texte, sauf le code et les touches de clavier."""
    for node in content.find_all(string=True):
        if node.find_parent(["code", "kbd"]) is None:
            node.replace_with(fr_typo(str(node)))


def colophon(soup, title, fiche):
    """Mention finale : en bas de la dernière page d'une fiche, sur la quatrième de couverture
    du guide."""
    box = tag(soup, "div", "colophon")
    if fiche:
        box.append(tag(soup, "p", text=fr_typo(
            f"{AUTHOR} — {title}, fiche pratique extraite du guide « {GUIDE_TITLE} », "
            f"version {VERSION} ({EDITION}), {date_label(RELEASE_DATE).lower()}.")))
    box.append(tag(soup, "p", text=fr_typo(
        LICENSE_NOTE.format(doc="cette fiche" if fiche else "ce guide"))))
    if SITE_URL:
        latest = tag(soup, "p", text=fr_typo("Dernière version du guide et des fiches : "))
        latest.append(tag(soup, "a", text=SITE_URL, href=SITE_URL))
        box.append(latest)
    contact = tag(soup, "p", text=fr_typo("Une erreur, une suggestion ? Écrivez à "))
    contact.append(tag(soup, "a", text=CONTACT, href=f"mailto:{CONTACT}"))
    contact.append(".")
    box.append(contact)
    box.append(tag(soup, "p", text=fr_typo(
        ("Cette fiche est fournie" if fiche else "Ce guide est fourni") + " à titre informatif. "
        "Les intitulés des menus peuvent varier selon la version et la langue de votre système "
        "d’exploitation.")))
    return box


def shield(cx, cy, w, h):
    """Tracé SVG d'un bouclier centré sur (cx, cy)."""
    t, l, r = cy - h / 2, cx - w / 2, cx + w / 2
    return (f"M{cx:.1f},{t:.1f} L{r:.1f},{t + h * .14:.1f} V{t + h * .47:.1f} "
            f"C{r:.1f},{t + h * .74:.1f} {cx + w * .2:.1f},{t + h * .9:.1f} {cx:.1f},{t + h:.1f} "
            f"C{cx - w * .2:.1f},{t + h * .9:.1f} {l:.1f},{t + h * .74:.1f} "
            f"{l:.1f},{t + h * .47:.1f} V{t + h * .14:.1f} Z")


def cover_art():
    """Bouclier et anneaux de la couverture."""
    rings = "".join(
        f'<path d="{shield(200, 240, 330 * s, 400 * s)}" fill="none" stroke="#5FD0D9" '
        f'stroke-width="{1.4 if k else 2.2}" stroke-opacity="{0.55 - k * 0.08:.2f}"/>'
        for k, s in enumerate((1, .86, .72, .58)))
    return f"""<svg class="art" viewBox="0 0 400 480" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2BB3BF"/><stop offset="1" stop-color="#127C88"/></linearGradient></defs>
  {rings}
  <path d="{shield(200, 240, 330 * .44, 400 * .44)}" fill="url(#g)"/>
  <circle cx="200" cy="222" r="20" fill="#0B2545"/>
  <path d="M190,234 L183,282 H217 L210,234 Z" fill="#0B2545"/>
</svg>"""


def dot_grid():
    """Trame de points, en fond de la couverture et de la quatrième de couverture."""
    dots = "".join(f'<circle cx="{x * 7 + 3.5}" cy="{y * 7 + 3.5}" r=".45"/>'
                   for x in range(30) for y in range(43))
    return ('<svg class="dots" viewBox="0 0 210 297" xmlns="http://www.w3.org/2000/svg" '
            f'fill="#FFFFFF" fill-opacity=".07">{dots}</svg>')


def chips(*labels):
    """Pastilles de la légende du sommaire, aux couleurs des encadrés."""
    kinds = {**OS_KIND, **CALLOUT_KIND}
    return "".join(f'<span class="chip {kinds[label]}">{label}</span>' for label in labels)


def guide_front(title, subtitle, toc):
    """Couverture et sommaire du guide."""
    toc_items = "".join(
        f'<li class="{"l2" if lvl == "h2" else "l3"}"><a href="#{hid}">'
        f'<span class="n">{num}</span><span class="t">{fr_typo(text)}</span></a></li>'
        for lvl, num, text, hid in toc)
    return f"""<section class="cover">
  {dot_grid()}
  {cover_art()}
  <div class="kicker">Guide pratique · Sécurité informatique</div>
  <div class="cover-main">
    <h1>{title}</h1>
    <div class="bar"></div>
    <p class="subtitle">{subtitle}</p>
  </div>
  <div class="cover-foot">
    <div class="topics">{TOPICS}</div>
    <div class="author">{AUTHOR}</div>
    <div class="date">{date_label(RELEASE_DATE)} · Version {VERSION}</div>
  </div>
</section>
<section class="toc">
  <div class="toc-title">Sommaire</div>
  <ul class="toc-list">{toc_items}</ul>
  <div class="legend">
    <div class="legend-title">Repères</div>
    <p>{chips("Windows", "macOS", "Linux")}
       Instructions propres à chaque système</p>
    <p>{chips("Exemple", "Solution", "Attention")}
       Mises en situation et points de vigilance</p>
  </div>
</section>"""


def back_cover(title, box):
    """Quatrième de couverture du guide, avec la mention finale `box`."""
    return f"""<section class="back">
  {dot_grid()}
  <div class="back-foot">
    <div class="title">{title}</div>
    <div class="edition">{AUTHOR} · Version {VERSION}, {EDITION} · {date_label(RELEASE_DATE)}</div>
    {box}
  </div>
</section>"""


def fiche_head(title, subtitle):
    """Bandeau-titre d'une fiche."""
    meta = (f"{AUTHOR} · {date_label(RELEASE_DATE)} · Version {VERSION} · "
            + fr_typo(f"Extrait du guide « {GUIDE_TITLE} »"))
    return f"""<header class="fiche-head">
  <div class="kicker">Fiche pratique · Sécurité informatique</div>
  <h1>{title}</h1>
  <p class="subtitle">{fr_typo(subtitle)}</p>
  <div class="meta">{meta}</div>
</header>"""


def fiche_page_style(title):
    """En-têtes de page d'une fiche : le titre de la fiche, sauf sur la première page."""
    return f"""<style>
@page {{ @top-left {{ content: "Fiche pratique · {title}"; }} }}
{FICHE_FIRST_PAGE}
</style>"""


def structure(md_text, fiche=False):
    """Arbre HTML du Markdown, avec la mise en forme commune au PDF et au site : titres numérotés,
    chapitres, encadrés, chemins de menus, touches, listes et typographie."""
    soup = parse(md_text)
    title = take_title(soup)
    for hr in soup.find_all("hr"):
        hr.decompose()
    toc = number_headings(soup, fiche)
    content, chapters = split_chapters(soup, title)
    mark_tables(content)
    wrap_cards(soup, content)
    split_callouts(soup, content)
    style_callouts(soup, content)
    style_menus_and_keys(soup, content)
    style_lists(soup, content)
    apply_typo(content)
    return Document(soup, title, toc, content, chapters)


def render_html(md_text, fiche=False, subtitle=None):
    """Page HTML complète du document, prête pour WeasyPrint."""
    subtitle = subtitle or GUIDE_SUBTITLE
    soup, title, toc, content, chapters = structure(md_text, fiche)
    mark_chapters(chapters, fiche)
    group_blocks(soup, chapters)
    box = colophon(soup, title, fiche)
    if fiche:
        (chapters[-1] if chapters else content).append(box)
        front, back, page_style = fiche_head(title, subtitle), "", fiche_page_style(title)
    else:
        front, back, page_style = guide_front(title, subtitle, toc), back_cover(title, box), ""
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>{title}</title>
<meta name="author" content="{AUTHOR}">
<meta name="description" content="{title} — {subtitle}">
<meta name="keywords" content="{KEYWORDS}">
<meta name="dcterms.created" content="{RELEASE_DATE.isoformat()}">
<meta name="dcterms.rights" content="CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/">
<link rel="stylesheet" href="style.css">
{page_style}
</head><body class="{'fiche' if fiche else 'guide'}">
{front}
{content}
{back}
</body></html>"""


def paginate(page):
    """Mise en pages de la page HTML `page` par WeasyPrint, prête à être écrite en PDF."""
    # style.css et rule.svg sont résolus depuis le dossier build/.
    return HTML(string=page, base_url=(BUILD_DIR / "style.css").as_uri()).render(**PDF_OPTIONS)


def page_count(md_text):
    """Nombre de pages du PDF du guide `md_text`, annoncé sur le site."""
    return len(paginate(render_html(md_text)).pages)


def build(md_text, out, *, fiche=False, subtitle=None, html_out=None):
    """Génère le PDF `out` et, si demandé, le HTML intermédiaire `html_out`."""
    page = render_html(md_text, fiche, subtitle)
    if html_out:
        html_out.write_text(page, encoding="utf-8")
    paginate(page).write_pdf(out, **PDF_OPTIONS)
    print(f"{out} ({out.stat().st_size // 1024} Ko)")


def main(argv=None):
    """Point d'entrée en ligne de commande."""
    parser = argparse.ArgumentParser(description="Génère le PDF du guide à partir du Markdown.")
    parser.add_argument("src", nargs="?", type=Path, default=GUIDE_MD)
    parser.add_argument("out", nargs="?", type=Path,
                        help="PDF de sortie (par défaut : à côté du Markdown)")
    parser.add_argument("--html", type=Path,
                        help="enregistre aussi le HTML intermédiaire (pour déboguer)")
    parser.add_argument("--fiche", action="store_true", help="mise en page d'une fiche pratique")
    parser.add_argument("--subtitle",
                        help="sous-titre (couverture du guide ou bandeau de la fiche)")
    args = parser.parse_args(argv)
    try:
        build(args.src.read_text(encoding="utf-8"), args.out or args.src.with_suffix(".pdf"),
              fiche=args.fiche, subtitle=args.subtitle, html_out=args.html)
    except SourceError as err:
        sys.exit(f"{args.src} : {err}")


if __name__ == "__main__":
    main()
