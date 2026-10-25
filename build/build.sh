#!/bin/sh
# Génère le PDF du guide, les fiches pratiques et le site web à partir du Markdown.
# Usage : ./build/build.sh                    -> guide + 3 fiches + site
#         ./build/build.sh guide.md sortie.pdf -> ce document seulement (options de build_pdf.py)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
. "$DIR/env.sh"
setup_python "$DIR/requirements.txt"

if [ "$#" -gt 0 ]; then
  exec "$PY" "$DIR/build_pdf.py" "$@"
fi
"$PY" "$DIR/build_pdf.py"
"$PY" "$DIR/build_fiches.py"
"$PY" "$DIR/build_site.py"
