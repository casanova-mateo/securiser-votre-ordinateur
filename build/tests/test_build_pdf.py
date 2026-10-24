"""Tests de la mise en page du guide et des fiches (build_pdf.py)."""
import datetime
import re

import pytest
from bs4 import BeautifulSoup

import build_pdf

NBSP = " "


def render(md_text, **options):
    """HTML produit pour `md_text`, sous forme d'arbre."""
    return BeautifulSoup(build_pdf.render_html(md_text, **options), "html.parser")


def doc(body):
    """Document minimal : titre, ligne d'auteur, introduction, puis `body` dans un chapitre."""
    return f"# 🛡️ Titre\n\n*par l'auteur*\n\nIntroduction.\n\n## 🔐 Chapitre\n\n{body}\n"


def chapter_of(page):
    """Le chapitre qui contient le `body` passé à doc()."""
    return page.select("main > section")[1]


@pytest.mark.parametrize(("text", "expected"), [
    ("Attention : danger !", f"Attention{NBSP}: danger{NBSP}!"),
    ("« Bonjour »", f"«{NBSP}Bonjour{NBSP}»"),
    ("Les 5 priorités", f"Les 5{NBSP}priorités"),
    ("Windows 11", "Windows 11"),
    ("de 2024 2025", "de 2024 2025"),
])
def test_fr_typo(text, expected):
    """Espaces insécables avant : ; ! ? », après « et entre un nombre et un mot."""
    assert build_pdf.fr_typo(text) == expected


def test_clean_retire_les_emojis():
    """Les emojis des titres (avec leur sélecteur de variante) disparaissent."""
    assert build_pdf.clean("🛡️ Sécuriser ✅") == "Sécuriser"


def test_date_label():
    """Mois en toutes lettres, avec une majuscule, suivi de l'année."""
    assert build_pdf.date_label(datetime.date(2026, 2, 1)) == "Février 2026"


def test_la_date_imprimee_est_celle_de_la_version(monkeypatch):
    """La couverture et les métadonnées portent RELEASE_DATE, et non la date du jour."""
    monkeypatch.setattr(build_pdf, "RELEASE_DATE", datetime.date(2020, 3, 15))
    page = render(doc("Texte."))
    assert page.select_one(".cover .date").get_text() == "Mars 2020 · Version " + build_pdf.VERSION
    assert "Mars 2020" in page.select_one(".back .edition").get_text()
    assert page.find("meta", attrs={"name": "dcterms.created"})["content"] == "2020-03-15"
    fiche = render(doc("Texte."), fiche=True)
    assert "Mars 2020" in fiche.select_one(".fiche-head .meta").get_text()
    assert "mars 2020." in fiche.select_one(".colophon").get_text()


def test_titre_et_ligne_d_auteur_passent_sur_la_couverture():
    """Le titre, sans emoji, va sur la couverture ; la ligne d'auteur n'est pas reprise."""
    page = render(doc("Texte."))
    assert page.select_one(".cover h1").get_text() == "Titre"
    assert page.title.get_text() == "Titre"
    assert "par l'auteur" not in page.main.get_text()
    assert "Introduction." in page.main.get_text()


@pytest.mark.parametrize(("first_paragraph", "kept"), [
    ("Premier paragraphe, sans italique.", "Premier paragraphe, sans italique."),
    ("*Note :* le paragraphe commence en italique.", "le paragraphe commence en italique."),
])
def test_un_paragraphe_qui_n_est_pas_une_ligne_d_auteur_est_conserve(first_paragraph, kept):
    """Sans ligne d'auteur en italique, le premier paragraphe reste dans le document."""
    page = render(f"# Titre\n\n{first_paragraph}\n\n## Chapitre\n\nTexte.\n")
    assert kept in page.main.get_text()


def test_titre_manquant():
    """Un document sans titre « # » est refusé avec un message clair."""
    with pytest.raises(build_pdf.SourceError, match="titre"):
        build_pdf.render_html("## Chapitre\n\nTexte.\n")


def test_numerotation_et_sommaire():
    """Chapitres « 01 », parties « 1.1 », ancres et sommaire."""
    page = render(doc("### Une partie\n\nTexte.\n\n## Deuxième chapitre\n\nTexte."))
    nums = [h.select_one(".num").get_text() for h in page.main.find_all(["h2", "h3"])]
    assert nums == ["01", "1.1", "02"]
    assert [h["id"] for h in page.main.find_all(["h2", "h3"])] == ["ch1", "s1-1", "ch2"]
    toc = [(li["class"][0], li.a["href"]) for li in page.select(".toc-list li")]
    assert toc == [("l2", "#ch1"), ("l3", "#s1-1"), ("l2", "#ch2")]
    assert chapter_of(page)["data-title"] == "Chapitre"


def test_premier_chapitre_et_introduction():
    """L'introduction forme le premier chapitre, en paragraphes mis en avant, sans saut de page."""
    page = render(doc("Texte."))
    intro, chapter = page.select("main > section")
    assert intro["data-title"] == "Titre"
    assert intro.p["class"] == ["lead"]
    assert chapter["class"] == ["chapter", "flow"]


def test_fiche():
    """Une fiche : bandeau-titre, sections non numérotées, mention finale en dernière page."""
    page = render(doc("Texte.\n\n## Dernier\n\nFin."), fiche=True, subtitle="Le sous-titre")
    assert page.body["class"] == ["fiche"]
    assert page.select_one(".fiche-head .subtitle").get_text() == "Le sous-titre"
    assert page.select_one(".cover") is None and page.select_one(".back") is None
    assert page.main.select(".num") == []
    assert page.select("main > section")[-1].select_one(".colophon") is not None
    assert 'content: "Fiche pratique · Titre"' in page.style.get_text()


@pytest.mark.parametrize(("body", "text"), [
    ("> Une simple citation, sans libellé.", "Une simple citation, sans libellé."),
    ("> 1. Une citation\n> 2. qui commence par une liste", "qui commence par une liste"),
    ("> Ouvrez **Paramètres > Comptes**, puis validez.", "Paramètres›Comptes, puis validez."),
])
def test_citation_sans_libelle(body, text):
    """Une citation sans libellé en gras au début devient un encadré bleu sans titre."""
    bq = chapter_of(render(doc(body))).blockquote
    assert bq["class"] == ["callout", "example"]
    assert bq.select_one(".callout-label") is None
    assert text in bq.get_text()


@pytest.mark.parametrize(("label", "kind"), [
    ("Exemple", "example"),
    ("Pourquoi c'est important", "important"),
    ("Par où commencer", "important"),
    ("Solution", "solution"),
    ("Pour se faire aider", "solution"),
    ("Attention", "warning"),
    ("Remarque", "example"),  # libellé inconnu : bleu
])
def test_couleur_des_encadres(label, kind):
    """La couleur dépend du libellé ; le libellé devient le titre de l'encadré."""
    bq = chapter_of(render(doc(f"> **{label} :** ne cliquez pas."))).blockquote
    assert bq["class"] == ["callout", kind]
    assert bq.select_one(".callout-label").get_text() == label
    assert bq.p.get_text() == "Ne cliquez pas."


def test_citations_consecutives_separees():
    """Trois encadrés à la suite, fusionnés par python-markdown, sont séparés."""
    body = "> **Exemple :** un.\n\n> **Attention :** deux.\n\n> **Solution :** trois."
    quotes = chapter_of(render(doc(body))).find_all("blockquote")
    assert [q["class"][1] for q in quotes] == ["example", "warning", "solution"]
    assert [q.p.get_text() for q in quotes] == ["Un.", "Deux.", "Trois."]


def test_chemin_de_menu():
    """**A > B** devient un chemin de menu, avec une flèche entre les étapes."""
    page = render(doc("Ouvrez **Paramètres > Comptes > Connexion**."))
    path = chapter_of(page).select_one(".path")
    assert path.get_text() == "Paramètres›Comptes›Connexion"
    assert len(path.select(".sep")) == 2


def test_raccourci_clavier():
    """**Ctrl + Alt + L** devient trois touches dessinées."""
    keys = chapter_of(render(doc("Appuyez sur **Ctrl + Alt + L**."))).select_one(".keys")
    assert [k.get_text() for k in keys.find_all("kbd")] == ["Ctrl", "Alt", "L"]
    assert chapter_of(render(doc("Un **mot important**."))).select_one(".keys") is None


def test_liste_de_verification():
    """Cases à cocher, ligne de date et chapitre jamais coupé entre deux pages."""
    chapter = chapter_of(render(doc("- [ ] Sauvegarder\n- [ ] Mettre à jour")))
    checklist = chapter.select_one("ul.checklist")
    assert [li.get_text() for li in checklist.find_all("li")] == ["Sauvegarder", "Mettre à jour"]
    assert checklist.find_next_sibling("p")["class"] == ["check-date"]
    assert chapter["class"] == ["chapter", "flow", "keep"]


def test_etapes_numerotees():
    """Une procédure courte n'est pas coupée ; une liste dans un encadré n'est pas une procédure."""
    short = "\n".join(f"{i}. Étape" for i in range(1, 4))
    long_steps = "\n".join(f"{i}. Étape" for i in range(1, 8))
    assert chapter_of(render(doc(short))).ol["class"] == ["steps", "short"]
    assert chapter_of(render(doc(long_steps))).ol["class"] == ["steps"]
    assert not chapter_of(render(doc("> **Exemple :**\n>\n> 1. Étape"))).ol.has_attr("class")


def test_encadres_systeme():
    """#### Windows et #### macOS : un encadré par système, jusqu'au titre suivant."""
    chapter = chapter_of(render(doc("#### Windows\n\nPour Windows.\n\n#### macOS\n\nPour Mac.")))
    cards = chapter.select("div.card")
    assert [c["class"] for c in cards] == [["card", "win"], ["card", "mac"]]
    assert cards[0].h4["class"] == ["card-title"]
    assert cards[0].p.get_text() == "Pour Windows."


def table(columns, rows):
    """Tableau Markdown de `columns` colonnes et `rows` lignes."""
    lines = ["| " + " | ".join(f"T{c}" for c in range(columns)) + " |",
             "|" + "---|" * columns]
    lines += ["| " + " | ".join("x" for _ in range(columns)) + " |" for _ in range(rows)]
    return "\n".join(lines)


def test_tableaux():
    """Tableau comparatif à partir de 3 colonnes ; au-delà de 12 lignes, il peut être coupé."""
    small = chapter_of(render(doc(table(2, 3)))).table
    assert not small.has_attr("class")
    assert chapter_of(render(doc(table(3, 3)))).table["class"] == ["compare"]
    chapter = chapter_of(render(doc(table(2, 13))))
    assert chapter.table["class"] == ["long"]
    assert chapter.table.find_parent("div", class_="block")["class"] == ["block", "free"]


def test_annexe_sur_une_nouvelle_page():
    """Un chapitre « Annexe » commence sur une nouvelle page (pas de classe flow)."""
    page = render(doc("Texte.\n\n## Annexe : glossaire\n\nMots."))
    assert page.select("main > section")[-1]["class"] == ["chapter"]


def test_blocs_insecables():
    """Chaque titre forme un bloc ; un titre suivi d'un texte court reste avec le bloc suivant."""
    chapter = chapter_of(render(doc("### Partie\n\nCourt.\n\n#### Détail\n\nTexte.")))
    blocks = chapter.find_all("div", class_="block", recursive=False)
    assert [b["class"] for b in blocks] == [["block", "lead-in"], ["block", "lead-in"], ["block"]]
    assert [b.find(["h2", "h3", "h4"]).name for b in blocks] == ["h2", "h3", "h4"]


def test_pas_de_typographie_dans_le_code():
    """Les espaces insécables ne sont pas ajoutés dans le code."""
    chapter = chapter_of(render(doc("Tapez `a : b` ici : c'est tout.")))
    assert chapter.code.get_text() == "a : b"
    assert f"ici{NBSP}:" in chapter.p.get_text()


def test_guide_complet():
    """Le vrai guide : un chapitre par titre « ## », tous les encadrés et cases reconnus."""
    md_text = build_pdf.GUIDE_MD.read_text(encoding="utf-8")
    page = render(md_text)
    assert len(page.select("main > section")) == len(re.findall(r"(?m)^## ", md_text))
    assert all("callout" in bq["class"] for bq in page.find_all("blockquote"))
    assert page.select("ul.checklist") and "[ ]" not in page.main.get_text()


def test_build_ecrit_le_pdf_et_le_html(tmp_path, capsys):
    """build() écrit un PDF, le HTML intermédiaire si demandé, et affiche la taille."""
    out, html_out = tmp_path / "test.pdf", tmp_path / "test.html"
    build_pdf.build(doc("Texte."), out, html_out=html_out)
    assert out.read_bytes().startswith(b"%PDF-")
    assert "<!doctype html>" in html_out.read_text(encoding="utf-8")
    assert f"{out} (" in capsys.readouterr().out


def test_ligne_de_commande(tmp_path):
    """Sans fichier de sortie, le PDF est écrit à côté du Markdown."""
    src = tmp_path / "doc.md"
    src.write_text(doc("Texte."), encoding="utf-8")
    build_pdf.main([str(src), "--fiche", "--subtitle", "Sous-titre"])
    assert (tmp_path / "doc.pdf").read_bytes().startswith(b"%PDF-")


def test_ligne_de_commande_document_invalide(tmp_path):
    """Un Markdown sans titre arrête le script avec un message qui nomme le fichier."""
    src = tmp_path / "sans-titre.md"
    src.write_text("Texte.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="sans-titre.md : le document doit commencer"):
        build_pdf.main([str(src)])
    assert not (tmp_path / "sans-titre.pdf").exists()
