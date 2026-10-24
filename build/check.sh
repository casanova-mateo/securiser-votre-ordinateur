#!/bin/sh
# Contrôle le code du dossier build/ : shellcheck, pylint (10/10 attendu), puis les tests.
# Usage : ./build/check.sh [options de pytest, par exemple -k fiche]
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
. "$DIR/env.sh"
setup_python "$DIR/requirements.txt" "$DIR/requirements-dev.txt"

cd "$DIR"
"$VENV/bin/shellcheck" -x build.sh check.sh env.sh
echo "shellcheck : aucun problème"
PYTHONPATH="$DIR" "$PY" -m pylint build_pdf.py build_fiches.py tests/*.py
PYTHONPATH="$DIR" "$PY" -m pytest tests "$@"
