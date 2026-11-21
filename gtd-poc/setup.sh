#!/usr/bin/env bash
# Prepara la prueba en ./.deps (nada global, nada permanente): compila OpenTodo desde
# el código en un commit fijado, baja el solver de Horolog en un commit fijado y arma
# un venv con versiones fijas. Necesita git, Go 1.24+ (baja solo el toolchain 1.27),
# Node 22+ con npm, y Python 3.12+.
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"
D="${DEPS:-$H/.deps}"
OPENTODO_COMMIT=fc5169e5e4b887096e956335ab5b6d1373804581   # main del 2026-11-21 (CHANGELOG: 1.6.0)
HOROLOG_COMMIT=91a5cbfff4c4b8bd2ce9d4b24e43f9cfce40d09a    # ujjwalredd/horolog, 2026-08-12 (0.2.0 beta)
mkdir -p "$D"

fetch() {  # repo commit dir
  if [ ! -d "$3/.git" ]; then git init -q "$3" && git -C "$3" remote add origin "$1"; fi
  git -C "$3" fetch -q --depth 1 origin "$2" && git -C "$3" checkout -q FETCH_HEAD
}

fetch https://github.com/OpenTodoApp/OpenTodo.git "$OPENTODO_COMMIT" "$D/opentodo"
fetch https://github.com/ujjwalredd/horolog.git "$HOROLOG_COMMIT" "$D/horolog"

if [ ! -x "$D/opentodo/bin/opentodo" ]; then
  (cd "$D/opentodo/web" && npm ci --no-audit --no-fund --ignore-scripts && npm run build)
  (cd "$D/opentodo" && GOTOOLCHAIN=auto CGO_ENABLED=0 go build -trimpath -o bin/opentodo ./cmd/opentodo \
                    && GOTOOLCHAIN=auto CGO_ENABLED=0 go build -trimpath -o bin/ot ./cmd/ot)
fi

[ -x "$D/venv/bin/python" ] || python3 -m venv "$D/venv"
"$D/venv/bin/pip" install -q -r "$H/requirements.txt"

cat > "$D/env.sh" <<EOF
export OPENTODO_BIN="$D/opentodo/bin/opentodo" OT_BIN="$D/opentodo/bin/ot"
export HOROLOG_API_DIR="$D/horolog/services/api" PY="$D/venv/bin/python"
EOF
echo "Listo. Ahora: source $D/env.sh && $H/run_demo.sh"
