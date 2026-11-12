# Spread · Brief de la web (original)

> **Fuente:** export «Distribution», mensaje del 16/10/26. Se conserva textual porque es la
> instrucción de trabajo para construir la web. Donde dice *Distribution*, leé *Spread* si se
> confirma el cambio de nombre (ver [`POSITIONING.md`](POSITIONING.md)).
>
> **Cómo se cruza con la biblia** (agregado, no es parte del brief):
> - Las tres opciones de hero que pide la sección 6 incluyen al menos una con encuadre de pérdida
>   actual (palanca 2), por ejemplo la del pitch de conversión: *«You're already paying to bring the
>   right companies to your site. We're fixing what happens before they disappear.»*
> - El copy de `COPY.md` pasa por `python3 spread/tools/copy_audit.py` antes de implementarse
>   (reglas PT08 y SP01 en particular).
> - Prospect Theory, signals y agentes no aparecen en la web: es mecanismo interno.
> - Sin resultados, testimonios ni casos inventados (coincide con las secciones 5 y 6).
> - Los valores exactos de marca no están en los exports: hay que recuperarlos del proyecto de la
>   web antes de implementar (sección 1).

---

# DISTRIBUTION WEBSITE: REVERSE ENGINEERING + IMPLEMENTATION

## MISSION

Build the Distribution website using this website as the mandatory primary reference:

https://guillaumezhu.com/

I want a faithful adaptation of its visual structure, editorial composition, scroll behavior, transitions, and motion language.

**This is not an invitation to find a similar template or create your own interpretation.**

Study and reconstruct the reference carefully, then adapt it to Distribution's existing brand identity and commercial positioning.

The result must feel like an exceptional creative developer built it, not like an AI generated agency template.

Work with greater depth, not greater scope.

## 1. NON NEGOTIABLE: PRESERVE DISTRIBUTION BRAND IDENTITY

You already have Distribution's brand colors, logo, typography, and visual preferences from our earlier work.

Before changing anything:

1. Inspect existing project files, design tokens, CSS variables, brand assets, and previous instructions.
2. Recover the exact existing color values and fonts.
3. Document those values before implementation.
4. Preserve them throughout the website.
5. Never replace them with the reference website's colors.

The intended identity is:

• Warm off white as the dominant background.

• Existing pale yellow as the controlled accent color.

• Existing charcoal or black for typography and contrast.

• Minimalist, slim, Swiss editorial aesthetic.

• Precise grid based composition.

• Generous negative space.

• Disciplined typography and spacing.

• No decorative gradients, random accent colors, generic illustrations, glassmorphism, or SaaS dashboards.

Use the EXACT brand values already provided.

Do not guess hex codes.

Do not modify the approved logo or typography.

If exact approved tokens cannot be recovered, identify what is missing instead of inventing a new palette.

## 2. REVERSE ENGINEER THE REFERENCE WEBSITE

PRIMARY REFERENCE:

https://guillaumezhu.com/

Use real browser inspection. Do not rely exclusively on screenshots or the site's HTML.

Study the complete desktop and mobile experience.

Investigate:

**A. Visual composition**

• Overall page architecture

• Section order and transitions

• Grid and alignment

• Typography, letter spacing, line height, scale

• Negative space and margins

• Section proportions

• Navigation and footer design

• Image and project presentation

**B. Interaction and motion**

• Initial page load and intro animation

• Hero typography animation

• Text reveals and masking

• Scroll driven transitions

• Pinned or sticky sections, if present

• Typography transformations

• Project interactions and hover states

• Cursor interactions, if present

• Scroll velocity and easing

• Mobile animation behavior

Do not assume how the animations work.

Determine the actual interaction model using browser observation.

Record scroll behavior at incremental positions and inspect element states.

**C. Technical implementation**

Identify which effects can be implemented with:

• GSAP

• ScrollTrigger

• SplitText

• CSS transforms

• Motion

• Lenis

• Three.js or WebGL only where actually necessary

Prioritize accurate behavior over unnecessary technical complexity.

## 3. USE EXISTING OPEN SOURCE IMPLEMENTATIONS

Research this cloning workflow:

https://github.com/JCodesMore/ai-website-cloner-template

Study its /clone-website skill and adapt its process.

Core method:

Map → Observe → Build → Compare.

Reuse relevant inspection methods, research artifacts, component specifications, and visual comparison procedures.

Do not blindly execute a cloning skill that would overwrite Distribution's approved branding.

Also investigate suitable existing repositories, Codrops experiments, and GSAP examples for any complex interaction.

Do not rebuild a solution from scratch if a proven, compatible implementation exists.

Check licensing and compatibility.

## 4. DISTRIBUTION COMMERCIAL POSITIONING

Distribution is an independent company, separate from Nexar.

Positioning direction:

**Distribution for Builders.**

Core thesis:

**Great products don't distribute themselves.**

Distribution helps companies and builders get discovered, reach the right audience, generate relevant demand, and convert attention into business opportunities.

However, treat the existing service structure as a hypothesis until it is validated against the original business context.

Review the two Distribution WhatsApp exports, previous strategy discussions, and available project documents.

Distinguish clearly between confirmed decisions and proposals.

Potential capabilities include:

**Get Discovered**

SEO, AI Search, GEO, search visibility, and organic discovery.

**Reach Your Market**

Paid acquisition, audience targeting, outbound, and distribution across relevant channels.

**Convert Demand**

Landing pages, conversion optimization, demand capture, and measurement.

These are internal organizing concepts, not mandatory website headings.

Do not force three generic service cards into the reference layout.

## 5. BENEFIT CENTERED COPY

The visitor must understand what Distribution helps them achieve.

Focus on:

• Being discovered by relevant buyers

• Reaching the right people

• Turning attention into qualified demand

• Converting demand into business opportunities

• Building repeatable acquisition processes

Avoid generic agency language.

Avoid leading with tools, AI agents, workflows, automations, dashboards, or software infrastructure.

Research the clarity of positioning used by:

https://beomniscient.com/

https://www.demandcurve.com/

https://linear.app/

These are COPY AND COMMUNICATION references only.

They must NOT replace guillaumezhu.com as the visual reference.

Use real business inputs to develop the final messaging.

Never invent customer results, testimonials, metrics, or case studies.

## 6. TRANSLATE GUILLAUME ZHU INTO DISTRIBUTION

Keep the reference website's visual and interaction logic wherever it supports the commercial narrative.

Adapt its underlying sections intentionally.

**Original introduction**

Transform it into Distribution's benefit centered introduction.

Keep the observed typography system, reveal behavior, spatial composition, and transition quality.

Develop three concise hero copy options before selecting the strongest one.

Possible direction:

"Get seen by the right people.
Turn attention into business."

This is a candidate, not approved final copy.

**Original journey section**

Explore adapting the editorial narrative into the way businesses move from invisibility to discovery, demand, and conversion.

Preserve the reference's typography led storytelling and actual animation behavior.

**Original toolkit section**

Replace the personal technology toolkit with a strategically relevant explanation of Distribution's commercial capabilities or operating model.

Preserve the layout and interaction structure where appropriate.

Avoid generic tool icon grids.

**Original projects section**

Adapt the existing project presentation system into relevant Distribution work, demonstrable capabilities, or concrete examples.

Do not fabricate client portfolios or business outcomes.

If verified work is unavailable, develop an honest alternative using the same interaction model.

**Original closing section**

Adapt the final experience into a clear commercial CTA.

Maintain the reference's pacing, proportions, and visual restraint.

## 7. CREATIVE DIRECTION

I want an editorial, highly refined website.

The motion should make the design feel authored by a world class designer and creative developer.

Prioritize:

• Large, expressive typography

• Carefully composed whitespace

• Exact alignment

• Deliberate pacing

• Fluid transitions

• Refined hover interactions

• Cohesive scroll storytelling

• Carefully controlled use of the yellow accent

Avoid:

• Generic agency sections

• Standard three card layouts

• Random floating elements

• Excessive gradients

• Decorative 3D objects

• Fake dashboards

• Overuse of fade up animations

• AI generated stock aesthetics

• Repetitive motion

The website should be visually distinctive without sacrificing commercial clarity.

## 8. IMPLEMENTATION

Work inside the existing Distribution project.

Inspect the codebase before changing files.

Preserve the current brand assets and approved work.

Preferred stack when compatible:

Next.js, React, TypeScript, Tailwind CSS, GSAP, ScrollTrigger, and Playwright.

Add other libraries only if a specific observed behavior requires them.

Build reusable components without creating an unnecessary design system.

Use appropriate responsiveness rather than simply shrinking the desktop layout.

Respect reduced motion accessibility preferences.

Do not copy Guillaume Zhu's personal branding, copyrighted portfolio assets, or text.

The goal is to reconstruct the interaction and layout language with Distribution's own identity.

## 9. VISUAL QUALITY ASSURANCE

Do not declare success when the page compiles.

Use Playwright to compare the reference and Distribution implementation.

Compare at:

• Desktop: 1440px

• Tablet: 768px

• Mobile: 390px

Capture:

• Initial load

• Hero after entrance animation

• Section transitions

• Intermediate scroll positions

• Interactive states

• Footer

Compare layout and motion at equivalent states.

Separate intentional brand and content differences from accidental layout or animation mismatches.

Correct issues iteratively.

Evaluate:

1. Structural fidelity to the reference.
2. Animation fidelity.
3. Preservation of Distribution's identity.
4. Quality and clarity of commercial copy.
5. Desktop and mobile implementation.
6. Performance and accessibility.

Test actual behavior rather than merely checking that components render.

## 10. WORKFLOW AND REQUIRED OUTPUTS

**Phase 1: Inspect**

Study the reference website and existing brand assets.

Produce:

REFERENCE_ANALYSIS.md

BRAND_TOKENS.md

ANIMATION_SPEC.md

**Phase 2: Position**

Audit the available Distribution business context.

Produce:

POSITIONING.md

COPY.md

Clearly label unresolved assumptions and unverified claims.

**Phase 3: Map**

Define exactly how every relevant section and animation of Guillaume Zhu maps to Distribution.

Produce:

PAGE_MAPPING.md

No unnecessary new sections.

**Phase 4: Build**

Implement the homepage in the current project.

Preserve brand colors and existing assets.

Reconstruct and adapt motion based on observed behavior.

**Phase 5: Compare and refine**

Run visual and interaction QA.

Fix deviations.

Provide actual screenshots of the resulting website.

## FINAL INSTRUCTION

Do not design a new creative concept unrelated to the reference.

Do not modify Distribution's approved brand colors.

Do not make the website look like a generic growth marketing agency.

The reference website determines the visual and interaction architecture.

Distribution's existing brand determines its visual identity.

The original business research determines the commercial narrative.

**Deliver a website that feels as carefully art directed and animated as the reference, but unmistakably belongs to Distribution.**

Start by inspecting the existing project and the live reference website. Then proceed through the full implementation and visual QA workflow without asking for approval at every routine step. Stop only if an essential business decision or approved brand value cannot be verified.
