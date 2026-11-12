# Nexar-Hub/.github

Repo de organización de **Nexar Hub**. Tiene tres funciones:

1. **Perfil público** de la organización en GitHub → `profile/README.md`
2. **Contexto legible por personas y agentes** sobre cómo piensa, decide, diseña y trabaja Nexar → `brain/`
3. **Defaults para todos los repos** de la organización: plantillas de issues y PRs → `.github/`, y plantilla de proyecto web → `templates/`

## Estructura

```
AGENTS.md                         Contrato de entrada para agentes (Claude Code lo carga vía CLAUDE.md)
CLAUDE.md                         Importa AGENTS.md
profile/README.md                 Perfil público de la organización
brain/
  nexar.md                        Qué es Nexar: posicionamiento, oferta, cliente ideal, qué no hacemos, principios, stack
  taste.md                        Qué diseños le gustan a Nexar: color, tipografía, layout, imagen, motion, método
  prompts.md                      Prompts que sobrevivieron uso real
  workflows/
    brand-project.md              Flujo de proyecto de marca con gates
    discovery.md                  Cuestionario de primera call (12 preguntas)
    website.md                    Blueprint de webs: intake → deploy → loop de optimización
    contenido.md                  Contenido y distribución (incluye flow de video IA)
templates/
  proyecto-web/                   Plantilla para cada cliente nuevo (BRIEF, DESIGN_SYSTEM, WORKFLOW, CHECKLIST, HANDOFF, SUPPORT_POLICY, CLAUDE.md)
.github/
  pull_request_template.md        Plantilla de PR por default para todos los repos
  ISSUE_TEMPLATE/task.yml         Formulario de tarea por default para todos los repos
```

## Cómo se usa

**Arrancar un proyecto web de cliente**

```bash
git clone https://github.com/Nexar-Hub/.github.git /tmp/nexar-hub
cp -r /tmp/nexar-hub/templates/proyecto-web/ ~/projects/cliente-nuevo/
```

Después seguir `templates/proyecto-web/README.md`.

**Darle contexto a un modelo**

- En este repo, Claude Code ya carga `AGENTS.md`.
- En cualquier otra herramienta, pasale `AGENTS.md` y después solo los archivos de `brain/` que la tarea necesita.

## Reglas del repo

- **Es público.** Nada de precios, datos de clientes, credenciales ni notas privadas. Eso va a un repo privado.
- Una sola versión de cada verdad: se edita el archivo existente.
- Nada entra si no viene de trabajo real o no mejora trabajo real.
- Imágenes de referencia: no se suben (son capturas de trabajo de terceros). Se documenta por qué funcionan en `brain/taste.md`.
