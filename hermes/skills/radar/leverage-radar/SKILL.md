---
name: leverage-radar
description: Radar de Leverage. Filtra links, posts, repos y videos guardados y avisa solo cuando algo cambia una decisión, mejora el stack o abre una apuesta. Usar cuando el usuario manda un link para evaluar, pide procesar el inbox del radar, importar un export de WhatsApp, el digest semanal, un scan de novedades, el dashboard, o corrige un veredicto del radar.
version: 2.0.0
author: Nexar Hub
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [radar, research, triage, decisions, leverage, inbox, evals]
    category: radar
---

# Leverage Radar

No busca maximizar información. Busca maximizar leverage.

Un ítem sirve solo si contesta **sí** a una de estas tres preguntas:

1. **¿Cambia una decisión?** Toca el "qué la revertiría" de `decisiones.md`.
2. **¿Mejora el stack?** Cumple el "lo reemplazaría si…" de `stack.md`, o elimina un componente que hoy se mantiene a mano.
3. **¿Abre una apuesta?** Un cliente, una oferta, un caso replicable, un evento o un canal para un proyecto activo de `perfil.md`.

Si las tres son "no", el veredicto es DROP y no se avisa. Casi siempre, lo correcto es no decir nada.

## Reparto del trabajo

**El motor hace lo mecánico. Vos ponés el juicio.**

Todo lo que se puede contar, deduplicar o validar lo hace `radar.py`, sin gastar tokens:

```
R="python3 ${HERMES_SKILL_DIR}/scripts/radar.py"   # correr siempre desde el workspace del radar
```

| comando | para qué |
|---|---|
| `$R ingest inbox/<export>.zip` | WhatsApp → `inbox/inbox.jsonl` (deduplica, normaliza, prioriza) |
| `$R capture <url> --note "…"` | Agrega un link y avisa si ya se había visto, con su veredicto anterior |
| `$R next -n 10 --fetch` | Lote siguiente en JSON, con el texto del post o repo cuando se puede bajar |
| `$R log` | Registra veredictos (JSONL por stdin). **Valida y rechaza contradicciones** |
| `$R alerts` | Rabbit holes, experimentos vencidos, WIP, radar parado, propuestas sin respuesta |
| `$R digest-data` | Todo lo que necesita el digest, en JSON |
| `$R exp list` · `exp open …` · `exp close EXP-00N ADOPT\|DROP "aprendizaje"` | Experimentos (máximo 3 activos) |
| `$R label <id\|url> <VEREDICTO> --por-que "…"` | Guarda la corrección del usuario en `evals/gold.jsonl` |
| `$R eval` · `$R eval --compare logA logB` | Mide qué tan bien juzga el radar, o compara dos modelos |
| `$R dashboard` | Genera `dashboard.html`, un panel visual para el celular |

Nunca calcules ids, contadores ni fechas a mano. Nunca edites `radar-log.jsonl`, `processed.txt` ni los bloques de `experimentos.md`: para eso están los comandos.

## Workspace

Antes de juzgar, leé `perfil.md`, `stack.md`, `decisiones.md` y `experimentos.md` del workspace, que es el directorio que tiene el `AGENTS.md` del radar. Los criterios están en `${HERMES_SKILL_DIR}/references/criterios.md` y el mapa en `${HERMES_SKILL_DIR}/references/mapa-de-capacidades.md`.

## Procedimiento

### CAPTURE: el usuario manda un link

1. `$R capture <url> --note "<su nota>"`. Si devuelve `"duplicado": true`, respondé con el veredicto anterior en una línea y terminá.
2. Bajá el contenido con `python3 ${HERMES_SKILL_DIR}/scripts/fetch_post.py <url>`. Si devuelve `ok: false`, usá web_extract o el navegador. En YouTube bajá solo los subtítulos (`yt-dlp --skip-download --write-auto-subs`).
3. Juzgalo completo (ver "Juicio") y registrá una línea con `etapa: "capture"`.
4. Respondé en el formato corto.

### INGEST: llega un export de WhatsApp

1. `$R ingest inbox/<archivo>.zip` y respondé con el resumen que imprime. No juzgues en este paso.
2. Revisá `inbox/thoughts.jsonl`, que son las notas del usuario sin link. Si alguna es un principio o una decisión que no está en `decisiones.md`, proponela, pero no la escribas sin un "sí".

### TRIAGE: lote, pensado para un modelo barato

1. `$R next -n 15 --fetch`.
2. Para cada ítem, aplicá el juicio con este límite: **con un modelo barato, el máximo es CANDIDATO**. ADOPT, TEST y WATCH los decide el DIGEST.
3. Pasale todas las líneas juntas a `$R log`. Si rechaza alguna, corregí lo que dice el error y reenviá.
4. Respondé una línea: `TRIAGE: n revisados · k candidatos · d drop · p pendientes`.

### DIGEST: semanal, con el modelo fuerte

1. `$R digest-data`.
2. Juzgá a fondo cada `candidato`: ADOPT, TEST, WATCH o DROP, con `etapa: "digest"`, y registrá con `$R log`.
   - Un TEST abre un experimento con `$R exp open --titulo … --hipotesis … --criterio … --capacidad … --origen <id>`. Si no hay cupo, el motor lo rechaza: dejalo en WATCH con `revisar_si: "cupo libre en experimentos"`.
   - Un ADOPT **nunca** edita `stack.md` ni `decisiones.md`. Escribí la propuesta en el digest y esperá el sí.
3. Guardá el texto en `digest-data.archivo_digest`. Corré `$R dashboard` y respondé en el formato de digest.

### SCAN: semanal, con presupuesto cerrado

1. El presupuesto es de 6 búsquedas y 15 páginas, solo sobre los temas Tier 1 de `perfil.md` y las apuestas abiertas.
2. Buscá herramientas que **reemplacen** algo de `stack.md`, casos replicables de empresas parecidas, señales de clientes, eventos en los próximos 60 días e ideas de distribución.
3. Cada hallazgo pasa por `$R capture <url> --source scan --note "<por qué>"` y queda en el inbox para TRIAGE. Cero hallazgos es un resultado válido.

### Correcciones: el usuario dice "no, esto era X"

1. `$R label <id o url> <VEREDICTO> --por-que "<lo que dijo>"`, y registrá también la línea corregida con `$R log`.
2. Cada 20 etiquetas nuevas, corré `$R eval` y mencioná en el digest el acierto del filtro y los desacuerdos repetidos. Si el radar se equivoca 3 veces por el mismo motivo, proponé una regla para `criterios.md`.

## Juicio

Escribí una línea JSON por ítem:

```json
{"id": "…", "veredicto": "CANDIDATO", "etapa": "triage", "capa": "orquestacion",
 "capacidad": "context-efficiency", "pregunta": "stack", "evidencia": "demo",
 "durabilidad": "media", "reversible": true, "reemplaza": "nada",
 "por_que": "reduce contexto en sesiones largas (afirmado por el autor)",
 "proximo_paso": "probar en 1 sesión real y medir tokens", "revisar_si": null}
```

1. **Ubicalo en una capa y una capacidad del mapa.** Si no entra en ninguna, es DROP con `capa: "ninguna"` y por qué "no sé para qué sirve".
2. **Pasalo por las 3 preguntas.** Si las tres dan no, es DROP con `pregunta: "ninguna"`.
3. **Asigná la evidencia con la escalera** sin-fuente → anecdota → demo → adopcion → medido → verificado. El motor rechaza estos casos:
   - ADOPT sin `verificado` o `medido`;
   - TEST con `anecdota` o `sin-fuente`;
   - WATCH sin `revisar_si`;
   - un ítem que pasa con `pregunta: "ninguna"`;
   - CANDIDATO fuera de triage o scan.
4. **Sumá los filtros extra.** Resta antes que suma, durabilidad, costo por cliente, reversibilidad y seguridad.

## Formato de respuesta

CAPTURE, en Telegram y como máximo 4 líneas:

```
TEST · Orquestación / Context Efficiency
Qué cambia: podría bajar ~30% de tokens en sesiones largas (afirmado por el autor, no medido)
Evidencia: demo · Durable: media · Reversible: sí
Próximo paso (≤30 min): probarlo en 1 sesión real y comparar tokens
```

Si es DROP: `DROP · <motivo en 1 línea>`.

DIGEST:

```
Radar semana SS: X señales de N revisados
1. ADOPT · <capa/capacidad>: <qué cambia> · evidencia <nivel> · paso: <≤30 min>
2. TEST · … (abre EXP-00N, corte AAAA-MM-DD)
Experimentos: a/3 · <el que vence y cuándo>
<alertas de digest-data, una por línea>
Propuestas que esperan tu sí: <lista corta>
```

Si no hay señales: `Radar semana SS: 0 señales de N. Nada cambia una decisión. Seguí con lo tuyo.`

## Pitfalls

- **Investigar herramientas en vez de capacidades.** "Probar X" se reformula como "¿qué capacidad necesito y X es la mejor forma?". Para eso está `capability-first`.
- **Confundir popularidad con evidencia.** Un post viral es una anécdota. Los números del autor van como "afirmado por el autor".
- **Sumar sin restar.** Gana lo que **elimina** un componente.
- **Rabbit holes.** Muchos links del mismo tema sin prueba es acumular, no aprender. `$R alerts` lo detecta.
- No guardes tokens, cookies ni datos de terceros. No te loguees en sitios para leer un post.

## Verification

- `$R log` aceptó todas las líneas sin `--force`.
- `$R next -n 1` ya no devuelve los ítems juzgados.
- `$R exp list` tiene como máximo 3 activos.
- Si el digest no tiene señales, dice explícitamente "0 señales".
