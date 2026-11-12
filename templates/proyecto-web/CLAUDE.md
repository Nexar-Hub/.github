# Instrucciones para Claude Code

> Claude Code carga este archivo automáticamente al iniciar sesión en el proyecto (por eso se llama `CLAUDE.md`). Define cómo debe comportarse en este proyecto específico.
> Contexto completo de Nexar (posicionamiento, gusto visual, workflows, prompts): repo `Nexar-Hub/.github`, carpeta `brain/`.

## Contexto Nexar (resumen que manda)

- Competimos con las mejores agencias del mundo. Lo correcto y lo seguro no es una opción.
- Cada decisión de diseño tiene que poder justificarse con psicología, historia o precedente cultural, no con tendencia.
- El diseño soporta objetivos de negocio: claridad, credibilidad, confianza, deseo, conversión. No se optimiza por estética sola.
- Lo más simple que logra el objetivo. Cada componente, librería, sección y animación justifica su existencia.
- WebGL y realtime no son default. Si la web estándar logra el 80% del resultado, se usa la web estándar.
- Si detectás sobreingeniería, optimización por tecnología en vez de resultados, o construcción de posibilidades futuras en vez de valor presente: decilo explícitamente.

## Stack y versiones

- Next.js (App Router), versión estable actual
- TypeScript en strict mode
- Tailwind CSS (no inline styles, no styled-components) + shadcn/ui
- Contenido en Markdown / JSON en el repo por default. Sanity solo si `BRIEF.md` dice que el cliente edita contenido seguido
- GSAP (+ ScrollTrigger, Lenis) para timelines y scrollytelling; Motion para micro-interacciones de UI
- React Hook Form + Zod para formularios
- Server actions + Resend o ZeptoMail para email transaccional
- GA4 + Search Console + Microsoft Clarity como analytics base
- Lucide React para íconos
- Deploy en Cloudflare Workers (adaptador OpenNext). No Vercel

## Convenciones de código

### Componentes

- Server Components por default
- Client Components SOLO cuando hay:
  - Interactividad (onClick, onChange, etc.)
  - Hooks de estado (useState, useEffect, etc.)
  - APIs del browser (window, document, etc.)
- Marcar Client Components con `"use client"` arriba de todo
- Componentes en `/components/[Section]/[ComponentName].tsx`
- Un componente por archivo
- Nombre del archivo igual al nombre del componente (PascalCase)

### TypeScript

- NUNCA usar `any`. Si no sabés el tipo, usar `unknown` y narrowing
- Tipos en archivos separados cuando se reusan: `/types/[domain].ts`
- Props de componentes con interface, no type alias
- Funciones con tipos explícitos de retorno cuando son exportadas
- Evitar inferencia de tipos cuando reduce legibilidad

### Estilos

- Tailwind utility classes únicamente
- NUNCA inline styles excepto cuando el valor es dinámico (ej: backgroundImage de URL variable)
- NUNCA archivos CSS separados excepto globals.css
- Usar tokens del design system, no valores arbitrarios
- Mobile-first: clases base son mobile, modificadores son desktop

### Imágenes

- SIEMPRE next/image, NUNCA `<img>` plano
- Width y height obligatorios
- Alt text descriptivo, NUNCA vacío excepto en imágenes puramente decorativas
- priority en LCP image (típicamente hero)
- sizes attribute apropiado
- AVIF (calidad 50–70 en fotos), variantes por tamaño real de uso (400w / 800w en cards, 960w / 1440w / 1920w en heroes)
- Fotos y video pesados desde CDN (Cloudflare R2 / Images); assets livianos optimizados en /public/

### Data fetching

- Server components con async/await directo (no useEffect)
- NUNCA fetch del lado cliente con useEffect a menos que sea estrictamente necesario
- Try/catch en todos los fetch con fallback útil
- Caché de Next.js usado correctamente (revalidate, no-store según caso)

### Estados

Cada componente que carga data debe tener:
- Loading state (skeleton, no spinner)
- Error state con mensaje útil
- Empty state cuando aplique
- Success state (default)

### Formularios

- React Hook Form para manejo
- Zod para schema de validación
- Validación on blur, no on change
- Mensajes de error en español
- Estados visuales: idle / submitting / success / error
- Honeypot field anti-spam
- Server action (o `/app/api/[name]/route.ts` si hace falta un endpoint público)
- Rate limiting
- Labels fuera del input, nunca solo placeholder
- Nunca deshabilitar el submit para "esconder" errores: mostrar los errores

### Naming

- Componentes: PascalCase (`HeroSection.tsx`)
- Funciones: camelCase (`getUserData`)
- Constantes: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Tipos/Interfaces: PascalCase (`UserProfile`)
- Archivos de utilidades: kebab-case (`format-date.ts`)

## Lo que NO hacer

### Tecnologías prohibidas
- NO useEffect para data fetching (usar Server Components)
- NO librerías de CSS-in-JS (styled-components, emotion)
- NO Redux / Zustand a menos que sea estrictamente necesario
- NO axios (usar fetch nativo)
- NO moment.js (usar date-fns o nativo)
- NO CMS "por las dudas": solo si el brief lo pide

### Patrones prohibidos
- NO `any` en TypeScript
- NO comentarios obvios (`// incrementa el contador`)
- NO console.log en código de producción
- NO TODO sin issue asociado
- NO hardcoded strings que deberían estar en config o en el contenido
- NO números mágicos sin constante explicativa

### UX prohibida
- Animaciones que bloquean una acción del usuario
- Transiciones de interacción de más de 300 ms
- Video con sonido en autoplay
- Carruseles en autoplay
- Más de 3 colores primarios, más de 2 familias tipográficas, más de 5 tamaños de fuente en una vista
- Gris claro sobre blanco, blanco puro sobre negro puro; contraste mínimo WCAG AA (4.5:1)
- Información transmitida solo con color
- Íconos sin label o tooltip; hamburguesa en desktop; navegación "ingeniosa" que confunde
- Tap targets de menos de 44×44 px; interacciones que dependen de hover en touch; elementos fijos que tapan contenido
- Scroll horizontal no intencional
- Muros de texto sin jerarquía; links "click acá"; Lorem Ipsum en producción
- Trampas de foco; auto-focus al cargar (salvo búsqueda)

### Prácticas prohibidas
- NO crear archivos sin que el usuario lo pida
- NO refactorizar código existente sin pedirlo
- NO instalar dependencias sin avisar
- NO modificar configuración sin avisar
- NO hacer cambios masivos en una sola operación
- NO tocar producción directamente: branch → preview → QA → aprobación → merge

## Filosofía de trabajo

### Construcción incremental
- Sección por sección, no "armame todo"
- Validar entre pasos
- Mostrar el código completo de lo construido antes de avanzar
- Si algo es complejo, partirlo en pasos más chicos

### Comentarios útiles
- Comentar el "por qué", no el "qué"
- Comentar decisiones no obvias
- Comentar workarounds y por qué existen
- NO comentar lo que el código ya dice claramente

### Performance por default
- Server components donde sea posible
- Lazy loading donde aplique
- Imágenes optimizadas siempre
- Bundle size en mente al elegir librerías (importar módulos puntuales de GSAP, no todo el core)

### Accesibilidad por default
- Semántica HTML correcta
- Heading hierarchy lógica
- Alt text en imágenes
- Focus states visibles
- Contraste adecuado
- Keyboard navigation funcional
- `prefers-reduced-motion` respetado

### Verificación visual
- Después de cada sección, screenshots con Playwright en 390, 768, 1280 y 1440 px
- Comparar contra `references/` y `DESIGN_SYSTEM.md` antes de dar algo por terminado

## Cuando el usuario pide algo

### Antes de empezar
1. Si el usuario pide algo grande ("armame la home"), proponer dividirlo en pasos
2. Si hay ambigüedad, preguntar antes de asumir
3. Si la decisión depende de información que no tenés, preguntar

### Durante la implementación
1. Mostrar el plan antes del código si es algo complejo
2. Construir incremental, validar entre pasos
3. Mostrar el código completo de cada paso, no fragmentos sueltos

### Después de implementar
1. Resumir qué se hizo
2. Mencionar archivos creados o modificados
3. Sugerir el siguiente paso lógico
4. Avisar si algo quedó pendiente o requiere atención

## Archivos del proyecto a leer al iniciar

Al empezar una sesión, leer en este orden:

1. `BRIEF.md` — contexto del cliente y proyecto
2. `DESIGN_SYSTEM.md` — tokens visuales y reglas
3. `CHECKLIST.md` — estado actual del proyecto
4. `WORKFLOW.md` — fase en la que estamos
5. Imágenes en `references/` — inspiración visual

## Cosas a recordar siempre

- El usuario prefiere precisión sobre cortesía
- Pushback constructivo es bienvenido
- Si hay un error en el approach, decirlo claro
- No suavizar mensajes para complacer
- Densidad alta en respuestas cuando importa
- Respuestas cortas en interacciones simples

## Stack alternativo (solo si el proyecto lo requiere)

Si el proyecto requiere algo no contemplado en el stack default:

- Cliente que edita contenido seguido: Sanity
- E-commerce: Shopify (Hydrogen solo si hace falta un front a medida)
- Multi-idioma: next-intl
- Auth: Clerk o NextAuth
- Database: Supabase
- Search: Pagefind (estático) o Algolia (dinámico)
- Funnels / producto: PostHog
- Objeto 3D o espacio explorable: React Three Fiber + Drei (GLB comprimido, KTX2)

Pero por default, no incluir nada de lo anterior.
