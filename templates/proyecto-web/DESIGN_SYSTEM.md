# DESIGN SYSTEM — [Nombre del Cliente]

> Este archivo se llena ANTES de generar componentes. Define todos los tokens visuales del proyecto. Si está vacío, Claude inventa decisiones inconsistentes.

## 1. Estilo general

### Categoría visual
- [ ] Minimal / clean
- [ ] Editorial / serio
- [ ] Bold / impactante
- [ ] Premium / lujoso
- [ ] Tech / moderno
- [ ] Warm / humano
- [ ] Brutal / experimental

### Adjetivos visuales
1. 
2. 
3. 

### Referencias visuales (links)
1. 
2. 
3. 

### Lo que NO queremos visualmente
- 
- 

## 2. Colores

### Paleta principal
```
Primary:        #
Primary hover:  #
Secondary:      #
Accent:         #
```

### Neutrales
```
Background:     #
Surface:        #
Surface alt:    #
Border:         #
Border hover:   #
```

### Texto
```
Text primary:    #
Text secondary:  #
Text tertiary:   #
Text on primary: #
```

### Estados
```
Success:  #
Warning:  #
Error:    #
Info:     #
```

### Modo oscuro
- [ ] Sí, definir paleta dark
- [ ] No, solo light mode

Si dark mode:
```
Dark background:   #
Dark surface:      #
Dark text primary: #
Dark border:       #
```

### Reglas de uso de color
- Primary se usa en: 
- Accent se usa solo en: 
- Nunca usar [color] en: 

## 3. Tipografía

### Fuentes
- **Headings:** [Familia]
  - Pesos disponibles: 
  - Fallback: 
- **Body:** [Familia]
  - Pesos disponibles: 
  - Fallback: 
- **Mono (si aplica):** [Familia]

### Carga de fuentes
- [ ] Google Fonts
- [ ] Self-hosted (subir archivos a /public/fonts)
- [ ] Adobe Fonts (requiere kit)
- [ ] Fonts.com / otra

### Escala tipográfica

| Nombre | Tamaño desktop | Tamaño mobile | Peso | Line height | Letter spacing |
|--------|----------------|---------------|------|-------------|----------------|
| Display | 80px | 48px | | | |
| H1 | 64px | 40px | | | |
| H2 | 48px | 32px | | | |
| H3 | 32px | 24px | | | |
| H4 | 24px | 20px | | | |
| Body Large | 18px | 16px | | 1.6 | |
| Body | 16px | 16px | | 1.6 | |
| Body Small | 14px | 14px | | 1.5 | |
| Caption | 12px | 12px | | 1.4 | |

### Reglas tipográficas
- Heading principal: usar siempre [fuente, peso]
- Body: usar siempre [fuente, peso]
- Mayúsculas: solo en [casos específicos]
- Cursiva: solo en [casos específicos]

## 4. Espaciado

### Escala base
Unidad base: 4px (todo es múltiplo de 4)

```
xs:    4px
sm:    8px
md:    16px
lg:    24px
xl:    32px
2xl:   48px
3xl:   64px
4xl:   96px
5xl:   128px
```

### Espaciado de secciones
- **Padding vertical de sección desktop:** 
- **Padding vertical de sección mobile:** 
- **Padding horizontal del container:** 
- **Max-width del container:** 

### Espaciado entre elementos
- **Entre párrafos:** 
- **Entre heading y body:** 
- **Entre secciones de bloques:** 

## 5. Layout y grid

### Container
- **Max-width:** 1280px / 1440px / otro
- **Padding lateral mobile:** 
- **Padding lateral desktop:** 

### Breakpoints
```
mobile:    < 640px
tablet:    640px - 1024px
desktop:   1024px - 1440px
wide:      > 1440px
```

### Grid
- **Columnas en desktop:** 12
- **Gap desktop:** 
- **Columnas en mobile:** 4
- **Gap mobile:** 

## 6. Border radius

```
none:   0
sm:     4px
md:     8px
lg:     12px
xl:     16px
2xl:    24px
full:   9999px
```

### Reglas de uso
- Botones: 
- Cards: 
- Inputs: 
- Imágenes: 

## 7. Sombras

```
shadow-sm:  
shadow-md:  
shadow-lg:  
shadow-xl:  
```

### ¿Usamos sombras?
- [ ] Sí, definidas arriba
- [ ] No, diseño flat
- [ ] Solo sutiles en hover states

## 8. Componentes base

### Botones

#### Primary
- Background: 
- Text: 
- Padding: 
- Border radius: 
- Font weight: 
- Hover: 
- Active: 
- Disabled: 

#### Secondary
- Background: 
- Border: 
- Text: 
- Hover: 

#### Ghost / Tertiary
- 

#### Tamaños
- Small: 
- Default: 
- Large: 

### Inputs
- Background: 
- Border: 
- Border focus: 
- Padding: 
- Border radius: 
- Font size: 
- Placeholder color: 
- Error state: 
- Label: posición y estilo

### Cards
- Background: 
- Border: 
- Border radius: 
- Padding: 
- Shadow: 
- Hover state: 

### Navegación
- Background: 
- Height desktop: 
- Height mobile: 
- ¿Sticky?: 
- ¿Fondo cambia al scrollear?: 
- Logo: tamaño y posición
- Items: estilo
- CTA principal: estilo

### Footer
- Background: 
- Padding: 
- Layout: [columnas / centrado / minimal]
- Contenido: 

## 9. Animaciones

### Filosofía
- [ ] Sutiles y rápidas
- [ ] Pronunciadas y notorias
- [ ] Mínimas / casi ninguna
- [ ] Solo functional (no decorativas)

### Duración default
- **Quick:** 150ms (hover states)
- **Default:** 300ms (transitions)
- **Slow:** 500ms (entradas grandes)

### Easing default
```
default:   cubic-bezier(0.4, 0, 0.2, 1)
in:        cubic-bezier(0.4, 0, 1, 1)
out:       cubic-bezier(0, 0, 0.2, 1)
spring:    [config de Motion / GSAP]
```

### Animaciones específicas
- **Page entry:** 
- **Section reveal on scroll:** 
- **Hover en botones:** 
- **Hover en cards:** 
- **Loading states:** 

### Reduced motion
- [ ] Respetar `prefers-reduced-motion` (default)

## 10. Iconografía

### Set de íconos
- [ ] Lucide React (default)
- [ ] Heroicons
- [ ] Phosphor
- [ ] Custom (cliente provee SVGs)
- [ ] Otro: 

### Estilo
- [ ] Outline / línea
- [ ] Solid / relleno
- [ ] Mezcla según contexto

### Tamaños base
- Small: 16px
- Default: 20px
- Large: 24px
- XL: 32px

### Color default
- 

## 11. Imágenes y media

### Tratamiento de imágenes
- [ ] Sin tratamiento (originales)
- [ ] Filtros / overlays sutiles
- [ ] Duotone / monocrómico
- [ ] Otro: 

### Aspect ratios estándar
- Hero: 
- Cards: 
- Thumbnails: 
- Testimoniales: 

### Formato preferido
- [ ] AVIF (default Nexar)
- [ ] WebP
- [ ] JPG fallback

### Lazy loading
- [ ] Sí en todas las imágenes below-fold (default)

## 12. Voz y copy guidelines

### Persona
[Una frase: "Hablamos como X"]

### Reglas de copy
- Personas vs nombres propios: 
- Tuteo / Usted / Vos: 
- Tecnicismos: [usar / evitar / explicar]
- Emojis: [permitidos / no / solo en X contextos]
- Mayúsculas en headings: [Title Case / Sentence case / lowercase]
- Signos de admiración: [permitidos / evitar]

### Frases recurrentes
- CTAs primarios: ["Hablemos" / "Empezar" / "Contactanos" / etc]
- CTAs secundarios: 
- Errores en formularios: 

## 13. Accesibilidad

### Compromiso
- [ ] WCAG AA (mínimo, default Nexar Hub)
- [ ] WCAG AAA (cliente lo requiere)

### Contraste
- Texto sobre fondo: ratio mínimo 4.5:1
- Texto grande sobre fondo: ratio mínimo 3:1
- Verificado con: 

### Focus states
- Color del focus ring: 
- Estilo: 

### Navegación por teclado
- [ ] Todo accesible por Tab
- [ ] Skip-to-content link en header
- [ ] Trap focus en modales

## 14. Stack técnico de implementación

```
Framework:        Next.js App Router
Language:         TypeScript (strict)
Styling:          Tailwind CSS
UI primitives:    shadcn/ui (sobre Radix)
Animations:       GSAP (timelines, scroll) + Motion (UI)
Icons:            Lucide React
Content:          Markdown/JSON en repo · Sanity si el cliente edita seguido
Forms:            React Hook Form + Zod
Email:            Resend o ZeptoMail (sistema) · mailbox aparte (humano)
Analytics:        GA4 + Search Console + Microsoft Clarity (PostHog si hay funnels)
```

## 15. Decisiones tomadas durante el proyecto

[Log de decisiones que afectan el design system pero no estaban definidas al inicio]

- [Fecha] - 
- [Fecha] - 
