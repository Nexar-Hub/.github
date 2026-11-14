# Diseño: criterio propio

Todo lo que fui guardando en el grupo de WhatsApp de inspiración, convertido en
un criterio que se puede **usar** y no solo mirar.

| Archivo | Para qué sirve |
|---------|----------------|
| [`criterios.md`](criterios.md) | **El ADN.** Las 10 leyes, la paleta, la composición, la tipografía, el motion y lo que NO. |
| [`checklist.md`](checklist.md) | Filtro antes de entregar, el sistema 3 × 20 min y cómo presentarle al cliente. |
| [`prompts.md`](prompts.md) | Prompts listos para que Claude, Gemini o ChatGPT trabajen con tu criterio. |
| [`design-dna.json`](design-dna.json) | El mismo criterio en formato máquina (para IA, tokens o herramientas). |
| [`referencias.md`](referencias.md) | La biblioteca de links del chat, limpia y ordenada por tema. |
| [`guia.html`](guia.html) | **La guía visual.** Paleta a escala con HEX para copiar, contraste calculado, diagramas de composición, preset de color, prompts listos y las 10 leyes como herramienta para puntuar una pieza antes de entregarla. Abrila en el navegador. |
| [`tokens.css`](tokens.css) | La paleta como variables CSS, lista para Webflow (panel Variables) o Figma. |
| [`tools/build.py`](tools/build.py) | Regenera `guia.html`, `tokens.css` y el zip de la skill desde `design-dna.json`. |

## Una sola fuente

`design-dna.json` es la fuente. La guía, los tokens y la skill salen de ahí:

```bash
python3 design/tools/build.py                                  # guia.html + tokens.css
python3 design/tools/build.py --skill-zip criterio-diseno.zip  # + zip de la skill para claude.ai
```

Cambiás un color o una regla en el JSON, corrés el comando y todo queda
alineado. `guia.html` y `tokens.css` no se editan a mano.

## Cómo aprovecharlo a tu favor

1. **Como filtro.** Antes de mandar algo, pasalo por el
   [checklist](checklist.md). Tiene 10 preguntas y una que manda: *¿esto lo
   habría propuesto un diseñador promedio?*
2. **Como criterio de Claude.** La skill
   [`criterio-diseno`](../.claude/skills/criterio-diseno/SKILL.md) hace que
   Claude aplique estas reglas solo cada vez que le pidas algo de diseño (ver
   abajo). Para Gemini o ChatGPT, usá [`prompts.md`](prompts.md).
3. **Con clientes.** Presentá 2–4 territorios de estilo y explicá cada decisión
   con la fórmula *"No [lo obvio]. En cambio, [la decisión]. Porque [la
   emoción]."* Pasás de "me gusta" a criterio defendible.
4. **Como punto de partida.** Arrancá cada proyecto desde la paleta base y las
   leyes, y cambiá solo lo que el proyecto pida. Así todo lo que hacés tiene
   una firma reconocible.

## Que Claude lo use solo (skill `criterio-diseno`)

- **En Claude Code**, dentro de este repo: la skill está en
  `.claude/skills/criterio-diseno/` y se activa sola con cualquier pedido de
  diseño.
- **En claude.ai** (web y app): subí el zip `criterio-diseno.zip` en la sección
  **Skills** de la configuración (*Subir skill*). Desde ahí, en cualquier chat,
  cuando pidas una marca, un post, una crítica o un prompt de imagen, Claude
  usa tu criterio.
- Para armar el zip: una carpeta `criterio-diseno/` con `SKILL.md` +
  `criterios.md`, `checklist.md`, `prompts.md` y `design-dna.json`,
  comprimida. Cada vez que actualices el criterio, volvé a subirla.

## Cómo mantenerlo vivo

Hoy, de unos 230 links guardados, **casi la mitad no tiene ningún comentario**. Y en tus
notas, el *porqué* vale más que el link: los links de X o LinkedIn se pierden
y sin la frase no se sabe qué te gustó.

Para que el criterio crezca solo:

- **Seguí usando el grupo**, pero sumá siempre **una línea de por qué** y una
  etiqueta:
  `#comp` composición · `#color` · `#tipo` · `#textura` · `#motion` ·
  `#web` · `#marca` · `#foto` · `#principio` · `#tool`
  > Ej.: *"#comp horizonte abajo + figura chica = escala"*
- **Guardá captura además del link** (el link puede morir).
- **Cada 2–3 meses**: exportá el chat (WhatsApp → Exportar chat → Adjuntar
  archivos) y actualizá estos archivos. Las notas que se repiten pasan a ser
  leyes; las que contradicen una ley la ajustan.
- Cuando no sepas por qué te gusta algo, usá el prompt *"Analizar una
  referencia nueva"* de [`prompts.md`](prompts.md).

> Nota: este repo es público. Acá hay solo principios y links públicos. Las
> imágenes del chat y las ideas de proyectos puntuales quedaron afuera.
