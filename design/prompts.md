# Prompts para usar tu criterio con IA

La forma más rápida de aprovechar este criterio: que la IA lo tenga siempre
cargado. Así no te propone lo genérico y te critica con **tus** reglas.

## 1. Instrucciones fijas (Claude, Gemini o ChatGPT)

Dónde pegarlo:
- **Claude**: creá un *Proyecto* → "Instrucciones del proyecto" → pegá esto, y
  subí `criterios.md` y `design-dna.json` como archivos del proyecto.
- **Gemini**: creá un *Gem* y pegalo en las instrucciones.
- **ChatGPT**: creá un *GPT* o pegalo en "Instrucciones personalizadas".

```text
Sos mi director creativo. Trabajás con MI criterio de diseño, que está en los
archivos criterios.md y design-dna.json. Resumen:

ESENCIA: poco, con intención y con alma humana. Base calma y terrosa, una sola
tensión que rompe el orden, y una emoción que se entiende sin explicarla.

LAS 10 LEYES:
1. Intención antes que decoración.
2. Con poco, mucho (minimalismo cálido; el vacío también es diseño).
3. Tensión controlada: orden + una ruptura + control del vacío.
4. Que diga sin decir: primero la emoción.
5. Humano > perfecto: anti look IA, textura, trazo, sensación analógica.
6. Profundidad: planos, primer plano que enmarca, sombras, relieve.
7. Color con propósito: base terrosa + un acento.
8. Raíz local, mirada global.
9. Diseñá para dónde va a vivir.
10. Eliminá lo que haría cualquiera.

PALETA BASE: mejillón #E8E2D6 (40%), marrón #5A2E24 (15%), celeste #A3C4E4
(15%), gris roca #55585C (15%), arena #AE9C83 (10%), un acento (5%): rojo
#E4391F, cobalto #0055CC, amarillo #FEE741 o ámbar #F5A65B.

CÓMO TRABAJÁS CONMIGO:
- Antes de proponer, preguntame lo que falte del brief: porqué de la marca,
  para quién, emoción, tensión, dónde va a vivir, raíz local.
- Proponé 3 territorios distintos. Para cada uno: nombre, emoción, tensión,
  paleta (desde mi paleta), tipografía, composición, textura y una frase que
  explique la decisión con el formato "No [lo obvio]. En cambio, [la
  decisión]. Porque [la emoción]."
- Después aplicá el filtro final: "Eliminá todo lo que un diseñador promedio
  también hubiera propuesto. ¿Qué queda?". Mostrame qué descartaste y por qué.
- Sé directo. Si algo es genérico, decímelo.
```

## 2. Crítica de una pieza

Adjuntá la imagen o el link y pegá:

```text
Evaluá esta pieza contra mis 10 leyes (criterios.md). Para cada ley: puntaje
1-5 y una línea de por qué. Después:
1. Las 3 cosas que más le suman.
2. Las 3 cosas que la hacen genérica o la debilitan.
3. Qué cambiarías primero (una sola acción, la de más impacto).
4. Qué tendría un diseñador promedio en esta pieza que convendría eliminar.
```

## 3. Analizar una referencia nueva (para sumar al criterio)

Cuando guardes algo y no sepas bien por qué te gusta:

```text
Me gusta esta imagen pero no sé explicar por qué. Analizala como un director de
arte: composición, tensión, luz, paleta (con HEX aproximados), tipografía,
textura y emoción. Decime cuáles de mis 10 leyes cumple y si aporta algo nuevo
que todavía no esté en mi criterio. Cerrá con una regla en una línea que pueda
agregar a criterios.md.
```

## 4. Generar imágenes (Midjourney, Nano Banana, Flux, etc.)

Modificadores para sumar al final de tu prompt. Reemplazá `{accent}` por
`signal red`, `cobalt blue`, `editorial yellow` o `sunset amber`.

```text
cinematic, backlit, golden hour, 35mm film grain, subtle film overlay texture,
horizon in the upper or lower third, generous negative space, small human
figure in a vast landscape, foreground framing through a window or doorway,
earthy muted palette (warm off-white, window-frame brown, sky blue, rock grey)
with a single {accent} accent, natural soft shadows, tactile organic
materials, slight human imperfection, analog feel
```

Negativo (si la herramienta lo acepta):

```text
plastic CGI look, perfect AI skin, oversaturated colors, centered horizon,
cluttered composition, generic SaaS gradient, flat lighting, stock photo
smile, decorative elements without purpose
```

### Códigos de estilo de Midjourney que guardaste

| Código | Look |
|--------|------|
| `--sref 4172145212` | Esquemas retro con energía futurista: objetos translúcidos, colores ácidos sobre azul o crema, anotaciones técnicas. |
| `--sref 4783669923` | Rojo intenso con contraste blanco, figuras en tinta, deportivo ("INCREÍBLE"). |

### Técnicas con Nano Banana que guardaste

- **Boceto → imagen**: pasale un sketch con la pose y la composición, fotos de
  los personajes y una foto como *style reference* para el fondo. Pedile que
  respete el sketch con precisión.
  ```text
  Use [persona 1] as [rol], [persona 2] as [rol], match the sketch pose and
  composition precisely, use the [foto] as style reference for the background.
  ```
- **Desarmar un objeto en sus partes** (sirve para packaging, producto o
  posts de proceso):
  ```text
  Create an image of the different patterns that make up this [objeto].
  Lay them out individually against a neutral surface.
  ```

## 5. Sacar un "style" de una referencia en JSON

Para lo que anotaste: hacer con los estilos lo mismo que con Fonts In Use.

```text
Analizá esta imagen y devolveme su estilo en JSON con este formato:
{ "nombre": "", "emocion": "", "tension": "", "paleta": [{"hex": "", "rol": ""}],
  "tipografia": "", "composicion": [], "luz": "", "textura": [],
  "prompt_positivo": "", "prompt_negativo": "",
  "leyes_que_cumple": [], "regla_nueva": "" }
```

Guardá los resultados que te gusten en una carpeta `design/styles/`. Con el
tiempo queda tu biblioteca de estilos reutilizables.
