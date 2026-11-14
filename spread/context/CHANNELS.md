# Spread · Canales y tácticas de distribución

> Síntesis de los links, capturas y notas de los exports «Distribution» y «27 Distribution».
> Cada táctica lleva la palanca de la [biblia](../bible/PLAYBOOK.md) que la potencia. Los links
> están sin parámetros de tracking; el inventario completo está en [`SOURCES.md`](SOURCES.md).
> Las afirmaciones de terceros (vistas, resultados) son de sus autores; no son datos de Spread.

## La tesis, en las capturas guardadas

- «Distribution is the only moat left. Everyone is a builder now. Few will ever make money simply
  because nobody knows they exist.» (viñeta: una puerta *Distribution* vacía y una fila enorme
  frente a *Building another product*; variante *Getting clients* contra *Building another feature*).
- «Stop investing in showing what you've done. Start investing in communicating how you think.»
- «Any brand with a phone and a modest budget can reach more people than most national campaigns
  twenty years ago.»
- Notas propias: «Hoy todo el mundo construye. Ser el distributor.» · «El problema no es hacer. El
  problema es vender.»

Todas son la **palanca 2**: el builder que «ya construyó» está parado en cero, y la tesis le
muestra que ese status quo ya es una pérdida (nadie sabe que existe).

Canales de adquisición anotados para 2026: **personal brand, paid ads, UGC, influencers.**

---

## X / Twitter: el canal principal

Notas propias: «En Twitter está la money.» · «Los reals influencers están en Twitter.» ·
«Twitter es la data.» · «Armar una automatización bien humana y un perfil bien persona.»

- Una cuenta con una persona real detrás (personal brand). La automatización asiste a esa persona
  a investigar, redactar y programar; **no** se crean perfiles falsos ni se simula a alguien que
  no existe (ver *Límites* en la biblia).
- Cold messaging: [paulklayvc](https://x.com/paulklayvc/status/2104626545868394594).
- Hooks con la palanca 2 y 3, siempre con un dato real detrás.

## SEO

- **Quick win:** Search Console → Performance → 12 meses → exportar `Pages.csv` y `Queries.csv`
  → pasarlos a una IA con navegador para que proponga y ejecute mejoras
  ([timb03](https://x.com/timb03/status/2086608189894840595),
  [rosoai](https://x.com/rosoai/status/2088601983531823229)).
- **Topic clusters en vez de keywords:** una página pilar profunda conectada a decenas de
  artículos específicos para cubrir todas las intenciones del funnel; contenido basado en datos
  reales, no parafraseo ([kokebcn](https://x.com/kokebcn/status/2112486769568739683)).
  Idea de marca: *anti SEO tradicional* + mucho contenido en carruseles y reels explicando el tema.
- Herramienta open source: [OpenSEO](https://openseo.so/) («con este me puedo pegar»).
- Google Maps SEO: [borjafat](https://x.com/borjafat/status/2087936510490186180).
- Más tácticas guardadas: [borjafat](https://x.com/borjafat/status/2087155605211320808),
  [timseo_](https://x.com/timseo_/status/2087203754324242918),
  [nicholasdulait](https://x.com/nicholasdulait/status/2087537648747286874),
  [bloggersarvesh](https://x.com/bloggersarvesh/status/2096231419874005474) («SEO arrancar ya»),
  [rrmdp](https://x.com/rrmdp/status/2101304177985024363) (SEO + SEM).

## AEO / GEO (respuestas de IA)

Del export «27 Distribution» (un post de un founder sobre cómo lo hicieron):

1. **Medir:** las frases exactas que el ICP le escribe a ChatGPT y Claude, y las fuentes de las que
   la IA saca sus respuestas. Tracker propio con [Elmo](https://github.com/elmohq/elmo) (open
   source), que corre los prompts por las interfaces reales vía DataForSEO y guarda cada respuesta.
2. **Ingeniería inversa del funnel:** a cada demo referida por una IA se le ofrecieron créditos a
   cambio del `/export` del chat que la mandó; después se analizaron prompts y fuentes.
3. **Ejecutar:** todo el copy de producto, web, docs y redes usa esas palabras exactas y cuenta la
   misma historia.
4. **Hacer todo, medir y preguntar:** nadie sabe todavía qué canal pesa más; se hace todo, se mide,
   se pregunta a quienes llegaron por IA y se duplica lo que funciona. Comunidad y meetups ayudan.

**Uso en Spread:** `spread/tools/prospect_audit.mjs` ya detecta si el robots.txt del prospecto
bloquea a los rastreadores de búsqueda de OpenAI, Anthropic o Perplexity. El paso siguiente es el
tracker de prompts. La auditoría AEO de la categoría del prospecto es el lead magnet ideal para la
palanca 2: «Cuando tu ICP le pregunta a ChatGPT por *[categoría]*, recomienda a
*[competidor]*». Pérdida actual, con evidencia, del propio prospecto.

## Paid

- **Meta ads:** [codyschneider](https://x.com/codyschneider/status/2106776383955366150),
  [cbwritescopy](https://x.com/cbwritescopy/status/2095209901769310304), con Claude
  ([oadrianolucas](https://x.com/oadrianolucas/status/2112840089558778038)); geo ads en Meta.
- **Ads interactivos:** playable demo ads, giros 3D de producto desde una foto, quiz funnels que
  califican leads mientras juegan, experiencias antes/después para servicios
  ([zackpaid](https://x.com/zackpaid/status/2095695603808309497)). El argumento del post es
  palanca 2 pura: «antes gastabas $5k y esperabas 6 semanas a una agencia por un playable ad».
- Carruseles que ya funcionan orgánicamente: «a un par de estas meterles plata en ads».
- Testear siempre variante pérdida contra variante ganancia sobre el mismo creativo.

## Video, UGC y contenido

- Presupuesto de referencia anotado: ~400 USD/mes para generar motion para Nexar, MG y FUT AI.
- Video con IA: [rileybrown](https://x.com/rileybrown/status/2096969016136908860) («video creation
  es por acá»), [cielodahy](https://x.com/cielodahy/status/2095649343629860986) (nota: «Codex
  mejor que Claude para videos»), [chddaniel](https://x.com/chddaniel/status/2095775049475313943).
- UGC con IA: [jasonzhou1993](https://x.com/jasonzhou1993/status/2099837130927427989),
  [LiliLanXin](https://x.com/LiliLanXin/status/2087597797801677273/video/1).
- **Spot the outlier:** las vistas relativas a seguidores dicen cuánto vale el formato; buscá
  formatos donde cuentas chicas explotan. **Llevá un formato probado a otro nicho**
  ([victorgu0](https://x.com/victorgu0/status/2117693795076854052/video/1)).
- Landing + video promocional como pieza de venta
  ([irabukht](https://x.com/irabukht/status/2101441120093823134)).
- Newsletter.

## Influencers y partners

- Idea anotada: ofrecer web y marketing a influencers a cambio de que suban stories (para Nexar).
- Con la palanca 4: un premio grande e improbable (un Build completo sorteado entre quienes
  comparten) suele mover más que descuentos chicos para muchos. Medir leads atribuidos.

## Lead generation y outbound

- Pipeline interno: discover → enrich → dedupe → score → verify sample → deliver.
- Automatizar lead gen: [everestchris6](https://x.com/everestchris6/status/2099161324555309092);
  GTM: [gengdaj](https://x.com/gengdaj/status/2098252168625332263).
- Outbound con palanca 2: abrir con una pérdida observable de esa cuenta.
  `node spread/tools/prospect_audit.mjs <url>` la mide y redacta el primer mensaje (ES/EN) solo con
  los hallazgos verificados.

## Medición («esto es Distribution en el core»)

- Centralizar todo en BigQuery: Google Ads, Search Console, Meta, ventas del CRM, vía Cloudflare
  Worker o similar; después pedir los insights sobre datos propios
  ([benemredoganer](https://x.com/benemredoganer/status/2112623085136629841)).
- Configurar todas las conversiones con Codex o Claude: Search Console, Analytics, Tag Manager,
  CRM.
- En la oferta V1: PostHog, UTMs, eventos de conversión.

## Vender

De [renapiermarini](https://x.com/renapiermarini/status/2113304032500412470), sobre vender software:

1. Demo funcional **gratis** para lograr el «wow moment» rápido.
2. Cero barrera de entrada: cuanto más fácil se adapte a su proceso, más se vende.
3. El producto perfecto es el que el cliente usa y le sirve, no el que el creador considera lindo.

Otra captura guardada («lo de abajo te convence»): un contador de prueba social bajo el CTA
(«7,925 people already got their feet wet»). Funciona solo con un número real y actualizado.

Con la biblia: la demo con datos propios mueve el punto de referencia (el prospecto *ve* lo que
pierde sin ella) y la certeza de un resultado visible vale más que una promesa probable.

## Referencias de marca y web

- Visual primaria de la web: [guillaumezhu.com](https://guillaumezhu.com/) (ver
  [`WEBSITE_BRIEF.md`](WEBSITE_BRIEF.md)).
- Copy y claridad: [beomniscient.com](https://beomniscient.com/),
  [demandcurve.com](https://www.demandcurve.com/), [linear.app](https://linear.app/).
- Inspiración guardada: identidad de LLYLL, anotada como «Distribution + media» (negro y amarillo,
  ilustración de línea, «Hit record, reach further»; también sugiere una línea de media/video),
  boceto de monograma (letras J y G con ejes de simetría), un post de LinkedIn
  sobre una identidad de Red Antler («Distribution brand puede ser algo así») y otro explicando un
  logo («algo así explicando el logo»).
