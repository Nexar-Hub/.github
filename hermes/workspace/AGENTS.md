# Workspace del Radar de Leverage

Este directorio es el workspace del radar. Hermes lo carga como contexto cuando un cron corre con `--workdir` apuntando acá, o cuando abrís Hermes en este directorio.

```
KIT=~/src/nexar-hub-github/hermes        # ajustar a donde clonaste el repo
```

## Reglas

1. Respondé en español rioplatense, en forma corta y sin relleno. En Telegram, como máximo una pantalla.
2. Antes de juzgar o recomendar, leé `perfil.md`, `stack.md`, `decisiones.md` y `experimentos.md`.
3. Los archivos `radar-log.jsonl`, `inbox/capturas.jsonl` e `inbox/processed.txt` solo admiten agregar líneas. Nunca borres ni reescribas lo que ya está.
4. En `inbox/inbox.jsonl` escribe solo el script de ingest.
5. `decisiones.md`, `stack.md` y `perfil.md` solo cambian con un "sí" explícito del usuario. Hasta entonces, escribí la propuesta en el digest o en la respuesta.
6. Puede haber como máximo 3 experimentos activos.
7. No hagas push, deploy, compras, publicaciones ni mensajes a terceros sin aprobación.
8. No guardes secretos, tokens, cookies ni datos personales de terceros en ningún archivo.
9. Para trabajar con evidencia, seguí `KIT/skills/radar/leverage-radar/references/criterios.md`. Nunca afirmes una causalidad que no se midió.

## Skills de este workspace

- `/leverage-radar`: CAPTURE, INGEST, TRIAGE, DIGEST y SCAN.
- `/capability-first`: cuando aparece "investigá X" o "¿sirve X?".
- `/goal-contract`: cuando hay que construir algo con Claude Code o Codex.
- `/session-distill`: errores y workflows repetidos se convierten en reglas, skills o memoria.

## Estructura

```
perfil.md          quién soy, proyectos, temas Tier 1/2/3, fuera de alcance
stack.md           capacidad → implementación → estado → "lo reemplazaría si…"
decisiones.md      decisiones vigentes + "qué la revertiría"
experimentos.md    pruebas abiertas (máx 3) y cerradas
radar-log.jsonl    un veredicto por línea
inbox/             export de WhatsApp, inbox.jsonl, capturas.jsonl, processed.txt
digests/           un digest por semana
runs/              contratos y evidencia de goal-contract
destilados/        informes de session-distill
```
