# Prospect Theory: el playbook de arquitectura de la decisión

> Base de trabajo para todo lo que construyamos: copy, UX, pricing, notificaciones, promos,
> onboarding, retención. Si una pieza le pide a alguien que decida algo con plata, pasa por acá.

Kahneman y Tversky publicaron *Prospect Theory: An Analysis of Decision under Risk* en
*Econometrica* (1979). El movimiento central es un cambio de objeto: la teoría clásica define la
utilidad sobre **estados finales de riqueza** (tenés tanto, valorás tanto). Prospect Theory la
redefine sobre **cambios respecto de un punto de referencia**. Recién ahí aparecen ganancias y
pérdidas como categorías separadas, y de eso salen dos curvas y todo lo demás.

**Regla de uso, antes que nada:** este marco es un **generador de hipótesis**, no una garantía.
Sirve para decidir *qué probar y por qué debería funcionar* cuando hay mil ideas y capacidad de
experimentación limitada. Después mandan los experimentos. Ver
[De la teoría al experimento](#de-la-teoría-al-experimento).

---

## Contenido

- [Cómo usar este documento](#cómo-usar-este-documento)
- [El modelo en una página](#el-modelo-en-una-página)
- [Las cuatro palancas](#las-cuatro-palancas)
- [Aplicarlo a todo: superficie por superficie](#aplicarlo-a-todo-superficie-por-superficie)
- [Banco de copy](#banco-de-copy)
- [Checklist de revisión](#checklist-de-revisión)
- [De la teoría al experimento](#de-la-teoría-al-experimento)
- [Límites éticos y regulatorios](#límites-éticos-y-regulatorios)
- [Qué tan sólido es cada efecto](#qué-tan-sólido-es-cada-efecto)
- [Referencias](#referencias)

---

## Cómo usar este documento

| Si estás… | Hacé esto |
|---|---|
| **Creando** una pieza (pantalla, mail, landing, promo) | Buscá la superficie en [Aplicarlo a todo](#aplicarlo-a-todo-superficie-por-superficie) y pasá la [checklist](#checklist-de-revisión). |
| **Revisando** archivos existentes (cientos o miles) | Corré el auditor: `python3 tools/copy_audit.py <carpeta> --format md > auditoria.md`. Cada hallazgo es una hipótesis con su palanca y su acción. |
| **Comparando dos encuadres** con números | Usá la calculadora: `python3 tools/prospect_theory.py --help` (ejemplos abajo). |
| **Proponiendo un experimento** | Abrí un issue con la plantilla *Behavioral experiment* (`.github/ISSUE_TEMPLATE/experiment.yml`). |
| **Abriendo un PR** que toca copy, UX o pricing | Completá la sección *Decision architecture* de la plantilla de PR. |

Todos los números de este documento salen de `tools/prospect_theory.py` con los parámetros que
Tversky y Kahneman estimaron en 1992 (α = β = 0,88; λ = 2,25; γ = 0,61; δ = 0,69) y están
cubiertos por tests (`python3 -m unittest discover -s tools/tests`).

---

## El modelo en una página

### Curva 1 · La curva de valor

![Curva de valor: cóncava en ganancias, convexa y más empinada en pérdidas](img/value-function.svg)

Cuatro conclusiones salen de este gráfico:

1. **Todo se mide contra un punto de referencia.** El cero está donde la persona *cree* que está
   parada hoy. Es subjetivo y, por eso mismo, se puede mover.
2. **Ganancias y pérdidas se procesan distinto.** En ganancias la curva es cóncava: somos aversos
   al riesgo. En pérdidas es convexa: buscamos riesgo. La misma persona elige $5 seguros antes que
   una moneda por $0 o $10, pero prefiere tirar la moneda para perder $0 o $10 antes que aceptar
   una pérdida segura de $5.
3. **Sensibilidad decreciente.** La curva es más empinada cerca del cero. Ganar $5 desde $0 vale
   4,12; pasar de $1.000 a $1.005 vale 1,92. Opera en los dos dominios: los primeros $5 perdidos
   duelen 9,27; los últimos $5 de una pérdida de $1.005, 4,32.
4. **Aversión a las pérdidas.** La rama de pérdidas cae más rápido de lo que sube la de ganancias.
   Perder $100 pesa −129,5; ganar $100, +57,5: unas **2,25 veces**.

```
v(x) = x^0,88               si x ≥ 0
v(x) = −2,25 · (−x)^0,88    si x < 0
```

### Curva 2 · El peso de las probabilidades

![Curva de ponderación de probabilidades: sobreestima lo improbable y subestima lo casi seguro](img/probability-weighting.svg)

Al decidir no usamos las probabilidades reales sino una versión deformada en los extremos:
**sobreestimamos las chicas y subestimamos las altas**. Por eso la misma persona compra un billete
de lotería y contrata un seguro el mismo día.

| Probabilidad real | Se procesa como (ganancias) | Se procesa como (pérdidas) |
|---:|---:|---:|
| 0,1 % | 1,5 % | 0,8 % |
| 1 % | **5,5 %** | 4,0 % |
| 5 % | 13,2 % | 11,1 % |
| 10 % | 18,6 % | 17,0 % |
| 50 % | 42,1 % | 45,4 % |
| 90 % | 71,2 % | 77,5 % |
| 95 % | **79,3 %** | 85,0 % |
| 99 % | 91,2 % | 94,5 % |

Dos consecuencias prácticas:

- **Lotería:** un premio de $1.000 al 1 % (valor esperado $10) se siente como **$37 seguros**.
- **Seguro:** un 1 % de perder $10.000 (valor esperado −$100) se siente como una pérdida segura de
  **$255**. La gente paga bastante más que el valor esperado por sacarse ese riesgo de encima.

---

## Las cuatro palancas

### 1. Hedonic editing: separá las ganancias y juntá las pérdidas

Consecuencia directa de la forma de la curva de valor. Como la rama de ganancias es cóncava, dos
ganancias separadas valen más que la misma plata en un solo evento: v(40) + v(40) = 51,4 >
v(80) = 47,3. Como la rama de pérdidas es convexa, pasa lo contrario: una pérdida grande duele
menos que dos chicas que suman lo mismo. Richard Thaler (1985) completó el ejercicio con dos
reglas más que salen de la misma geometría.

```
python3 tools/prospect_theory.py edit 40 40        # → SEGREGATE
python3 tools/prospect_theory.py edit -3 -1.5 -0.5 # → INTEGRATE (comisión, spread, fee de red)
```

#### R1. Separá las ganancias

- **Rendimientos: mostralos todos los días.** Cada actualización es una ganancia nueva medida desde
  un punto de referencia nuevo. 30 días de $10 se sienten como 227,6; $300 de una vez, como 151,3.
  El acumulado mensual comprime treinta eventos de valor en uno.
- **Beneficios en momentos distintos.** Cashback, bonificación de fee y premio por referido se
  entregan por separado, aunque operativamente sea más cómodo liquidarlos juntos.
- **Cuidado:** solo hay evento si el usuario lo ve. Medí fatiga (opt-outs de push, desinstalaciones)
  como guardrail.

#### R2. Juntá las pérdidas

- **Costos en un solo número.** Comisión, spread y fee de red en una línea («Costo total»). Desglosar
  en tres hace que el usuario procese tres pérdidas: −10,35 contra −9,27 juntos.
- **El detalle sigue disponible** (un toque, un tooltip, el comprobante). Integrar es *presentar
  juntas* las pérdidas, nunca esconderlas. Ver [límites](#límites-éticos-y-regulatorios).
- **Malas noticias, una sola vez.** Cambios de precio o de condiciones: un único anuncio con todo,
  no un goteo de mails.

#### R3. Pérdida chica al lado de ganancia grande: integrala

- Una pérdida chica al lado de una ganancia grande conviene absorberla adentro de la ganancia:
  +1.000 y −20 por separado valen 405,1; +980 neto vale 428,8.
- Ejemplo: en el resumen de rendimientos, mostrar el rendimiento **neto** del fee de gestión como
  número principal, con el fee visible en el detalle.

#### R4. Ganancia chica al lado de pérdida grande: separala

- Thaler: una ganancia chica al lado de una pérdida grande conviene mostrarla separada (*silver
  lining*). Por eso el cashback se comunica solo y **nunca como descuento del cargo mensual**.
- **Ojo, esta es la regla con evidencia más débil.** Con aversión a las pérdidas (λ = 2,25) la
  curva sola la respalda solo si la ganancia es unas 300 veces más chica que la pérdida. Para un
  cashback de $2 sobre una cuota de $10, el modelo dice integrar (−14,0 contra −15,2). La regla de
  Thaler se apoya en su evidencia de encuestas y en contabilidad mental (el beneficio vive en otra
  «cuenta» y en otro momento), no en la curva. **Tratala siempre como experimento.**

```
python3 tools/prospect_theory.py edit 2 -10   # el modelo y la heurística discrepan → testear
```

### 2. Mové el punto de referencia y movés la actitud frente al riesgo

La más potente y la menos usada. Quien nunca usó una fintech y evalúa salir del sistema
tradicional está evaluando si acepta un riesgo. Si en su cabeza está parado en cero, la curva ahí
es cóncava: tiende a rechazarlo y quedarse con lo conocido.

La jugada es **correr el punto de referencia hacia el dominio de las pérdidas**. Ahí la curva es
convexa y la misma persona se vuelve buscadora de riesgo. Cuando el status quo se lee como
pérdida, probar algo nuevo se siente como una recuperación.

| Encuadre | Mensaje | Qué transmite |
|---|---|---|
| Ganancia (punto de referencia en cero) | «Lo que hacés hoy funciona, pero las stablecoins son más rápidas y económicas.» | Podrías ganar algo si cambiás. |
| Pérdida (status quo como pérdida) | «Hoy estás perdiendo $X y N días en cada envío por SWIFT. Con stablecoins dejás de perderlos.» | Ya estás perdiendo y podés recuperarlo. |

Sirve para cualquier caso donde el enemigo es la inercia: migrar usuarios entre rails, sacarlos del
efectivo, dolarizar, pasar del plazo fijo a una cuenta remunerada.

**Condición:** el número de la pérdida tiene que ser real, calculado contra un baseline honesto y
verificable (fuente de las tarifas SWIFT, inflación oficial, etc.).

**Límite:** esta palanca vuelve a la gente más propensa al riesgo. Usala para que prueben un rail
mejor, **nunca** para empujar a alguien hacia apuestas o productos volátiles. Ver
[límites](#límites-éticos-y-regulatorios).

### 3. Aversión a las pérdidas: hablá de lo que están perdiendo

Usuario con saldo ocioso, queremos que active los rendimientos de la cuenta remunerada:

- Versión ganancia: «Activá rendimientos y ganá 300 USD al año.»
- Versión pérdida: «Estás dejando sobre la mesa 300 USD por año.»

Mismo número, misma oferta. Por aversión a las pérdidas la segunda pesa unas 2,25 veces más en el
modelo (`python3 tools/prospect_theory.py frame 300`). Eso es una predicción para priorizar el
test, no el uplift que vas a ver en el funnel.

- Calculá el monto **con el saldo real del usuario**, no con un ejemplo genérico.
- Reforzá con continuidad: «Ayer dejaste de ganar $0,82» activa la palanca 3 y la R1 a la vez.

### 4. Los sorteos funcionan por la curva de peso de probabilidades

La gente participa de sorteos por la misma razón por la que compra seguros. Un 1 % se procesa
como 5,5 %, así que el premio grande e improbable le gana al incentivo chico y seguro aunque en
plata sean equivalentes.

```
python3 tools/prospect_theory.py raffle --prize 1000 --prob 0.01 --sure 10
# valor esperado por participante: 10 · valor sentido: 37,2 (3,7×) → el modelo prefiere el sorteo
```

- Aunque recompense a una sola persona, genera acciones previas (registro, primer depósito,
  referido) en muchas.
- **Un premio grande pesa más que muchos premios chicos** del mismo costo total.
- Medí también la **calidad** de quienes entran por el sorteo (retención a 30/90 días), no solo el
  volumen.
- Bases y condiciones y requisitos legales de cada jurisdicción **antes** de publicar.

**Extensión (misma curva, menos probada en nuestro contexto): efecto certeza.** Un 95 % se procesa
como 79 %, así que «garantizado» vale desproporcionadamente más que «casi seguro»: $105 al 95 % se
sienten como $80,7, menos que $100 seguros. Si una promesa es cierta (acreditación, tipo de cambio
congelado, devolución), decila como certeza. Si no lo es, no la vendas como tal.

---

## Aplicarlo a todo: superficie por superficie

| Superficie | Palanca principal | Hacé | Evitá | Métrica principal |
|---|---|---|---|---|
| **Landing y ads** | 2 · Punto de referencia | Abrí con lo que el usuario pierde hoy (costo, días, inflación) con fuente. | «Más rápido y más barato» como único argumento. | CTR → registro |
| **Onboarding y primer depósito** | 2 + 4 | Mostrá el costo del status quo calculado para su caso; sorteo atado al primer depósito. | Bonos chicos y seguros sin testear contra sorteo. | Activación (primer depósito) |
| **Home y saldo** | R1 · Separá ganancias | Movimiento del día visible («+$0,82 hoy»). | Mostrar solo el saldo total sin variación. | Sesiones/semana, retención D30 |
| **Rendimientos / cuenta remunerada** | 3 + R1 + R3 | «Estás dejando sobre la mesa $X/año» con su saldo; rendimiento diario neto de fees. | «Ganá X» genérico; resumen solo mensual. | Tasa de activación |
| **Remesas / transferencias internacionales** | 2 · Punto de referencia | «Cada envío por SWIFT te cuesta $X y N días.» | Comparar como si el status quo fuera neutro. | Primer envío, envíos/mes |
| **Cambio, dolarización, stablecoins** | 2 | Encuadrá la inercia como pérdida (inflación, brecha, costo de efectivo). | Empujar a especular o a productos volátiles. | Conversión del primer cambio |
| **Pricing, checkout, comprobantes** | R2 + R3 | Un solo «Costo total» antes de confirmar; detalle a un toque. | Tres líneas de cargos; costos que aparecen después del pago. | Abandono de checkout, tickets de soporte |
| **Tarjeta y cashback** | R1 + R4 (testear) | Cashback como evento propio, otro día y otro mensaje. | «Cuota $10 − cashback $2» en el mismo renglón. | Uso de tarjeta, percepción de valor (encuesta) |
| **Notificaciones push / email** | R1 | Una notificación por ganancia; costos agrupados en un único aviso. | Goteo de malas noticias; push diarios sin opt-out claro. | Open rate, opt-outs (guardrail) |
| **Referidos y promociones** | 4 + R1 | Sorteo de premio grande por referido; premio entregado aparte del bono. | Bono fijo chico sin probar alternativa. | Referidos/usuario, calidad de referidos |
| **Retención y cancelación** | 3 | Mostrá con honestidad lo que deja de recibir (rendimiento acumulado, beneficios). | Confirmshaming, pasos extra para cancelar. | Churn, reactivación |
| **Cambios de precio y condiciones** | R2 + R4 | Un solo anuncio con todo junto; si hay un beneficio nuevo, comunicalo por separado. | Anunciar cada aumento por separado. | Churn post-anuncio, quejas |
| **Seguridad y protección** | Curva 2 | Comunicá las protecciones con certeza («100 % cubierto» solo si es cierto). | Amplificar riesgos chicos para vender miedo. | Adopción de 2FA/protección |

---

## Banco de copy

Pares de partida para testear. Reemplazá `X`, `N` y las fuentes con datos reales del usuario.

| Situación | Antes | Después (hipótesis) | Palanca |
|---|---|---|---|
| Saldo ocioso | Activá rendimientos y ganá X USD al año. | Estás dejando sobre la mesa X USD por año. | 3 |
| Saldo ocioso (diario) | Tu dinero puede rendir más. | Ayer dejaste de ganar $X. Activá rendimientos. | 3 + R1 |
| Remesas | Enviá más rápido y más barato que con SWIFT. | Hoy perdés $X y N días en cada envío por SWIFT. Dejá de perderlos. | 2 |
| Salir del efectivo | Pagá más fácil con la app. | Tener efectivo te cuesta X % por mes de inflación. | 2 |
| Rendimientos | Este mes ganaste $X. | Hoy ganaste $0,82. *(push diario + resumen mensual)* | R1 |
| Checkout | Comisión $3 · Spread $1,50 · Fee de red $0,50 | Costo total $5 *(ver detalle)* | R2 |
| Resumen de inversión | Rendimiento $1.000 · Fee de gestión −$20 | Rendimiento neto $980 *(fee en el detalle)* | R3 |
| Tarjeta | Cuota mensual $10 − cashback $2 | *Mensaje aparte, otro día:* «Te acreditamos $2 de cashback.» | R4 (testear) |
| Referidos | Invitá a un amigo y llevate $5. | Invitá a un amigo y participá por $5.000 *(mismo costo esperado)*. | 4 |

---

## Checklist de revisión

Para cualquier pieza que pida una decisión con plata:

1. **¿Dónde está parado el usuario?** ¿Cuál es su punto de referencia hoy y lo estamos moviendo a
   propósito?
2. **¿Es un caso de inercia?** Si queremos que cambie algo, ¿el status quo está encuadrado como
   pérdida (con números reales)?
3. **¿Las ganancias están separadas?** ¿Cada beneficio es su propio evento?
4. **¿Las pérdidas están juntas?** ¿Hay un solo «Costo total» visible antes de confirmar?
5. **¿Hay pérdidas chicas al lado de ganancias grandes** que convenga mostrar netas?
6. **¿Hay ganancias chicas al lado de pérdidas grandes** que convenga separar (y testear)?
7. **¿El encuadre es de ganancia cuando podría ser de pérdida evitada?**
8. **¿Hay un incentivo chico y seguro** que podría ser un sorteo del mismo costo esperado?
9. **¿Algo prometido como cierto es realmente cierto?** ¿Algo improbable se presenta honestamente?
10. **¿Pasa los [límites éticos](#límites-éticos-y-regulatorios)?** ¿Lo publicaríamos con el
    razonamiento a la vista?

---

## De la teoría al experimento

El salto entre «fenómeno robusto en laboratorio» y «esto me mueve el funnel un 20 %» nunca es
automático. El marco decide **qué** probar; el experimento decide **si** funcionó.

**Formato de hipótesis**

> Si **[cambio]** en **[superficie]**, entonces **[métrica principal]** va a **[subir/bajar]**,
> porque **[mecanismo de Prospect Theory: palanca y curva]**.

**Antes de lanzar (pre-registro)**

- Una métrica principal. Guardrails: tickets de soporte, quejas, opt-outs, reembolsos, churn.
- Efecto mínimo detectable, tamaño de muestra y duración en semanas completas, **fijados antes**.
- Regla de decisión escrita: qué hacemos si gana, si pierde y si no es concluyente.

**Durante y después**

- No mirar resultados a mitad de camino para cortar cuando conviene.
- No buscar segmentos a posteriori hasta que algo «gane». Si aparece algo, es una hipótesis nueva.
- Los encuadres de pérdida y las notificaciones diarias tienen efecto novedad: mirá la curva en el
  tiempo, no solo el promedio.
- **Confiá en el resultado.** Si es insatisfactorio, se documenta y se aprende; no se fuerza.

**Priorización.** Con capacidad limitada, ordená por (impacto esperado × solidez del mecanismo) /
esfuerzo. Para la solidez usá la tabla de [abajo](#qué-tan-sólido-es-cada-efecto).

Plantilla lista: issue *Behavioral experiment* (`.github/ISSUE_TEMPLATE/experiment.yml`).

---

## Límites éticos y regulatorios

Ser arquitecto de la decisión es una responsabilidad. Estas reglas no se negocian, ni siquiera si
un test dice que «funciona»:

1. **La pérdida que nombramos es real.** Calculada para ese usuario, contra un baseline honesto y
   con fuente. Nada de pérdidas inventadas o infladas.
2. **Integrar no es esconder.** El costo total se ve antes de confirmar; el desglose está a un
   toque; nada aparece después del pago. «Gratis» con asterisco no es gratis.
3. **Probabilidades honestas.** Las chances de un sorteo se publican tal como son. Bases y
   condiciones y requisitos legales de cada jurisdicción antes de lanzar.
4. **La palanca 2 no se usa para empujar riesgo financiero.** Poner a alguien en el dominio de las
   pérdidas lo vuelve más propenso al riesgo: sirve para que pruebe un rail mejor, nunca para
   llevarlo a apalancarse, especular o comprar productos volátiles.
5. **Sin confirmshaming ni fricción para irse.** Cancelar tiene que ser tan fácil como entrar.
6. **Cumplimos las normas de transparencia de cada mercado** (costo financiero total, tasas
   nominales y efectivas, publicidad de productos financieros). Si una norma y una técnica de este
   documento chocan, gana la norma.
7. **Test de la vidriera:** si no te animarías a explicarle al usuario por qué el copy está escrito
   así, no se publica.

---

## Qué tan sólido es cada efecto

Prospect Theory aguantó bien la crisis de replicación y sigue siendo de lo más sólido de la
disciplina. Aun así, no todo pesa igual:

| Efecto | Solidez | Nota |
|---|---|---|
| Aversión a las pérdidas (palanca 3) | Alta | El efecto existe; su tamaño varía mucho según contexto y monto. |
| Punto de referencia y encuadre (palanca 2) | Alta | Muy replicado; el reto práctico es que el usuario crea el número. |
| Ponderación de probabilidades (palanca 4) | Alta | Sorteos y seguros son evidencia de campo masiva. |
| Separá ganancias / juntá pérdidas (R1, R2) | Media | Consecuencia directa de la curva; depende de que el usuario vea cada evento. |
| Integrar pérdida chica en ganancia grande (R3) | Media | Respaldado por la curva con cualquier parámetro razonable. |
| Separar ganancia chica de pérdida grande (R4) | Baja-media | La curva con λ = 2,25 no la respalda en la mayoría de los casos reales. Testear siempre. |

---

## Referencias

- Kahneman, D. y Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk.
  *Econometrica*, 47(2), 263–291.
- Tversky, A. y Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of
  Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323.
- Thaler, R. (1985). Mental Accounting and Consumer Choice. *Marketing Science*, 4(3), 199–214.
