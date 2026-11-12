---
name: session-distill
description: Destila sesiones pasadas de Hermes, Claude Code, Codex y chats exportados (ChatGPT/Claude) en errores repetidos → reglas de una línea, workflows repetidos → skills (verbos) y preferencias estables → memoria. Propone borradores y guarda solo con aprobación. Usar cuando el usuario pide "destilá mis sesiones", "qué aprendimos", "convertí esto en skill", o en el cron mensual.
version: 1.0.0
author: Nexar Hub
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [memory, skills, learning, sessions, distill]
    category: radar
---

# Session Distill

El valor de la memoria no está en recordar más. Está en que el agente cometa **menos veces los mismos errores** y reutilice **más rápido** lo que ya salió bien.

La regla de 3 es simple: si algo aparece 3 veces, se promueve.

## Cuándo usar

- Pedido explícito, o cron mensual.
- Después de cerrar un proyecto o un experimento.

## Fuentes

Leé solo las que existan. Nunca cargues todo el historial al contexto: buscá y muestreá.

| fuente | dónde |
|---|---|
| Hermes | tool `session_search` (`~/.hermes/state.db`) |
| Claude Code | `~/.claude/projects/**/*.jsonl` |
| Codex | `~/.codex/sessions/**/*.jsonl` |
| ChatGPT y Claude exportados | `conversations.json` en `sesiones/` del workspace, si el usuario los dejó ahí |
| Notas propias | `inbox/thoughts.jsonl` del radar |

## Procedimiento

1. **Definí la ventana**: los últimos 30 días, salvo que el usuario pida otra.
2. **Buscá señales con grep o jq**, no leyendo todo:
   - correcciones del usuario: "no", "otra vez", "te dije", "mal", "revertí", "eso no", "de nuevo";
   - tool calls fallidas y reintentos;
   - el mismo pedido escrito 3 o más veces;
   - secuencias de pasos que se repiten entre proyectos.
3. **Clasificá cada patrón** con su evidencia (fecha o id de sesión, y cantidad de veces):

   | tipo | se convierte en | destino |
   |---|---|---|
   | error repetido (≥3) | regla de 1 línea | `AGENTS.md` o `CLAUDE.md` del proyecto donde ocurrió |
   | workflow repetido (≥3) | skill con nombre de verbo (`auditar-landing`, `publicar-reel`, `armar-propuesta`) | `~/.hermes/skills/<categoria>/<verbo>/SKILL.md` |
   | preferencia estable | 1 línea de memoria | memoria `user` de Hermes (USER.md tiene un límite de ~1.375 caracteres) |
   | decisión tomada | entrada con su "qué la revertiría" | `decisiones.md` del radar |

4. **Redactá los borradores.** Cada skill lleva frontmatter (`name`, `description`, `version`, `metadata.hermes.tags`) y las secciones When to Use, Procedure, Pitfalls y Verification. Separá lo **verificado** (funcionó en una sesión real) de lo **no probado** (recomendación).
5. **Mostrá todo antes de guardar.** Guardá solo lo que el usuario apruebe. Si Hermes tiene `skills.write_approval` o `memory.write_approval` activos, respetalos.
6. **Consolidá.** Una regla nueva reemplaza o fusiona a otra parecida, en vez de sumarse. Si `CLAUDE.md` o `AGENTS.md` crecen más de lo necesario, proponé qué borrar.
7. Guardá el informe en `destilados/AAAA-MM-DD.md` del workspace del radar.

## Pitfalls

- No copies secretos, tokens, emails ni datos de clientes que aparezcan en los transcripts. Redactalos.
- No conviertas un caso único en una regla. Menos de 3 apariciones es una anécdota.
- No sobreconfigures. Un `CLAUDE.md` de dos líneas que se respeta vale más que uno de doscientas que se ignora.
- La popularidad no hace correcto a un método. Que un workflow aparezca en muchos tutoriales no cuenta como evidencia.

## Verification

- Cada propuesta cita al menos 3 apariciones con fecha o id.
- Nada se guardó sin aprobación.
- Las instrucciones del proyecto quedaron igual de cortas o más cortas, salvo que la regla nueva tenga justificación.
