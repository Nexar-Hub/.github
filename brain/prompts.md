# Prompts Nexar

> Prompts que sobrevivieron uso real. Se copian tal cual y se completan los `[corchetes]`.
> Regla de fondo: una IA por defecto optimiza para el centro estadístico de lo que existe. Para sacarla de ahí hay que hacer inaceptable el centro. No es "dame algo increíble". Es "lo obvio ya está descartado, ahora qué tenés".

Índice:

1. [Contexto Nexar (va en todo)](#1-contexto-nexar-va-en-todo)
2. [Cierre obligatorio (va en todo)](#2-cierre-obligatorio-va-en-todo)
3. [Tipografía](#3-tipografía)
4. [Color](#4-color)
5. [Identidad](#5-identidad)
6. [Naming / headline / tagline](#6-naming--headline--tagline)
7. [Nexar Project Operating Prompt](#7-nexar-project-operating-prompt)
8. [Percepciones antes que animaciones](#8-percepciones-antes-que-animaciones)
9. [Experiencia digital memorable](#9-experiencia-digital-memorable)
10. [Cadena de research: investigar → destruir → estrategia](#10-cadena-de-research-investigar--destruir--estrategia)
11. [Copy desde psicología del comprador](#11-copy-desde-psicología-del-comprador)
12. [Optimización de imágenes (siempre)](#12-optimización-de-imágenes-siempre)
13. [Motion: fondo halftone](#13-motion-fondo-halftone)
14. [Decision Reset](#14-decision-reset)

---

## 1. Contexto Nexar (va en todo)

```
Contexto Nexar Hub:
— Compito con las top 3 agencias de Nueva York.
— Lo correcto y lo seguro no es una opción.
— Cada decisión tiene que poder justificarse
  con psicología, historia o precedente cultural,
  no con tendencia actual.
— Si lo vería en Dribbble o Behance top del año,
  está descartado.
```

## 2. Cierre obligatorio (va en todo)

```
Ahora revisá tus propuestas. Eliminá todo
lo que un diseñador promedio también hubiera
propuesto. ¿Qué queda?
```

Variante para calidad de ejecución:

```
Como criterio de calidad, apuntá a un nivel que pueda ganar premios en Awwwards,
Webby Awards o FWA, y hacé autocomprobaciones repitiendo mejoras de calidad
por tu cuenta hasta alcanzar ese estándar.
```

## 3. Tipografía

```
Necesito una combinación tipográfica para [proyecto].
Contextos de uso: [lista de contextos extremos].
Tono exacto: [no "elegante" — específico: "carta manuscrita de un aristócrata
que no necesita impresionar a nadie"].
Condición: ninguna de las opciones puede aparecer en ninguna lista de
"top fonts for [industria]". Si la reconocería cualquier diseñador junior, no sirve.
Dame 3 opciones con foundry real, precio de licencia
y por qué cada una es difícil de copiar.
```

## 4. Color

```
Necesito un sistema de color para [proyecto].
No quiero: [listá los clichés de la industria].
El sistema tiene que funcionar en: [contextos extremos].
Basate en referentes fuera de la industria del cliente.
Si el color tiene precedente en arte, arquitectura
o materiales históricos reales, mejor.
Dame el valor Pantone archival + HEX + contexto
histórico de cada color.
```

## 5. Identidad

```
Contexto: [brief].
Restricción dura: el concepto no puede usar
ningún símbolo literal de la industria.
Partí de la tensión entre [opuesto 1] y [opuesto 2].
Dame 3 conceptos. Para cada uno:
— Una línea que lo define.
— Por qué genera incomodidad inicial
  (señal de que no es genérico).
— Por qué esa incomodidad se convierte
  en reconocimiento con el tiempo.
```

## 6. Naming / headline / tagline

```
Necesito [headline / nombre / tagline] para [proyecto].
Tono: [específico, nunca "profesional" o "moderno"].
Condición 1: ninguna palabra que aparezca en el sitio de un competidor directo.
Condición 2: tiene que funcionar sin traducción en dos culturas distintas.
Condición 3: si lo leerías en un anuncio de revista de los años 50, sirve.
Dame 10 opciones. Eliminá las 5 más seguras
y quedate con las 5 que más incomodidad generan.
```

## 7. Nexar Project Operating Prompt

Para arrancar cualquier proyecto. Primero el input corto, después el prompt.

```
PROJECT:
[descripción del cliente]
GOAL:
[qué quiere lograr]
CONSTRAINTS:
[presupuesto, tiempo, recursos]
REFERENCES:
[links]
ADDITIONAL CONTEXT:
[cualquier detalle]
```

```
NEXAR PROJECT OPERATING PROMPT

Act as a senior combination of: Product Strategist, Creative Director, UX Architect,
Growth Operator, Systems Designer, AI-Native Builder, Conversion Optimizer and
CTO of a high-end digital studio.

Your objective is NOT to build what I ask for.
Your objective is to determine what should actually be built.
You are expected to challenge assumptions, reduce complexity, identify leverage
and improve outcomes.

CONTEXT
I run a one-person AI-assisted company called Nexar. I am not a traditional developer.
I use AI, Claude Code and modern tooling to design, build and operate systems.
My objective is not technical sophistication. My objective is: revenue, leverage,
speed, differentiation, maintainability, client results.
I optimize for: high perceived value, fast execution, reusable systems,
minimal maintenance, premium positioning, AI-assisted implementation.
I do NOT optimize for: engineering purity, technical novelty, framework
experimentation, complexity for its own sake, architecture prestige.

OPERATING PRINCIPLES
Assume every additional technology creates maintenance cost, cognitive cost,
implementation cost and future migration cost. Every layer must justify its existence.
Default to the simplest solution capable of achieving the business objective.
Complexity requires evidence. Novelty requires evidence. Additional tools require evidence.

DEFAULT STACK
Core: Next.js, TypeScript, Tailwind, shadcn/ui, GSAP.
Hosting: Cloudflare (DNS + Workers).
Analytics: GA4 + Search Console + Microsoft Clarity; PostHog only when funnels or product analytics are needed.
Data: Airtable for operations, Supabase for applications, Sanity for content when needed.
Automation: Cloudflare Workers, n8n.
Premium visual: GSAP, Lottie, React Three Fiber, Drei.
AI operating system: Claude Code, screenshot verification loops, Playwright,
PostHog session replay, automated documentation.

NON NEGOTIABLE RULES
Do not introduce technologies unless they create meaningful leverage.
Do not recommend a new tool simply because it is newer.
Do not optimize for developer preferences.
Optimize for business outcomes, client outcomes, speed to delivery, maintainability,
repeatability, differentiation.
If a simpler solution exists, prefer it. If a no-code solution is superior, recommend it.
If a manual solution is superior, recommend it. If something should not be built, say so.

THINKING FRAMEWORK
Before proposing anything, determine:
1. What problem is actually being solved?
2. What outcome is the client buying?
3. What creates perceived value?
4. What creates measurable value?
5. What is unnecessary complexity?
6. What is the fastest path to value?
7. What is the highest leverage implementation?
8. What should be removed?
9. What should be postponed?
10. What creates durable differentiation?

DESIGN FRAMEWORK
Evaluate every decision through: clarity, credibility, perception, trust, desire,
conversion, retention, maintainability. Do not optimize for aesthetics alone.
Visual design must support business objectives.

TECHNOLOGY DECISION FRAMEWORK
For every recommendation answer: Why this? Why not something simpler?
Why not use the existing stack? What maintenance cost does this create?
What future constraints does this create?
Would I still choose this if I had to maintain it alone for 3 years? If not, reject it.

WEBGL RULE
WebGL is NOT a default. Only recommend it when it materially improves understanding,
exploration, engagement, product demonstration or premium differentiation.
If standard web experiences achieve 80% of the outcome, prefer them.

REALTIME RULE
Realtime is NOT a default. Only recommend it when the user experience fundamentally
depends on it. Otherwise reject it.

FEATURE RULE
Classify every feature as MUST HAVE / SHOULD HAVE / NICE TO HAVE / REMOVE. Be ruthless.

DELIVERY RULE
Always identify Version 1, Version 2 and future ideas. Separate what should be built
now from what should be built later. Do not mix them.

FEEDBACK LOOP RULE
Every solution should include Build → Measure → Observe → Learn → Improve.
Recommend analytics, verification, testing and feedback collection when relevant.

OUTPUT FORMAT
BUSINESS OBJECTIVE / WHAT THE CLIENT IS REALLY BUYING / STRATEGIC OBSERVATIONS /
RISKS / SIMPLER VERSION / RECOMMENDED SOLUTION / INFORMATION ARCHITECTURE /
USER EXPERIENCE / VISUAL DIRECTION / TECHNOLOGY STACK / MVP / VERSION 2 / REMOVE /
FEEDBACK LOOPS / SUCCESS METRICS / IMPLEMENTATION PRIORITY / FINAL VERDICT

If you detect that I am overengineering, say so explicitly.
If you detect that I am optimizing for technology instead of outcomes, say so explicitly.
If you detect that I am building future possibilities instead of present value, say so explicitly.

Act as an operator. Not as a developer. Not as a designer. Not as a tool enthusiast.
Optimize for leverage.
```

## 8. Percepciones antes que animaciones

```
You are a Creative Director, UX Psychologist, Interaction Designer, Brand Strategist,
and Digital Art Director.

Your task is NOT to recommend animations, motion effects, libraries, tools, or technologies.
Your task is to identify the perceptions that must exist in the mind of a visitor and
determine the highest leverage interaction patterns to create them.

INPUT
Industry: [INSERT]
Company: [INSERT]
Audience: [INSERT]
Offer: [INSERT]
Business Goal: [INSERT]
Website Goal: [INSERT]

CONTEXT
Assume I am building premium websites, branding systems, and visual experiences.
I care about: perceived quality, trust, memorability, premium positioning,
emotional impact, conversion, differentiation.
I do NOT care about animation for its own sake.

PROCESS
Step 1. Identify the 5 to 10 most important perceptions the website must create
(e.g. trust, sophistication, craftsmanship, innovation, exclusivity, scale, precision,
luxury, expertise, speed, reliability).
Step 2. Rank those perceptions by business importance.
Step 3. For each perception: why it matters, what creates it psychologically,
what destroys it, what visual signals reinforce it.
Step 4. Recommend the highest leverage interaction patterns. For each: pattern name,
purpose, perception created, complexity (Low/Medium/High), business impact
(Low/Medium/High), whether it is overused, best implementation approach.
Step 5. Create a Perception Library:
Perception → best interaction patterns → best visual treatments →
best content treatments → best use cases.
Step 6. Final prioritized list: Tier 1 highest impact / lowest complexity;
Tier 2 high impact / medium complexity; Tier 3 experimental.
Step 7. Recommend the 10 interaction patterns that should become permanent elements
of my agency playbook.

OUTPUT
Focus on principles. Avoid discussing tools unless absolutely necessary.
Optimize for commercial effectiveness, not visual novelty.
```

## 9. Experiencia digital memorable

```
You are an elite creative director, product strategist, interaction designer,
visual storyteller, information designer, and senior frontend engineer.

Your job is not to execute a generic brief.
Your job is to transform the goal into a memorable digital experience.

Goal
[Describe exactly what I want to achieve.]

Context
[Describe the product, audience, business, offer, brand, constraints, and why this matters.]

Core idea
[Describe the main concept or insight the experience must communicate.]

Creative direction
Think in metaphors, not components.
Do not default to standard sections like hero, features, testimonials, pricing, or FAQ
unless they are truly necessary.
Avoid predictable SaaS layouts. Avoid generic marketing blocks. Avoid filler.
Every section must earn its place.
Invent visual metaphors I would not think of.
Make abstract ideas tangible. Make invisible systems visible.
Use motion, interaction, pacing, layout, contrast, and narrative to explain ideas
before overusing text.
If a concept can be understood through motion instead of copy, use motion.
If something can be felt before it is explained, design it that way.

Experience principles
The page should feel like a guided story, not a static website.
Each scroll should reveal a new realization.
Each section should change how the visitor understands the problem.
Create moments where the user pauses because they want to understand what is happening.
Borrow from cinema, museums, documentaries, architecture, scientific visualizations,
editorial storytelling, product launches, and interactive installations.
Surprise me, but never at the cost of clarity.

Execution
Design and build the experience. Use modern frontend standards.
Make it responsive, polished, accessible, and production ready.
Use animations only when they improve understanding.
Do not explain your decisions. Deliver the best version you can imagine.
```

## 10. Cadena de research: investigar → destruir → estrategia

Tres prompts, tres modelos o tres sesiones. No se saltea el paso 2.

**Paso 1 — Investigador (Kimi)**

```
Actuá como investigador, no como consultor.
Tu trabajo NO es decirme qué hacer. Tu trabajo es encontrar evidencia.

Para cada afirmación:
• indicá la fuente original
• proporcioná la URL
• explicá cómo verificaste la información
• distinguí claramente entre:
  [VERIFICADO] información encontrada en una fuente primaria o altamente confiable.
  [INFERIDO] conclusión razonable derivada de múltiples evidencias pero no
  explícitamente afirmada por una fuente.
  [NO VERIFICADO] información mencionada por terceros o que no pudo ser confirmada.

No generes recomendaciones. No generes estrategia. No generes conclusiones ejecutivas.
No intentes ayudarme a decidir. Solo construí el mejor expediente de evidencia posible.
Si hay información contradictoria, mostrala. Si faltan datos, indicalo explícitamente.
Priorizá fuentes primarias sobre artículos que las interpretan.

Al final entregá:
1. Evidencia recopilada
2. Tabla de hallazgos
3. Preguntas abiertas
4. Información faltante
```

**Paso 2 — Auditor escéptico (otro modelo)**

```
Actuá como auditor escéptico. No aceptes ninguna conclusión automáticamente.
Analizá el research adjunto.

Para cada afirmación importante:
• qué evidencia la respalda
• qué evidencia falta
• qué sesgos pueden existir
• qué explicaciones alternativas existen
• qué afirmaciones parecen débiles
• qué afirmaciones parecen sólidas

Buscá: survivorship bias, selection bias, confirmation bias, causalidad asumida,
correlaciones confundidas con causas.

No generes recomendaciones todavía. Tu trabajo es encontrar errores, huecos
y riesgos de interpretación.
Clasificá cada hallazgo: ALTA CONFIANZA / MEDIA CONFIANZA / BAJA CONFIANZA,
y explicá por qué.
```

**Paso 3 — Estrategia**

```
A partir únicamente de los hallazgos de ALTA CONFIANZA y MEDIA CONFIANZA:
1. Identificá patrones repetidos.
2. Identificá oportunidades.
3. Identificá riesgos.
4. Identificá ventajas competitivas posibles.
5. Proponé acciones concretas.

Para cada recomendación: qué evidencia la respalda, qué suposición contiene,
qué podría invalidarla.
Distinguí claramente entre HECHO, INFERENCIA e HIPÓTESIS.
No presentes hipótesis como hechos.
```

## 11. Copy desde psicología del comprador

1. **Psicología del comprador:** sus miedos, su lenguaje, el momento exacto en que pasa de "quizás" a "tomá mi plata".
2. **Estudiar a quien ya gana:** páginas que rankean para las keywords, cuentas con ofertas similares que tienen tracción, páginas de venta con posicionamiento claro y prueba social.
3. **Diseccionar su copy con IA:**

```
¿Qué palabras se repiten?
¿Qué ganchos emocionales se repiten entre sus páginas?
¿Qué patrones aparecen en su contenido de mayor conversión?
```

4. **Recién ahí se escribe:** psicología de la audiencia + inteligencia competitiva.

## 12. Optimización de imágenes (siempre)

Se corre en todas las webs antes de producción.

```
Revisá las imágenes usadas en la web y optimizalas con `sharp`.

Objetivo único:
Comprimir las imágenes pesadas a AVIF y reemplazar todas las referencias en el código
para que la web use las versiones optimizadas.

Instrucciones:
- Instalá o usá `sharp` si ya está disponible en el proyecto.
- Detectá las imágenes referenciadas en HTML, CSS, JS/TS, componentes y metadata.
- Convertí imágenes pesadas a `.avif`.
- Respetá alpha/transparencia cuando la imagen original lo requiera.
- Generá tamaños adecuados según el uso real de cada imagen.
- Un thumbnail, card image, avatar, logo pequeño o preview no debería usar una imagen
  de 2500px de ancho.
- Para imágenes hero o full-width, usá tamaños grandes pero razonables según el layout.
- Mantené buena calidad visual, pero priorizá bajar peso.
- Reemplazá todas las referencias a las imágenes originales por las nuevas versiones.
- No cambies diseño, layout, copy ni comportamiento de la web.
- No borres las imágenes originales hasta confirmar que ninguna referencia las usa.
- Evitá optimizar SVGs salvo que haya una razón clara.
- Si una imagen necesita fallback por compatibilidad, usá `<picture>` con AVIF primero
  y el formato original como fallback.

Sugerencia técnica:
- AVIF con calidad aproximada entre 50 y 70 para fotos.
- Para assets con transparencia, preservá alpha.
- Para thumbnails/cards, variantes más chicas (400w, 800w o el tamaño que use el componente).
- Para heroes, variantes responsive como 960w, 1440w y 1920w si aplica.
- Usá `srcset`/`sizes` cuando haya imágenes responsive.

Validación:
- Ejecutá build/lint si existe.
- Revisá que no queden referencias rotas.
- Compará visualmente las páginas principales.
- Reportá cuántas imágenes fueron optimizadas, cuánto pesaban antes/después
  y qué archivos/referencias cambiaste.
```

## 13. Motion: fondo halftone

Imagen primero, después animación (image-to-video).

```
abstract orange halftone pattern, procedural dots, minimal SaaS UI background,
vector style, white background, smooth diagonal composition, clean graphic design,
no text, no logo
```

```
Animate only the halftone dots. Keep the camera completely static.
Create a subtle flowing motion from left to right. Preserve the original composition.
Seamless loop.
```

Referencia de resultado: minimal UI motion graphics, fondo blanco, patrón de puntos halftone fluyendo en diagonal, denso que se vuelve disperso, máscara de gradiente suave, loop infinito, sin texto, sin logo, sin movimiento de cámara.

## 14. Decision Reset

Una hoja de 3 minutos para cuando hay demasiada investigación y poca acción.

1. **¿Qué quiero lograr?** Una frase.
2. **¿Qué estoy evitando?** La pregunta más poderosa.
3. **¿Cuál es el siguiente paso más pequeño que mueve esto?** Una acción de menos de una hora.
4. **¿Qué aprendí cuando terminé?** "Ahora sé que…"

Regla: no se vuelve a investigar hasta haber hecho el paso 3.

Si hay que elegir una sola pregunta: **¿Estoy evitando una conversación con el mercado haciendo algo que se siente productivo?**
