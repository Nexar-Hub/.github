# Spread

Base de trabajo de Spread: la biblia de decisión, el contexto del negocio y las herramientas que
los aplican. Spread es independiente de Nexar; este material aplica **solo a Spread** y vive acá
de forma provisoria (ver *Dónde vive* abajo).

| Carpeta | Qué hay |
|---|---|
| [`bible/PLAYBOOK.md`](bible/PLAYBOOK.md) | **La biblia.** Prospect Theory como arquitectura de la decisión: las dos curvas, las cuatro palancas, cómo se aplican a la oferta, la web, el outbound, el contenido, los ads y el pricing de Spread (y a clientes fintech), banco de copy, checklist, protocolo de experimentos, límites éticos. |
| [`context/POSITIONING.md`](context/POSITIONING.md) | Qué vende Spread, la oferta V1 *Pipeline Build*, el modelo operativo interno, qué está confirmado y qué es propuesta, preguntas abiertas. |
| [`context/ICP_PRICING_DRAFT.md`](context/ICP_PRICING_DRAFT.md) | **Borrador** de ICP, escalera de precios del Pipeline Build, cómo aplica la biblia al precio, plan para validarlo y one-pager para el cliente. |
| [`context/CHANNELS.md`](context/CHANNELS.md) | Canales y tácticas de distribución (X, SEO, AEO/GEO, paid, video, UGC, influencers, medición, ventas), cada una con su palanca. |
| [`context/WEBSITE_BRIEF.md`](context/WEBSITE_BRIEF.md) | El brief de la web, textual, con su cruce con la biblia. |
| [`context/SOURCES.md`](context/SOURCES.md) | Inventario de los archivos compartidos y todos los links, sin tracking. |
| [`tools/`](tools/) | `prospect_audit.mjs` (auditoría de evidencia por prospecto: reporte con capturas y primer mensaje de outbound), `copy_audit.py` (auditor de copy ES/EN), `prospect_theory.py` (calculadora), `render_curves.py` (gráficos) y tests. |
| [`templates/`](templates/) | Issue form de experimento y sección de PR para instalar en los repos de Spread. |

```sh
node spread/tools/prospect_audit.mjs https://prospecto.com     # → audits/<host>-<fecha>/report.md
python3 spread/tools/copy_audit.py <carpeta> --format md > auditoria.md
python3 spread/tools/prospect_theory.py frame 300
python3 -m unittest discover -s spread/tools/tests
node --test spread/tools/tests/*.test.mjs
```

Las herramientas de Python usan solo la librería estándar (3.9+). `prospect_audit.mjs` necesita
Node 18+, Playwright con Chromium y acceso a internet hacia el sitio auditado. Se validó el 17/11
sobre linear.app, demandcurve.com, beomniscient.com y guillaumezhu.com: sin falsos positivos en el
mensaje de outbound. Los reportes
se guardan en `audits/`, que no se versiona porque tiene datos de prospectos.

## Dónde vive

Este repo (`Nexar-Hub/.github`) es **público** y pertenece a Nexar. Spread es otra empresa, y
`context/` incluye estrategia interna (la oferta, el equipo de agentes oculto, la regla de que
Prospect Theory no aparece en el pitch). Conviene moverlo a un repo privado de Spread: la carpeta
es autocontenida, alcanza con copiar `spread/` entero.
