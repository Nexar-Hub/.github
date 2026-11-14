---
name: goal-contract
description: Convierte un pedido de construcción en un contrato verificable (estado final, evidencia, restricciones, presupuesto), elige el verificador antes de correr y supervisa a Claude Code / Codex como loop externo hasta que el verificador pase. Usar cuando hay que construir, arreglar o automatizar algo con un agente de código, o el usuario dice "armá", "implementá", "dejalo funcionando", "/goal".
version: 2.0.0
author: Nexar Hub
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [loop-engineering, coding, delegation, verification, claude-code, codex]
    category: radar
---

# Goal Contract

Un buen agente puede seguir escribiendo. Un buen sistema sabe cuándo hacerlo seguir intentando.

Esta skill no reemplaza a Claude Code ni a Codex, porque ya traen su propio loop. Lo que agrega es el **contrato**, el **verificador** y el **loop externo**.

## Cuándo usar

- Hay que construir, arreglar o automatizar algo en un repo.
- Una tarea va a correr sola mucho tiempo, sea por cron o de noche.

**¿Loop existente o agente propio?** Si el loop de Claude Code o Codex alcanza para la tarea, se usa ese, adaptado con instrucciones, skills y hooks. Un agente propio se diseña solo cuando el agente es parte del producto y hay que controlar el workflow paso a paso. Por ejemplo, cuándo pide aprobación antes de reembolsar.

## Procedimiento

### 1. Escribí el contrato

```
C="python3 ${HERMES_SKILL_DIR}/scripts/contract.py"
$C new <slug> --dir runs        # crea runs/AAAA-MM-DD-<slug>.md con la plantilla
```

Completá en ese archivo: el objetivo como estado final observable, las restricciones (scope, qué no tocar, sin push/merge/deploy sin aprobación, rama o worktree), el presupuesto y el criterio de corte.

En **Evidencia requerida**, escribí una línea por chequeo con el formato `` - `comando` ``. Por ejemplo `` - `npm test` ``, `` - `npx tsc --noEmit` `` o `` - `python3 bench.py --max-ms 200` ``. Lo que no se puede expresar como comando (un screenshot, una revisión humana) va como texto: queda NOT TESTED, nunca PASS.

**Lo que el agente dice sobre su propio trabajo no cuenta como evidencia. Si no existe un verificador, el primer paso es crearlo.**

### 2. Prototipá antes de comprometerte

Usá esto solo si el camino no es obvio.

- **Interfaz**: "Generá 5 propuestas funcionales en una única página para compararlas. No conectes el backend todavía."
- **Sistema**: "Diseñá 5 arquitecturas en diagramas Mermaid. Para cada una mostrá el flujo de datos, la fuente de verdad, los puntos de falla y los tradeoffs."
- **Oferta**: "Generá 5 formas de empaquetarla. Para cada una mostrá promesa, scope, entregables, exclusiones y mecanismo de medición."

### 3. Planificá en forma crítica

Pasá este prompt:

> "Antes de implementar, interrogá la propuesta. Identificá requisitos faltantes, edge cases, riesgos, decisiones irreversibles, dependencias, problemas de seguridad y criterios de aceptación. No escribas código todavía."

### 4. Implementá de forma autónoma

Trabajá en una rama o un worktree aislado. Hay dos formas de correr al agente:

- Con las skills de Hermes para Claude Code o Codex, si están instaladas.
- Desde la terminal: `claude -p "<prompt>"` o `codex exec "<prompt>"`, siempre dentro del repo.

El prompt de implementación es:

> "Implementá el plan completo. Trabajá de forma autónoma dentro del repositorio. Ejecutá typecheck, tests, build y validaciones después de cada etapa. No marques una tarea como terminada sin evidencia verificable."

### 5. Corré el loop externo

Despertá, inspeccioná el progreso y juzgá con el script:

```
$C verify runs/<run>.md --cwd <repo>    # exit 0 solo si todos los chequeos pasan
```

El resultado, con la salida de lo que falló, se agrega al archivo del run. Mandá la siguiente instrucción con esos errores y repetí hasta PASS o hasta que se agote el presupuesto.

- Si el mismo error aparece 2 veces seguidas, cambiá de estrategia. No reintentes igual.
- Si el contexto se degrada, cortá la sesión, resumí el estado en la Bitácora del run y arrancá una sesión limpia. Una señal es que el agente pierde instrucciones básicas.
- Para correrlo solo, de noche: `hermes cron create "every 2h" "Seguí el contrato runs/<run>.md hasta PASS" --skill goal-contract --workdir <repo> --repeat 6`.

### 6. Hacé la revisión humana

El usuario no aprueba cada comando. Revisa cinco cosas:

1. Si resuelve el problema correcto.
2. Si el diseño tiene calidad.
3. Si la experiencia es clara.
4. Si sirve al negocio.
5. Si aceptó algo mediocre solo porque funciona.

### 7. Pedí una revisión cruzada a otro modelo

> "Revisá esta implementación como un revisor externo escéptico. Buscá errores funcionales, deuda técnica, problemas de UX, seguridad, accesibilidad, rendimiento y casos límite. No modifiques nada todavía. Ordená los hallazgos por impacto y evidencia."

### 8. Dejá los artefactos

En el archivo del run quedan: los comandos corridos y su resultado, el diff, los screenshots, el costo estimado y las decisiones tomadas. Si un error se repitió 3 veces entre runs, pasalo a `session-distill`, que lo convierte en una regla de una línea en el AGENTS.md o CLAUDE.md del proyecto.

## Pitfalls

- Usar un verificador elegido después de ver el resultado. Eso no es un verificador.
- Hacer push, merge, deploy o publicar sin aprobación explícita. Nunca.
- Armar un mega flujo con 10 agentes. Conviene empezar con un ejecutor y un juez, y sumar escuadrones chicos por especialidad solo cuando se hayan probado.
- Sobreconfigurar. Lo mínimo es permitir lo rutinario, negar lo peligroso y preguntar por el resto.

## Verification

- El contrato existe y fija el verificador antes de la primera ejecución.
- La última `## Verificación` del archivo dice PASS (`$C status runs/<run>.md`).
- El reporte final marca cada criterio como **PASS**, **FAIL** o **NOT TESTED**, con el comando y la salida que lo respaldan.
- No hubo acciones irreversibles sin aprobación.
