#!/usr/bin/env bash
# Radar de Leverage: instalador para Hermes Agent. Idempotente: se puede correr varias veces.
#
#   bash hermes/install.sh                          # workspace en ~/radar + skills en Hermes
#   bash hermes/install.sh --private radar-privado.zip --cron --cheap-model <modelo> [--cheap-provider openrouter]
#   bash hermes/install.sh --doctor                 # solo chequea, no cambia nada
#
# Qué hace (y nada más):
#   1. Crea el workspace (por defecto ~/radar). Nunca pisa archivos que ya editaste.
#   2. Si pasás --private, copia tu perfil/stack/decisiones/experimentos. Si ya tenés versiones
#      editadas, deja las nuevas como *.nuevo.md para que compares.
#   3. Agrega las skills a skills.external_dirs de Hermes (con backup de config.yaml).
#   4. Copia 2 scripts chicos a <HERMES_HOME>/scripts/ (los cron solo corren scripts de ahí).
#   5. Con --cron, crea los cron jobs del radar (salta los que ya existen).
# No toca tu memoria, ni tu SOUL.md, ni tus tokens, ni hace push de nada.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${HOME}/radar"
PRIVATE="" ; DO_CRON=0 ; DOCTOR=0 ; CHEAP_MODEL="" ; CHEAP_PROVIDER="" ; DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) WS="$2"; shift 2 ;;
    --private) PRIVATE="$2"; shift 2 ;;
    --cron) DO_CRON=1; shift ;;
    --cheap-model) CHEAP_MODEL="$2"; shift 2 ;;
    --cheap-provider) CHEAP_PROVIDER="$2"; shift 2 ;;
    --doctor) DOCTOR=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "opción desconocida: $1" >&2; exit 2 ;;
  esac
done

ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$*"; }
run()  { if [ "$DRY" = 1 ]; then echo "  (dry-run) $*"; else "$@"; fi; }

# --- python
PY=""
for c in python3 python "py -3"; do
  if $c -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { bad "Falta Python 3.10+ (python3)."; exit 1; }

# --- native paths (Git Bash on Windows hands Windows paths to Hermes)
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
[ "$DOCTOR" = 1 ] || mkdir -p "$WS"
WS="$(cd "$WS" 2>/dev/null && pwd || printf '%s' "$WS")"
RADAR="$KIT/skills/radar/leverage-radar/scripts/radar.py"
SKILLS_DIR="$KIT/skills"

HERMES=0; command -v hermes >/dev/null 2>&1 && HERMES=1
HH=""
if [ "$HERMES" = 1 ]; then
  CFG="$(hermes config path 2>/dev/null | tail -1 || true)"
  [ -n "$CFG" ] && HH="$(dirname "$CFG")"
fi
[ -n "$HH" ] || HH="${HERMES_HOME:-$HOME/.hermes}"

doctor() {
  set +o pipefail  # grep -q cierra el pipe antes: no es un error
  echo "Radar · diagnóstico"
  ok "python: $PY"
  [ -f "$RADAR" ] && $PY "$RADAR" self-test >/dev/null 2>&1 && ok "motor radar.py: self-test OK" || bad "motor radar.py falla: corré $PY $RADAR self-test"
  for f in AGENTS.md perfil.md stack.md decisiones.md experimentos.md; do
    [ -f "$WS/$f" ] || { bad "falta $WS/$f"; continue; }
    grep -q '<completar\|<…>\|<proyecto>' "$WS/$f" && warn "$f tiene campos <completar>" || ok "$f"
  done
  if [ "$HERMES" = 0 ]; then bad "no encuentro el comando 'hermes' en el PATH"; return; fi
  ok "hermes: $(hermes --version 2>/dev/null | head -1 || echo instalado)"
  hermes config get skills.external_dirs --json 2>/dev/null | grep -qF "$(native "$SKILLS_DIR" | sed 's/\\/\\\\/g')" \
    && ok "skills.external_dirs incluye el kit" || bad "skills.external_dirs no incluye $SKILLS_DIR (corré el instalador)"
  local sl; sl="$(hermes skills list 2>/dev/null || true)"
  for s in leverage-radar capability-first goal-contract session-distill; do
    echo "$sl" | grep -q "$s" && ok "skill /$s visible" || warn "skill /$s no aparece en 'hermes skills list'"
  done
  for s in radar-pending.sh radar-alerts.sh; do [ -f "$HH/scripts/$s" ] && ok "script $s" || warn "falta $HH/scripts/$s"; done
  local cl; cl="$(hermes cron list --all 2>/dev/null || true)"
  for j in radar-triage radar-alertas radar-digest; do
    echo "$cl" | grep -q "$j" && ok "cron $j" || warn "cron $j no existe (instalá con --cron)"
  done
  hermes gateway status >/dev/null 2>&1 && ok "gateway responde (los cron corren dentro del gateway)" \
    || warn "no pude confirmar el gateway: corré 'hermes gateway status'"
  local al; al="$(cd "$WS" && $PY "$RADAR" alerts 2>/dev/null || true)"
  [ -z "$al" ] && ok "sin alertas del radar" || { warn "alertas del radar:"; echo "$al" | sed 's/^/      /'; }
}

if [ "$DOCTOR" = 1 ]; then doctor; exit 0; fi

echo "Radar de Leverage · instalando"
echo "  kit:       $KIT"
echo "  workspace: $WS"
echo "  hermes:    $([ "$HERMES" = 1 ] && echo "$HH" || echo 'no encontrado (solo armo el workspace)')"

# 1. workspace (never overwrite)
run mkdir -p "$WS/inbox" "$WS/digests" "$WS/runs" "$WS/destilados" "$WS/evals" "$WS/sesiones"
for f in AGENTS.md perfil.md stack.md decisiones.md experimentos.md; do
  if [ -e "$WS/$f" ]; then ok "$f ya existe (no lo toco)"; else run cp "$KIT/workspace/$f" "$WS/$f"; ok "$f creado"; fi
done
if [ "$DRY" = 0 ] && grep -q '^KIT=' "$WS/AGENTS.md"; then
  tmp="$(mktemp)"; sed "s#^KIT=.*#KIT=$(native "$KIT")#" "$WS/AGENTS.md" > "$tmp" && mv "$tmp" "$WS/AGENTS.md"
  ok "AGENTS.md apunta al kit"
fi

# 2. private pack
if [ -n "$PRIVATE" ]; then
  [ -f "$PRIVATE" ] || { bad "no existe $PRIVATE"; exit 1; }
  tmpd="$(mktemp -d)"
  $PY -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$PRIVATE" "$tmpd"
  for f in perfil.md stack.md decisiones.md experimentos.md; do
    src="$(find "$tmpd" -name "$f" | head -1)"; [ -n "$src" ] || continue
    if cmp -s "$WS/$f" "$KIT/workspace/$f" 2>/dev/null; then run cp "$src" "$WS/$f"; ok "$f ← pack privado"
    elif cmp -s "$WS/$f" "$src"; then ok "$f ya está al día"
    else run cp "$src" "$WS/${f%.md}.nuevo.md"; warn "$f ya estaba editado: dejé ${f%.md}.nuevo.md para comparar"; fi
  done
  for f in primer-pase.md USER-semilla.md dashboard.html; do
    src="$(find "$tmpd" -name "$f" | head -1)"; [ -n "$src" ] && run cp "$src" "$WS/$f" && ok "$f copiado"
  done
  # inbox and evals already processed (e.g. your history): copy only what is missing, never overwrite
  for d in inbox evals; do
    srcd="$(find "$tmpd" -type d -name "$d" | head -1)"; [ -n "$srcd" ] || continue
    for src in "$srcd"/*; do
      [ -f "$src" ] || continue
      dst="$WS/$d/$(basename "$src")"
      if [ -e "$dst" ]; then ok "$d/$(basename "$src") ya existe (no lo toco)"; else run cp "$src" "$dst"; ok "$d/$(basename "$src") ← pack privado"; fi
    done
  done
  rm -rf "$tmpd"
fi

if [ "$HERMES" = 0 ]; then
  warn "Instalá Hermes y volvé a correr este script para conectar skills y cron."
  exit 0
fi

# 3. external_dirs (merge, with backup)
SK_NATIVE="$(native "$SKILLS_DIR")"
current="$(hermes config get skills.external_dirs --json 2>/dev/null || echo '[]')"
# (python -c instead of a heredoc inside $(): bash 3.2 on macOS mis-parses those)
merged="$($PY -c 'import json, sys
try:
    cur = json.loads(sys.argv[1] or "[]")
except ValueError:
    cur = []
cur = cur if isinstance(cur, list) else ([cur] if cur else [])
if sys.argv[2] not in cur:
    cur.append(sys.argv[2])
print(json.dumps(cur))' "$current" "$SK_NATIVE")"
if [ "$merged" = "$current" ] || echo "$current" | grep -qF "$(printf '%s' "$SK_NATIVE" | sed 's/\\/\\\\/g')"; then
  ok "skills.external_dirs ya incluye el kit"
else
  CFG="$(hermes config path 2>/dev/null | tail -1)"
  [ -f "$CFG" ] && run cp "$CFG" "$CFG.bak-radar-$(date +%Y%m%d%H%M%S)" && ok "backup de config.yaml"
  run hermes config set skills.external_dirs "$merged" >/dev/null && ok "skills.external_dirs += $SK_NATIVE"
fi

# 4. cron scripts (Hermes only runs scripts from <HERMES_HOME>/scripts/)
run mkdir -p "$HH/scripts"
for pair in "radar-pending.sh:pending" "radar-alerts.sh:alerts"; do
  name="${pair%%:*}"; sub="${pair##*:}"
  if [ "$DRY" = 0 ]; then
    printf '#!/usr/bin/env bash\n# Radar de Leverage (generado por install.sh)\ncd "%s" && exec %s "%s" %s\n' "$WS" "$PY" "$RADAR" "$sub" > "$HH/scripts/$name"
    chmod +x "$HH/scripts/$name"
  fi
  ok "script $name"
done

# 5. cron jobs
if [ "$DO_CRON" = 1 ]; then
  WSN="$(native "$WS")"
  existing="$(hermes cron list --all 2>/dev/null || true)"
  cheap=(); [ -n "$CHEAP_MODEL" ] && cheap+=(--model "$CHEAP_MODEL"); [ -n "$CHEAP_PROVIDER" ] && cheap+=(--provider "$CHEAP_PROVIDER")
  mk() { local name="$1"; shift
    if echo "$existing" | grep -q "$name"; then ok "cron $name ya existe"; else run hermes cron create "$@" --name "$name" >/dev/null && ok "cron $name"; fi; }
  # Filtro diario: no despierta al modelo si el inbox no cambió (--monitor-script).
  mk radar-triage "daily at 8am" "Modo TRIAGE: procesá el próximo lote del radar." \
     --skill leverage-radar --workdir "$WSN" --monitor-script radar-pending.sh --deliver local ${cheap[@]+"${cheap[@]}"}
  # Alertas sin LLM: si no hay nada, no manda nada (stdout vacío = silencio).
  mk radar-alertas "daily at 9am" --no-agent --script radar-alerts.sh --deliver telegram --no-wrap-response
  # El único mensaje semanal.
  mk radar-digest "every monday 9am" "Modo DIGEST: juzgá los CANDIDATO de la semana y mandame el digest." \
     --skill leverage-radar --workdir "$WSN" --deliver telegram --continuity
  mk radar-scan "every thursday 9am" "Modo SCAN: buscá novedades en mis temas Tier 1 y apuestas abiertas, con presupuesto cerrado." \
     --skill leverage-radar --workdir "$WSN" --deliver local ${cheap[@]+"${cheap[@]}"}
  mk radar-destilado "0 10 1 * *" "Destilá mis sesiones de los últimos 30 días y mostrame las propuestas." \
     --skill session-distill --workdir "$WSN" --deliver telegram
  [ -z "$CHEAP_MODEL" ] && warn "TRIAGE y SCAN usan tu modelo principal. Para abaratar: hermes cron edit <id> --model <barato>"
fi

echo
echo "Listo. Próximos pasos:"
echo "  1. Completá los <completar> de $WS/perfil.md (el radar juzga contra ese archivo)."
[ -f "$WS/USER-semilla.md" ] && echo "  2. En Hermes: \"sumá a mi memoria de usuario lo de $WS/USER-semilla.md, respetando el límite\"."
echo "  3. Exportá el chat de WhatsApp (sin archivos) a $WS/inbox/ y en Hermes: /leverage-radar ingest"
echo "  4. Mandá links al bot: /leverage-radar <url> <nota>"
echo "  5. Chequeo: bash $KIT/install.sh --doctor --workspace $WS"
