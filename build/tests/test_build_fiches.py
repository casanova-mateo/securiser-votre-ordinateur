"""Tests de l'assemblage des fiches pratiques (build_fiches.py)."""
import pytest
from bs4 import BeautifulSoup

import build_fiches
import build_pdf

GUIDE = build_pdf.GUIDE_MD.read_text(encoding="utf-8")

SAMPLE = """# Guide

## 🔐 Chapitre un

Intro.

### Partie A

Contenu A.

#### Détail

Détail A.

### Partie B

Contenu B.

---

## Chapitre deux

> **Attention :** premier encadré
> sur deux lignes.

Texte entre les deux.

> **Attention :** second encadré.
"""


def test_section_s_arrete_au_titre_de_meme_niveau():
    """Une partie contient ses sous-titres et s'arrête à la partie suivante."""
    assert build_fiches.section(SAMPLE, "Partie A") == "Contenu A.\n\n#### Détail\n\nDétail A."


def test_section_s_arrete_au_separateur():
    """Un chapitre s'arrête au séparateur « --- » ; l'emoji du titre est ignoré."""
    text = build_fiches.section(SAMPLE, "Chapitre un")
    assert text.startswith("Intro.") and text.endswith("Contenu B.")


def test_section_introuvable():
    """Un titre absent du guide arrête la génération avec un message qui le nomme."""
    with pytest.raises(build_fiches.MissingPassage, match="« Partie Z »"):
        build_fiches.section(SAMPLE, "Partie Z")


def test_quote():
    """Un encadré : sa première ligne et les lignes « > » qui suivent."""
    assert build_fiches.quote(SAMPLE, "> **Attention :** premier") == (
        "> **Attention :** premier encadré\n> sur deux lignes.")


def test_quote_introuvable():
    """Un début d'encadré absent du guide arrête la génération avec un message qui le nomme."""
    with pytest.raises(build_fiches.MissingPassage, match="Encadré introuvable"):
        build_fiches.quote(SAMPLE, "> **Solution :**")


def test_unquote():
    """Les « > » de début de ligne disparaissent, y compris sur les lignes vides."""
    assert build_fiches.unquote("> un\n>\n> deux") == "un\n\ndeux"


def test_fiche_bien_demarrer():
    """Fiche 1 : priorités sans libellé ni renvoi final, renvois réécrits, liste à cocher."""
    md = build_fiches.bien_demarrer(GUIDE)
    assert md.startswith(f"# Bien démarrer\n\n{build_fiches.AUTHOR_LINE}\n")
    assert "**Par où commencer :**" not in md
    assert "(voir " not in md and "(guide, partie 2.1 : mises à jour)" in md
    assert "La liste de vérification, à la fin du guide" not in md
    assert "## Le kit de secours" in md and "- [ ] " in md


def test_fiche_bons_reflexes():
    """Fiche 2 : les bons réflexes, deux encadrés « Attention » et la partie sur les arnaques."""
    md = build_fiches.bons_reflexes(GUIDE)
    assert "> **Attention :** une fenêtre ou une page web qui affirme" in md
    assert "> **Attention :** le cadenas affiché" in md
    assert "## Signalez les arnaques" in md


def test_chaque_fiche_se_met_en_page():
    """Les trois fiches se mettent en page, chacune avec son titre et son sous-titre."""
    urgence = build_fiches.URGENCE_MD.read_text(encoding="utf-8")
    titles = []
    for _, md, subtitle in build_fiches.fiches(GUIDE, urgence):
        page = BeautifulSoup(build_pdf.render_html(md, fiche=True, subtitle=subtitle),
                             "html.parser")
        assert page.select_one(".fiche-head .subtitle").get_text() == subtitle
        titles.append(page.select_one(".fiche-head h1").get_text())
    assert titles[:2] == ["Bien démarrer", "Les bons réflexes"] and titles[2]


def test_main_genere_les_trois_pdf(tmp_path):
    """La ligne de commande écrit les trois PDF dans le dossier demandé."""
    build_fiches.main([str(build_pdf.GUIDE_MD), "--out-dir", str(tmp_path / "fiches")])
    pdfs = sorted(p.name for p in (tmp_path / "fiches").iterdir())
    assert pdfs == ["fiche-1-bien-demarrer.pdf", "fiche-2-bons-reflexes.pdf",
                    "fiche-3-en-cas-d-urgence.pdf"]
    assert all((tmp_path / "fiches" / p).read_bytes().startswith(b"%PDF-") for p in pdfs)


def test_main_passage_manquant(tmp_path):
    """Un guide où un passage a disparu arrête le script avant d'écrire la moindre fiche."""
    guide = tmp_path / "guide.md"
    guide.write_text("# Guide\n\n## Chapitre\n\nTexte.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="introuvable"):
        build_fiches.main([str(guide), "--out-dir", str(tmp_path / "fiches")])
    assert not (tmp_path / "fiches").exists()
