# GTD + programación con IA + bloques de tiempo: prueba de concepto

Prueba ejecutable, **solo con datos ficticios**, de un sistema donde Claude lee fichas de un vault de
Obsidian, propone bloques horarios alrededor de los compromisos del calendario y la persona
acepta, edita o rechaza cada bloque. No toca ningún vault real, calendario real ni servidor permanente:
todo corre en `./work` y se borra al volver a correr.

```bash
./setup.sh                          # ~1 min: compila OpenTodo y baja Horolog en commits fijados, venv con versiones fijas
source .deps/env.sh && ./run_demo.sh   # ~1 min: los 8 pasos desde cero, 42 chequeos, capturas en work/capturas
```

Requisitos: git, Go 1.24+ (descarga solo el toolchain 1.27), Node 22+ con `playwright` (para las capturas), Python 3.12+.

## Qué hace cada pieza (no se reconstruye nada que ya exista)

```
 Obsidian (fuente de verdad)                 OpenTodo (capa de tiempo)                     Calendario
 ──────────────────────────                  ──────────────────────────                    ──────────
 10-Empresas/<E>/Proyectos/<ficha>.md  ◄─┐   proyectos y tareas, estimación, energía       Principal (solo lectura)
   estado · prioridad · quien · …        │   vista Día / Semana / Plan, filtro @propuesta   │ CalDAV / Google
 Acciones/<ficha>.md  ◄──── ot vault ────┼──►tareas ↔ líneas «- [ ] … [time:: ] 🆔»         ▼
   ficha: "[[<ficha>]]"   (bidireccional)│   historial por campo, papelera                 eventos → «ocupado»
   - [ ] acción [estimate:: 45m]         │   Replanificar (bloques atrasados de hoy) ────► Bloques (escritura)
                                         │   MCP (token agent)                              un evento por bloque
 planificar.py ──── lee fichas ──────────┘        ▲          │
   prioridad = prioridad/clase/negocio            │ schedule_tasks + etiqueta «propuesta»
   Horolog solve(intents, ocupado, previo) ───────┘ lotes/*.json → revertir
```

| Pieza | Qué resuelve | Qué se escribió acá |
|---|---|---|
| **OpenTodo** (AGPL, Go + SQLite, un binario) | Tareas, Día/Semana, sincronización con calendario (CalDAV, Google, Microsoft), sincronización bidireccional con Markdown (`ot vault`), MCP con permisos de escritura, historial, Replanificar con vista previa y Deshacer | Nada |
| **Horolog** (solo `horolog.solver.solve`, función pura, pydantic) | Dónde cae cada bloque, alrededor de lo ocupado, con prioridad, ventanas de energía y fecha límite, moviendo lo mínimo respecto del plan anterior | Nada |
| `capturar.py` (88 líneas) | Idea de la nota diaria → ficha (regla del vault: una idea suelta es una ficha con `prioridad: después`) → `Acciones/<ficha>.md` | Pegamento |
| `planificar.py` (~400 líneas con comentarios) | Traduce fichas + tareas + eventos → intents de Horolog → `schedule_tasks`; marca `propuesta`; guarda un lote por corrida para revertir | Pegamento |
| `demo.py`, `run_demo.sh`, `capturas.mjs` | La prueba: 8 pasos, 42 chequeos, capturas reales de la interfaz | Solo prueba |

## Protocolo de revisión (en la interfaz de OpenTodo, sin interfaz nueva)

- **Ver lo que falta revisar:** Calendario → ⋯ → Filtrar… → `@propuesta`.
- **Aceptar:** sacarle la etiqueta `propuesta` (o selección múltiple → Etiquetas).
- **Editar:** arrastrar el bloque, o cambiar `[time:: ]` en `Acciones/<ficha>.md`. Cuenta como aceptarlo con tu horario.
- **Rechazar:** ponerle la etiqueta `rechazada`. La corrida siguiente lo saca del calendario y no lo vuelve a proponer.
- **Deshacer una corrida del planificador:** `planificar.py revertir <lote>`. Solo revierte la hora y la etiqueta `propuesta`, y saltea lo que la persona tocó después.

## Los 8 pasos que prueba `run_demo.sh`

1. **Captura:** una línea `- Idea: … (Faro)` de `Diario/2026-11-21.md` se vuelve una ficha. La línea queda enlazada, y capturar dos veces no duplica.
2. **Proyecto con próximas acciones:** se escribe `Acciones/<ficha>.md`. `ot vault` crea 4 proyectos y 11 tareas, y la segunda sincronización no crea nada. El proyecto es secuencial, así que solo la primera acción está disponible.
3. **Calendario:** 4 compromisos ficticios en un CalDAV local (Radicale), cargados dos veces sin duplicarse. OpenTodo los lee y `find_free_time` los saca del tiempo libre.
4. **Propuesta:** Horolog arma 7 bloques. Ninguno pisa un compromiso, `[energy:: deep]` va solo a la mañana, no se agenda la ficha bloqueada y se avisa lo que no tiene estimación. Correrlo dos veces no cambia nada, y cada bloque está una sola vez en el calendario «Bloques».
5. **Visual:** capturas de Semana y Día.
6. **Reunión imprevista:** se mueve solo el bloque que choca. Revertir el lote lo devuelve a su lugar, y replanificar da lo mismo otra vez. El evento se mueve, no se duplica.
   **6b.** «Replanificar» nativo de OpenTodo, con vista previa, mueve los bloques atrasados de hoy sin pisar una llamada nueva.
7. **Revisión:**
   - Aceptada: queda fija.
   - Editada en la app: se respeta la hora.
   - Editada en Obsidian: `[time:: ]` llega a OpenTodo.
   - Rechazada: sale del calendario y no vuelve.
   - El filtro `@propuesta` muestra solo lo pendiente.
8. **Sincronización y reversa:**
   - El calendario «Bloques» tiene tantos eventos como tareas con hora, sin UID repetido.
   - El calendario principal nunca se escribe.
   - Revertir todo deshace lo del planificador y respeta lo que tocó la persona.

## Limitaciones verificadas (OpenTodo 1.6.0, commit `fc5169e`)

1. **`ot vault` sincroniza una carpeta con toda la cuenta.** Si apuntás una carpeta a cada `10-Empresas/*/Proyectos/`, cada carpeta recibe los proyectos de las otras (primera corrida de esta prueba). Un token limitado a workspaces no sirve: `/api/v1/sync` responde `403 token_restricted` (docs/api.md). Por eso las acciones viven en una sola carpeta, `Acciones/`, y la ficha queda donde estaba.
2. **`opentodo-flow: sequential` se ignora en un archivo nuevo:** el proyecto se crea paralelo y la clave se borra. Agregarla después de la primera sincronización sí funciona. `capturar.secuencial()` hace eso.
3. **Las propuestas no se distinguen a simple vista en Día/Semana** (la etiqueta no se dibuja en el bloque). Lo resuelve el filtro nativo `@propuesta`, que se guarda en cada dispositivo.
4. **Los cambios por MCP se aplican directamente** y se deshacen desde el historial. La revisión con forma de calendario de OpenTodo (editar, Aplicar, Deshacer) existe solo para su asistente integrado, que necesita una clave de proveedor de IA. No se probó porque no hay clave.
5. **«Replanificar» nativo solo mueve bloques atrasados de hoy.** Un choque con una reunión de mañana solo marca la superposición. Ese caso lo cubre `planificar.py` con Horolog.
6. **La sincronización de calendario escribe toda tarea con fecha**, también las propuestas, en el calendario elegido. Se filtra por workspace o proyecto, no por etiqueta.
7. **Google Calendar** necesita que el dueño del servidor cree un cliente OAuth y habilite la API CalDAV (unos 10 minutos). En modo Testing, el acceso vence a los 7 días. OpenTodo marca a Google como «no verificado» contra el servicio real. Esta prueba usó CalDAV local. La alternativa solo lectura es la dirección iCal secreta de Google como feed, que se refresca cada hora.
8. **Horolog es joven:** 0.2.0 beta, 29 commits en 5 días de agosto de 2026, AGPL. Se usa solo el solver, fijado por commit, y el pegamento es lo único que lo conoce.
9. **Lo que no modela el planificador:** el tope de horas por día y los colchones entre bloques. El lunes quedó con 4 h 45 m seguidas.
10. **No probado:**
    - el plugin de Obsidian (enviar línea y carpeta en el celular): requiere Obsidian;
    - Google y Microsoft reales;
    - el asistente integrado de OpenTodo;
    - Windows: el servidor y `ot vault watch` tienen que quedar corriendo en algún lado.
