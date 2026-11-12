---
name: capability-first
description: Antes de investigar, instalar o comparar una herramienta, la reformula como capacidad y compara implementaciones (incluida "no hacer nada" y "lo que ya tengo"). Usar cuando el usuario dice "investigá X", "¿sirve X?", "qué uso para…", "¿me conviene X o Y?" o quiere sumar una herramienta al stack.
version: 1.0.0
author: Nexar Hub
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [research, stack, decisions, tools, capability]
    category: radar
---

# Capability First

Nunca se investiga una herramienta como objetivo. Se investiga una **capacidad**, y las herramientas son solo implementaciones posibles de esa capacidad.

- Mal: "Voy a investigar Obsidian."
- Bien: "Necesito una capacidad de conocimiento operativo humano. Comparo Obsidian, Logseq, AFFiNE, Outline, Git + Markdown, construir algo propio… y lo que ya uso."

La regla es **Problema → Capacidades → Stack → Oferta**, nunca al revés. El orden de trabajo es: primero buscar, después integrar y recién al final construir.

## Cuándo usar

- El usuario nombra una herramienta, un repo o un modelo y pregunta si le sirve.
- El radar marca un ítem como "herramienta sin capacidad".
- Antes de mover algo a ADOPT en `stack.md`.

## Procedimiento

1. **Nombrá la capacidad** con un verbo, un objeto y un resultado. Por ejemplo: "extraer datos estructurados de PDFs de clientes sin revisión manual". Ubicala en `mapa-de-capacidades.md` (skill `leverage-radar`, carpeta `references/`). Si no entra en ninguna capa, frená y preguntá para qué es.
2. **Definí el problema real.** Respondé estas preguntas:
   - ¿En qué proyecto de `perfil.md` aparece el problema?
   - ¿Cuántas veces pasó?
   - ¿Qué cuesta hoy en tiempo, dinero o errores?
   - ¿Cuál es el criterio de éxito medible?

   Si el problema no existe todavía, el veredicto es WATCH. No diseñes para casos que todavía no existen.
3. **Mirá lo que ya hay.** Revisá la implementación actual en `stack.md` y su "lo reemplazaría si…". La opción 0 siempre es "seguir igual".
4. **Listá de 3 a 5 implementaciones**, en este orden: lo que ya tengo, open source o herramienta existente, servicio pago y construir propio (siempre al final).
5. **Comparalas en una tabla:**

   | opción | resuelve el problema | costo/mes y por cliente | reversible | mantenimiento | evidencia | encaja con el stack | datos propios | riesgo de seguridad |
   |---|---|---|---|---|---|---|---|---|

   Para la evidencia usá la escalera de `criterios.md`: sin-fuente → anécdota → demo → adopción → medido → verificado.
6. **Recomendá una opción** con su prueba mínima: hipótesis, criterio de éxito y timebox de 20 a 40 minutos. "No cambiar nada" es una recomendación válida.
7. **Registrá** la recomendación como propuesta en `stack.md`, con la columna "lo reemplazaría si…" completa. No la marques adoptada hasta que la prueba pase.

## Pitfalls

- No compares 12 herramientas. Más de 5 opciones es un rabbit hole.
- No confundas la herramienta con la oferta. El cliente compra resultados, no NocoDB.
- Hay que pagar el costo de sumar: configuración, contexto del agente, mantenimiento y superficie de ataque. Tiene ventaja la opción que **saca** un componente.
- Usar SaaS por comodidad superficial se multiplica por cliente. Mantené una arquitectura pensada para 10 clientes, no para 10.000.

## Verification

- La capacidad tiene verbo, objeto y resultado, y está ubicada en una capa.
- La opción 0 ("seguir igual") está en la tabla.
- La recomendación tiene un criterio de éxito medible y un timebox.
- `stack.md` tiene la propuesta y nada quedó marcado como adoptado sin una prueba.
