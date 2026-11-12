# Mapa de capacidades

Todo ítem del radar se ubica en **una capa** y **una capacidad**. Si no se puede ubicar, probablemente todavía no se entiende para qué sirve.

El circuito funciona como un ciclo, no como una línea que termina:

**Identidad → Distribución → Conversión → Aprendizaje → Identidad**

La **Orquestación** conecta las cuatro capas. Es la infraestructura, no el producto que se vende.

## 1. Identidad (`identidad`)

Qué es la marca y por qué alguien debería prestarle atención.

| capacidad | incluye |
|---|---|
| `brand-kernel` | posicionamiento, audiencia, problema, propuesta de valor, oferta, principios |
| `narrativa-voz` | narrativa, personalidad, voz y tono |
| `identidad-visual` | dirección visual, sistema de activos, diseño, motion, 3D |

## 2. Distribución (`distribucion`)

Cómo llega la identidad a personas concretas, de forma repetible.

| capacidad | incluye |
|---|---|
| `contenido` | contenido orgánico, redes, video, UGC, avatares, reutilización |
| `search-visibility` | SEO, SEM, GEO (visibilidad en IA), entidades, menciones de marca |
| `paid` | ads (Meta, Google), creativos, testing de anuncios |
| `alianzas-comunidad` | influencers, partnerships, comunidades, PR, newsletter |
| `outbound` | prospección, lead engines, outreach |

## 3. Conversión (`conversion`)

Cómo se convierte la atención en una acción económica o estratégica.

| capacidad | incluye |
|---|---|
| `web-landing` | página web, landings, formularios, lead magnets, reservas, e-commerce |
| `flujo-comercial` | CRM, secuencias de email, WhatsApp, propuestas, agentes de ventas |
| `onboarding-retencion` | onboarding, soporte, retención |

## 4. Aprendizaje (`aprendizaje`)

Qué aprendimos y qué hay que modificar en consecuencia.

| capacidad | incluye |
|---|---|
| `medicion` | analytics, PostHog, GA4, atribución, tracking |
| `experimentos` | pruebas de mensajes, de ads y de contenido, cohortes |
| `evals-calidad` | evals de agentes, golden datasets, regresiones, revisión cruzada, seguridad |
| `research-datos` | scraping, extracción de documentos, research de mercado y de competencia |
| `memoria-org` | documentación de aprendizajes y memoria organizacional |

## 5. Orquestación (`orquestacion`)

Lo que permite que el sistema funcione sin trabajo manual constante.

| capacidad | incluye |
|---|---|
| `planning-before-coding` | prototipar → planificar críticamente → implementar → revisar → validar |
| `current-library-knowledge` | docs actualizadas de librerías (por ejemplo Context7) |
| `codebase-understanding` | grafos de código, consultas estructurales, MCP de código |
| `context-efficiency` | compresión, poda y selección de contexto, ahorro de tokens |
| `knowledge-packaging` | skills, plugins, roles completos con reglas, checklists y comandos |
| `memory` | memoria de agentes: cometer menos los mismos errores, reutilizar lo que salió bien |
| `evidence-based-decisions` | evidencia → hipótesis → intervención → medición → resultado → aprendizaje |
| `hard-task-routing` | qué modelo para qué tarea (barato para el 80%, fuerte donde está la mayor incertidumbre) |
| `testing-validation` | tests, typecheck, build, screenshots, verificadores elegidos antes de correr |
| `observability` | logs, trazas, costo por tarea exitosa, healthchecks |
| `agent-loop-harness` | loops, harness, subagentes, permisos, sandbox, worktrees |
| `infra-acceso` | VPS, máquinas locales, acceso desde cualquier dispositivo, modelos locales |

## Temas del radar (por defecto)

`perfil.md` puede reordenarlos.

- **Tier 1 (seguir de cerca)**: Context Engineering, Evals & Reliability, GEO / Agent Discoverability, Service as Software, Forward Deployed Engineering.
- **Tier 2 (muy importante)**: Operational AI, Cost of Intelligence, Human Premium.
- **Tier 3 (conocer, sin obsesionarse)**: MCP, Agent Systems, Memory Systems, Knowledge Graphs.

Cómo se reparten:

- Construcción: Context Engineering, Evals, Service as Software, FDE.
- Distribución: GEO, Agent Discoverability.
- Economía: Cost of Intelligence, Human Premium.
- Operación: Operational AI.

## Correspondencia tag → capa

Los tags los asigna el script de ingest a partir de tus notas. Son una pista, no un veredicto.

| tag | capa |
|---|---|
| content-video, search-geo | distribucion |
| growth-sales, jobs-income | conversion |
| design-motion-3d | identidad |
| evals-quality, scraping-data | aprendizaje |
| hermes, router-model, loop-engineering, harness, graph-engineering, memory-knowledge, context-tokens, local-models, infra-vps, agents-skills, grok | orquestacion |
