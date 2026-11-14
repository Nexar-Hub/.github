# Nexar Hub — contexto para agentes

Este archivo existe para que una sesión en la nube (por ejemplo, abierta desde el celular) arranque
con el mismo contexto que una sesión en la computadora de Nico. Este repo es público: acá va solo
lo que ya es público en nexarhub.com. El contexto completo vive en el vault privado.

## Antes de producir cualquier cosa para Nexar

1. **Cargá el vault.** El contexto completo está en el repo privado `Webflowrepository/context-vault`
   (el vault de Obsidian). El hook de inicio de sesión de este repo lo busca y, si está, imprime la
   ficha de la marca. Si el hook avisa que falta:
   - adjuntalo con `add_repo` (owner `Webflowrepository`, repo `context-vault`, acceso `read`) y clonalo
     al lado de este repo;
   - corré `python3 -I -X utf8 <vault>/30-Skills/cargar-marca.py --marca Nexar`;
   - leé, en este orden, `10-Empresas/Nexar/Nexar-Canon.md`, `Nexar-Hechos.md` y `Nexar-Aprendido.md`
     (los sí y los no de Nico; lo más reciente manda sobre el Canon cuando lo contradice y está
     fechado después).
2. **Si el vault no se puede cargar, decilo y frená.** No completes con supuestos: ni qué es la
   empresa, ni colores, ni servicios, ni clientes. Preguntá o leé nexarhub.com.
3. **El sitio es la referencia pública.** `nexarhub.com` y `www.nexarhub.com` están permitidos en la
   red del entorno «Nexar». Si un pedido menciona la marca, sus colores o sus trabajos, se verifica
   contra el sitio o el vault antes de escribir.

## Qué es Nexar Hub (lo público, verificado en nexarhub.com)

- Estudio de **brand y web design** de Nicolás Arocena. Argentina · Uruguay. Est. 2023.
- La marca es **Nexar Hub** / NexarHub (nexarhub.com); «Nexar» es el nombre corto de las carpetas.
- Tres servicios: estrategia de marca, identidad visual, diseño y desarrollo web.
- Frase del sitio: «Estrategia de marca, identidad visual y sitios web para negocios que son mejores
  de lo que parecen.»
- Portfolio: Ellerstina, El Médano, Solo Cracks, Grupo Mascardi, ZUM.

## Identidad visual (la del sitio en vivo)

- Tinta `#0a0a0c`, papel `#ffffff`, azul de marca `#018bfa`, azul profundo `#0171cb` para texto
  chico sobre blanco. **Nunca elegir otro color de acento por cuenta propia.**
- Tipografías: Satoshi (títulos y texto, peso 500) y JetBrains Mono (etiquetas y datos).
- Isotipo: las dos «N» espejadas. Archivos de marca en el vault: `10-Empresas/Nexar/Marca/`.
- Si el Canon del vault y el sitio no coinciden, decilo y preguntá cuál vale antes de diseñar.

## Reglas que no se negocian

- Voz en **plural** («hacemos», «diseñamos»), directa, sin vender humo. De vos (rioplatense).
- No inventar clientes, trabajos, resultados, precios, procesos ni testimonios.
- Las cifras que se muestran de un cliente son las que ese cliente publica; se aclara.
- Si algo no se pudo verificar, se dice.
- Mergear o publicar: solo cuando Nico lo pide para ese cambio puntual.

## Al cerrar una sesión en la nube

Lo que se aprendió o decidió no llega solo al vault: resumilo al final para que Nico (o una sesión en
la computadora) lo anote en `10-Empresas/Nexar/Nexar-Aprendido.md`.
