#!/bin/bash
# SessionStart para sesiones en la nube (celular, web): carga el contexto del vault con el
# mismo script que usan las computadoras (30-Skills/contexto.py start). Sin vault, avisa cómo
# conseguirlo en vez de dejar que la sesión complete con supuestos.
# Reemplaza al hook de la rama claude/fable5-2-instructions-sez4lb (que solo servía para Nexar
# y copiaba estado vivo, como los colores, en un archivo que se carga en cada sesión).
set -uo pipefail

# En la computadora el contexto lo carga el hook del vault: acá no hay nada que hacer.
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

repo="${CLAUDE_PROJECT_DIR:-$(pwd)}"
padre="$(dirname "$repo")"

vault=""
for c in "${NEXAR_VAULT:-}" "$padre/context-vault" "$HOME/context-vault" "$HOME/Vault"; do
  if [ -n "$c" ] && [ -f "$c/30-Skills/contexto.py" ]; then vault="$c"; break; fi
done

if [ -z "$vault" ]; then
  cat <<EOT
SIN CONTEXTO: el vault de Nico (repo privado Webflowrepository/context-vault) no está en esta sesión.
Antes de proponer, diseñar o construir algo:
1. Adjuntalo con add_repo (owner Webflowrepository, repo context-vault, acceso read) y clonalo en
   $padre/context-vault. Arreglo permanente (lo hace Nico una vez): sumar context-vault en
   Repositories del entorno de la nube (menú del entorno en la barra del título → Edit).
2. Corré: python3 -I -X utf8 $padre/context-vault/30-Skills/contexto.py start --tarea "<pedido>"
3. Antes de construir, buscá si ya existe: python3 -I -X utf8 $padre/context-vault/30-Skills/capacidades.py para "<pedido>"
Si no se puede, decíselo a Nico y no completes con supuestos (marca, colores, clientes, precios).
EOT
  exit 0
fi

py="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
salida=""
[ -n "$py" ] && salida="$(cd "$repo" && "$py" -I -X utf8 "$vault/30-Skills/contexto.py" start 2>/dev/null || true)"

printf 'Vault cargado desde %s (copia de GitHub, solo lectura). Donde dice ~/Vault, acá es %s.\n' "$vault" "$vault"
cat <<EOT
Reglas de esta sesión en la nube:
- Antes de construir: python3 -I -X utf8 $vault/30-Skills/capacidades.py para "<pedido>". Si ya existe, usalo o decí por qué no.
- No escribas ni commitees en el vault (lo hace el sync de la PC). Al cerrar, dejá el relevo en el chat con
  contexto.py wrap (sin --escribir) para que una sesión en la PC lo anote.
- Este repo (Nexar-Hub/.github) es PÚBLICO: nada de contexto de negocio, clientes, precios ni perfil.

EOT
if [ -n "$salida" ]; then
  # Claude Code corta la salida de un hook en 10.000 caracteres.
  printf '%s\n' "$salida" | head -c 8500
else
  echo "contexto.py no devolvió nada: leé a mano $vault/00-Contexto/Kernel.md, Preferencias.md y Control Tower.md."
fi
exit 0
