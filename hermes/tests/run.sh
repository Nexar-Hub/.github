#!/usr/bin/env bash
# Corre todas las pruebas del kit, sin red ni LLM: self-tests de los scripts y una
# instalación completa contra un `hermes` falso (tests/hermes-stub) en un HOME temporal.
set -euo pipefail
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
SK="$KIT/skills/radar"
fail() { echo "FAIL: $*" >&2; exit 1; }

echo "== self-tests"
"$PY" -I "$SK/leverage-radar/scripts/whatsapp_to_inbox.py" --self-test
"$PY" -I "$SK/leverage-radar/scripts/fetch_post.py" --self-test
"$PY" -I "$SK/leverage-radar/scripts/radar.py" self-test | tail -1
"$PY" -I "$SK/session-distill/scripts/distill_sessions.py" --self-test
"$PY" -I "$SK/goal-contract/scripts/contract.py" self-test

echo "== skills frontmatter"
for f in "$SK"/*/SKILL.md; do
  head -1 "$f" | grep -q '^---$' || fail "$f sin frontmatter"
  n="$(sed -n 's/^name: //p' "$f" | head -1)"
  [ "$n" = "$(basename "$(dirname "$f")")" ] || fail "$f: name '$n' no coincide con la carpeta"
  echo "$n" | grep -Eq '^[a-z0-9][a-z0-9._-]{0,63}$' || fail "$f: name inválido para Hermes"
  d="$(sed -n 's/^description: //p' "$f" | head -1)"
  [ "${#d}" -le 1024 ] || fail "$f: description > 1024 caracteres"
  grep -q '<KIT>' "$f" && fail "$f usa <KIT>: usá \${HERMES_SKILL_DIR}"
  echo "  ok $n"
done

echo "== instalación contra hermes falso"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/home" "$T/hh"; cp "$KIT/tests/hermes-stub" "$T/bin/hermes"; chmod +x "$T/bin/hermes"
echo "model: x" > "$T/hh/config.yaml"
export PATH="$T/bin:$PATH" HOME="$T/home" FAKE_HH="$T/hh"
bash "$KIT/install.sh" --cron --cheap-model cheap/m >/dev/null
grep -q "skills.external_dirs" "$T/hh/calls.log" || fail "no configuró external_dirs"
[ "$(grep -c '^cron create' "$T/hh/calls.log")" = 5 ] || fail "esperaba 5 cron jobs"
grep -q -- "--monitor-script radar-pending.sh" "$T/hh/calls.log" || fail "TRIAGE sin monitor-script"
grep -q -- "--no-agent --script radar-alerts.sh" "$T/hh/calls.log" || fail "alertas deberían correr sin LLM"
bash "$KIT/install.sh" --cron >/dev/null
[ "$(grep -c '^cron create' "$T/hh/calls.log")" = 5 ] || fail "la segunda corrida duplicó cron jobs"
[ "$(grep -c '^config set' "$T/hh/calls.log")" = 1 ] || fail "la segunda corrida reescribió la config"
out="$(bash "$T/hh/scripts/radar-alerts.sh")"; [ -z "$out" ] || fail "alertas debería estar en silencio: $out"
[ "$(bash "$T/hh/scripts/radar-pending.sh")" = "pendientes=0" ] || fail "monitor-script"
doc="$(bash "$KIT/install.sh" --doctor)"; echo "$doc" | grep -q "skill /leverage-radar visible" || fail "doctor: $doc"

echo "== pack privado con inbox ya procesado"
mkdir -p "$T/pack/inbox" "$T/pack/evals"
printf '# Perfil\nprivado\n' > "$T/pack/perfil.md"
echo '{"id":"abc123def456","url":"https://x.com/a/status/1","notes":["Bible"],"tags":[],"first_seen":"2026-11-01T10:00:00"}' > "$T/pack/inbox/inbox.jsonl"
echo '{"id":"abc123def456","veredicto":"WATCH","fuente":"notas"}' > "$T/pack/evals/gold-debil.jsonl"
(cd "$T/pack" && "$PY" -c 'import zipfile,os; z=zipfile.ZipFile("../pack.zip","w"); [z.write(os.path.join(r,f)) for r,_,fs in os.walk(".") for f in fs]')
bash "$KIT/install.sh" --workspace "$T/ws2" --private "$T/pack.zip" >/dev/null
grep -q privado "$T/ws2/perfil.md" || fail "perfil del pack no se aplicó"
[ "$(cd "$T/ws2" && "$PY" -I "$SK/leverage-radar/scripts/radar.py" pending)" = "pendientes=1 primero=abc123def456" ] || fail "inbox del pack"
echo '{"id":"zzz"}' > "$T/ws2/inbox/inbox.jsonl"
bash "$KIT/install.sh" --workspace "$T/ws2" --private "$T/pack.zip" >/dev/null
grep -q zzz "$T/ws2/inbox/inbox.jsonl" || fail "el pack pisó un inbox existente"

echo "== demo + dashboard"
"$PY" -I "$SK/leverage-radar/scripts/radar.py" demo "$T/demo" >/dev/null
grep -q "Radar de Leverage" "$T/demo/dashboard.html" || fail "dashboard"
al="$(cd "$T/demo" && "$PY" -I "$SK/leverage-radar/scripts/radar.py" alerts)"; echo "$al" | grep -q "router-model" || fail "rabbit hole en demo"
echo "TODO OK"
