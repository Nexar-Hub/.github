# Spread · ICP y precio del Pipeline Build (BORRADOR)

> **Estado: borrador para que el fundador lo corrija.** Nada de esto está aprobado. Los números no
> salen de datos de mercado propios (todavía no hay ventas): son hipótesis con su razonamiento y
> un plan para validarlas con las primeras propuestas. Contexto en
> [`POSITIONING.md`](POSITIONING.md); marco en [`../bible/PLAYBOOK.md`](../bible/PLAYBOOK.md).

---

## ICP

### Primario (V1): B2B SaaS que ya construyó y no consigue pipeline

| Criterio | Hipótesis | Por qué |
|---|---|---|
| Etapa | Seed a Serie A, 5 a 50 personas | Tienen producto y algo de caja, pero todavía no tienen equipo de demanda. |
| Ventas | Founder-led: el fundador todavía vende | Es quien siente el problema («el problema no es hacer, es vender») y quien decide rápido. |
| Producto | En producción, con los primeros clientes pagos | Hay algo que distribuir y casos propios para usar como prueba. |
| Ticket (ACV) | USD 6.000 al año o más | Un solo deal nuevo paga buena parte del Build: la cuenta cierra sin promesas. |
| Mercado | Vende en inglés (EE. UU. o global) | La oferta V1 y la web están pensadas en inglés. |
| Falta | Sin responsable de growth o demand gen | Si ya lo tienen, Spread compite con su equipo interno. |

**Disparadores para priorizar cuentas** (uso interno): ronda reciente; búsqueda abierta para su
primer SDR, AE o marketer; lanzamiento de producto o vertical; relanzamiento de web; la
competencia aparece en respuestas de IA y ellos no; **`prospect_audit.mjs` encuentra pérdidas
medibles en su web.**

### Secundario: SaaS y fintech de LatAm que venden o se expanden a EE. UU.

Uruguay, Argentina y Chile (la red del fundador). Necesitan posicionamiento y pipeline en inglés.
La ventaja de Spread acá es la doble lengua y el contexto. Se cobra en USD. Es la pregunta abierta
del 3/9: «¿con quiénes me junto para potenciarnos en UY/ARG/Chile?».

### Clientes cero: los proyectos propios

Nexar, MG y FUT AI. El sistema se prueba ahí primero («que me sirva a mí y después lo vendemos»),
y eso deja evidencia verificable para usar en la venta, en vez de casos inventados.

### No ahora

- Builders sin producto en producción.
- B2C o self-serve con ticket menor a USD 1.000 al año: el pipeline calificado no es su cuello de
  botella.
- Quien solo quiere «manejo de ads» o «branding»: no es la oferta.
- Equipos sin tiempo para tomar reuniones: el sistema genera conversaciones que alguien tiene que
  atender.

---

## Precio

### La escalera

| Oferta | Precio (hipótesis) | Rango a testear | Qué es |
|---|---|---|---|
| **Auditoría de evidencia** | Gratis | — | El reporte de `prospect_audit.mjs` sobre su web, revisado a mano. Es el lead magnet y la prueba del trabajo. |
| **Pipeline Build** | **USD 9.500**, precio único | 7.500 a 12.000 | Seis semanas. El sistema completo de la oferta V1 (los nueve entregables). |
| **Pipeline Operate** | **USD 3.500 por mes**, mínimo 3 meses | 2.500 a 5.000 | Después del Build: operar el outbound, los experimentos, el contenido y el reporting semanal. |

**Por qué esos números.** Con un ticket de USD 6.000 o más, un solo cliente nuevo que salga del
sistema cubre buena parte del Build. Spread arranca sin casos propios, así que el precio va por
debajo del de una agencia establecida de EE. UU., pero no barato: un precio bajo comunica poca
confianza en el resultado. Son números para discutir, no una conclusión.

### Cómo aplica la biblia al precio

| Decisión | Palanca | Qué hacemos |
|---|---|---|
| Un solo precio por el Build | R2 · Juntá las pérdidas | «Pipeline Build: USD 9.500». No siete líneas, una por componente. |
| Setup incluido | R3 · Integrá la pérdida chica | Ningún «setup fee» aparte: va dentro del precio. |
| Entregables uno por uno | R1 · Separá las ganancias | Los nueve entregables listados por separado, cada uno con su beneficio. |
| Forma de pago | R2 | Un pago, o como mucho dos (50 % al firmar y 50 % en la semana 4). Nunca seis cuotas. |
| Operate | R2 | Facturación trimestral en vez de mensual: una pérdida cada tres meses en lugar de tres. |
| Extra | R4 (testear) | La auditoría AEO de su categoría como regalo aparte, nunca como descuento. |
| Garantía | Efecto certeza | Solo sobre lo que Spread controla: «Si en la semana 6 el sistema no está operando (lista activa, outbound enviando, landing publicada, tracking midiendo), seguimos sin cargo hasta que lo esté.» **Nunca** se garantizan reuniones ni ingresos. |
| Pitch del precio | 2 · Punto de referencia | Comparar contra lo que ya pierden, con su evidencia (auditoría), no contra el precio de otra agencia. |

### Cómo validarlo

1. Las primeras 5 propuestas salen a USD 9.500. Se registra cada una: cerró o no, y la objeción
   principal.
2. Si cierran 4 o 5 de 5, el precio está bajo: la próxima tanda sube a USD 12.000.
3. Si no cierra ninguna y el precio es la objeción, se testea USD 7.500 o una entrada más chica:
   un *Pipeline Sprint* de dos semanas (ICP, mensaje, lista de cuentas y la primera secuencia) por
   unos USD 3.000.
4. Para LatAm, mismo precio en USD hasta tener datos. No bajarlo por suposición.

Plantilla para registrarlo: [`../templates/experiment-issue.yml`](../templates/experiment-issue.yml).

---

## Borrador de one-pager (para el cliente, en inglés)

Sin jerga interna, sin resultados inventados. Los corchetes se completan con la auditoría del
prospecto.

> **Pipeline Build**
>
> For B2B SaaS teams that built a great product and need a repeatable way to turn their market
> into qualified sales conversations.
>
> **What we found on [their site]:** [two measured findings from the evidence audit].
>
> **USD 9,500 · six weeks.** You get:
>
> - Your ideal customer profile and the offer they respond to
> - A researched, prioritized list of the accounts worth pursuing
> - Outbound running across email and LinkedIn
> - Landing pages built to turn interest into meetings
> - One paid acquisition experiment, where it makes sense
> - Your CRM organized, with routing and follow-ups automated
> - Tracking that shows which message and channel creates pipeline
> - The first experiments, run and documented
>
> **Included, separately:** an AI search audit of your category, showing which companies
> assistants recommend today.
>
> **Our commitment:** if the system isn't running by week six, we keep working at no extra cost
> until it is.

---

## Preguntas para el fundador

1. ¿El ICP primario es el correcto, o arrancamos solo con LatAm y los proyectos propios?
2. ¿Los rangos de precio te parecen razonables para tu mercado? ¿Hay algún número de referencia
   que ya tengas (cotizaciones previas, competencia)?
3. ¿La garantía de entrega te parece viable con la capacidad actual?
4. ¿Querés ofrecer el *Pipeline Sprint* desde el arranque o solo si el Build no cierra?
