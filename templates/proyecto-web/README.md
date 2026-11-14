# Nexar Hub — Sistema Operativo de Proyectos Web

Este es el sistema único que vas a usar para cada cliente nuevo. No improvisás. No mezclás workflows. Seguís este flujo y entregás con consistencia.

## Filosofía

Tres principios no negociables:

1. **Contexto pesado al inicio** — Todo lo importante se define antes de escribir una línea de código.
2. **Construcción incremental con validación** — Página por página, sección por sección. Nunca "armame todo el sitio."
3. **Sistema antes que herramienta** — La calidad del entregable depende del proceso, no de qué CMS uses.

## Cómo usar este template

### Para cada cliente nuevo:

```bash
git clone https://github.com/Nexar-Hub/.github.git /tmp/nexar-hub
cp -r /tmp/nexar-hub/templates/proyecto-web/ ~/projects/cliente-nuevo/
cd ~/projects/cliente-nuevo/
git init && npm install && cp .env.example .env.local
npm run dev
```

El sitio arranca en http://localhost:3000 con el esqueleto neutro: header, hero, contacto y footer.

### Después:

1. Llenás `BRIEF.md` con el contexto del cliente
2. Llenás `DESIGN_SYSTEM.md` con tokens visuales
3. Subís referencias visuales a `references/`
4. Abrís Claude Code y seguís `WORKFLOW.md` paso a paso
5. Tildás items en `CHECKLIST.md` mientras avanzás

### Stack default

Alineado con el blueprint de webs (`brain/workflows/website.md` en `Nexar-Hub/.github`). Se suma complejidad solo cuando el proyecto la exige.

- **Framework:** Next.js (App Router) + TypeScript strict
- **Estilos y UI:** Tailwind CSS + shadcn/ui
- **Contenido:** Markdown / JSON en el repo por default. Sanity solo si el cliente edita contenido seguido
- **Hosting:** Cloudflare Workers (Next.js vía adaptador OpenNext) · DNS en Cloudflare · media pesada en R2 / Images
- **Formularios:** server action + Resend o ZeptoMail
- **Animaciones:** GSAP (+ ScrollTrigger y Lenis para scrollytelling) para timelines; Motion para micro-interacciones de UI
- **3D (solo si mejora comprensión, deseo o exploración):** React Three Fiber + Drei
- **Analytics:** GA4 + Search Console + Microsoft Clarity. PostHog si hacen falta funnels

## Archivos del sistema

```
proyecto-web/
├── README.md                    Este archivo
├── BRIEF.md                     Brief del cliente (llenar siempre)
├── DESIGN_SYSTEM.md             Sistema de diseño del proyecto
├── WORKFLOW.md                  Pasos exactos a seguir con Claude Code
├── CHECKLIST.md                 Checklist completo del proyecto
├── HANDOFF.md                   Plantilla de entrega al cliente
├── SUPPORT_POLICY.md            Política de soporte post-entrega
├── CLAUDE.md                    Instrucciones que Claude Code carga solo al iniciar
├── references/
│   ├── inspiration/             Sitios que le gustan al cliente
│   ├── competitors/             Capturas de competencia
│   └── brand-assets/            Logo, colores oficiales, fuentes
└── (código: ver abajo)
```

## Código incluido

Un starter que ya pasa el diagnóstico de Nexar (31 de 33 checks en local; los otros dos son HTTPS y la carga de GA4/Clarity, que se resuelven en producción).

```
content/site.ts                  Datos del sitio (desde BRIEF.md): única fuente para metadata, sitemap, robots, llms.txt y JSON-LD
app/
  layout.tsx                     Metadata, Open Graph, JSON-LD Organization, skip link, medición
  page.tsx                       Home: hero + contacto (las secciones se suman en la fase 2)
  actions.ts                     Server action del formulario: Zod, honeypot, envío por Resend
  globals.css                    Tokens (desde DESIGN_SYSTEM.md), compatibles con shadcn/ui
  not-found.tsx                  404 real
  robots.ts · sitemap.ts         SEO técnico
  llms.txt/route.ts              Resumen para motores de IA (GEO)
  icon.svg                       Favicon (reemplazar)
components/
  analytics/Analytics.tsx        GA4 + Microsoft Clarity si hay IDs
  analytics/TrackedLink.tsx      Link que mide clics (CTA, WhatsApp)
  contact/ContactForm.tsx        Formulario accesible con estados y evento generate_lead
  layout/Header.tsx · Footer.tsx
lib/analytics.ts                 track() y nombres de eventos; nunca rompe el sitio
lib/utils.ts                     cn() de shadcn/ui
public/og.png                    Imagen OG 1200×630 (reemplazar)
next.config.ts                   Headers de seguridad (CSP, HSTS, nosniff, frame) y AVIF
wrangler.jsonc · open-next.config.ts   Deploy en Cloudflare Workers
.env.example                     Variables de build y secretos
```

| Comando | Para qué |
|---------|----------|
| `npm run dev` | Desarrollo local |
| `npm run build` | Build de Next.js (incluye TypeScript) |
| `npm run typecheck` | Solo TypeScript |
| `npm run preview` | Build para Cloudflare + Worker local (runtime real) |
| `npm run deploy` | Deploy manual. Lo normal es Workers Builds conectado al repo, con preview por branch |

Para sumar componentes de shadcn/ui: `npx shadcn@latest add button`. Para la QA: el skill de diagnóstico de `Nexar-Hub/.github` sobre la preview (cero `fail`).

## Reglas de oro del sistema

1. **Nunca arrancás Claude Code sin haber llenado BRIEF.md y DESIGN_SYSTEM.md.**
2. **Nunca aceptás un cliente sin haber leído juntos SUPPORT_POLICY.md.**
3. **Nunca entregás un proyecto sin haber tildado todos los items críticos de CHECKLIST.md.**
4. **Nunca prometés rankings de SEO. Solo SEO técnico de fundación.**
5. **Nunca subís imágenes sin optimizar al repo.** Fotos y video pesados en CDN (Cloudflare R2 / Images); el resto en AVIF con variantes por tamaño.

## Cuándo NO usar este sistema

- Cliente quiere e-commerce con catálogo grande → Shopify + integración (no se construye a medida)
- Cliente con presupuesto mínimo → derivá
- Cliente no tiene contenido ni claridad de marca → primero brand strategy, después web

## Mantenimiento del sistema

Cada 3 meses revisás este template:
- ¿Qué archivos te faltaron en proyectos recientes?
- ¿Qué pasos del WORKFLOW.md no funcionaron?
- ¿Qué items del CHECKLIST.md son redundantes?

Iterás el sistema con la fricción real, no en abstracto.
