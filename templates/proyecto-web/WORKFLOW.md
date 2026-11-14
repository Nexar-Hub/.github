# WORKFLOW — Cómo construir el sitio con Claude Code

> Seguí estos pasos en orden. No saltes pasos. No improvises. Si algo no aplica, marcalo como N/A pero no lo ignores.

---

## FASE 0: Pre-trabajo (antes de abrir Claude Code)

### Tiempo estimado: 30-60 minutos

- [ ] **BRIEF.md llenado completamente** (todas las secciones, no solo las "fáciles")
- [ ] **DESIGN_SYSTEM.md llenado** con tokens base (paleta, tipografía, espaciado)
- [ ] **Referencias visuales en `references/inspiration/`** (mínimo 3 sitios que le gustan al cliente)
- [ ] **Brand assets en `references/brand-assets/`** (logo SVG, colores, fuentes)
- [ ] **Capturas de competencia en `references/competitors/`** (mínimo 2)
- [ ] **Decisiones críticas confirmadas con cliente:**
  - Stack
  - Idiomas
  - Páginas MVP vs nice-to-have
  - Quién aprueba qué
- [ ] **Política de soporte enviada y aceptada por el cliente** (`SUPPORT_POLICY.md`)

**Si alguno de estos items no está hecho, NO ABRAS CLAUDE CODE.** Volvé al cliente, conseguilo, después arrancás.

---

## FASE 1: Setup técnico inicial

### 1.1 — Iniciar Claude Code

```bash
cd ~/projects/[cliente]
claude
```

### 1.2 — Primer mensaje (CRÍTICO: no pedir código todavía)

Copia y pegá este prompt:

```
Vamos a construir el sitio web de [Cliente].

Antes de escribir cualquier código, leé estos archivos en este orden exacto:

1. BRIEF.md
2. DESIGN_SYSTEM.md
3. CLAUDE.md (ya cargado, pero confirmá que lo leíste)
4. Las imágenes en references/inspiration/
5. Las imágenes en references/competitors/
6. Las imágenes en references/brand-assets/

Después de leer todo, respondeme con:

1. Resumen del proyecto en 3 líneas (qué entendiste)
2. Audiencia objetivo y acción principal del visitante
3. 3-5 decisiones de arquitectura que propondrías para este proyecto específico
4. Dudas o ambigüedades que detectaste en el brief que necesito aclarar antes de seguir

NO escribas código todavía. NO empieces a generar componentes. NO crees archivos.
```

### 1.3 — Validar comprensión

Leé la respuesta. Corregí lo que entendí mal. Aclará ambigüedades. **No avances hasta que la dirección esté clara.**

### 1.4 — Plan de arquitectura

Una vez alineados, decile:

```
Bien. Ahora hacé un plan de arquitectura del proyecto. Solo plan, no código.

Incluí:

1. Estructura de carpetas completa
2. Stack confirmado con versiones
3. Lista de páginas con sus rutas
4. Lista de componentes globales (Header, Footer, etc.)
5. Lista de componentes por página
6. Modelo de contenido: Markdown/JSON en el repo, o schema de Sanity si BRIEF.md dice que el cliente edita seguido
7. Lista de integraciones externas necesarias (formularios, etc.)
8. Variables de entorno que vamos a necesitar

Mostrame el plan completo en un solo mensaje, sin escribir código.
```

### 1.5 — Iniciar el proyecto Next.js

```
Inicializá el proyecto:
- Next.js (App Router, versión estable actual) y TypeScript estricto
- shadcn/ui inicializado
- Tailwind con la config que refleje DESIGN_SYSTEM.md (paleta, tipografía, espaciado, breakpoints)
- Estructura de carpetas que definimos en el plan
- Carga de fuentes en layout.tsx (next/font)
- Metadata base configurada
- Sin CMS todavía
- Sin componentes de página todavía
- Solo el esqueleto

Mostrame el árbol de archivos cuando termines.
```

---

## FASE 2: Construcción de páginas

### Orden estricto:

1. Home (define el lenguaje visual de todo el sitio)
2. Componentes globales (Header, Footer) — surgen al construir home
3. Página secundaria más importante (Servicios / Portfolio / Productos)
4. Resto de páginas en orden de importancia
5. Página de contacto al final

### 2.1 — Home, sección por sección

**No "armame toda la home." Vamos sección por sección.**

#### Hero

```
Vamos a construir la home, sección por sección.

Empezamos con el Hero.

Características:
- [Layout específico: full-screen / contenido + visual / etc]
- [Elementos: title, subtitle, CTA, imagen/video, etc]
- Mobile-first responsive
- Server component
- Props tipadas (van a conectarse al contenido después)
- Por ahora datos hardcodeados directamente en el componente
- Tomá referencia de [archivo en references/]
- Aplicá tokens de DESIGN_SYSTEM.md

Mostrame el código completo del Hero y dónde lo importás. No avances a la siguiente sección.
```

**Reviso, ajusto, valido. Después sigo.**

#### Cada sección siguiente con el mismo formato:

```
Ahora la sección [Nombre]. 

Características:
- [Detalles específicos]
- [Layout]
- [Elementos]
- Server component (a menos que necesite interactividad)
- Props tipadas
- Datos hardcodeados por ahora

Mostrame el código y dónde lo integrás. No avances.
```

### 2.2 — Header y Footer (cuando aparecen en Home)

```
La home está tomando forma. Necesitamos Header y Footer ahora.

Header:
- Logo (importar SVG desde references/brand-assets/)
- Navegación: [items]
- CTA primario: [texto]
- Mobile: [hamburger menu / drawer / otro]
- Sticky con cambio de fondo al scrollear: [sí/no]
- Z-index correcto

Footer:
- Layout: [columnas y contenido]
- Links de navegación
- Datos de contacto
- Redes sociales
- Copyright dinámico (año actual)
- Política de privacidad y términos

Server components donde sea posible. Client component solo si hay interactividad.
```

### 2.3 — Resto de páginas

Para cada página, mismo flujo: sección por sección, validar entre cada una, no avanzar a la siguiente hasta aprobar la actual.

---

## FASE 3: Estados y manejo de errores

> Esto es lo que separa un sitio amateur de uno profesional. NO lo skipees.

### 3.1 — Loading states

```
Para cada componente que carga datos asincrónicamente o se conecta a APIs externas, necesito:

- Skeleton loader (NO spinner) que respete el layout final
- Skeletons en componentes server con Suspense boundaries
- Mostrame qué componentes van a tener loading state y cómo se ven

Aplicalo a: [lista]
```

### 3.2 — Error states

```
Para cada componente que puede fallar (API externa, fetch de datos, formulario):

- Try/catch en server components con fallback útil
- Error boundaries en client components
- Mensaje de error en español, claro, no técnico
- Acción de recuperación cuando es posible (botón de retry)

Aplicalo a: [lista]
```

### 3.3 — Empty states

```
Para cada componente que renderiza listas dinámicas (proyectos, testimonios, blog posts):

- Empty state visualmente cuidado, no solo "no hay items"
- Texto contextual según el caso
- CTA para acción relacionada cuando aplica

Aplicalo a: [lista]
```

---

## FASE 4: Formularios profesionales

### 4.1 — Setup base del form

```
Vamos a construir el formulario de contacto.

Stack:
- React Hook Form para manejo
- Zod para validación
- Server action (o /app/api/contact/route.ts si hace falta endpoint público)
- Resend o ZeptoMail para email del sistema (separado del mailbox humano del cliente)
- Honeypot field anti-spam (no captcha)
- Rate limiting básico por IP

Estados visuales:
- idle (default)
- submitting (botón deshabilitado, indicator visible)
- success (mensaje de confirmación, no redirect)
- error (mensaje claro, mantener data del form)

Validaciones:
- [Lista de campos y validaciones específicas]
- Mensajes de error en español
- Validación on blur, no on change

Email:
- Plantilla HTML branded para el cliente
- Email de confirmación al usuario que envía
- Replyable (reply-to del usuario)
```

### 4.2 — Persistencia (opcional pero recomendado)

```
Si el usuario llena el form parcialmente y refresca, perdemos el lead.

Implementá persistencia en localStorage del form data, con clear automático al success.
```

---

## FASE 5: Contenido

> Solo después de que todas las páginas estén bien diseñadas y aprobadas con datos hardcodeados.
> Gate: ¿el cliente necesita editar contenido seguido? Está en BRIEF.md (sección 7). No se mete un CMS preventivamente.

### 5.1 — Opción A: contenido en el repo (default)

```
Mové el contenido hardcodeado a archivos de contenido:

- Markdown (MDX si hace falta) para textos largos y listas (proyectos, posts, casos)
- JSON o TS tipado para singletons (datos de contacto, home, navegación)
- Carpeta /content/
- Tipos generados o declarados para cada archivo
- Los componentes reciben la data por props; no cambies el diseño visual

Mostrame la estructura de /content/ y cómo se lee desde cada page.tsx.
```

Flujo de cambios: el cliente pide → se cambia el archivo → branch → preview → merge → deploy.

### 5.2 — Opción B: Sanity (solo si el cliente edita seguido)

```
Integrá Sanity con Next.js App Router.

Schema cerrado y estricto:
- Máximo 5-7 campos editables por sección
- Alt text obligatorio en TODAS las imágenes
- Description en cada campo de imagen indicando dimensiones y peso recomendado
- Validación de longitud en strings (max y min cuando aplique)
- Listas con límites razonables (ej: máximo 10 testimonios)
- Labels en español, descriptivos
- Imágenes servidas desde el CDN de Sanity (no en repo)
- Revalidate on publish con webhook

Schema basado en: [referenciar componentes ya construidos]

Mostrame los schemas completos antes de conectar las páginas.
NO cambies el diseño visual. Solo el origen de los datos.
Mantené todos los estados que ya armamos (loading, error, empty).
```

### 5.3 — Probar flujo completo

- [ ] Hacer un cambio de contenido (archivo o CMS)
- [ ] Ver la preview
- [ ] Publicar
- [ ] Ver el cambio en producción

---

## FASE 6: Animaciones (GSAP + Motion)

> Solo cuando la estructura está estable. Animar antes es perder tiempo.

### 6.1 — Filosofía de animaciones

```
Vamos a sumar animaciones siguiendo lo definido en DESIGN_SYSTEM.md sección 9.

Filosofía: [pegar de design system]

Animaciones a implementar:

1. Page entry: fade in + subtle slide up
2. Section reveal on scroll: stagger según elementos
3. Hover states refinados en botones y cards
4. Smooth scroll entre secciones (con offset por header sticky)

Implementación:
- GSAP + ScrollTrigger para timelines y reveals de scroll (Lenis solo si hay scrollytelling, con prevent en forms, canvas y touch)
- Motion para hover, layout transitions y micro-interacciones de UI
- Importar solo los módulos usados
- Respetar prefers-reduced-motion
- Server components mantenerse server cuando sea posible
- Crear wrappers client component para animar contenido server

Empezamos por: [primera animación específica]
```

### 6.2 — Animar sección por sección

Igual que con páginas: una a la vez, validar, después seguir.

---

## FASE 7: SEO técnico

### 7.1 — Metadata

```
Configurar metadata por página:

- Title (50-60 chars) específico por página
- Description (150-160 chars) específico por página
- OG image (1200x630) específica por página principal
- X (Twitter) Card configurada
- Canonical URLs
- Locale correcto

Crear helper para generar metadata consistente.
```

### 7.2 — Datos estructurados (Schema.org)

```
Implementar JSON-LD según el rubro:

- Organization en layout.tsx (todas las páginas)
- LocalBusiness si aplica (con dirección, horarios, teléfono)
- Service schema en página de servicios
- Person schema si hay equipo
- BreadcrumbList en páginas internas
- FAQPage en sección de FAQs si existe

Validar con Google Rich Results Test al final.
```

### 7.3 — Sitemap y robots

```
- Crear sitemap.xml dinámico (app/sitemap.ts)
- Crear robots.txt (app/robots.ts)
- Verificar URLs limpias (no .html, no query params innecesarios)
- Configurar trailing slash policy
```

### 7.4 — Imágenes optimizadas

```
- Convertir TODAS las <img> a <Image> de Next.js
- Width y height correctos
- Alt text en todas (chequear)
- priority en LCP image (hero principal)
- sizes attribute correcto
- placeholder blur donde aplique
```

---

## FASE 8: Accesibilidad

### 8.1 — Audit de accesibilidad

```
Hacé audit de accesibilidad del sitio:

1. Heading hierarchy correcta (1 H1 por página, jerarquía lógica)
2. Alt text en todas las imágenes (no decorativas con alt="")
3. Labels asociadas correctamente con inputs
4. Contraste de colores cumpliendo WCAG AA (4.5:1 mínimo)
5. Focus states visibles en todos los elementos interactivos
6. Skip-to-content link en header
7. ARIA labels en botones de íconos sin texto
8. Navegación por teclado funcional
9. Reduced motion respetado

Mostrame los issues encontrados y arreglemos uno por uno.

Target: Lighthouse Accessibility 95+
```

### 8.2 — Internacionalización (si aplica)

```
[Solo si el proyecto requiere multi-idioma]

Setup de next-intl:
- Routing /es y /en
- Archivos de traducción en /messages/
- Switcher de idioma en header
- Hreflang tags
- Idioma por defecto detectado por browser
```

---

## FASE 9: Performance

### 9.1 — Audit de performance

```
Audit de performance del sitio:

1. Lighthouse en cada página principal (target: 90+)
2. Core Web Vitals:
   - LCP < 2.5s
   - INP < 200ms
   - CLS < 0.1
3. Bundle size analysis (@next/bundle-analyzer)
4. Identificar componentes pesados que pueden ser dynamic imports
5. Verificar lazy loading below-fold

Mostrame issues y arreglemos.
```

### 9.2 — Optimizaciones específicas

- [ ] Fonts con `display: swap` y preload
- [ ] Imágenes con sizes correctos
- [ ] Componentes interactivos con dynamic import
- [ ] Third-party scripts con `next/script` strategy="lazyOnload"
- [ ] CSS crítico inline cuando aplique

---

## FASE 10: Tracking y conversiones

### 10.1 — Setup de analytics

```
Configurar tracking:

1. GA4 (default)
2. Search Console verificado + sitemap enviado
3. Microsoft Clarity (heatmaps y grabaciones)
4. PostHog solo si hay funnels o producto
3. Eventos custom para:
   - Form submissions
   - Click en CTAs principales (WhatsApp, llamadas)
   - Scroll depth en páginas largas
   - Click en links externos

Crear helper de tracking para que sea fácil agregar eventos después.
```

---

## FASE 11: Legales y compliance

### 11.1 — Páginas legales

```
Crear páginas legales (placeholders si cliente no tiene textos):

- /privacidad — Política de privacidad
- /terminos — Términos y condiciones
- /cookies — Política de cookies (si aplica)

Layout simple, accesible desde footer.
```

### 11.2 — Aviso de cookies (si analytics tracking)

```
Implementar banner de cookies:
- No invasivo (no oculta contenido)
- Aceptar / Rechazar / Configurar
- Persistencia de preferencia
- Bloquear analytics hasta aceptación

Stack: react-cookie-consent o custom simple.
```

---

## FASE 12: Pre-launch

### 12.1 — Testing manual

- [ ] Test en Chrome desktop
- [ ] Test en Safari desktop
- [ ] Test en Firefox desktop
- [ ] Test en iPhone real (Safari)
- [ ] Test en Android real (Chrome)
- [ ] Test con throttling 3G en dev tools
- [ ] Test de cada formulario punta a punta (incluido email recibido)
- [ ] Test de cada link interno
- [ ] Test de cada CTA externo (WhatsApp, llamada, etc.)
- [ ] Validar que no hay links rotos (broken-link-checker)

### 12.1b — QA automática

```
Corré la QA completa antes de pedir aprobación.
La evidencia de la web publicada la junta el skill de diagnóstico de Nexar-Hub/.github:
`node /tmp/nexar-hub/.claude/skills/diagnostico/scripts/audit.mjs <preview-url>` (cero `fail`).

1. Build, TypeScript y lint sin errores
2. Links rotos, metadata, sitemap y robots.txt
3. Errores de consola en cada página
4. Forms y eventos de analytics disparando
5. Screenshots con Playwright en 390, 768, 1280 y 1440 px de cada página principal
6. Comparación visual contra references/ y DESIGN_SYSTEM.md

Reportá lo que falla y arreglemos uno por uno.
```

### 12.2 — Spell check y revisión

- [ ] Revisar copy de cada página (sin errores ortográficos)
- [ ] Revisar coherencia tipográfica
- [ ] Revisar que datos de contacto sean correctos
- [ ] Revisar que precios y números sean correctos
- [ ] Cliente aprueba copy final

### 12.3 — OG images y favicon

- [ ] Generar OG image por página principal (1200x630)
- [ ] Verificar preview en WhatsApp, LinkedIn y X
- [ ] Favicon en múltiples tamaños (16, 32, 180, 192, 512)
- [ ] Apple touch icon
- [ ] manifest.json con theme color

---

## FASE 13: Deploy y DNS

### 13.1 — Deploy (Cloudflare Workers)

Pipeline: branch → GitHub → preview → QA visual → aprobación → merge a main → producción. **Nunca se edita producción directamente.**

```
- [ ] Preview aprobada por el cliente
- [ ] Merge a main
- [ ] Verificar que build pasa sin errores ni warnings
- [ ] Variables de entorno configuradas en el hosting
- [ ] CMS conectado (si aplica)
- [ ] Domain custom configurado
```

### 13.2 — DNS y email

```
- [ ] DNS en Cloudflare apuntando al hosting (CNAME o A records)
- [ ] SSL automático verificado
- [ ] SPF record configurado para email
- [ ] DKIM record configurado
- [ ] DMARC record configurado
- [ ] Test de email del form llegando sin spam folder
```

### 13.3 — Redirects (si migra de sitio anterior)

```
- [ ] Lista de URLs antiguas a redirigir
- [ ] Configurar redirects en next.config.js (o en la config del hosting)
- [ ] Test de cada redirect
```

---

## FASE 14: Post-launch

### 14.1 — Documentación al cliente

- [ ] Loom de uso del CMS o del flujo de pedidos de cambio (5-10 min, paso a paso)
- [ ] PDF con credenciales y accesos (en 1Password compartido)
- [ ] Guía rápida de "cómo editar X" para casos comunes
- [ ] README en el repo (técnico, para futuros devs)
- [ ] Lista de servicios externos usados con sus accesos

### 14.2 — Handoff meeting

- [ ] Demostración en vivo del CMS (Zoom/Meet)
- [ ] Cliente edita algo en vivo (verificar que entiende)
- [ ] Política de soporte revisada
- [ ] Período de revisión de 14 días explicado
- [ ] Canales de comunicación claros para soporte

### 14.3 — Setup de monitoreo

- [ ] Notificaciones de deploy del hosting
- [ ] Analytics revisándose primer mes
- [ ] Alerta de errores (hosting o servicio de monitoreo)

---

## Anti-patrones a evitar siempre

1. **"Armame todo el sitio"** → Construir incremental, sección por sección
2. **Saltar BRIEF.md** → Resultado: refactor masivo después
3. **Animar antes de tener layout estable** → Animar al final, siempre
4. **CMS al inicio (o "por las dudas")** → Estructura primero; CMS solo si el cliente edita seguido
5. **Skip de loading/error/empty states** → El cliente rompe algo y la web tira 500
6. **Imágenes sin Next/Image** → Performance pobre, SEO pobre
7. **Forms sin validación robusta** → 30-50% menos conversión
8. **Lanzar sin testing en mobile real** → Bugs vergonzosos día 1
9. **Sin OG images por página** → Cliente comparte el link, queda mal
10. **Sin política de soporte por escrito** → Trabajás gratis para siempre

---

## Cuando algo sale mal a mitad de proyecto

### Cliente cambia de idea sobre el diseño después de aprobado

→ Es scope creep. Cobrar aparte o decir que no según contrato.

### Cliente no entrega contenido a tiempo

→ Pausar el proyecto. No avanzar con placeholders eternamente.

### Algo técnico no funciona y no podés debuggear

→ Pedile a Claude Code: "este es el error, este es el contexto, qué probarías." Iterar con info real, no adivinanzas.

### Te das cuenta que el stack elegido no era el correcto

→ Si es semana 1, podés cambiar. Si es semana 4, no. Documentá la lección y seguí adelante.
