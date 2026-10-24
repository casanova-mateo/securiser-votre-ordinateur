"""Génère les fiches pratiques (PDF) dans le dossier fiches/.

Usage : python build_fiches.py [guide.md] [--out-dir dossier]

Les fiches 1 et 2 reprennent mot pour mot des passages du guide : elles restent synchronisées.
La fiche 3 (urgence) est rédigée à part dans fiches/fiche-urgence.md, version condensée
du chapitre 5.
"""
import argparse
import re
import sys
from pathlib import Path

import build_pdf

FICHES_DIR = build_pdf.ROOT / "fiches"
URGENCE_MD = FICHES_DIR / "fiche-urgence.md"
AUTHOR_LINE = f"*Fiche pratique — par {build_pdf.AUTHOR}*"
HEADING = re.compile(r"^(#+) (.*)$")


class MissingPassage(LookupError):
    """Passage du guide introuvable : un titre ou le début d'un encadré a changé."""


def section(md, title):
    """Contenu sous le titre qui commence par `title`, jusqu'au titre suivant de même niveau
    (ou ---)."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and build_pdf.clean(m.group(2)).startswith(title):
            out = []
            for nxt in lines[i + 1:]:
                n = HEADING.match(nxt)
                if (n and len(n.group(1)) <= len(m.group(1))) or nxt.strip() == "---":
                    break
                out.append(nxt)
            return "\n".join(out).strip()
    raise MissingPassage(f"Section introuvable dans le guide : « {title} »")


def quote(md, start):
    """Encadré (citation Markdown) qui commence par `start`."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(start):
            out = [line]
            for nxt in lines[i + 1:]:
                if not nxt.startswith(">"):
                    break
                out.append(nxt)
            return "\n".join(out)
    raise MissingPassage(f"Encadré introuvable dans le guide : « {start} »")


def unquote(block):
    """Texte d'une citation Markdown, sans les « > »."""
    return "\n".join(re.sub(r"^> ?", "", line) for line in block.splitlines())


def bien_demarrer(guide):
    """Fiche 1 : les 5 priorités et le kit de secours au recto, la liste de vérification
    au verso."""
    priorities = unquote(quote(guide, "> **Par où commencer :**"))
    priorities = priorities.replace("**Par où commencer :** si", "Si", 1)
    priorities = re.sub(r"\(voir (\d[\d.]*), ([^)]+)\)", r"(guide, partie \1 : \2)", priorities)
    priorities = re.sub(r"\n\nLa liste de vérification, à la fin du guide.*$", "", priorities,
                        flags=re.S)
    return f"""# Bien démarrer

{AUTHOR_LINE}

## Par où commencer : les 5 priorités

{priorities}

Cochez ensuite, au verso, la liste de vérification complète.

## Le kit de secours

{section(guide, "Le kit de secours")}

## Liste de vérification

{section(guide, "Récapitulatif : liste de vérification")}
"""


def bons_reflexes(guide):
    """Fiche 2 : les bons réflexes au quotidien, les pièges à connaître et où signaler."""
    return f"""# Les bons réflexes

{AUTHOR_LINE}

## Au quotidien

{section(guide, "Les bons réflexes en ligne")}

## Deux pièges à connaître

{quote(guide, "> **Attention :** une fenêtre ou une page web qui affirme")}

{quote(guide, "> **Attention :** le cadenas affiché")}

## Signalez les arnaques

{section(guide, "Signalez les arnaques")}
"""


def fiches(guide, urgence):
    """Les trois fiches : (nom du PDF, Markdown, sous-titre)."""
    return [
        ("fiche-1-bien-demarrer", bien_demarrer(guide),
         "Les mesures essentielles et la liste de vérification"),
        ("fiche-2-bons-reflexes", bons_reflexes(guide),
         "Reconnaître les arnaques et les pièges les plus courants"),
        ("fiche-3-en-cas-d-urgence", urgence,
         "Que faire en cas de virus, de piratage ou de fraude bancaire"),
    ]


def main(argv=None):
    """Point d'entrée en ligne de commande."""
    parser = argparse.ArgumentParser(description="Génère les fiches pratiques à partir du guide.")
    parser.add_argument("guide", nargs="?", type=Path, default=build_pdf.GUIDE_MD)
    parser.add_argument("--out-dir", type=Path, default=FICHES_DIR,
                        help="dossier des PDF (par défaut : fiches/)")
    args = parser.parse_args(argv)
    try:
        docs = fiches(args.guide.read_text(encoding="utf-8"),
                      URGENCE_MD.read_text(encoding="utf-8"))
    except MissingPassage as err:
        sys.exit(str(err))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, md, subtitle in docs:
        try:
            build_pdf.build(md, args.out_dir / f"{name}.pdf", fiche=True, subtitle=subtitle)
        except build_pdf.SourceError as err:
            sys.exit(f"Fiche « {name} » : {err}")


if __name__ == "__main__":
    main()
