"""Tests du site web du guide (build_site.py)."""
import base64
import hashlib
import posixpath
import re
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

import pytest
from bs4 import BeautifulSoup

import build_pdf
import build_site

NBSP = "\u00a0"

SAMPLE = """# 🛡️ Titre

*par l'auteur*

## 🔐 Introduction

Premier paragraphe de l'introduction.

> **Par où commencer :** les priorités.
>
> 1. Faites les mises à jour (voir 2.1, mises à jour)
> 2. Lisez tout le guide

## Les bases

### 🔄 Mises à jour

Texte des mises à jour (2.1) : voir la partie Linux.

#### 🪟 Windows

- Ouvrez **Paramètres > Windows Update**

#### 🍎 macOS

- Ouvrez les réglages

### Mots de passe

Comme en 2.1, mais pas dans `9.9.9.9`, ni pour Windows 10 ou la version 2.10.

#### Le kit de secours

Notez-les.

#### Le kit de secours

Doublon.

## Linux

Le chapitre Linux.

### Installer

1. Une étape

### Vérifier

- [ ] Première case
- [ ] Seconde case
"""

SAMPLE_PAGES = {
    "Introduction": ("intro", "Introduction"),
    "Mises à jour": ("mises-a-jour", "Mises à jour"),
    "Mots de passe": ("mots-de-passe", "Mots de passe"),
    "Linux": ("linux", "Linux, en bref"),
}


@pytest.fixture(name="sample")
def fixture_sample(monkeypatch):
    """Réglages du site pour SAMPLE ; renvoie les pages par adresse."""
    monkeypatch.setattr(build_site, "SPLIT", ("Les bases",))
    monkeypatch.setattr(build_site, "PAGES", SAMPLE_PAGES)
    monkeypatch.setattr(build_site, "NAMED_REFS", {"la partie Linux": "linux"})
    monkeypatch.setattr(build_site, "HELP_PAGE", "linux")
    return {page.slug: page for page in build_site.guide_pages(SAMPLE).pages}


def parse(page_html):
    """Arbre HTML d'une page produite."""
    return BeautifulSoup(page_html, "html.parser")


def article(page):
    """Contenu d'une page du guide, tel qu'il sera publié."""
    return parse(str(page.article)).article


@pytest.mark.usefixtures("sample")
@pytest.mark.parametrize(("text", "slug"), [
    ("Le kit de secours", "le-kit-de-secours"),
    ("L’entropie des mots de passe (pourquoi le hasard compte)",
     "l-entropie-des-mots-de-passe-pourquoi-le-hasard-compte"),
    (f"Sécurisez votre réseau{NBSP}!", "securisez-votre-reseau"),
])
def test_slugify(text, slug):
    """Minuscules sans accents, un tiret entre les mots."""
    assert build_site.slugify(text) == slug


def test_une_page_par_chapitre_ou_par_partie(sample):
    """Une page par chapitre, sauf pour les chapitres de SPLIT : une page par partie."""
    assert list(sample) == ["intro", "mises-a-jour", "mots-de-passe", "linux"]
    assert [(p.num, p.chapter) for p in sample.values()] == [
        ("01", ""), ("2.1", "Les bases"), ("2.2", "Les bases"), ("03", "")]
    assert sample["linux"].label == "Linux, en bref"
    assert sample["linux"].path == "guide/linux/"


def test_titres_de_page(sample):
    """Le titre de chaque page devient <h1>, et ses sous-titres remontent d'autant."""
    updates, linux = article(sample["mises-a-jour"]), article(sample["linux"])
    assert updates.h1.get_text() == "2.1 Mises à jour"
    assert [h.get_text() for h in updates.find_all("h2")] == ["Windows", "macOS"]
    assert linux.h1.get_text() == "03 Linux"
    assert [h["id"] for h in linux.find_all("h2")] == ["s3-1", "s3-2"]
    assert all(len(article(page).find_all("h1")) == 1 for page in sample.values())
    assert updates.select_one("p.kicker").get_text() == "Les bases"
    assert linux.select_one("p.kicker") is None


@pytest.mark.parametrize(("levels", "expected"), [
    ([3, 4, 4], [1, 2, 2]),  # partie et sous-parties
    ([2, 3, 4, 3], [1, 2, 3, 2]),  # chapitre, parties et sous-parties
    ([2, 4, 4], [1, 2, 2]),  # « #### » directement sous « ## » : pas de niveau sauté
    ([2, 4, 3, 4], [1, 2, 2, 3]),
])
def test_niveaux_de_titres(levels, expected):
    """Le titre de la page devient <h1>, chaque sous-titre se place un niveau sous son parent."""
    page = parse("<article>" + "".join(f"<h{n}>T</h{n}>" for n in levels) + "</article>").article
    build_site.promote_headings(page)
    assert [int(h.name[1]) for h in page.find_all(build_site.HEADING)] == expected


@pytest.mark.usefixtures("sample")
def test_titre_sans_adresse(monkeypatch):
    """Un chapitre ou une partie absent de PAGES arrête la génération, en le nommant."""
    monkeypatch.setattr(build_site, "PAGES", {k: v for k, v in SAMPLE_PAGES.items()
                                              if k != "Linux"})
    with pytest.raises(build_pdf.SourceError, match="« Linux » n'a pas d'adresse"):
        build_site.guide_pages(SAMPLE)


@pytest.mark.usefixtures("sample")
def test_adresse_sans_titre(monkeypatch):
    """Une entrée de PAGES qui ne correspond à aucun titre (titre renommé) est signalée."""
    monkeypatch.setattr(build_site, "PAGES", {**SAMPLE_PAGES, "Ancien titre": ("x", "X")})
    with pytest.raises(build_pdf.SourceError, match="introuvable dans le guide : « Ancien titre »"):
        build_site.guide_pages(SAMPLE)


@pytest.mark.usefixtures("sample")
@pytest.mark.parametrize(("md_text", "message"), [
    (SAMPLE.replace("## Les bases\n", "## Les bases\n\nIntroduction des bases.\n"),
     "« Les bases » a une page par partie"),
    (SAMPLE.replace("## 🔐 Introduction", "Texte sans chapitre.\n\n## 🔐 Introduction"),
     "avant tout texte"),
])
def test_structure_refusee(md_text, message):
    """Un texte qui n'aurait pas de page (introduction d'un chapitre de SPLIT, texte avant le
    premier chapitre) arrête la génération."""
    with pytest.raises(build_pdf.SourceError, match=message):
        build_site.guide_pages(md_text)


def test_renvois(sample):
    """Les renvois numérotés et ceux de NAMED_REFS deviennent des liens, sauf vers la page
    elle-même, dans le code et dans les nombres qui ne sont pas des numéros de partie."""
    links = {slug: [(a.get_text(), a["href"]) for a in article(page).find_all("a")]
             for slug, page in sample.items()}
    assert ("2.1", "../../guide/mises-a-jour/") in links["intro"]
    assert links["mises-a-jour"] == [("la partie Linux", "../../guide/linux/")]
    assert links["mots-de-passe"] == [("2.1", "../../guide/mises-a-jour/")]
    text = article(sample["mots-de-passe"]).get_text()
    assert "9.9.9.9" in text and "version 2.10" in text


def test_ancres_des_sous_parties(sample):
    """Chaque sous-partie reçoit une ancre lisible et unique ; un encadré système n'en a pas."""
    ids = [h.get("id") for h in article(sample["mots-de-passe"]).find_all("h2")]
    assert ids == ["le-kit-de-secours", "le-kit-de-secours-2"]
    assert article(sample["mises-a-jour"]).select_one(".card-title").get("id") is None
    reserved = parse("<main><h4>Sur cette page</h4></main>").main
    build_site.name_subsections(reserved)
    assert reserved.h4["id"] == "sur-cette-page-2"  # ancre déjà prise par chaque page


def test_encadres_systeme_repliables(sample):
    """Les encadrés système gardent leur titre, suivi de leur contenu regroupé pour que site.js
    puisse le replier ; le choix du système est ajouté (masqué sans JavaScript par site.css)."""
    page = article(sample["mises-a-jour"])
    cards = page.select(".card[data-os]")
    assert [c["data-os"] for c in cards] == ["win", "mac"]
    assert [[child.name for child in c.find_all(recursive=False)] for c in cards] == [
        ["h2", "div"], ["h2", "div"]]
    assert cards[0].h2["class"] == ["card-title"]
    assert cards[0].select_one(".card-body").get_text(strip=True).startswith("Ouvrez")
    assert len({c.select_one(".card-body")["id"] for c in cards}) == 2
    assert page.find(attrs={"data-kind": True}) is None
    choice = page.select_one("fieldset.os-filter")
    assert not choice.has_attr("hidden")  # affiché dès le début : pas de décalage
    assert [(r["value"], r.has_attr("checked")) for r in choice.find_all("input")] == [
        ("all", True), ("win", False), ("mac", False), ("linux", False)]
    assert page.select_one("p.lead + fieldset.os-filter") is not None
    assert article(sample["mots-de-passe"]).select_one("fieldset") is None


def test_chemins_de_menus_secables(sample):
    """Un long chemin de menu peut passer à la ligne après chaque flèche."""
    path = article(sample["mises-a-jour"]).select_one(".path")
    assert [el.name for el in path.find_all(True)] == ["span", "wbr"]
    assert path.get_text() == "Paramètres›Windows Update"


@pytest.mark.usefixtures("sample")
def test_titres_des_tableaux():
    """Chaque tableau a pour titre celui de sa partie ; un tableau comparatif défile."""
    md_text = SAMPLE.replace("Le chapitre Linux.\n", "Le chapitre Linux.\n\n"
                             "| A | B | C |\n|---|---|---|\n| x | y | z |\n")
    pages = {page.slug: page for page in build_site.guide_pages(md_text).pages}
    table = article(pages["linux"]).table
    assert table["aria-labelledby"] == "ch3"
    assert table.parent["class"] == ["table-scroll"] and table.parent["tabindex"] == "0"


def test_liste_de_verification(sample):
    """De vraies cases à cocher, chacune avec son libellé, suivies des outils de site.js."""
    page = article(sample["linux"])
    items = page.select("ul.checklist > li")
    assert [(li.input["id"], li.label["for"], li.label.get_text()) for li in items] == [
        ("case-1", "case-1", "Première case"), ("case-2", "case-2", "Seconde case")]
    tools = page.select_one("ul.checklist + div.check-tools")
    assert tools.has_attr("hidden") and tools.button.get_text() == "Tout décocher"
    assert page.select_one("p.check-date") is not None  # imprimée seulement


@pytest.mark.usefixtures("sample")
def test_sur_cette_page(monkeypatch):
    """Une page qui a assez de sous-parties en affiche la liste en tête."""
    monkeypatch.setattr(build_site, "ON_PAGE_MIN", 2)
    pages = {page.slug: page for page in build_site.guide_pages(SAMPLE).pages}
    box = article(pages["linux"]).select_one("p.lead + nav.on-page")
    assert [a["href"] for a in box.find_all("a")] == ["#s3-1", "#s3-2"]
    assert article(pages["mises-a-jour"]).select_one("nav.on-page") is None


def test_description():
    """La description reprend le premier paragraphe, coupé entre deux mots s'il est long."""
    short = parse(f"<article><h1>T</h1><p>Un texte court{NBSP}: voilà.</p></article>").article
    assert build_site.describe(short, "T") == f"Un texte court{NBSP}: voilà."
    long_text = parse(f"<article><p>{'mot ' * 60}</p></article>").article
    description = build_site.describe(long_text, "T")
    assert len(description) <= build_site.DESCRIPTION_MAX and description.endswith("mot…")
    empty = parse("<article><ul><li>x</li></ul></article>").article
    assert build_site.describe(empty, "Liste").startswith(f"Liste — {build_pdf.GUIDE_TITLE}")


def test_page_du_guide(sample):
    """Une page complète : métadonnées, sommaire latéral, pages voisines, signalement."""
    site = build_site.guide_pages(SAMPLE)
    page = parse(build_site.render_page(site, site.pages[1], 27))
    assert page.title.get_text() == f"Mises à jour — {build_pdf.GUIDE_TITLE}"
    assert page.find("link", rel="canonical")["href"] == f"{build_pdf.SITE_URL}guide/mises-a-jour/"
    assert page.find("meta", attrs={"name": "description"})["content"].startswith("Texte des")
    assert re.fullmatch(r"\.\./\.\./site\.css\?v=[0-9a-f]{10}",
                        page.find("link", rel="stylesheet")["href"])
    assert page.select_one('.sidebar [aria-current="page"]')["href"] == "../../guide/mises-a-jour/"
    assert [a["href"] for a in page.select(".pager a")] == ["../../guide/intro/",
                                                            "../../guide/mots-de-passe/"]
    mailto = unquote(page.select_one(".page-end a")["href"])
    assert f"Guide « {build_pdf.GUIDE_TITLE} », 2.1 Mises à jour" in mailto
    assert f"Page : {build_pdf.SITE_URL}guide/mises-a-jour/" in mailto
    assert sample["linux"].slug == build_site.HELP_PAGE
    assert page.select_one(".topnav .urgent")["href"] == "../../guide/linux/"


@pytest.mark.usefixtures("sample")
def test_sommaire():
    """Le sommaire relie chaque chapitre et chaque partie à sa page ; le titre d'un chapitre de
    SPLIT, qui n'a pas de page, n'est pas un lien."""
    page = parse(build_site.render_contents(build_site.guide_pages(SAMPLE), 27))
    chapters = [(li.select_one(".chap .t").get_text(), li.select_one(".chap a"))
                for li in page.select(".toc-full > li")]
    assert [title for title, _ in chapters] == ["Introduction", "Les bases", "Linux"]
    assert chapters[1][1] is None
    assert [a["href"] for a in page.select(".toc-full ol a")] == [
        "../guide/mises-a-jour/", "../guide/mots-de-passe/", "../guide/linux/#s3-1",
        "../guide/linux/#s3-2"]
    assert page.select_one(".actions .btn-primary")["href"] == "../guide/intro/"


@pytest.mark.usefixtures("sample")
def test_page_404():
    """La page 404 n'est pas indexée et ses liens partent de la racine du site."""
    page = parse(build_site.render_not_found(build_site.guide_pages(SAMPLE)))
    root = urlsplit(build_pdf.SITE_URL).path
    assert page.find("meta", attrs={"name": "robots"})["content"] == "noindex"
    assert page.find("link", rel="canonical") is None
    assert page.find("link", rel="stylesheet")["href"].startswith(f"{root}site.css?v=")
    assert all(a["href"].startswith((root, "#", "mailto:", "https://"))
               for a in page.find_all("a", href=True))


@pytest.mark.usefixtures("sample")
def test_accueil():
    """L'accueil reprend la version, la date, le nombre de pages du PDF, le sommaire et les
    priorités du guide, chacune reliée à sa page."""
    page = parse(build_site.render_home(build_site.guide_pages(SAMPLE), 42))
    assert f"Version{NBSP}{build_pdf.VERSION}" in page.select_one(".byline").get_text()
    assert build_pdf.date_label(build_pdf.RELEASE_DATE).replace(" ", NBSP) in page.get_text()
    assert f"(42{NBSP}pages)" in page.select_one(".hero .actions").get_text()
    priorities = page.select("ol.priorities > li")
    assert [(li.get_text(), li.a["href"] if li.a else None) for li in priorities] == [
        ("Faites les mises à jour", "guide/mises-a-jour/"), ("Lisez tout le guide", None)]
    assert [a["href"] for a in page.select(".toc a")] == [
        "guide/intro/", "guide/mises-a-jour/", "guide/mots-de-passe/", "guide/linux/"]
    assert "build/accueil.html" in page.find(string=lambda s: "Généré par" in s)


@pytest.mark.usefixtures("sample")
def test_accueil_sans_priorites():
    """Sans l'encadré « Par où commencer », l'accueil ne peut pas être généré."""
    site = build_site.guide_pages(SAMPLE.replace("Par où commencer", "Pour commencer"))
    with pytest.raises(build_pdf.SourceError, match="« Par où commencer » introuvable"):
        build_site.render_home(site, 27)


@pytest.mark.usefixtures("sample")
def test_politique_de_securite():
    """Chaque page déclare la CSP ; elle n'a ni style ni script écrit dans la page, sauf
    EARLY_JS, autorisé par son empreinte, et ne charge aucune ressource externe."""
    early = base64.b64encode(hashlib.sha256(build_site.EARLY_JS.encode()).digest()).decode()
    for path, text in build_site.render_site(SAMPLE, 27).items():
        if not path.endswith(".html"):
            continue
        page = parse(text)
        policy = page.find("meta", attrs={"http-equiv": "Content-Security-Policy"})["content"]
        assert "default-src 'none'" in policy and "style-src 'self';" in policy, path
        inline = [s.string for s in page.find_all("script") if not s.has_attr("src")]
        assert all(script == build_site.EARLY_JS for script in inline), path
        assert not inline or f"'sha256-{early}'" in policy, path
        assert page.find("style") is None and page.find(style=True) is None, path
        assert not page.find(lambda el: any(a.startswith("on") for a in el.attrs)), path
        loaded = [el["src"] for el in page.find_all(["script", "img"], src=True)]
        loaded += [el["href"] for el in page.find_all("link", rel=["stylesheet", "icon"])]
        assert loaded and not [url for url in loaded if urlsplit(url).netloc], path
    assert parse(build_site.render_site(SAMPLE, 27)["guide/intro/index.html"]).head.script


@pytest.mark.usefixtures("sample")
def test_plan_du_site():
    """sitemap.xml donne l'adresse complète de l'accueil, du sommaire et de chaque page."""
    sitemap = ElementTree.fromstring(build_site.render_site(SAMPLE, 27)["sitemap.xml"].encode())
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    assert [loc.text for loc in sitemap.findall("s:url/s:loc", ns)] == [
        build_pdf.SITE_URL + path for path in ("", "guide/", "guide/intro/", "guide/mises-a-jour/",
                                               "guide/mots-de-passe/", "guide/linux/")]
    assert {m.text for m in sitemap.findall("s:url/s:lastmod", ns)} == {
        build_pdf.RELEASE_DATE.isoformat()}


@pytest.mark.usefixtures("sample")
def test_generation_reproductible():
    """Deux générations du même guide donnent exactement les mêmes fichiers."""
    assert build_site.render_site(SAMPLE, 27) == build_site.render_site(SAMPLE, 27)


def heading_levels(page):
    """Niveaux des titres d'une page, dans l'ordre."""
    return [int(h.name[1]) for h in page.find_all(re.compile(r"^h[1-6]$"))]


def test_guide_complet():
    """Le vrai guide : chaque titre sur une seule page, une hiérarchie de titres sans saut,
    des ancres uniques, et chaque renvoi relié à une ancre qui existe."""
    site = build_site.guide_pages(build_pdf.GUIDE_MD.read_text(encoding="utf-8"))
    assert [page.slug for page in site.pages] == [slug for slug, _ in build_site.PAGES.values()]
    assert build_site.HELP_PAGE in {page.slug for page in site.pages}
    assert set(build_site.NAMED_REFS.values()) <= {page.slug for page in site.pages}
    pages = {page.slug: article(page) for page in site.pages}
    ids = {slug: [el["id"] for el in page.find_all(id=True)] for slug, page in pages.items()}
    split = {hid for _, _, text, hid in site.toc if text in build_site.SPLIT}
    for _, _, _, hid in site.toc:
        found = [slug for slug, page_ids in ids.items() if hid in page_ids]
        assert len(found) == (0 if hid in split else 1), hid
    for slug, page in pages.items():
        levels = heading_levels(page)
        assert levels[0] == 1 and levels.count(1) == 1, slug
        assert all(b - a <= 1 for a, b in zip(levels, levels[1:])), slug
        assert len(ids[slug]) == len(set(ids[slug])), slug
        for a in page.find_all("a", href=True):
            target = urlsplit(a["href"])
            target_slug = target.path.split("/")[-2] if target.path else slug
            assert target.fragment in ids[target_slug] or not target.fragment, a["href"]
    assert sum(len(page.select("a[href]")) for page in pages.values()) > 20  # renvois reliés


def site_targets(path, url):
    """Fichier (relatif à la racine du site) et ancre visés par le lien `url` de la page `path`."""
    parts = urlsplit(url)
    root = urlsplit(build_pdf.SITE_URL).path
    if parts.path.startswith(root):
        target = parts.path[len(root):]
    else:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(path), parts.path or
                                                   posixpath.basename(path)))
    if parts.path.endswith("/") or target in (".", ""):
        target = posixpath.join(target, "index.html")
    return posixpath.normpath(target), parts.fragment


def test_ligne_de_commande(tmp_path, capsys):
    """Le site complet : tous les fichiers sont écrits, chaque lien interne mène à un fichier
    qui existe (généré, ou écrit à la main dans le dossier du guide) et à une ancre qui existe ;
    une page dont l'adresse a disparu est retirée."""
    stale = tmp_path / "guide" / "ancienne-adresse" / "index.html"
    stale.parent.mkdir(parents=True)
    stale.write_text("ancienne page", encoding="utf-8")
    kept = tmp_path / "guide" / "autre" / "notes.txt"
    kept.parent.mkdir(parents=True)
    kept.write_text("pas une page", encoding="utf-8")
    build_site.main([str(build_pdf.GUIDE_MD), "--out-dir", str(tmp_path)])
    assert not stale.parent.exists() and kept.exists()
    files = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*.html"))
    assert len(files) == len(build_site.PAGES) + 3
    assert f"{tmp_path} : {len(files) + 1} fichiers du site" in capsys.readouterr().out
    assert (tmp_path / "sitemap.xml").exists()
    pdf_pages = build_pdf.page_count(build_pdf.GUIDE_MD.read_text(encoding="utf-8"))
    home = parse((tmp_path / "index.html").read_text(encoding="utf-8"))
    assert f"({pdf_pages}{NBSP}pages)" in home.select_one(".hero .actions").get_text()
    for path in files:
        page = parse((tmp_path / path).read_text(encoding="utf-8"))
        for el in page.find_all(["a", "link", "script", "img"]):
            url = el.get("href") or el.get("src")
            if url is None or urlsplit(url).scheme:  # https:, mailto:
                continue
            target, fragment = site_targets(path, url)
            source = tmp_path / target if (tmp_path / target).exists() else build_pdf.ROOT / target
            assert source.exists(), f"{path} : {url}"
            if fragment:
                target_page = parse(source.read_text(encoding="utf-8"))
                assert target_page.find(id=fragment), f"{path} : {url}"


def test_ligne_de_commande_document_invalide(tmp_path):
    """Un Markdown sans titre arrête le script avec un message qui nomme le fichier, sans rien
    écrire."""
    src = tmp_path / "sans-titre.md"
    src.write_text("Texte.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="sans-titre.md : le document doit commencer"):
        build_site.main([str(src), "--out-dir", str(tmp_path / "site")])
    assert not (tmp_path / "site").exists()
