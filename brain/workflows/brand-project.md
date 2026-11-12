# Workflow — Proyecto de marca (Brand Project Flow v2)

> Sistema operacional. Herramientas elegidas por capacidad, no por marca. Gates humanos obligatorios.

## Objective

Llevar un proyecto de marca desde el brief hasta la entrega con cada decisión fundamentada, sin que la estética se discuta antes que la estrategia.

## Inputs

- Brief validado con el cliente (`discovery.md`)
- Accesos y assets existentes del cliente
- Referencias del cliente (3 marcas de cualquier industria + por qué)

## Flow en una línea

```
Brief validado ↔ CI (scraper + analista) → Dirección estratégica → Gate 1
→ Estructuras → Gate 2 (cliente) → Sistema y assets → Gate 3 (QA continuo) → Entrega
```

## Steps

| Etapa | Objetivo | Rol primario | Dueño | Herramienta típica | Criterio de salida | Loop permitido |
|-------|----------|--------------|-------|--------------------|--------------------|----------------|
| **0. Brief** | Brief corto, validado, con información suficiente para decidir. | No se delega a un modelo. | Fundador + cliente | Call + documento de brief | ¿Info suficiente para decidir? Si no → volver al cliente. | Sin límite, hasta que el brief sea accionable. |
| **1. CI** | Mapa de patrones competitivos + dolores y ganancias reales. | Scraper (datos brutos) + LLM analista (síntesis) | Herramienta por tarea | Firecrawl / Apify + Claude / Kimi | Mapa claro de campo ocupado y vacío. | Micro-loop: ajustar queries y fuentes. |
| **2. Dirección** | Posición deseada, campo vacío, trigger psicológico, ejes de tono / contraste / jerarquía. | LLM generalista como sparring; el fundador firma. | Fundador | Modelo fuerte con prompt de comportamiento + antropología | ¿Defendible frente al cliente y coherente con CI? → **Gate 1** | Ajustes mínimos. No se diseña sin Gate 1. |
| **3. Estructuras** | 2–3 rutas estructurales condicionadas por la dirección. | Generador de layouts / arquitecturas | Fundador + cliente | El modelo que mejor rinda en sitemaps según benchmark | Cliente elige ruta; comenta contenido y énfasis → **Gate 2** | Feedback acotado a estructura y prioridades, no estética. |
| **4. Sistema** | Tokens, componentes, reglas. Máx. 3 variantes por bloque. | Ejecutor de UI / código | Fundador | Claude Code u otro ejecutor elegido por tarea | Mini QA estratégico por bloque → **Gate 3** | Corrección por bloque; los errores no se acumulan al QA final. |
| **5. QA + Handoff** | Check integral: estrategia, CI, brief, restricciones de implementación. | Checker estratégico + checker técnico (mismo modelo, dos prompts) | Fundador | Checklist contra los criterios de todas las etapas | Cliente recibe assets + racional + próxima iteración (sprint 2). | Sin loop. Lo estructural se escala como nuevo brief. |

## Gates — qué puede y qué no puede cambiar

| Gate | Pregunta | ✓ Puede cambiar | ✗ No puede cambiar |
|------|----------|-----------------|--------------------|
| **0 — Brief** | ¿Hay información suficiente para decidir estratégicamente? | Contenido del brief: objetivos, contexto, restricciones, audiencia. | La estructura del proceso. |
| **1 — Dirección** | ¿Es defendible y coherente con CI? | Posicionamiento: campo elegido, trigger psicológico, ejes de tono. | Estética, layouts, tipografía, color (van al sprint de diseño). |
| **2 — Estructuras** | El cliente elige ruta y deja comentarios accionables. | Navegación, prioridades de contenido, jerarquía de mensajes. | Color, tipografía, estilo visual (se documenta para el sprint de diseño). |
| **3 — QA por bloque** | ¿El componente sigue la dirección y el mapa CI? | Correcciones de desvíos y errores técnicos. | Cambios de concepto o de dirección (escalan como nuevo brief). |

## Reglas de selección de herramientas

1. La herramienta se elige por capacidad concreta para la tarea, no por marca.
2. Para cada rol (scraper, analista, generador de layouts, ejecutor) se define un benchmark interno mínimo de 2 tareas tipo antes de fijar la herramienta.
3. El dueño humano firma cada gate. Sin firma no se avanza.
4. Máximo 3 variantes por bloque en la etapa 4. Si hacen falta más, la dirección no estaba clara → volver a Gate 1.
5. El cliente no opina sobre estética en Gate 2. Si lo hace, se redirige al criterio: ¿esto sirve al objetivo estratégico?
6. Si una herramienta falla 2 veces seguidas en una tarea, se prueba una alternativa y se documenta qué hizo mejor o peor. El flow aprende su propio stack.

## Outputs

- Documento de dirección estratégica (el "ADN" del que se derivan las decisiones)
- Ruta estructural elegida
- Sistema visual: tokens, componentes, reglas
- Assets finales + racional de cada decisión
- Propuesta de sprint 2

## Checklist

- [ ] Brief accionable (Gate 0)
- [ ] Mapa CI con campo ocupado y vacío
- [ ] Dirección firmada (Gate 1)
- [ ] Ruta estructural elegida por el cliente (Gate 2)
- [ ] Cada bloque pasó su mini QA (Gate 3)
- [ ] Cada decisión visual responde "¿por qué?" con psicología, historia o precedente cultural
- [ ] Entrega con racional y próxima iteración
