# Radar de Leverage para Hermes Agent

Un kit mínimo que convierte el grupo de WhatsApp donde se guardan links en un **radar que solo avisa cuando algo cambia una decisión, mejora el stack o abre una apuesta**.

Está pensado para [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research). Los comandos de este README se revisaron contra los docs del repo de Hermes (v0.23.x, noviembre de 2026). Si tu versión es otra, confirmalos con `hermes --help`.

```
WhatsApp / Telegram ──► inbox ──► TRIAGE (modelo barato, diario) ──► CANDIDATO / DROP
                                                     │
                       DIGEST (modelo fuerte, semanal) ◄─┘──► Telegram: ≤5 señales
                                                     │
                     ADOPT ─► propuesta en stack/decisiones (con tu "sí")
                     TEST  ─► experimentos.md (máx 3, 20–40 min por sesión)
```

## Qué hay acá

| ruta | qué es |
|---|---|
| `skills/radar/leverage-radar/` | Skill principal (CAPTURE, INGEST, TRIAGE, DIGEST, SCAN), con sus criterios, el mapa de capacidades y los scripts |
| `skills/radar/leverage-radar/scripts/whatsapp_to_inbox.py` | Pasa un export de WhatsApp a `inbox.jsonl`: deduplica, normaliza URLs, ordena por prioridad. Sin red y sin LLM |
| `skills/radar/leverage-radar/scripts/fetch_post.py` | Trae el texto de un post de X (fxtwitter, con oEmbed de respaldo) o los metadatos y el README de un repo de GitHub, sin navegador |
| `skills/radar/capability-first/` | Pasa de "investigá X" a capacidad → opciones → prueba mínima |
| `skills/radar/goal-contract/` | Arma un contrato verificable y deja a Hermes como loop externo de Claude Code o Codex |
| `skills/radar/session-distill/` | Aplica la regla de 3: errores repetidos se vuelven reglas, workflows repetidos se vuelven skills y preferencias estables se vuelven memoria |
| `workspace/` | Plantilla del workspace del radar: `AGENTS.md`, perfil, stack, decisiones, experimentos |

Tus datos personales (perfil completo, inbox, notas) **no van a este repo**, porque es público. Quedan en tu máquina, en el workspace. `.gitignore` bloquea `hermes/private/` y los archivos del inbox.

## Instalación (unos 10 minutos)

```bash
# 1. Kit
git clone https://github.com/Nexar-Hub/.github ~/src/nexar-hub-github

# 2. Workspace (también puede ir dentro de tu vault de Obsidian)
cp -r ~/src/nexar-hub-github/hermes/workspace ~/radar
mkdir -p ~/radar/{digests,runs,destilados}
#    → completá perfil.md, stack.md y decisiones.md (o pegá tu pack privado encima)
#    → corregí la línea KIT= en ~/radar/AGENTS.md si clonaste en otra ruta
```

Sumá las skills en `~/.hermes/config.yaml` sin copiarlas. Así, un `git pull` las actualiza:

```yaml
skills:
  external_dirs:
    - ~/src/nexar-hub-github/hermes/skills
```

Para comprobar que cargaron, abrí `hermes` y probá `/leverage-radar`. Si tenés una skill con el mismo nombre en `~/.hermes/skills/`, esa tiene prioridad.

**Windows:** si Hermes corre en WSL, cloná y creá `~/radar` dentro de WSL.

**Telegram:** si todavía no está, corré `hermes gateway setup`, elegí Telegram, ejecutá `/sethome` en el chat con el bot y dejá corriendo `hermes gateway`. Los cron jobs corren dentro del gateway.

## Primer uso

1. En WhatsApp, abrí el grupo y elegí **Exportar chat → Sin archivos**. Dejá el `.zip` en `~/radar/inbox/`.
2. En Hermes, abierto en `~/radar`, pedí: `/leverage-radar ingest`. El comando ejecuta esto:

   ```bash
   python3 ~/src/nexar-hub-github/hermes/skills/radar/leverage-radar/scripts/whatsapp_to_inbox.py \
     ~/radar/inbox/"WhatsApp Chat - Articles Twitter.zip" --out ~/radar/inbox
   ```

   Genera `inbox.jsonl` con un link único por línea, `thoughts.jsonl` con tus notas sin link y `inbox.md` con un resumen de temas y links compartidos más de una vez. Re-exportar más adelante es seguro: lo que ya se juzgó queda como `done`.
3. Desde ese momento, **mandá los links al bot de Hermes en vez de al grupo**: `/leverage-radar https://x.com/... nota opcional`. Te contesta el veredicto en 4 líneas, o `DROP · motivo`.

## Cron jobs

`--workdir` hace que el job cargue el `AGENTS.md` del radar. `--model` fija un modelo por job: el barato para filtrar y el fuerte solo donde hay más incertidumbre.

```bash
# Filtro diario, silencioso (no manda nada a Telegram)
hermes cron create "daily at 8am" \
  "Modo TRIAGE: procesá hasta 15 ítems nuevos del radar." \
  --skill leverage-radar --workdir ~/radar --model <modelo-barato> --deliver local

# Digest semanal, el único que te escribe
hermes cron create "0 9 * * 1" \
  "Modo DIGEST: juzgá los CANDIDATO de la semana y mandame el digest." \
  --skill leverage-radar --workdir ~/radar --deliver telegram

# Scan semanal con presupuesto cerrado (opcional)
hermes cron create "0 9 * * 4" \
  "Modo SCAN: buscá novedades en mis temas Tier 1 y apuestas abiertas." \
  --skill leverage-radar --workdir ~/radar --model <modelo-barato> --deliver local

# Destilado mensual de sesiones (opcional)
hermes cron create "0 10 1 * *" \
  "Destilá mis sesiones de los últimos 30 días y mostrame las propuestas." \
  --skill session-distill --workdir ~/radar --deliver telegram
```

Para verificar y operar los jobs:

- `hermes cron list`: lista los jobs.
- `hermes cron run <id>`: corre un job ahora.
- La salida queda en `~/.hermes/cron/output/<id>/`.

Si el modelo barato lo provee un proveedor distinto del principal, sumá `--provider`.

## Memoria

Hermes inyecta `~/.hermes/memories/USER.md`, con un límite de unos 1.375 caracteres, al inicio de cada sesión. Dejá ahí solo lo que cambia el juicio en cualquier conversación: quién sos, el norte y 3 principios. El resto vive en el workspace, que no tiene ese límite. No pises tu USER.md actual: agregale contenido o pedile a Hermes que lo fusione.

## Diseño

Estas reglas salen de las notas que dieron origen al radar:

- **El radar no trae más información.** Lo normal es quedarse en silencio: el digest muestra 5 señales como máximo y DROP nunca avisa.
- **Capability first.** Nada se evalúa como herramienta suelta. Todo se ubica en una capa (identidad, distribución, conversión, aprendizaje u orquestación) y en una capacidad.
- **Evidencia antes que entusiasmo.** La escalera va de sin-fuente a anécdota, demo, adopción, medido y verificado. Para ADOPT hace falta una prueba propia.
- **Pruebas acotadas.** Hay 3 experimentos activos como máximo, con bloques de 20 a 40 minutos y cierre obligatorio en ADOPT o DROP.
- **Anti rabbit hole.** El digest avisa cuando guardás muchos links del mismo tema sin probar ninguno.
- **Lo determinístico va en scripts.** Parsear, deduplicar y traer texto no gasta tokens. El LLM solo pone juicio.
- **Mínimo de configuración.** Son 4 skills que cargan bajo demanda, sin MCPs nuevos ni servicios extra.

## Pruebas

```bash
python3 -I skills/radar/leverage-radar/scripts/whatsapp_to_inbox.py --self-test
python3 -I skills/radar/leverage-radar/scripts/fetch_post.py --self-test
```

`fetch_post.py` se probó en vivo contra READMEs de GitHub. La rama de X (fxtwitter y oEmbed) solo tiene pruebas con datos simulados, porque el sandbox donde se armó no llega a esos hosts. Si falla en tu máquina, la skill cae sola en `web_extract` o en el navegador.
