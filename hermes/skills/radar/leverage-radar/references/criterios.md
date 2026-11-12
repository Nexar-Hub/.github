# Criterios del radar

## Veredictos

| Veredicto | Significa | Requisito mínimo | Qué deja escrito |
|---|---|---|---|
| **ADOPT** | Cambia algo ahora | evidencia `verificado`, o `medido` + reversible + barato | propuesta concreta para `stack.md` o `decisiones.md` |
| **TEST** | Merece una prueba acotada | evidencia ≥ `demo` y una pregunta en "sí" | hipótesis, criterio de éxito, timebox, fecha de corte |
| **WATCH** | Es relevante, pero no ahora | capacidad ubicada en el mapa | `revisar_si`: un disparador concreto (sin disparador, es DROP) |
| **CANDIDATO** | Pasó el filtro barato | una pregunta en "sí" | lo confirma el DIGEST |
| **DROP** | No cambia nada | — | una línea de motivo, sin aviso |

## Escalera de evidencia

Usá siempre el nivel más bajo que aplique.

1. `sin-fuente`: solo existe la nota o el título.
2. `anecdota`: un post o hilo que afirma algo.
3. `demo`: video, repo con código o demo que funciona.
4. `adopcion`: uso real verificable. Ejemplos: commits recientes, issues de usuarios, empresas que lo usan, estrellas en crecimiento.
5. `medido`: benchmark independiente, paper o datos propios.
6. `verificado`: el usuario lo probó en su workflow y cumplió el criterio de éxito.

Los números del autor ("10x", "−40% tokens") se citan como "afirmado por el autor". Varias copias del mismo hilo no cuentan como evidencia independiente.

## Filtros extra

Se aplican después de que una de las tres preguntas dé "sí".

- **Durabilidad**:
  - `alta`: fortalece contexto, criterio, distribución, relaciones o datos propios.
  - `media`: es un patrón o una arquitectura.
  - `baja`: es un truco de prompt o un parche contra una debilidad del modelo, y suele caducar en meses.
- **Resta antes que suma**: ¿elimina un componente, un costo o un paso manual? Eso puntúa más que agregar una capacidad nueva.
- **Costo por cliente**: un SaaS que se multiplica por cliente cuenta en contra. "Primero buscar, después integrar, al final construir."
- **Reversible**: ¿se puede sacar en un día sin perder datos? Si no, el requisito sube un nivel de evidencia.
- **Seguridad**: si pide tokens, acceso total al sistema o manda datos de clientes a terceros, el veredicto máximo es TEST en un sandbox.

## Pruebas (experimentos.md)

- Hay **3 activas como máximo**. Para abrir una cuarta hay que cerrar otra.
- El timebox es de **20 a 40 minutos por sesión y 2 sesiones como máximo**. Cada sesión hace solo esa prueba.
- Cada prueba cierra con ADOPT o DROP y una línea de aprendizaje. "Sigo viendo" no es un cierre válido.

## Alertas del digest

- **Rabbit hole**: un tag con ≥5 ítems nuevos en 14 días y 0 pruebas cerradas en ese tag. El mensaje es: "Estás orbitando `<tag>`: n links, 0 pruebas. Elegí 1 para TEST y hacé DROP del resto."
- **Experimento vencido**: pasó la fecha de corte sin cierre.
- **WATCH despierto**: su `revisar_si` se cumplió con algo de esta semana.
- **Herramienta sin capacidad**: varios links de la misma herramienta que no se pueden ubicar en el mapa.

## Formato de `radar-log.jsonl`

```json
{"id": "a1b2c3d4e5f6", "url": "https://x.com/u/status/1", "fecha": "2026-11-12", "etapa": "triage",
 "veredicto": "CANDIDATO", "capa": "orquestacion", "capacidad": "context-efficiency",
 "pregunta": "stack", "evidencia": "demo", "durabilidad": "media", "reversible": true,
 "reemplaza": "nada", "por_que": "reduce contexto en sesiones largas de Claude Code",
 "proximo_paso": "probar en 1 sesión real y medir tokens", "revisar_si": null}
```

`pregunta` toma uno de estos valores: `decision`, `stack`, `apuesta` o `ninguna`. `etapa` toma uno de estos: `triage`, `capture`, `digest` o `scan`.
