#!/usr/bin/env bash
# Prueba ejecutable de punta a punta, desde cero, con datos ficticios.
# No toca el vault real, Google Calendar ni nada fuera de $WORK.
#
# Necesita (ver README.md): binarios de OpenTodo (OPENTODO_BIN, OT_BIN), Horolog en
# HOROLOG_API_DIR (commit fijado), un venv con radicale/caldav/pyyaml/pydantic (PY),
# y Node con playwright para las capturas.
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$H/work}"
: "${OPENTODO_BIN:?ruta al binario opentodo}" "${OT_BIN:?ruta al binario ot}" "${HOROLOG_API_DIR:?horolog/services/api}" "${PY:?python del venv}"
PORT=8080; CAL=5232; B="http://127.0.0.1:$PORT"

# --- 0. Reinicio limpio ------------------------------------------------------
for f in "$WORK"/logs/*.pid; do [ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null || true; done
pkill -f "opentodo$" 2>/dev/null || true; pkill -f "radicale --config" 2>/dev/null || true
sleep 1; rm -rf "$WORK"; mkdir -p "$WORK"/{otdata,logs,radicale/collections,capturas,evidencia}
cp -r "$H/fixtures/vault-demo" "$WORK/vault"
git -C "$WORK/vault" init -q && git -C "$WORK/vault" -c user.name=demo -c user.email=demo@local add -A \
  && git -C "$WORK/vault" -c user.name=demo -c user.email=demo@local commit -qm "vault ficticio inicial"

cat > "$WORK/radicale/config" <<EOF
[server]
hosts = 127.0.0.1:$CAL
[auth]
type = htpasswd
htpasswd_filename = $WORK/radicale/users
htpasswd_encryption = plain
[storage]
filesystem_folder = $WORK/radicale/collections
[logging]
level = warning
EOF
echo "persona:sandbox-pass" > "$WORK/radicale/users"
nohup "$PY" -m radicale --config "$WORK/radicale/config" > "$WORK/logs/radicale.log" 2>&1 & echo $! > "$WORK/logs/radicale.pid"
TZ=America/Argentina/Buenos_Aires nohup env OPENTODO_DATA_DIR="$WORK/otdata" OPENTODO_ADDR="127.0.0.1:$PORT" \
  OPENTODO_MCP=true OPENTODO_MCP_WRITES=true OPENTODO_CALENDAR_FEEDS=true OPENTODO_WEBHOOKS_ALLOW_PRIVATE=true \
  "$OPENTODO_BIN" > "$WORK/logs/opentodo.log" 2>&1 & echo $! > "$WORK/logs/opentodo.pid"
for i in $(seq 1 60); do curl -fsS "$B/healthz" >/dev/null 2>&1 && curl -fsS -o /dev/null "http://127.0.0.1:$CAL/.web/" 2>/dev/null && break; sleep 0.25; done

# --- Cuenta, tokens y permisos (lo que la persona hace una vez en Ajustes) ---
J="$WORK/jar"; HJ=(-s -c "$J" -b "$J" -H 'Content-Type: application/json' -H "Origin: $B")
curl "${HJ[@]}" -X POST "$B/api/v1/auth/register" -d '{"email":"persona@sandbox.local","name":"Persona (sandbox)","password":"Sandbox-Pass-2026!"}' >/dev/null
FULL=$(curl "${HJ[@]}" -X POST "$B/api/v1/tokens" -d '{"name":"persona (sandbox)","scope":"full"}' | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["secret"])')
curl "${HJ[@]}" -X PUT "$B/api/v1/me/agent-access" -d '{"allow_writes":true}' >/dev/null
AGENT=$(curl "${HJ[@]}" -X POST "$B/api/v1/tokens" -d '{"name":"claude-planificador","scope":"agent"}' | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["secret"])')
curl "${HJ[@]}" -X PUT "$B/api/v1/settings/calendar-sync" -d '{"enabled":true}' >/dev/null
printf '{"full":"%s","agent":"%s"}\n' "$FULL" "$AGENT" > "$WORK/tokens.json"; chmod 600 "$WORK/tokens.json"
OPENTODO_CONFIG="$WORK/ot-config.json" "$OT_BIN" auth set-token "$FULL" --server "$B" >/dev/null

export WORK B PY OT_BIN HOROLOG_API_DIR OPENTODO_URL="$B" OPENTODO_AGENT_TOKEN="$AGENT" OPENTODO_FULL_TOKEN="$FULL" \
  OPENTODO_CONFIG="$WORK/ot-config.json" VAULT="$WORK/vault" LOTES="$WORK/lotes" CAPTURAS="$WORK/capturas"
cd "$H" && "$PY" demo.py "$@"
