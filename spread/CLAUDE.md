# Instrucciones para Claude: Spread

Todo lo que está en `spread/` es de Spread (empresa independiente de Nexar) y la biblia aplica
**solo a Spread**: su oferta, web, outbound, contenido, ads, pricing, propuestas y el trabajo para
sus clientes. No la apliques a otros proyectos de la org salvo que te lo pidan.

Antes de trabajar en cualquier pieza de Spread, leé:

1. `bible/PLAYBOOK.md`: la biblia (Prospect Theory como arquitectura de la decisión).
2. `context/POSITIONING.md`: qué vende Spread y qué está confirmado y qué es propuesta.
3. `context/CHANNELS.md` y `context/WEBSITE_BRIEF.md` si la tarea toca canales o la web.

## Cuando te compartan archivos para Spread

1. Guardá los originales fuera del repo (scratchpad). No versiones chats crudos, capturas ni datos
   personales; destilá lo útil en `context/` y registrá el archivo en `context/SOURCES.md`.
2. Separá siempre lo **confirmado** de lo **propuesto**, con fecha y fuente.
3. Si hay copy, corré `python3 spread/tools/copy_audit.py <ruta> --format md` y priorizá por
   impacto × solidez del mecanismo. En copy B2B de Spread, PT08 (promesa de ganancia) y SP01
   (jerga interna) suelen ser lo primero.
4. Para cada cambio, escribí la hipótesis en el formato de la biblia y proponé el experimento
   (`templates/experiment-issue.yml`).

## Reglas de la casa

- **Mecanismo, no categoría.** Prospect Theory, signals, agentes, decision architecture: nunca en
  copy para clientes. Se vende pipeline calificado.
- **Palanca 2 con evidencia.** El status quo como pérdida solo con datos del propio prospecto o una
  fuente citada.
- **Nada inventado:** ni resultados, ni testimonios, ni métricas, ni casos, ni clientes.
- **Personas reales:** la automatización asiste a una persona real; no se crean perfiles falsos.
- Los **límites éticos** de la biblia no se negocian. Si un pedido los cruza, decilo y proponé una
  alternativa que sí los cumpla.
- Voz: español rioplatense con voseo para docs internos; la web y el outbound pueden ir en inglés
  (el idioma está abierto, ver `context/POSITIONING.md`).

## Cuando haya un prospecto

1. `node spread/tools/prospect_audit.mjs <url>`: mide lo que pierde y redacta el primer mensaje.
2. Verificá cada hallazgo en el reporte antes de usarlo. Si no hay pérdidas medibles, no uses
   encuadre de pérdida.
3. No envíes nada: el mensaje lo revisa y lo manda una persona.

## Herramientas

- `node spread/tools/prospect_audit.mjs --help`: auditoría de evidencia por prospecto.
- `python3 spread/tools/copy_audit.py --list-rules`: reglas del auditor.
- `python3 spread/tools/prospect_theory.py --help`: calculadora.
- `python3 spread/tools/render_curves.py`: regenera los SVG de la biblia.
- Tests: `python3 -m unittest discover -s spread/tools/tests` y
  `node --test spread/tools/tests/*.test.mjs`. Corrélos antes de commitear cambios en `tools/` o en
  los títulos de la biblia (verifican que los anchors de las reglas existan).
- Python: solo stdlib 3.9+. Node: solo Playwright. No agregues otras dependencias.
