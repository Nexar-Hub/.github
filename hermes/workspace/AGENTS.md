# Workspace del Radar de Leverage

Este directorio es el workspace del radar. Hermes lo carga como contexto cuando un cron corre con `--workdir` apuntando acá, o cuando abrís Hermes en este directorio.

```
KIT=~/src/nexar-hub-github/hermes        # install.sh lo ajusta solo
```

## Reglas

1. Respondé en español rioplatense, en forma corta y sin relleno. En Telegram, como máximo una pantalla.
2. Antes de juzgar o recomendar, leé `perfil.md`, `stack.md`, `decisiones.md` y `experimentos.md`.
3. **Lo mecánico lo hace `radar.py`, no vos.** Eso incluye ids, deduplicar, lotes, registrar veredictos, contar, alertas, experimentos y el dashboard. Nunca edites a mano `radar-log.jsonl`, `inbox/*.jsonl`, `inbox/processed.txt` ni los bloques de `experimentos.md`.
4. Si `radar.py log` rechaza un veredicto, corregí lo que dice el error. Usá `--force` solo con un "sí" del usuario.
5. `decisiones.md`, `stack.md` y `perfil.md` solo cambian con un "sí" explícito del usuario. Hasta entonces, escribí la propuesta en el digest o en la respuesta.
6. Puede haber como máximo 3 experimentos activos, y el motor lo hace cumplir.
7. Cuando el usuario corrige un veredicto, guardá la corrección con `radar.py label`, porque así se mide el radar.
8. No hagas push, deploy, compras, publicaciones ni mensajes a terceros sin aprobación.
9. No guardes secretos, tokens, cookies ni datos personales de terceros en ningún archivo.
10. Nunca afirmes una causalidad que no se midió. Los números de un autor van como "afirmado por el autor".

## Skills

- `/leverage-radar`: CAPTURE, INGEST, TRIAGE, DIGEST, SCAN, correcciones y dashboard.
- `/capability-first`: cuando aparece "investigá X" o "¿sirve X?".
- `/goal-contract`: cuando hay que construir algo con Claude Code o Codex. El juez es `contract.py verify`.
- `/session-distill`: errores y pedidos repetidos se convierten en reglas, skills o memoria (`distill_sessions.py`).

## Estructura

```
perfil.md          quién soy, proyectos, temas Tier 1/2/3, fuera de alcance
stack.md           capacidad → implementación → estado → "lo reemplazaría si…"
decisiones.md      decisiones vigentes + "qué la revertiría"
experimentos.md    pruebas abiertas (máx 3) y cerradas
radar-log.jsonl    un veredicto por línea (lo escribe radar.py log)
dashboard.html     panel visual (radar.py dashboard)
inbox/             export de WhatsApp, inbox.jsonl, capturas.jsonl, processed.txt
evals/gold.jsonl   tus correcciones (radar.py label) para medir al radar
digests/           un digest por semana
runs/              contratos y verificaciones de goal-contract
destilados/        candidatos e informes de session-distill
sesiones/          exports de ChatGPT o Claude.ai para destilar (opcional)
```
