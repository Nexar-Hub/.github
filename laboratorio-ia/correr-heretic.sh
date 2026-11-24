#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -f .venv/bin/activate ] || { echo "Primero corré ./instalar.sh"; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate
exec python lab/correr_heretic.py "$@"
