# Rúbrica del diagnóstico

Cada área se puntúa de 0 a 3. El puntaje necesita una línea de evidencia: un check de `checks.txt` o una observación concreta de un screenshot.

| Área | 0 — Roto | 1 — Débil | 2 — Correcto | 3 — Excepcional |
|------|----------|-----------|--------------|-----------------|
| **Claridad del mensaje** | En 3 s no se entiende qué venden. | Se entiende el rubro, no la oferta ni el diferencial. | Oferta clara en el primer pantallazo. | Oferta + para quién + por qué ellos, en una frase que no podría usar un competidor. |
| **Confianza** | Sin prueba: ni casos, ni clientes, ni caras. | Prueba genérica (logos sin contexto, testimonios sin nombre). | Casos o testimonios reales y visibles. | Prueba específica y medible cerca de cada decisión. |
| **Conversión** | Sin vía de contacto o escondida. | Contacto existe pero compite con muchas acciones. | Una acción principal clara, repetida en el recorrido. | Acción principal + vía rápida (WhatsApp / agenda) + seguimiento medido. |
| **Medición** | Sin analytics: no saben qué funciona. | Analytics sin eventos de conversión. | Analytics + conversiones definidas. | Analytics + comportamiento (Clarity / PostHog) + atribución por canal. |
| **Visibilidad (Google e IA)** | No indexable, sin title / description, soft 404. | Básicos presentes, faltan sitemap, OG o datos estructurados. | SEO técnico completo (title, description, H1, canonical, OG, sitemap, robots, 404 real, JSON-LD). | Todo lo anterior + `llms.txt` y contenido legible para motores de IA. |
| **Velocidad** | LCP mobile > 4 s o página > 4 MB. | LCP mobile 2,5–4 s o imágenes pesadas. | LCP mobile ≤ 2,5 s, peso ≤ 2 MB. | Lo anterior + AVIF / WebP y tamaños correctos en todas las imágenes. |
| **Mobile** | Sin viewport o con scroll horizontal. | Funciona, pero con layout roto o tap targets chicos. | Correcto en 390 px. | Pensado para mobile primero: el recorrido funciona mejor en el celular. |
| **Base técnica** | Sin HTTPS. | HTTPS sin headers de seguridad. | HTTPS + HSTS + headers básicos. | Lo anterior + CSP. |
| **Coherencia de marca** | Cada sección parece de otra marca. | Paleta y tipografía consistentes, sin carácter. | Sistema visual reconocible. | Sistema reconocible que además se diferencia de toda su categoría. |

## Cómo leer el total (máximo 27)

| Total | Lectura | Siguiente paso típico |
|-------|---------|-----------------------|
| 0–9 | La web le resta al negocio. | Rebuild Sprint o marca + web. |
| 10–17 | La web existe pero pierde oportunidades. | Upgrade focalizado en las 3 fugas. |
| 18–23 | Base sólida, sin sistema de mejora. | Monthly System: medición + experimentos. |
| 24–27 | Excepcional. | Crecimiento: contenido, distribución, paid. |

El total ordena la conversación; no reemplaza a las 3 fugas.
