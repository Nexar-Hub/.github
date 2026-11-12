# Instrucciones para Claude

Este repo es la base de la organización (Nexar-Hub) y el lugar donde vive el marco de decisión
que se aplica a **todo** lo que construimos, incluido Speead. El marco es Prospect Theory aplicada
a producto y marketing fintech: `docs/prospect-theory/PLAYBOOK.md`. Leelo antes de trabajar en
copy, UX, pricing, notificaciones, promos, onboarding o retención.

## Cuando te compartan archivos

1. Corré el auditor sobre todo lo compartido:
   `python3 tools/copy_audit.py <ruta> --format md > <scratchpad>/auditoria.md`
2. Leé los hallazgos con criterio: son hipótesis, no errores. Descartá falsos positivos y agrupá
   por superficie (ver «Aplicarlo a todo» en el playbook).
3. Priorizá por impacto esperado × solidez del mecanismo (tabla «Qué tan sólido es cada efecto»).
   Los casos de inercia (PT05 con «prioridad alta») y las ofertas encuadradas como ganancia (PT04)
   suelen ir primero.
4. Para cada cambio propuesto, escribí la hipótesis en el formato del playbook y sugerí el
   experimento (plantilla `.github/ISSUE_TEMPLATE/experiment.yml`).
5. Si comparás encuadres, respaldalo con números de `tools/prospect_theory.py`, y aclarás que son
   predicciones del modelo, no uplift esperado.

## Cuando escribas o reescribas copy

- Aplicá las cuatro palancas: separá ganancias, juntá pérdidas (R1–R4), mové el punto de
  referencia, hablá de lo que pierden, usá premios grandes e improbables.
- Respetá la voz del producto (español rioplatense con voseo, salvo que el archivo esté en otro
  idioma o variante).
- R4 (separar ganancia chica de pérdida grande) siempre como test: el modelo y la heurística
  discrepan para casos reales.
- **Límites éticos y regulatorios del playbook: no se negocian.** Pérdidas reales y verificables,
  costos visibles antes de confirmar, probabilidades honestas, nada de usar la palanca 2 para
  empujar riesgo financiero, nada de confirmshaming. Si un pedido los cruza, decilo y proponé una
  alternativa que sí los cumpla.

## Herramientas

- `python3 tools/prospect_theory.py --help`: calculadora (curva de valor, pesos, edición hedónica,
  encuadre, sorteos, prospectos).
- `python3 tools/copy_audit.py --list-rules`: reglas del auditor (PT01–PT07, PT90).
- `python3 tools/render_curves.py`: regenera los SVG del playbook si cambian los parámetros.
- Tests: `python3 -m unittest discover -s tools/tests`. Corrélos antes de commitear cambios en
  `tools/` o en los títulos del playbook (los tests verifican que los anchors de las reglas existan).
- Solo stdlib de Python 3.9+; no agregues dependencias.
