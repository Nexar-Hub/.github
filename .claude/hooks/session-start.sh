#!/bin/bash
# Hook SessionStart para las sesiones en la nube (las que se abren desde el celular o la web).
# Busca el vault de contexto y, si está, imprime la ficha de la marca con el mismo script que usa
# la computadora (cargar-marca.py). Si no está, avisa qué hacer en vez de dejar la sesión sin contexto.
set -uo pipefail

# En la computadora el contexto lo carga el hook del vault: acá no hay nada que hacer.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

MARCA="Nexar"
repo="${CLAUDE_PROJECT_DIR:-$(pwd)}"
padre="$(dirname "$repo")"

vault=""
for candidato in "${NEXAR_VAULT:-}" "$padre/context-vault" "$HOME/context-vault" "$HOME/Vault"; do
  if [ -n "$candidato" ] && [ -f "$candidato/30-Skills/cargar-marca.py" ]; then
    vault="$candidato"
    break
  fi
done

if [ -z "$vault" ]; then
  cat <<EOF
FALTA EL CONTEXTO DE ${MARCA}: el vault no está en esta sesión.
Antes de responder cualquier pedido sobre la marca:
1. Adjuntá el repo privado con add_repo (owner Webflowrepository, repo context-vault, acceso read)
   y clonalo en $padre/context-vault.
2. Corré: python3 -I -X utf8 $padre/context-vault/30-Skills/cargar-marca.py --marca ${MARCA}
3. Leé 10-Empresas/${MARCA}/${MARCA}-Canon.md, ${MARCA}-Hechos.md y ${MARCA}-Aprendido.md.
Si no se puede, decíselo a Nico y no completes con supuestos. Ver CLAUDE.md.
EOF
  exit 0
fi

py="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
ficha=""
if [ -n "$py" ]; then
  ficha="$("$py" -I -X utf8 "$vault/30-Skills/cargar-marca.py" --marca "$MARCA" 2>/dev/null || true)"
fi

if [ -n "$ficha" ]; then
  printf 'Vault de contexto cargado desde %s (copia de GitHub, de solo lectura). Donde la ficha dice ~/Vault, en esta sesión es %s.\n\n' "$vault" "$vault"
  # Claude Code corta la salida de un hook en 10.000 caracteres.
  printf '%s\n' "$ficha" | head -c 9500
else
  cat <<EOF
El vault está en $vault pero la ficha de ${MARCA} no se pudo armar.
Leé a mano: $vault/10-Empresas/${MARCA}/${MARCA}-Canon.md, ${MARCA}-Hechos.md y ${MARCA}-Aprendido.md.
EOF
fi
exit 0
