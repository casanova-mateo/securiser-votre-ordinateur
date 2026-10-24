# Partagé par build.sh et check.sh (chargé avec « . ») : environnement Python et bibliothèque pango.
# shellcheck shell=sh

# L'environnement Python est créé hors du dossier du guide : sur un disque externe (exFAT), il
# occuperait des centaines de Mo et se couvrirait de fichiers cachés « ._* ». BUILD_VENV le déplace.
VENV="${BUILD_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/securiser-votre-ordinateur/venv}"
PY="$VENV/bin/python"

# Installe les fichiers de dépendances donnés quand l'un d'eux a changé depuis la dernière
# installation : une copie de chaque fichier installé, gardée dans l'environnement, sert de repère.
setup_python() {
  stale=
  [ -x "$PY" ] || stale=1
  for req in "$@"; do
    cmp -s "$req" "$VENV/$(basename "$req")" || stale=1
  done
  if [ -n "$stale" ]; then
    echo "Installation des dépendances dans $VENV (connexion Internet nécessaire)…"
    [ -x "$PY" ] || python3 -m venv --clear "$VENV"
    for req in "$@"; do
      "$PY" -m pip install -q --disable-pip-version-check -r "$req"
      cp "$req" "$VENV/$(basename "$req")"
    done
  fi
}

# WeasyPrint charge la bibliothèque pango : MacPorts l'installe dans /opt/local/lib,
# Homebrew dans /opt/homebrew/lib (Apple Silicon) ou /usr/local/lib (Intel).
export DYLD_FALLBACK_LIBRARY_PATH="/opt/local/lib:/opt/homebrew/lib:/usr/local/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"
