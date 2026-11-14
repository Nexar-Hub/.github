# Radar de Leverage para Hermes Agent

Convierte el grupo de WhatsApp donde guardás links en un radar que **solo te escribe cuando algo cambia una decisión, mejora tu stack o abre una apuesta**. Todo lo demás lo descarta en silencio.

```
mandás un link al bot ──► el radar lo guarda y te da el veredicto en 4 líneas
todos los días        ──► un modelo barato filtra lo nuevo (si no hay nada nuevo, no gasta)
todos los días        ──► alertas sin LLM: rabbit holes, experimentos vencidos, radar parado
los lunes             ──► el único mensaje: máximo 5 señales, con el próximo paso de cada una
cuando quieras        ──► dashboard.html: el panel visual, desde el celular
```

## Instalar (3 comandos)

En la máquina donde corre Hermes. En Windows, desde Git Bash o WSL.

```bash
git clone https://github.com/Nexar-Hub/.github ~/src/nexar-hub-github
bash ~/src/nexar-hub-github/hermes/install.sh --private ~/Downloads/radar-privado.zip --cron \
     --cheap-model <modelo-barato> --cheap-provider <proveedor>
bash ~/src/nexar-hub-github/hermes/install.sh --doctor
```

El instalador hace estas cinco cosas y nada más:

- Crea `~/radar` sin pisar nada que ya hayas editado.
- Carga tu pack privado.
- Agrega las skills a Hermes, con backup de `config.yaml`.
- Copia 2 scripts a `<HERMES_HOME>/scripts/`.
- Crea 5 cron jobs, y si ya existen no los duplica.

No toca tu memoria, tu SOUL.md ni tus tokens. `--doctor` muestra en verde lo que funciona y en amarillo lo que falta.

Sin `--private`, el workspace arranca con plantillas para completar. Sin `--cron`, no se programa nada. Si no le pasás `--cheap-model`, todo usa tu modelo principal.

## Usarlo

| querés… | hacés… |
|---|---|
| evaluar un link | mandale al bot `/leverage-radar https://… tu nota` |
| cargar todo lo que ya guardaste | WhatsApp → Exportar chat → Sin archivos → dejá el `.zip` en `~/radar/inbox/` → `/leverage-radar ingest` (si tu pack privado ya trae `inbox/`, saltealo) |
| vaciar el backlog la primera vez | `hermes cron create "every 30m" "Modo TRIAGE: lote de 20." --skill leverage-radar --workdir "$HOME/radar" --model <barato> --repeat 32 --deliver local`: unos 640 ítems en 16 horas, y después se borra solo |
| saber si el radar respeta lo que vos ya marcaste | `radar.py gold-from-notes` y después `radar.py eval --gold evals/gold-debil.jsonl`: qué porcentaje de tus "Bible", "10/10" y "clave" deja pasar |
| ver el panel | `/leverage-radar dashboard` → abrí `~/radar/dashboard.html` |
| corregir al radar | "no, esto era TEST porque…": queda guardado y mejora la medición |
| construir algo con Claude Code o Codex | `/goal-contract`: contrato + verificador; el juez es un script, no el agente |
| aprender de tus sesiones | `/session-distill`: lo que se repite 3 veces se propone como regla o skill |
| evaluar una herramienta | `/capability-first`: capacidad → opciones (incluida "no hacer nada") → prueba mínima |

## Qué corre solo

| job | cuándo | modelo | te escribe |
|---|---|---|---|
| `radar-triage` | todos los días, 8:00 | barato · **no corre si el inbox no cambió** (`--monitor-script`) | no |
| `radar-alertas` | todos los días, 9:00 | **ninguno** (`--no-agent`) | solo si hay una alerta |
| `radar-digest` | lunes, 9:00 | principal | sí: el digest semanal |
| `radar-scan` | jueves, 9:00 | barato, con presupuesto de 6 búsquedas | no (los hallazgos van al inbox) |
| `radar-destilado` | día 1 de cada mes | principal | sí: propuestas para aprobar |

Para revisarlos: `hermes cron list`. Para correr uno ya: `hermes cron run <id>`. Para pausar uno: `hermes cron pause <id>`.

## Cómo está hecho

El modelo solo pone el juicio. Todo lo mecánico es código determinístico (Python stdlib, sin dependencias):

| pieza | qué hace |
|---|---|
| `skills/radar/leverage-radar/scripts/radar.py` | El motor: ingest, captura con deduplicación, lotes, **validación de veredictos** (rechaza ADOPT sin evidencia, TEST sin cupo, WATCH sin disparador…), alertas, experimentos con máximo 3 activos, datos del digest, evals y dashboard |
| `…/whatsapp_to_inbox.py` | Pasa el export de WhatsApp (iOS o Android) a un inbox deduplicado, sin trackers ni números sueltos |
| `…/fetch_post.py` | Trae el texto de un post de X o los metadatos y el README de un repo de GitHub, sin navegador |
| `skills/radar/goal-contract/scripts/contract.py` | `new` crea el contrato. `verify` corre los chequeos y registra PASS, FAIL o NOT TESTED |
| `skills/radar/session-distill/scripts/distill_sessions.py` | Lee Claude Code, Codex y Hermes (`state.db`, en modo solo lectura) y agrupa correcciones, pedidos y errores repetidos, con los secretos redactados |
| `install.sh` | Instalación idempotente y diagnóstico con `--doctor` |
| `workspace/` | Plantillas: `AGENTS.md`, perfil, stack, decisiones, experimentos |

Tus datos (perfil, inbox, veredictos, correcciones) viven solo en `~/radar`. Este repo es público y nunca los recibe.

## Medir al radar

Cada vez que corregís un veredicto, la corrección queda en `evals/gold.jsonl`. Con eso:

```bash
R=~/src/nexar-hub-github/hermes/skills/radar/leverage-radar/scripts/radar.py
cd ~/radar && python3 $R eval
```

Muestra el acierto del filtro, la precisión y el recall de lo que pasa, el veredicto exacto y los desacuerdos.

Para comparar dos modelos (EXP-002: local vs nube): copiá el workspace dos veces, corré TRIAGE en cada copia con un modelo distinto y comparalas con

```bash
python3 $R eval --compare A/radar-log.jsonl B/radar-log.jsonl
```

El resultado incluye acuerdo, kappa y la lista de desacuerdos.

Para ver todo funcionando antes de tener datos propios: `python3 $R demo /tmp/radar-demo` genera un workspace sintético y su dashboard.

## Verificado contra Hermes

Revisé el código fuente de Hermes Agent (commit `18ea4218`, 14/11/2026). Esto es lo confirmado:

- `skills.external_dirs` acepta rutas con `~` y `${VAR}`. La precedencia es proyecto, después `~/.hermes/skills`, después `create_dir` y por último las rutas externas.
- `${HERMES_SKILL_DIR}` se reemplaza dentro de SKILL.md (`skills.template_vars: true` por defecto).
- El nombre de una skill solo admite `a-z0-9._-` y hasta 64 caracteres. La descripción admite hasta 1.024 caracteres. `platforms` acepta `[macos, linux, windows]`.
- `hermes cron create` acepta `--skill` (repetible), `--workdir` (**ruta absoluta y existente**: carga el `AGENTS.md` de ese directorio), `--model`/`--provider`, `--deliver`, `--monitor-script` (si la salida del script no cambia, el agente no corre), `--no-agent --script` (sin LLM; si la salida está vacía, no manda nada), `--continuity`, `--repeat`, `--timezone` y `--name`.
- Los horarios aceptan formas como `daily at 8am`, `every monday 9am`, `weekdays at 9am` y expresiones cron.
- Los scripts de cron **tienen que estar dentro de** `<HERMES_HOME>/scripts/`: un symlink hacia afuera se bloquea. Por eso el instalador copia wrappers.
- La memoria `USER.md` tiene un límite de 1.375 caracteres y `MEMORY.md` de 2.200.
- `HERMES_HOME` es `~/.hermes` en macOS y Linux, y `%LOCALAPPDATA%\hermes` en Windows nativo. El instalador lo pregunta con `hermes config path`.

Lo que **no** probé:

- Ejecutar Hermes en sí. No pude instalarlo en el entorno donde se armó esto; el instalador se probó contra un `hermes` falso (`tests/hermes-stub`).
- El fetch de X (fxtwitter y oEmbed) contra la red real.
- El formato de Codex y de los exports de ChatGPT con archivos reales.

Si algo de esto falla, `--doctor` y los scripts lo dicen. Ninguno inventa un PASS.

## Pruebas

```bash
bash hermes/tests/run.sh
```

Corre los self-tests, valida las skills con las reglas de Hermes, hace una instalación completa contra el stub (incluida la segunda corrida, para confirmar que es idempotente) y genera el dashboard demo. CI lo corre en Ubuntu y en macOS (bash 3.2).
