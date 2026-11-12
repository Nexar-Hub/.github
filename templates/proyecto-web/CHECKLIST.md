# CHECKLIST — [Nombre del Cliente]

> Tildá items mientras avanzás. Items marcados con 🔴 son críticos: NO entregás sin tildarlos.

---

## Pre-kickoff 🔴

- [ ] 🔴 Brief firmado o aprobado por escrito
- [ ] 🔴 Política de soporte enviada y aceptada
- [ ] 🔴 Pago inicial recibido (50% es lo recomendado)
- [ ] BRIEF.md llenado completamente
- [ ] DESIGN_SYSTEM.md llenado con tokens base
- [ ] Brand assets recibidos (logo SVG, colores, fuentes)
- [ ] Contenido base recibido (copy de cada página)
- [ ] Imágenes / fotos recibidas
- [ ] Acceso al dominio actual (si migra)
- [ ] Acceso a Google Analytics existente (si tiene)
- [ ] Referencias visuales en `references/inspiration/`
- [ ] Capturas de competencia en `references/competitors/`
- [ ] Stakeholder principal identificado
- [ ] Plazo de entrega acordado por escrito

---

## Diseño y aprobación

- [ ] Moodboard presentado (si aplica)
- [ ] Diseño aprobado para mobile
- [ ] Diseño aprobado para desktop
- [ ] Sistema de diseño cerrado y documentado
- [ ] Cliente aprobó dirección visual antes de empezar dev

---

## Desarrollo: setup

- [ ] Repositorio en GitHub creado
- [ ] Next.js inicializado con App Router
- [ ] TypeScript configurado en strict mode
- [ ] Tailwind configurado con tokens del DESIGN_SYSTEM
- [ ] Fuentes cargadas con next/font
- [ ] Estructura de carpetas establecida
- [ ] Variables de entorno definidas en .env.example
- [ ] Proyecto en Cloudflare Workers creado y conectado al repo con previews por branch

---

## Desarrollo: páginas

### Home
- [ ] Hero
- [ ] Secciones intermedias (listar todas):
  - [ ] 
  - [ ] 
  - [ ] 
- [ ] CTA final
- [ ] Mobile responsive verificado
- [ ] Aprobada por cliente

### Página secundaria 1: ___________
- [ ] Estructura completa
- [ ] Mobile responsive
- [ ] Aprobada por cliente

### Página secundaria 2: ___________
- [ ] Estructura completa
- [ ] Mobile responsive
- [ ] Aprobada por cliente

### Contacto
- [ ] Formulario funcional
- [ ] Información de contacto
- [ ] Mapa (si aplica)
- [ ] WhatsApp button (si aplica)

### Páginas legales
- [ ] /privacidad
- [ ] /terminos
- [ ] /cookies (si aplica)

---

## Desarrollo: componentes globales

- [ ] Header con navegación
- [ ] Header mobile (hamburger menu o equivalente)
- [ ] Footer completo
- [ ] Botones del sistema (primary, secondary, ghost)
- [ ] Cards del sistema
- [ ] Inputs y forms del sistema

---

## Estados (crítico) 🔴

- [ ] 🔴 Loading states en componentes async
- [ ] 🔴 Error states con fallback útil
- [ ] 🔴 Empty states en listas dinámicas
- [ ] 🔴 404 page custom
- [ ] 🔴 500 page custom
- [ ] Try/catch en server components
- [ ] Error boundaries en client components

---

## Formularios 🔴

- [ ] 🔴 React Hook Form + Zod implementados
- [ ] 🔴 Validación client-side
- [ ] 🔴 Mensajes de error en español
- [ ] 🔴 Estado submitting visible
- [ ] 🔴 Estado success post-envío
- [ ] 🔴 Estado error con retry
- [ ] 🔴 Honeypot anti-spam
- [ ] 🔴 Rate limiting en endpoint
- [ ] 🔴 Email al cliente con plantilla HTML branded
- [ ] 🔴 Email de confirmación al usuario
- [ ] 🔴 Test punta a punta del form en producción
- [ ] Persistencia en localStorage (opcional pero recomendado)

---

## Contenido / CMS

> Solo si `BRIEF.md` dice que el cliente edita contenido seguido. Si no, el contenido vive en Markdown/JSON en el repo y esta sección queda N/A.

- [ ] 🔴 Sanity instalado y configurado
- [ ] 🔴 Schema cerrado (máximo 5-7 campos por sección)
- [ ] 🔴 Alt text obligatorio en imágenes
- [ ] 🔴 Imágenes servidas desde el CDN del CMS (NO en repo)
- [ ] 🔴 Variables de entorno en el hosting
- [ ] 🔴 Webhook al hosting para rebuild / revalidate on publish
- [ ] 🔴 Cliente invitado con rol Editor (no Admin)
- [ ] Schema con descriptions útiles
- [ ] Validaciones de longitud en campos texto
- [ ] Crops predefinidos donde aplique

---

## Animaciones

- [ ] GSAP (timelines/scroll) y/o Motion (UI) instalados, solo los módulos usados
- [ ] Page entry animation
- [ ] Section reveal on scroll
- [ ] Hover states refinados
- [ ] Smooth scroll con offset por header
- [ ] Reduced motion respetado
- [ ] No animaciones que afecten LCP

---

## SEO técnico 🔴

- [ ] 🔴 Title único por página (50-60 chars)
- [ ] 🔴 Description única por página (150-160 chars)
- [ ] 🔴 OG image por página principal
- [ ] 🔴 X (Twitter) Card configurada
- [ ] 🔴 Canonical URLs
- [ ] 🔴 Heading hierarchy correcta (1 H1 por página)
- [ ] 🔴 Alt text en todas las imágenes
- [ ] 🔴 sitemap.xml dinámico
- [ ] 🔴 robots.txt
- [ ] JSON-LD Organization schema
- [ ] JSON-LD específico por rubro (LocalBusiness, Service, etc.)
- [ ] Validado con Google Rich Results Test
- [ ] URLs limpias (sin extensiones, sin query params innecesarios)

---

## Imágenes 🔴

- [ ] 🔴 Todas las imágenes con next/image
- [ ] 🔴 Width y height correctos
- [ ] 🔴 Alt text descriptivo en todas
- [ ] 🔴 priority en LCP image
- [ ] sizes attribute correcto
- [ ] Formatos modernos (WebP/AVIF) servidos
- [ ] Lazy loading below-fold
- [ ] Imágenes en CDN (o /public/ optimizadas a AVIF con variantes por tamaño)

---

## Accesibilidad 🔴

- [ ] 🔴 Lighthouse Accessibility 95+
- [ ] 🔴 Contraste WCAG AA cumplido (4.5:1 mínimo)
- [ ] 🔴 Focus states visibles en todos los interactivos
- [ ] 🔴 Navegación por teclado funcional
- [ ] Skip-to-content link en header
- [ ] ARIA labels en botones de íconos
- [ ] Labels asociadas a inputs
- [ ] Estructura semántica correcta (header, nav, main, footer, etc.)
- [ ] Reduced motion respetado

---

## Performance 🔴

- [ ] 🔴 Lighthouse Performance 90+ en home
- [ ] 🔴 Lighthouse Performance 90+ en páginas principales
- [ ] 🔴 LCP < 2.5s
- [ ] 🔴 CLS < 0.1
- [ ] 🔴 INP < 200ms
- [ ] Bundle size razonable (< 200KB inicial)
- [ ] Fuentes con display: swap
- [ ] Componentes pesados con dynamic import
- [ ] Third-party scripts con strategy correcta
- [ ] Preload de recursos críticos

---

## Tracking y analytics

- [ ] GA4 configurado
- [ ] Search Console verificado y sitemap enviado
- [ ] Microsoft Clarity configurado
- [ ] PostHog (solo si hay funnels o producto)
- [ ] Eventos custom para form submissions
- [ ] Eventos custom para CTAs principales (WhatsApp, llamadas)
- [ ] Eventos custom para clicks en links externos
- [ ] Conversiones definidas explícitamente

---

## Legales

- [ ] Política de privacidad publicada
- [ ] Términos y condiciones publicados
- [ ] Aviso de cookies (si tiene tracking)
- [ ] Links legales accesibles desde footer
- [ ] Cliente conseguió textos legales de abogado (NO redactarlos vos)

---

## Multi-idioma (si aplica)

- [ ] Setup de next-intl o equivalente
- [ ] Archivos de traducción completos
- [ ] Switcher de idioma funcional
- [ ] Hreflang tags
- [ ] URLs con prefijo de idioma (/es, /en)
- [ ] Detección de idioma por browser

---

## Testing pre-launch 🔴

### Browser
- [ ] 🔴 Chrome desktop
- [ ] 🔴 Safari desktop
- [ ] 🔴 Firefox desktop
- [ ] 🔴 iPhone Safari (real device)
- [ ] 🔴 Android Chrome (real device)
- [ ] Edge desktop

### Funcional
- [ ] 🔴 Cada formulario enviado punta a punta
- [ ] 🔴 Email recibido por cliente sin caer en spam
- [ ] 🔴 Email de confirmación recibido por usuario
- [ ] 🔴 Cada link interno funciona
- [ ] 🔴 Cada CTA externo funciona (WhatsApp, mailto, tel:)
- [ ] No hay broken links (broken-link-checker)
- [ ] CMS funciona en producción

### Network
- [ ] Test con throttling 3G
- [ ] Test con conexión lenta
- [ ] Verificación de tiempos de carga reales

### Contenido
- [ ] Spell check en cada página
- [ ] Datos de contacto correctos
- [ ] Precios y números correctos
- [ ] Cliente aprueba copy final
- [ ] Cliente aprueba imágenes finales

---

## Compartibilidad

- [ ] OG images verificadas en WhatsApp
- [ ] OG images verificadas en LinkedIn (LinkedIn Inspector)
- [ ] OG images verificadas en X (compartiendo en un post de prueba; el Card Validator ya no muestra preview)
- [ ] Favicon visible en todos los browsers
- [ ] Apple touch icon en iOS
- [ ] Theme color en mobile

---

## Deploy 🔴

- [ ] 🔴 Build pasa sin errores ni warnings
- [ ] 🔴 Variables de entorno configuradas en el hosting
- [ ] 🔴 Domain custom configurado y funcionando
- [ ] 🔴 SSL verificado (https sin warnings)
- [ ] 🔴 SPF record configurado
- [ ] 🔴 DKIM record configurado
- [ ] 🔴 DMARC record configurado
- [ ] 🔴 Test de email no cae en spam
- [ ] Redirects 301 desde sitio anterior (si aplica)
- [ ] CMS conectado en producción (si aplica)
- [ ] Webhook de rebuild funcionando (si aplica)
- [ ] 🔴 Screenshots Playwright en 390 / 768 / 1280 / 1440 revisados
- [ ] 🔴 Nada se editó directo en producción (todo pasó por branch → preview → aprobación)

---

## Post-launch 🔴

- [ ] 🔴 Loom de uso del CMS (o del flujo de pedidos de cambio) grabado y enviado al cliente (5-10 min)
- [ ] 🔴 PDF con credenciales y accesos compartido
- [ ] 🔴 Política de soporte revisada con cliente
- [ ] 🔴 Período de revisión de 14 días iniciado
- [ ] 🔴 Cliente confirmó recepción y aceptación del entregable
- [ ] 🔴 Pago final solicitado y recibido
- [ ] README en el repo actualizado
- [ ] Lista de servicios externos documentada
- [ ] 1Password vault compartido con cliente
- [ ] Backup inicial verificado

---

## Tracking de uso post-entrega (90 días)

> Para refinar el sistema y decisiones futuras de stack

### Métricas a trackear
- [ ] Cantidad de logins del cliente al CMS: ___
- [ ] Tipo de cambios realizados (texto / imagen / nuevos items): ___
- [ ] Errores o bloqueos reportados por cliente: ___
- [ ] Cambios solicitados al equipo (fuera del CMS): ___

### Aprendizajes para próximo proyecto
- 
- 
- 

---

## Cierre del proyecto

- [ ] Cliente firmó conformidad final
- [ ] Pago final recibido
- [ ] Documentación archivada en sistema interno
- [ ] Caso de estudio documentado para portfolio
- [ ] Pedido de testimonio enviado al cliente
- [ ] Pedido de referidos enviado al cliente
- [ ] Retainer / mantenimiento ofrecido (si aplica)
