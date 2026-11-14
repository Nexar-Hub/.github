---
name: diagnostico
description: Diagnóstico de presencia digital de Nexar a partir de una URL. Junta evidencia real (SEO técnico, GEO, medición, velocidad, mobile, conversión, seguridad, screenshots en 4 anchos) y arma el informe en formato Nexar (problema → fuga → oportunidad → sistema → mejora medible). Usalo cuando pidan diagnosticar, auditar o "poner a prueba" una web, preparar el diagnóstico gratuito para un prospecto, o hacer la QA pre-launch de una web de cliente.
---

# Diagnóstico Nexar

Es el **Audit** de `Audit → Upgrade → Monthly System` (`brain/nexar.md` §4). Lo que se vende no es el informe: es la claridad sobre dónde se pierde crecimiento y qué sistema lo recupera.

Dos modos:

- **Prospecto / cliente:** diagnóstico de una web existente → informe para mandar.
- **QA pre-launch:** la misma evidencia sobre la preview de una web Nexar → cero `fail` antes de producción (`brain/workflows/website.md` §10).

## 1. Juntar evidencia

Desde la raíz de este repo:

```bash
node .claude/skills/diagnostico/scripts/audit.mjs <url>
```

- Requiere Playwright con Chromium (`npm i -D playwright && npx playwright install chromium`).
- Deja todo en `diagnosticos/<dominio>-<fecha>/`: `evidence.json`, `checks.txt` y `screens/` (primer pantallazo y página completa en 390, 768, 1280 y 1440 px).
- `diagnosticos/` está en `.gitignore`. **Nunca se commitea: el repo es público.**
- Las métricas de velocidad son de laboratorio (mobile con red tipo Slow 4G y CPU 4× más lenta). Son una señal, no los Core Web Vitals de campo. Si hace falta el dato de campo, se completa con PageSpeed Insights.

## 2. Mirar como un visitante (juicio, no script)

Abrí `screens/mobile-390-fold.png` y `screens/desktop-1440-fold.png`. Contestá en una línea cada una, sin mirar el resto del sitio:

1. **¿Qué es esto?** ¿Se entiende en 3 segundos qué venden?
2. **¿Es para mí?** ¿A quién le habla? ¿Se parece al cliente ideal de la marca?
3. **¿Qué hago ahora?** ¿Hay una acción principal obvia?
4. **¿Le creo?** ¿Qué prueba ve (casos, clientes, números, caras)?

Después recorré las `-full.png`: jerarquía, prueba social, recorrido hasta el contacto, coherencia visual entre anchos.

Para estas respuestas usá la arquitectura cognitiva de `brain/workflows/website.md` §1 (desorientación → comprensión → relevancia → confianza → acción): ¿en qué estado se queda trabado el visitante?

## 3. Puntuar

Puntuá cada área de 0 a 3 con `rubric.md`. Cada puntaje se apoya en una línea de evidencia (un check del script o una observación concreta de un screenshot).

## 4. Escribir el informe

Copiá `report-template.md` a `diagnosticos/<dominio>-<fecha>/informe.md` y completalo.

- **Máximo 3 fugas.** Las que más plata o confianza le cuestan. El resto va al anexo.
- **Encuadre de pérdida, no de ganancia:** "hoy no sabés qué trae clientes" pega más que "mejoremos tu analytics" (`brain/nexar.md` §2).
- Etiquetá cada afirmación: **[Hecho]** (medido o visible), **[Inferencia]** (razonable a partir de la evidencia) o **[Hipótesis]** (hay que validarla con datos del cliente).
- Sin jerga en la parte para el cliente: nada de "signals", "GEO", "CLS" sin traducir.
- Idioma: el del prospecto.

## 5. Gates antes de entregar

- [ ] Cada fuga tiene evidencia concreta (check o screenshot) y una acción.
- [ ] Ninguna promesa de rankings, leads o conversión garantizados.
- [ ] Ninguna afirmación sin etiqueta.
- [ ] El resumen se entiende sin leer el resto.
- [ ] La propuesta de Upgrade sale de las fugas, no de un menú de servicios.
- [ ] Modo QA: cero `fail` en `checks.txt`, o cada `fail` justificado por escrito.

Si un gate no pasa, se corrige antes de mandar. Si pasan todos, se para: no se pule por pulir.
