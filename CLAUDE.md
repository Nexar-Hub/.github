# Nexar-Hub/.github — instrucciones para agentes

Este repo es **público**: guarda solo las plantillas de issues y PRs de la organización.
Las sesiones abiertas desde el celular o la web lo usan como repo por defecto; por eso existe este archivo.

## Al arrancar
El hook `.claude/hooks/session-start.sh` carga el contexto del vault privado (`Webflowrepository/context-vault`)
con `30-Skills/contexto.py start`. Si avisa «SIN CONTEXTO», seguí sus pasos antes de proponer nada.
Este archivo no repite estado (colores, clientes, pendientes): eso vive en el vault y se vuelve mentira si se copia acá.

## Reglas
- Las de `00-Contexto/Kernel.md` y `Preferencias.md` del vault. Ante la duda, mandan esas.
- Antes de construir algo, buscá si ya existe: `capacidades.py para "<pedido>"` y las ramas abiertas de este repo.
- **Nada de contexto de negocio en este repo** (marcas, clientes, precios, perfil, estrategia): es público.
  Lo que produzca una sesión en la nube va al chat como relevo (`contexto.py wrap`, sin `--escribir`)
  o al repo privado que corresponda, con el OK de Nico.
- Push, merge y deploy, solo con un OK de Nico para ese caso puntual.
