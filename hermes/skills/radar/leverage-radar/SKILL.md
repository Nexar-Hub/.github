---
name: leverage-radar
description: Radar de Leverage. Filtra links, posts, repos y videos guardados y avisa solo cuando algo cambia una decisión, mejora el stack o abre una apuesta. Usar cuando el usuario manda un link para evaluar, pide procesar el inbox del radar, importar un export de WhatsApp, el digest semanal o un scan de novedades.
version: 1.0.0
author: Nexar Hub
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [radar, research, triage, decisions, leverage, inbox]
    category: radar
---

# Leverage Radar

No busca maximizar información. Busca maximizar leverage.

Un ítem sirve solo si contesta **sí** a una de estas tres preguntas:

1. **¿Cambia una decisión?** Toca el "qué la revertiría" de algo en `decisiones.md`.
2. **¿Mejora el stack?** Cumple el "lo reemplazaría si…" de `stack.md`, o elimina un componente que hoy se mantiene a mano.
3. **¿Abre una apuesta?** Un cliente, una oferta, un caso replicable, un evento o un canal para un proyecto activo de `perfil.md`.

Si las tres son "no", el veredicto es DROP y no se avisa. Casi siempre el resultado correcto es no decir nada.

## Cuándo usar

- El usuario manda un link, con o sin nota, por Telegram o CLI: modo **CAPTURE**.
- Aparece un export de WhatsApp (`.zip` o `_chat.txt`) en `inbox/`: modo **INGEST**.
- Cron diario o "procesá el radar": modo **TRIAGE**.
- Cron semanal o "¿qué hay de nuevo?": modo **DIGEST**.
- Cron semanal de búsqueda activa: modo **SCAN**.

El modo lo define el prompt. Si no lo dice, un link suelto es CAPTURE y cualquier otro caso es TRIAGE.

## Workspace

Se trabaja dentro del directorio de trabajo del radar, el que tiene el `AGENTS.md` del radar. Por defecto es `~/radar` y puede vivir dentro del vault de Obsidian. Antes de juzgar cualquier cosa, leé:

- `perfil.md`: quién es el usuario, proyectos activos, temas Tier 1, 2 y 3, y qué queda afuera.
- `stack.md`: capacidad → implementación actual → "lo reemplazaría si…".
- `decisiones.md`: decisiones vigentes con su disparador de revisión.
- `experimentos.md`: pruebas abiertas, con un máximo de 3 activas.

Lo que escribe esta skill:

- `inbox/inbox.jsonl`: lo genera el script desde WhatsApp. Nunca se edita a mano.
- `inbox/capturas.jsonl`: links que llegan por chat o scan. Solo se agregan líneas.
- `inbox/processed.txt`: ids ya juzgados, uno por línea.
- `radar-log.jsonl`: un veredicto por línea. Solo se agregan líneas.
- `digests/AAAA-SS.md`: el digest de cada semana.

Los scripts están en `scripts/`, dentro de esta skill. Si no conocés la ruta, está en el `AGENTS.md` del workspace como `KIT`.

## Procedimiento

### INGEST

1. Corré `python3 <KIT>/skills/radar/leverage-radar/scripts/whatsapp_to_inbox.py inbox/<export>.zip --out inbox`.
2. El script deduplica, normaliza las URLs (saca `?s=48`, `igsh` y los trackers), descarta números sueltos y ordena por prioridad. Las notas sin link quedan en `inbox/thoughts.jsonl`.
3. Respondé solo con el resumen: cuántos links son nuevos, los 5 temas más guardados y los links compartidos más de una vez. No juzgues en este paso.
4. Revisá `thoughts.jsonl`. Si una nota es un principio o una decisión del usuario y no está en `decisiones.md`, proponela, pero no la escribas sin confirmación.

### CAPTURE (un link)

1. Agregá `{"id", "url", "notes": [nota], "first_seen", "source": "chat", "status": "new"}` a `inbox/capturas.jsonl`. El id son los primeros 12 caracteres del sha1 de la URL canónica.
2. Buscá el contenido con `scripts/fetch_post.py <url>`. Si devuelve `ok: false`, usá web_extract o el navegador. Para YouTube, bajá solo los subtítulos con `yt-dlp --skip-download --write-auto-subs`.
3. Aplicá el juicio completo (pasos 3 a 5 de TRIAGE) y respondé con el formato corto de abajo.

### TRIAGE (lote; está pensado para un modelo barato)

1. Tomá los próximos N ítems (por defecto 10) con `status: "new"` de `inbox/capturas.jsonl` y después de `inbox/inbox.jsonl`, en el orden del archivo, que ya está ordenado por prioridad. Salteá los ids que estén en `processed.txt`.
2. Buscá el contenido igual que en CAPTURE. Si no hay contenido, juzgá solo con la nota, usá evidencia `sin-fuente` y el veredicto máximo es WATCH.
3. Ubicalo en el mapa: una capa (identidad, distribución, conversión, aprendizaje u orquestación) y una capacidad de `references/mapa-de-capacidades.md`. Si no se puede ubicar, es DROP con el motivo "no sé para qué sirve".
4. Pasalo por las 3 preguntas. Si todas dan "no", es DROP con una línea de motivo.
5. Si pasa, completá `evidencia`, `durabilidad`, `costo`, `reversible` y `reemplaza` según `references/criterios.md`.
   - Con un modelo barato, el veredicto máximo es **CANDIDATO**. El DIGEST lo confirma.
   - En CAPTURE o con el modelo principal, el veredicto puede ser ADOPT, TEST, WATCH o DROP.
6. Registrá una línea por ítem en `radar-log.jsonl` y su id en `processed.txt`.
7. Al final respondé una sola línea: `TRIAGE: n revisados · k candidatos · d drop`. Agregá un detalle solo si hay un ítem con la pregunta "decision" en sí.

### DIGEST (semanal; usa el modelo fuerte)

1. Juntá los CANDIDATO de `radar-log.jsonl` desde el último digest y juzgá cada uno a fondo: ADOPT, TEST, WATCH o DROP. Cada veredicto final va como línea nueva en `radar-log.jsonl` con `etapa: "digest"`.
2. Un TEST entra a `experimentos.md` solo si hay menos de 3 activos. Si no hay lugar, queda en WATCH con `revisar_si: "cupo libre en experimentos"`.
3. Un ADOPT nunca edita `stack.md` ni `decisiones.md` directamente. Escribí la propuesta en el digest y esperá el "sí".
4. Corré los chequeos de `references/criterios.md`: rabbit holes, experimentos vencidos y WATCH cuyo disparador ya se cumplió.
5. Guardá `digests/AAAA-SS.md` y respondé con el formato de digest. Mostrá como máximo 5 señales.

### SCAN (semanal, con presupuesto cerrado)

- El presupuesto es de 6 búsquedas web y 15 páginas leídas. Al llegar al límite, cortá.
- Buscá solo en los temas Tier 1 de `perfil.md` y en las apuestas abiertas.
- Buscá estas cosas:
  - herramientas que reemplacen algo de `stack.md`;
  - empresas parecidas en otros mercados que hayan hecho algo replicable;
  - señales de clientes con el problema que resuelve una oferta;
  - eventos en los próximos 60 días;
  - ideas de distribución o ads para un proyecto activo.
- Cada hallazgo va a `inbox/capturas.jsonl` con `source: "scan"` y pasa por los mismos pasos 3 a 6 de TRIAGE. No inventes ni rellenes. Cero hallazgos es un resultado válido.

## Formato de respuesta

CAPTURE (Telegram, máximo 6 líneas):

```
TEST · Orquestación / Context Efficiency
Qué cambia: podría bajar ~30% de tokens en sesiones largas (afirmado por el autor, no medido)
Evidencia: demo · Durable: media · Reversible: sí
Próximo paso (≤30 min): probarlo en 1 sesión real de <proyecto> y comparar tokens
```

Si es DROP: `DROP · <motivo en 1 línea>`. Nada más.

DIGEST:

```
Radar semana SS: X señales de N revisados
1. ADOPT · <capa/capacidad>: <qué cambia> · evidencia <nivel> · paso: <≤30 min>
2. TEST · ...
Experimentos: a/3 activos · <exp que vence y cuándo>
⚠ Rabbit hole: <tag> n links / 0 pruebas en 14 días
Propuestas que esperan tu sí: <lista corta>
```

Si no hay señales: `Radar semana SS: 0 señales de N. Nada cambia una decisión. Seguí con lo tuyo.`

## Pitfalls

- **Investigar herramientas en vez de capacidades.** "Probar X" se reformula como "¿qué capacidad necesito y X es la mejor forma?". Para eso está la skill `capability-first`.
- **Confundir popularidad con evidencia.** Un post viral es una anécdota. Las estrellas de un repo son adopción, no calidad.
- **Afirmar causalidad.** Un "+40%" del autor se reporta como "afirmado por el autor", nunca como un hecho.
- **Sumar sin restar.** Cada herramienta nueva cuesta configuración, contexto y mantenimiento. Gana la que **elimina** un componente.
- **Rabbit holes.** Muchos links del mismo tema sin ninguna prueba es acumular, no aprender.
- **Hacks contra debilidades del modelo.** Duran meses. Puntúan bajo en durabilidad.
- No guardes tokens, cookies ni datos de terceros en el log. No te loguees en sitios para leer un post.

## Verification

- Toda línea de `radar-log.jsonl` tiene `veredicto`, `capa`, `pregunta` y `por_que`. Si el veredicto no es DROP, también tiene `proximo_paso`. Si es WATCH, también tiene `revisar_si`.
- Cada id juzgado está en `processed.txt`, así que un nuevo INGEST lo marca `done`.
- `experimentos.md` nunca tiene más de 3 activos.
- Si el digest no tiene señales, dice explícitamente "0 señales".
