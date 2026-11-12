# Workflow — Web (Nexar blueprint)

> Cada web nueva no empieza de cero. Empieza desde un blueprint probado y solo suma complejidad cuando el proyecto la exige.
> La plantilla ejecutable está en `templates/proyecto-web/`.

## Objective

Entregar una web rápida, editable y medible, con diseño que soporte objetivos de negocio, y dejarla lista para el loop de optimización.

## Inputs (intake)

```
Cliente
Dominio
Objetivo principal
Páginas necesarias
CTA principal
Contenido disponible
¿Necesita editar contenido?        sí / no
¿Necesita leads?                   sí / no
¿Necesita newsletter?              sí / no
¿Necesita login o datos dinámicos? sí / no
```

Resultado: `BRIEF.md` del proyecto.

## Steps

### 1. Arquitectura cognitiva antes que UI

Se diseña la secuencia mental del visitante, no la interfaz. El scroll es un vector cognitivo, no un layout.

| Estado | El visitante… |
|--------|---------------|
| 0 · Desorientación | acaba de llegar |
| 1 · Comprensión | entiende qué es esto |
| 2 · Relevancia | siente que es para él |
| 3 · Confianza | cree que funciona |
| 4 · Acción | da el paso |

Cada sección responde: estado mental de entrada, fricción que elimina, información mínima necesaria, estado mental de salida.

Decisiones que se fijan acá: qué se muestra primero, qué se oculta, qué se retrasa, qué nunca se dice, dónde entra el shock visual, dónde entra el silencio.

### 2. Elegir blueprint

Default: **Lean Company Web** — Next.js, TypeScript, Tailwind, shadcn/ui, GitHub, Cloudflare DNS, Vercel o Cloudflare Workers, analytics, email transaccional si hace falta. Estas cosas no se vuelven a decidir para cada cliente. Ver stack completo en `brain/nexar.md` §9.

### 3. Scaffold

El agente recibe `BRIEF.md` + blueprint + referencias de diseño + brand assets y genera: repo, páginas, componentes, SEO base, analytics, `.env.example`, config de deploy y README. Queda en GitHub con preview URL.

### 4. Diseño (el trabajo diferencial)

```
Brief → Dirección visual → Home → Páginas core → Motion → Responsive
```

El agente construye. El fundador decide jerarquía, dirección visual, pacing, motion, qué mostrar y qué eliminar. Ver `brain/taste.md`.

### 5. Contenido

¿El cliente necesita editar contenido seguido?

- **No:** Markdown / JSON / TS en el repo. El cliente pide el cambio → se cambia → merge → deploy.
- **Sí:** Sanity → Next.js.

No se mete un CMS preventivamente.

### 6. Formularios y leads

```
Web → server action → Resend o ZeptoMail → cliente
```

Si además hace falta CRM: `Web → webhook → HubSpot / Airtable / Supabase`. Solo si existe la necesidad.

### 7. Email

Separado siempre:

- **Email humano** (`nombre@empresa.com`) → proveedor de mailbox.
- **Email del sistema** (formularios, confirmaciones, notificaciones) → Resend / ZeptoMail.

Así la infraestructura nunca queda atada a un solo proveedor.

### 8. Analytics

Baseline para todos: **GA4 + Search Console + Microsoft Clarity**. PostHog cuando hacen falta funnels o producto. No se instalan cinco sistemas de analytics por defecto.

### 9. Deploy

```
Agente → branch → GitHub → preview → QA visual → aprobación → merge a main → producción
```

**Nunca se edita producción directamente.**

### 10. QA

Checklist automática: build, TypeScript, lint, links rotos, metadata, sitemap, robots.txt, responsive, performance, forms, analytics, errores de consola.

Después Playwright con screenshots en **390 · 768 · 1280 · 1440** px y comparación visual. Solo después, producción.

### 11. Infra final del cliente

```
DOMAIN          → registrar
DNS             → Cloudflare
CODE            → GitHub
WEB             → Vercel / Cloudflare
CONTENT         → Git o Sanity
BUSINESS EMAIL  → proveedor de mailbox
SYSTEM EMAIL    → Resend / ZeptoMail
LEADS           → email o HubSpot o Airtable
ANALYTICS       → GA4 + Clarity + GSC
OPTIONAL DATA   → Supabase
```

### 12. Después de entregar

La web no termina en "shipped". Pasa a ser la infraestructura inicial del servicio de growth:

```
Web → tráfico → comportamiento → conversiones → problemas → experimentos → cambios → medición → aprendizaje
```

## El loop que más importa

```
Cliente 1 → se descubre algo que funciona → se valida → se vuelve capability
Cliente 2 → arranca con esa capability
Cliente 3 → arranca todavía mejor
```

No es construir webs más rápido. Es que cada web futura arranque desde un baseline mejor que la anterior. Cuando algo se valida en un proyecto real, se actualiza este archivo o la plantilla.

## Outputs

- Repo del cliente con README, `.env.example` y deploy configurado
- Preview aprobada y producción
- Analytics baseline funcionando
- `HANDOFF.md` completado

## Checklist

- [ ] Arquitectura cognitiva definida por sección
- [ ] Blueprint elegido y justificado si se sale del default
- [ ] CMS solo si el cliente edita seguido
- [ ] Email humano y de sistema separados
- [ ] GA4 + GSC + Clarity instalados
- [ ] QA automática y screenshots en 4 anchos
- [ ] Ningún cambio directo en producción
- [ ] Aprendizajes del proyecto volcados al blueprint
