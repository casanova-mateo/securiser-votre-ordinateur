"""Génère le site web du guide à partir du Markdown (publié tel quel par GitHub Pages).

Usage : python build_site.py [guide.md] [--out-dir dossier]
Par défaut, le site est écrit dans le dossier du guide :
- index.html : l'accueil (gabarit accueil.html) ;
- guide/index.html : le sommaire ;
- guide/<adresse>/index.html : une page par chapitre, ou par partie pour les chapitres de SPLIT ;
- 404.html : la page affichée pour une adresse inconnue ;
- sitemap.xml : le plan du site, pour les moteurs de recherche.
Les pages du guide, le sommaire et la page 404 suivent le gabarit page.html. site.css et
site.js, à la racine du guide, sont écrits à la main.
"""
import argparse
import base64
import contextlib
import hashlib
import html
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from urllib.parse import quote, urlsplit

from bs4 import Tag

import build_pdf
from build_pdf import AUTHOR, CONTACT, GUIDE_TITLE, SITE_URL, SourceError, fr_typo, tag

HOME_TEMPLATE = build_pdf.BUILD_DIR / "accueil.html"
PAGE_TEMPLATE = build_pdf.BUILD_DIR / "page.html"
GUIDE_DIR = "guide"
GUIDE_PDF = build_pdf.GUIDE_MD.with_suffix(".pdf").name
REPO_URL = "https://github.com/casanova-mateo/securiser-votre-ordinateur"
HOST = "GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis"
GENERATED = "Généré par build/build_site.py à partir de {source} : ne modifiez pas ce fichier."
# Script placé en tête des pages du guide, exécuté avant leur premier affichage : il signale que
# JavaScript est actif, pour que le choix du système (site.js) s'affiche d'emblée, sans décaler
# la page une fois chargée.
EARLY_JS = 'document.documentElement.classList.add("js");'
# Politique de sécurité du contenu (GitHub Pages ne permet pas de l'envoyer en en-tête HTTP) :
# une page ne charge que les fichiers du site, et n'exécute que site.js et EARLY_JS, autorisé
# par son empreinte. Aucun style ni script écrit dans la page, aucune ressource externe.
CSP = ("default-src 'none'; script-src 'self' '{early}'; style-src 'self'; img-src 'self'; "
       "base-uri 'none'; form-action 'none'")

# Une page par chapitre ; les chapitres de SPLIT, trop longs pour une seule page, ont une page
# par partie.
SPLIT = ("Les bases",)
# Adresse (dossier sous guide/) et nom court (menu, liens précédent et suivant) de chaque page,
# d'après le titre de son chapitre ou de sa partie, sans emoji. Ces adresses sont partagées et
# imprimées : ne les changez jamais, même quand le titre change.
PAGES = {
    "Pourquoi sécuriser votre ordinateur ?":
        ("pourquoi-securiser", "Pourquoi sécuriser votre ordinateur ?"),
    "Gardez votre système et vos logiciels à jour": ("mises-a-jour", "Mises à jour"),
    "Utilisez l’antivirus intégré": ("antivirus", "Antivirus"),
    "Sécurisez vos mots de passe et vos accès": ("mots-de-passe", "Mots de passe et accès"),
    "Activez le chiffrement complet du disque": ("chiffrement", "Chiffrement du disque"),
    "Maîtrisez vos comptes en ligne (Microsoft, iCloud)": ("comptes-en-ligne", "Comptes en ligne"),
    "Sécurisez votre navigation sur le web": ("navigation", "Navigation sur le web"),
    "Sécurisez votre réseau": ("reseau", "Réseau et Wi-Fi"),
    "Sauvegardez vos données": ("sauvegardes", "Sauvegardes"),
    "Protégez aussi votre smartphone": ("smartphone", "Smartphone"),
    "Linux, une alternative gratuite et sûre":
        ("linux", "Linux, une alternative gratuite et sûre"),
    "Bonnes pratiques au quotidien": ("bonnes-pratiques", "Bonnes pratiques au quotidien"),
    "Que faire en cas de problème ?": ("en-cas-de-probleme", "Que faire en cas de problème ?"),
    "Récapitulatif : liste de vérification": ("liste-de-verification", "Liste de vérification"),
    "Annexe : correspondance avec les 42 mesures de l’ANSSI":
        ("annexe-anssi", "Annexe : les 42 mesures de l’ANSSI"),
}
# Page signalée en haut de chaque page, pour les victimes d'une attaque.
HELP_PAGE = "en-cas-de-probleme"
# Renvois écrits en toutes lettres, reliés à la page qu'ils désignent. Les renvois numérotés
# (« voir 2.3 ») sont reliés automatiquement.
NAMED_REFS = {"la partie Linux": "linux", "la partie sur les sauvegardes": "sauvegardes",
              "l’annexe": "annexe-anssi"}
# Encadré du guide dont l'accueil reprend la liste, chaque point relié à sa page.
PRIORITIES = "Par où commencer"
OS_NAMES = {kind: name for name, kind in build_pdf.OS_KIND.items()}
HEADING = re.compile(r"^h[1-6]$")
# Un renvoi n'est pas relié dans un lien, du code, une touche ou un titre.
NO_REFS = ("a", "code", "kbd", "h1", "h2", "h3", "h4", "h5", "h6")
PRIORITY_REF = re.compile(r"\s*\(voir (\d+\.\d+)[^)]*\)\s*$")
PAGE_ROOT = "../../"  # racine du site, vue depuis une page du guide (guide/<adresse>/)
# Ancres des éléments ajoutés à chaque page (lien d'évitement, liste des sous-parties) : une
# sous-partie ne peut pas les prendre.
RESERVED_IDS = ("contenu", "sur-cette-page")
DESCRIPTION_MAX = 160  # longueur d'une description affichée en entier par les moteurs de recherche
ON_PAGE_MIN = 3  # nombre de sous-parties à partir duquel une page en affiche la liste


@dataclass
class Page:
    """Une page du guide : un chapitre, ou une partie d'un chapitre de SPLIT."""
    slug: str
    label: str  # nom court
    num: str  # numéro du chapitre (« 03 ») ou de la partie (« 2.3 »)
    title: str  # titre complet, sans emoji
    chapter: str  # titre du chapitre d'une partie ; vide pour un chapitre
    article: Tag  # contenu, qui commence par le titre de la page
    description: str = ""

    @property
    def path(self):
        """Adresse de la page, relative à la racine du site."""
        return f"{GUIDE_DIR}/{self.slug}/"

    @property
    def anchor(self):
        """Ancre du titre de la page."""
        return self.article.find(HEADING)["id"]


@dataclass
class Chapter:
    """Un chapitre du guide et sa page, ou ses pages pour un chapitre de SPLIT."""
    num: str
    title: str
    pages: list = field(default_factory=list)


@dataclass
class Site:
    """Les pages du guide, dans l'ordre, et de quoi retrouver la page de chaque titre."""
    chapters: list
    pages: list
    toc: list  # sommaire du guide : (niveau, numéro, texte, ancre)
    anchors: dict  # ancre d'un titre -> page qui le contient


def esc(text):
    """Texte prêt à être inséré dans le HTML, avec la typographie française."""
    return html.escape(fr_typo(text))


def slugify(text):
    """Identifiant lisible dans une adresse : « L’entropie (2) » -> « l-entropie-2 »."""
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fill(template, source, **values):
    """Le gabarit `template` complété par `values`, avec la mention de fichier généré."""
    text = Template(template.read_text(encoding="utf-8"))
    return text.substitute(generated=GENERATED.format(source=source), **values)


# ---------- Découpage du guide en pages ----------

def name_subsections(content):
    """Ancre lisible pour chaque sous-partie (titre « #### »), sauf les encadrés système."""
    used = {el["id"] for el in content.find_all(id=True)} | set(RESERVED_IDS)
    for h in content.find_all("h4"):
        if h.has_attr("id") or h.has_attr("data-kind"):
            continue
        base = slugify(h.get_text()) or "partie"
        anchor, n = base, 2
        while anchor in used:
            anchor, n = f"{base}-{n}", n + 1
        h["id"] = anchor
        used.add(anchor)


def parts(elements, title):
    """Les parties d'un chapitre de SPLIT : chaque titre « ### » avec son contenu."""
    body = elements[1:]
    if not body or body[0].name != "h3":
        raise SourceError(f"le chapitre « {title} » a une page par partie (SPLIT, build_site.py) : "
                          "il doit commencer directement par un titre « ### »")
    groups = []
    for el in body:
        if el.name == "h3":
            groups.append([])
        groups[-1].append(el)
    return groups


def new_page(soup, elements, titles, unused, chapter):
    """Page des éléments `elements`, qui commencent par son titre. Son adresse est prise dans
    `unused`, les entrées de PAGES pas encore attribuées."""
    num, title = titles[elements[0]["id"]]
    if title not in unused:
        raise SourceError(f"« {title} » n'a pas d'adresse : ajoutez-la dans PAGES "
                          "(build_site.py)")
    slug, label = unused.pop(title)
    article = tag(soup, "article", "prose")
    for el in elements:
        article.append(el.extract())
    return Page(slug, label, num, title, chapter, article)


def split_pages(doc):
    """Répartit les chapitres du document en pages, d'après SPLIT et PAGES ; renvoie les chapitres
    et les pages, dans l'ordre du guide."""
    titles = {hid: (num, text) for _, num, text, hid in doc.toc}
    unused = dict(PAGES)
    chapters = []
    for section in doc.chapters:
        elements = [el for el in section.contents if isinstance(el, Tag)]
        if not elements or elements[0].name != "h2":
            raise SourceError("le site attend un titre de chapitre « ## » avant tout texte")
        chapter = Chapter(*titles[elements[0]["id"]])
        if chapter.title in SPLIT:
            chapter.pages = [new_page(doc.soup, group, titles, unused, chapter.title)
                             for group in parts(elements, chapter.title)]
        else:
            chapter.pages = [new_page(doc.soup, elements, titles, unused, "")]
        chapters.append(chapter)
    if unused:
        raise SourceError(f"titre introuvable dans le guide : « {next(iter(unused))} » "
                          "(PAGES, build_site.py)")
    return chapters, [page for chapter in chapters for page in chapter.pages]


def href(page, anchor, root, current=None):
    """Adresse de la page `page`, ou de son titre `anchor`, depuis la page `current`."""
    if page is current:
        return f"#{anchor}"
    url = root + page.path
    return url if anchor in (None, page.anchor) else f"{url}#{anchor}"


def reference_targets(site):
    """Texte de chaque renvoi -> (page, ancre) : numéros des parties, puis NAMED_REFS."""
    by_slug = {page.slug: page for page in site.pages}
    targets = {num: (site.anchors[hid], hid) for level, num, _, hid in site.toc if level == "h3"}
    targets.update({text: (by_slug[slug], None) for text, slug in NAMED_REFS.items()
                    if slug in by_slug})
    return targets


def link_references(soup, page, targets):
    """Renvois du texte (« voir 2.3 », « la partie Linux ») -> liens vers la page désignée."""
    keys = "|".join(re.escape(key) for key in sorted(targets, key=len, reverse=True))
    pattern = re.compile(rf"(?<![\w.])(?:{keys})(?!\w|\.\d)")
    for node in page.article.find_all(string=pattern):
        if node.find_parent(NO_REFS) is not None:
            continue
        text, pos, pieces = str(node), 0, []
        for m in pattern.finditer(text):
            target, anchor = targets[m.group()]
            if target is page and anchor in (None, page.anchor):
                continue  # renvoi vers la page elle-même
            if m.start() > pos:
                pieces.append(text[pos:m.start()])
            pieces.append(tag(soup, "a", text=m.group(),
                              href=href(target, anchor, PAGE_ROOT, page)))
            pos = m.end()
        if pieces:
            if pos < len(text):
                pieces.append(text[pos:])
            node.replace_with(*pieces)


# ---------- Mise en forme web d'une page ----------

def promote_headings(article):
    """Le titre de la page devient <h1>, et chaque sous-titre se place juste un niveau sous son
    titre parent, sans niveau sauté : un « #### » directement sous un « ## » devient <h2>."""
    parents = []  # (niveau dans le Markdown, niveau dans la page) des titres englobants
    for h in article.find_all(HEADING):
        level = int(h.name[1])
        while parents and parents[-1][0] >= level:
            parents.pop()
        new_level = parents[-1][1] + 1 if parents else 1
        parents.append((level, new_level))
        h.name = f"h{new_level}"


def describe(article, title):
    """Description de la page pour les moteurs de recherche et les partages : le début de son
    premier paragraphe, sinon son titre."""
    p = article.find("p", recursive=False)
    if p is None:
        return fr_typo(f"{title} — {GUIDE_TITLE} : guide pratique gratuit pour Windows, macOS "
                       "et Linux.")
    text = re.sub(r"[ \t\n]+", " ", p.get_text()).strip()  # garde les espaces insécables
    if len(text) <= DESCRIPTION_MAX:
        return text
    return text[:DESCRIPTION_MAX - 1].rsplit(" ", 1)[0].rstrip(",;:\u00a0") + "…"


def foldable_cards(soup, article):
    """Encadrés propres à un système : leur contenu est regroupé, pour que site.js puisse le
    replier quand le lecteur a choisi un autre système. Le titre reste un vrai titre (site.js y
    ajoute un bouton), que les lecteurs d'écran retrouvent dans la liste des titres."""
    for n, card in enumerate(article.select("div.card"), 1):
        title = card.find(class_="card-title")
        del title["data-kind"]  # sert au PDF ; la classe de l'encadré suffit ici
        kind = build_pdf.class_names(card)[1]
        if kind in OS_NAMES:
            card["data-os"] = kind
            body = tag(soup, "div", "card-body", id=f"encadre-{n}")
            for el in title.find_next_siblings():
                body.append(el.extract())
            card.append(body)


def checkboxes(soup, article):
    """Liste de vérification -> vraies cases à cocher, que site.js retient d'une visite à
    l'autre."""
    for n, li in enumerate(article.select("ul.checklist > li"), 1):
        label = tag(soup, "label", **{"for": f"case-{n}"})
        for child in list(li.contents):
            label.append(child.extract())
        li.append(tag(soup, "input", type="checkbox", id=f"case-{n}"))
        li.append(label)
    for checklist in article.select("ul.checklist"):
        tools = tag(soup, "div", "check-tools", hidden="")
        tools.append(tag(soup, "p", "check-progress", **{"aria-live": "polite"}))
        tools.append(tag(soup, "button", "btn btn-small", "Tout décocher", type="button"))
        tools.append(tag(soup, "p", "check-note", fr_typo(
            "Les cases cochées sont enregistrées dans ce navigateur, sur cet appareil "
            "uniquement.")))
        checklist.insert_after(tools)


def label_tables(soup, article):
    """Chaque tableau a pour titre celui de sa partie ; un tableau comparatif défile
    horizontalement sur un écran étroit."""
    for table in article.find_all("table"):
        heading = table.find_previous(HEADING)
        if heading.has_attr("id"):  # un titre d'encadré système n'a pas d'ancre
            table["aria-labelledby"] = heading["id"]
        if "compare" in build_pdf.class_names(table):
            title = (heading.find(class_="t") or heading).get_text()
            table.wrap(tag(soup, "div", "table-scroll", role="region", tabindex="0",
                           **{"aria-label": f"Tableau : {title}"}))


def break_menu_paths(soup, article):
    """Chemins de menus (« Réglages › Confidentialité ») : une coupure de ligne possible après
    chaque flèche, sans quoi un long chemin déborde sur un petit écran."""
    for sep in article.select(".path .sep"):
        sep.insert_after(soup.new_tag("wbr"))


def os_filter(soup, article):
    """Choix du système, en tête d'une page qui a des encadrés système ; site.js l'affiche."""
    if not article.select(".card[data-os]"):
        return None
    fieldset = tag(soup, "fieldset", "os-filter")  # masqué sans JavaScript (site.css)
    fieldset.append(tag(soup, "legend", text="Afficher les instructions pour"))
    options = tag(soup, "div", "os-options")
    for value, name in (("all", "Tous les systèmes"), *OS_NAMES.items()):
        radio = tag(soup, "input", type="radio", value=value)
        radio["name"] = "systeme"  # « name » est déjà le nom de l'élément pour tag()
        if value == "all":
            radio["checked"] = ""
        label = tag(soup, "label")
        label.append(radio)
        label.append(tag(soup, "span", text=name))
        options.append(label)
    fieldset.append(options)
    return fieldset


def on_this_page(soup, article):
    """Liste des sous-parties d'une longue page, en tête de page."""
    headings = [h for h in article.find_all("h2") if h.has_attr("id")]
    if len(headings) < ON_PAGE_MIN:
        return None
    box = tag(soup, "nav", "on-page", **{"aria-labelledby": "sur-cette-page"})
    box.append(tag(soup, "p", "on-page-title", "Sur cette page", id="sur-cette-page"))
    items = tag(soup, "ul", "on-page-list")
    for h in headings:
        item = tag(soup, "li")
        item.append(tag(soup, "a", text=h.get_text(), href=f"#{h['id']}"))
        items.append(item)
    box.append(items)
    return box


def shape_page(soup, page):
    """Mise en forme web d'une page : titres, encadrés repliables, cases à cocher, tableaux,
    chemins de menus, puis liste des sous-parties et choix du système en tête de page."""
    article = page.article
    promote_headings(article)
    page.description = describe(article, page.title)
    top = article.h1
    first = top.find_next_sibling()
    if first is not None and first.name == "p":
        first["class"] = "lead"
        top = first
    foldable_cards(soup, article)
    checkboxes(soup, article)
    label_tables(soup, article)
    break_menu_paths(soup, article)
    # Chacun est inséré juste après `top` : le dernier de la liste apparaît en premier.
    for tool in (os_filter(soup, article), on_this_page(soup, article)):
        if tool is not None:
            top.insert_after(tool)
    if page.chapter:
        article.insert(0, tag(soup, "p", "kicker", fr_typo(page.chapter)))


def guide_pages(md_text):
    """Le guide découpé en pages, mises en forme pour le web."""
    doc = build_pdf.structure(md_text)
    name_subsections(doc.content)
    chapters, pages = split_pages(doc)
    anchors = {el["id"]: page for page in pages for el in page.article.find_all(id=True)}
    site = Site(chapters, pages, doc.toc, anchors)
    targets = reference_targets(site)
    for page in pages:
        link_references(doc.soup, page, targets)
        shape_page(doc.soup, page)
    return site


# ---------- Éléments communs aux pages ----------

def csp():
    """Politique de sécurité du contenu (CSP), avec l'empreinte du script EARLY_JS."""
    digest = base64.b64encode(hashlib.sha256(EARLY_JS.encode()).digest()).decode()
    return CSP.format(early=f"sha256-{digest}")


def asset(root, name):
    """Adresse d'un fichier écrit à la main (site.css, site.js), suivie d'une empreinte de son
    contenu : les navigateurs rechargent le fichier dès qu'il change."""
    digest = hashlib.sha256((build_pdf.ROOT / name).read_bytes()).hexdigest()[:10]
    return f"{root}{name}?v={digest}"


def footer(wide=False):
    """Pied de page, commun à l'accueil et aux pages du guide."""
    day = build_pdf.date_label(build_pdf.RELEASE_DATE).lower()
    edition = f"{GUIDE_TITLE}, version {build_pdf.VERSION} ({build_pdf.EDITION}), {day}."
    subject = quote(f"Guide « {GUIDE_TITLE} »")
    disclaimer = ("Ce guide est un travail personnel, indépendant de l’ANSSI et de "
                  "Cybermalveillance.gouv.fr. Il est fourni à titre informatif ; les intitulés "
                  "des menus peuvent varier selon la version et la langue de votre système "
                  "d’exploitation.")
    privacy = ("Ce site n’utilise ni cookie ni outil de mesure d’audience : le système choisi et "
               "les cases cochées restent dans votre navigateur. "
               f"Éditeur : {AUTHOR}, {CONTACT}. Hébergeur : {HOST}.")
    return f"""<footer class="site-footer">
  <div class="wrap{" wide" if wide else ""}">
    <p><strong>{AUTHOR}</strong> — {esc(edition)}</p>
    <p>{esc("Une erreur, une suggestion ? Écrivez à")}
      <a href="mailto:{CONTACT}?subject={subject}">{CONTACT}</a>.</p>
    <p class="links"><a href="{REPO_URL}">Sources et historique des versions</a></p>
    <p>{esc(disclaimer)}</p>
    <p>{esc(privacy)}</p>
  </div>
</footer>"""


def nav_item(page, root, current):
    """Lien vers une page dans le sommaire latéral."""
    here = ' aria-current="page"' if page is current else ""
    return (f'<li><a href="{root}{page.path}"{here}><span class="n">{page.num}</span>'
            f'<span>{esc(page.label)}</span></a></li>')


def sidebar(site, root, current=None):
    """Sommaire latéral : les chapitres, et les parties des chapitres de SPLIT."""
    items = []
    for chapter in site.chapters:
        if chapter.title in SPLIT:
            links = "".join(nav_item(page, root, current) for page in chapter.pages)
            items.append(f'<li><span class="nav-group"><span class="n">{chapter.num}</span>'
                         f'<span>{esc(chapter.title)}</span></span><ol>{links}</ol></li>')
        else:
            items.append(nav_item(chapter.pages[0], root, current))
    newline = "\n    "
    return f"""<nav class="sidebar" aria-label="Sommaire du guide">
  <p class="sidebar-title"><a href="{root}{GUIDE_DIR}/">Sommaire</a></p>
  <ol class="nav">
    {newline.join(items)}
  </ol>
</nav>"""


def pager(site, page):
    """Liens vers les pages précédente et suivante."""
    i = site.pages.index(page)
    neighbours = (("prev", "Précédent", site.pages[i - 1] if i > 0 else None),
                  ("next", "Suivant", site.pages[i + 1] if i + 1 < len(site.pages) else None))
    links = "".join(
        f'<a class="{rel}" href="{PAGE_ROOT}{other.path}" rel="{rel}"><span class="dir">{label}'
        f'</span><span class="n">{other.num}</span> {esc(other.label)}</a>'
        for rel, label, other in neighbours if other is not None)
    return f'<nav class="pager" aria-label="Pages précédente et suivante">{links}</nav>'


def report(page, pdf_pages):
    """Fin de page : signaler une erreur (e-mail prérempli), télécharger le guide et les
    fiches."""
    subject = f"Guide « {GUIDE_TITLE} », {page.num} {page.label}"
    body = f"Page : {SITE_URL}{page.path}\n\nCorrection proposée : "
    mailto = f"mailto:{CONTACT}?subject={quote(subject)}&body={quote(body)}"
    return f"""<aside class="page-end" aria-label="À propos de cette page">
  <p><a href="{html.escape(mailto)}">Signaler une erreur sur cette page</a></p>
  <p><a href="{PAGE_ROOT}{GUIDE_PDF}">Le guide complet en PDF ({pdf_pages}&nbsp;pages)</a>
    · <a href="{PAGE_ROOT}#fiches">Les fiches à imprimer</a></p>
</aside>"""


def layout(root, meta, content, nav="", current=None):
    """Page complète du site autour du contenu `content` (gabarit PAGE_TEMPLATE), avec le sommaire
    latéral `nav`. `meta` : titre, description et adresse de la page ; sans adresse (page 404),
    la page n'est pas indexée par les moteurs de recherche."""
    title, description, url = meta
    if url:
        indexing = (f'<link rel="canonical" href="{url}">\n'
                    f'<meta property="og:url" content="{url}">')
    else:
        indexing = '<meta name="robots" content="noindex">'
    here = current is not None and current.slug == HELP_PAGE
    return fill(PAGE_TEMPLATE, build_pdf.GUIDE_MD.name, root=root, title=esc(title),
                description=html.escape(description), indexing=indexing,
                csp=csp(), early_js=EARLY_JS,
                css=asset(root, "site.css"), js=asset(root, "site.js"),
                guide=f"{root}{GUIDE_DIR}/", help=f"{root}{GUIDE_DIR}/{HELP_PAGE}/",
                help_current=' aria-current="page"' if here else "",
                layout="wrap wide layout with-nav" if nav else "wrap wide layout",
                content=content, nav=nav, footer=footer(wide=True))


# ---------- Les pages du site ----------

def render_page(site, page, pdf_pages):
    """Page d'un chapitre ou d'une partie."""
    article = page.article.decode(formatter="html5")  # <input>, et non <input/>
    content = f"{article}\n{report(page, pdf_pages)}\n{pager(site, page)}"
    meta = (f"{page.title} — {GUIDE_TITLE}", page.description, SITE_URL + page.path)
    return layout(PAGE_ROOT, meta, content, sidebar(site, PAGE_ROOT, page), page)


def contents_list(site, root):
    """Sommaire complet : chaque chapitre et chaque partie, relié à sa page."""
    chapters = []
    for level, num, text, hid in site.toc:
        page = site.anchors.get(hid)  # pas de page pour le titre d'un chapitre de SPLIT
        title = esc(text) if page is None else f'<a href="{href(page, hid, root)}">{esc(text)}</a>'
        item = f'<span class="n">{num}</span><span class="t">{title}</span>'
        if level == "h2":
            chapters.append((item, []))
        else:
            chapters[-1][1].append(f"<li>{item}</li>")
    return "\n".join(f'<li><div class="chap">{item}</div>'
                     + (f'<ol>{"".join(subs)}</ol>' if subs else "") + "</li>"
                     for item, subs in chapters)


def render_contents(site, pdf_pages):
    """Sommaire du guide (guide/index.html)."""
    root = "../"
    edition = (f"« {GUIDE_TITLE} », chapitre par chapitre. Version {build_pdf.VERSION}, "
               f"{build_pdf.date_label(build_pdf.RELEASE_DATE).lower()}.")
    legend = ("Instructions propres à chaque système : choisissez le vôtre en haut de la page "
              "pour replier les autres.")
    content = f"""<article class="prose contents">
<p class="kicker">Guide pratique · Sécurité informatique</p>
<h1>Sommaire du guide</h1>
<p class="lead">{esc(edition)}</p>
<p class="actions">
  <a class="btn btn-primary" href="{root}{site.pages[0].path}">Commencer la lecture</a>
  <a class="btn btn-outline" href="{root}{GUIDE_PDF}">Le guide en PDF
    <small>({pdf_pages}&nbsp;pages)</small></a>
</p>
<ol class="toc-full">
{contents_list(site, root)}
</ol>
<div class="legend">
  <p class="legend-title">Repères</p>
  <p><span class="chip win">Windows</span><span class="chip mac">macOS</span><span
    class="chip linux">Linux</span> {esc(legend)}</p>
  <p><span class="chip example">Exemple</span><span class="chip solution">Solution</span><span
    class="chip warning">Attention</span> Mises en situation et points de vigilance.</p>
</div>
<p>{esc("Pour garder l’essentiel sous la main :")}
  <a href="{root}#fiches">les trois fiches pratiques à imprimer</a>.</p>
</article>"""
    description = fr_typo(f"Sommaire du guide pratique gratuit « {GUIDE_TITLE} » : mises à jour, "
                          "mots de passe, chiffrement, sauvegardes, réseau, arnaques, et que "
                          "faire en cas de problème.")
    return layout(root, (f"Sommaire — {GUIDE_TITLE}", description, f"{SITE_URL}{GUIDE_DIR}/"),
                  content)


def render_not_found(site):
    """Page affichée par GitHub Pages pour une adresse inconnue, à n'importe quelle profondeur :
    ses liens partent donc de la racine du site."""
    root = urlsplit(SITE_URL).path
    lead = ("Cette adresse ne correspond à aucune page du guide. Elle a peut-être été mal "
            "recopiée : vérifiez-la, ou retrouvez ce que vous cherchez dans le sommaire.")
    content = f"""<article class="prose">
<h1>Page introuvable</h1>
<p class="lead">{esc(lead)}</p>
<p class="actions">
  <a class="btn btn-primary" href="{root}{GUIDE_DIR}/">Sommaire du guide</a>
  <a class="btn btn-outline" href="{root}">{esc("Page d’accueil")}</a>
</p>
<p>{esc("Vous êtes victime en ce moment ?")}
  <a href="{root}{GUIDE_DIR}/{HELP_PAGE}/">Que faire en cas de problème</a>.</p>
</article>"""
    description = fr_typo(f"Page introuvable sur le site du guide « {GUIDE_TITLE} ».")
    return layout(root, (f"Page introuvable — {GUIDE_TITLE}", description, ""), content,
                  sidebar(site, root))


def home_priorities(site):
    """Les priorités de l'encadré PRIORITIES, chacune reliée à la page qui l'explique."""
    labels = [el for page in site.pages for el in page.article.select(".callout-label")
              if el.get_text() == PRIORITIES]
    steps = labels[0].parent.find("ol") if labels else None
    if steps is None:
        raise SourceError(f"encadré « {PRIORITIES} » introuvable, ou sans liste numérotée : "
                          "l'accueil en reprend les priorités")
    numbers = {num: hid for _, num, _, hid in site.toc}
    items = []
    for li in steps.find_all("li", recursive=False):
        text = li.get_text().strip()
        m = PRIORITY_REF.search(text)
        if m is None or m.group(1) not in numbers:
            items.append(f"<li>{html.escape(text)}</li>")
        else:
            hid = numbers[m.group(1)]
            items.append(f'<li><a href="{href(site.anchors[hid], hid, "")}">'
                         f'{html.escape(text[:m.start()])}</a></li>')
    return "\n      ".join(items)


def home_toc(site):
    """Sommaire de l'accueil : les chapitres, et les parties des chapitres de SPLIT."""
    items = []
    for chapter in site.chapters:
        if chapter.title in SPLIT:
            links = " · ".join(f'<a href="{page.path}">{esc(page.label)}</a>'
                               for page in chapter.pages)
            items.append(f'<li><span class="n">{chapter.num}</span><span>{esc(chapter.title)}<br>'
                         f'<span class="parts">{links}</span></span></li>')
        else:
            items.append(f'<li><span class="n">{chapter.num}</span>'
                         f'<a href="{chapter.pages[0].path}">{esc(chapter.title)}</a></li>')
    return "\n      ".join(items)


def render_home(site, pdf_pages):
    """Page d'accueil (index.html), à partir du gabarit HOME_TEMPLATE."""
    return fill(HOME_TEMPLATE, f"build/{HOME_TEMPLATE.name}",
                csp=csp(), css=asset("", "site.css"), version=build_pdf.VERSION,
                date=build_pdf.date_label(build_pdf.RELEASE_DATE).replace(" ", "\u00a0"),
                pdf=GUIDE_PDF, pdf_pages=pdf_pages,
                guide=f"{GUIDE_DIR}/", help=f"{GUIDE_DIR}/{HELP_PAGE}/",
                priorities=home_priorities(site), toc=home_toc(site), footer=footer())


def render_sitemap(site):
    """Plan du site (sitemap.xml) : l'adresse de chaque page, avec la date de la version."""
    day = build_pdf.RELEASE_DATE.isoformat()
    urls = "\n".join(f"  <url><loc>{html.escape(SITE_URL + path)}</loc><lastmod>{day}</lastmod>"
                     "</url>"
                     for path in ("", f"{GUIDE_DIR}/", *(page.path for page in site.pages)))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n")


def render_site(md_text, pdf_pages):
    """Fichiers du site (chemin -> contenu) pour le guide `md_text`, dont le PDF a `pdf_pages`
    pages."""
    site = guide_pages(md_text)
    files = {"index.html": render_home(site, pdf_pages),
             f"{GUIDE_DIR}/index.html": render_contents(site, pdf_pages),
             "404.html": render_not_found(site),
             "sitemap.xml": render_sitemap(site)}
    for page in site.pages:
        files[f"{page.path}index.html"] = render_page(site, page, pdf_pages)
    return files


def write_site(files, out_dir):
    """Écrit les fichiers du site dans `out_dir`, et retire les pages d'une génération
    précédente dont l'adresse n'existe plus."""
    for path, text in files.items():
        target = out_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for old in (out_dir / GUIDE_DIR).glob("*/index.html"):
        if old.relative_to(out_dir).as_posix() not in files:
            old.unlink()
            with contextlib.suppress(OSError):  # le dossier contient encore autre chose
                old.parent.rmdir()
    print(f"{out_dir} : {len(files)} fichiers du site")


def main(argv=None):
    """Point d'entrée en ligne de commande."""
    parser = argparse.ArgumentParser(description="Génère le site web du guide à partir du "
                                                 "Markdown.")
    parser.add_argument("src", nargs="?", type=Path, default=build_pdf.GUIDE_MD)
    parser.add_argument("--out-dir", type=Path, default=build_pdf.ROOT,
                        help="dossier du site (par défaut : le dossier du guide)")
    args = parser.parse_args(argv)
    md_text = args.src.read_text(encoding="utf-8")
    try:
        files = render_site(md_text, build_pdf.page_count(md_text))
    except SourceError as err:
        sys.exit(f"{args.src} : {err}")
    write_site(files, args.out_dir)


if __name__ == "__main__":
    main()
