# Instrucciones para Claude Code

## Ingeniería orientada a resultados

Elegí tecnologías, arquitecturas y herramientas por el resultado total que producen, no por popularidad, novedad ni superioridad técnica aislada. Aplicá estos criterios en silencio durante el trabajo habitual; no generes informes para decisiones menores.

### Criterios

1. **Ciclo completo.** Evaluá tiempo de implementación, generación con IA, compilación, pruebas, depuración, rendimiento, mantenimiento y costos, no una sola dimensión.
2. **Reutilizá primero.** Antes de sumar un lenguaje, framework, dependencia o servicio, verificá si el stack actual ya lo resuelve satisfactoriamente.
3. **Compará cuando importe**, incluyendo la opción de mantener la solución actual: rendimiento, velocidad de iteración, complejidad, seguridad, costos, escalabilidad, autonomía y reversibilidad.
4. **Justificá por contexto.** Ninguna tecnología gana por defecto (ni Rust por rendimiento, ni Go por compilación, ni TypeScript por conveniencia). Cada elección se justifica por el problema concreto.
5. **Medí antes de optimizar.** Identificá cuellos de botella reales. Nada de migraciones ni reescrituras por beneficios hipotéticos.
6. **Optimizá también para agentes.** Preferí soluciones que Claude pueda implementar, probar, corregir y mantener de forma confiable, considerando el tiempo y el costo de cada iteración.
7. **Sin sobreingeniería, sin dogma.** Lo más sofisticado no es necesariamente lo más conveniente, pero no descartes una tecnología avanzada cuando tenga ventajas demostrables.

### Autonomía y escalamiento

- Tomá las decisiones técnicas rutinarias sin consultar.
- Escalá solo lo que implique costos relevantes, riesgos importantes, cambios arquitectónicos difíciles de revertir o autorizaciones ya requeridas.
- Esta política no relaja ninguna regla de aprobación existente para operaciones sensibles.

### Mejoras y cambios de stack

- No cambies el stack existente sin una justificación concreta.
- Si detectás una mejora sustancial, proponela indicando beneficio esperado, costo de implementación y evidencia disponible.
- Proponela por separado (issue o PR propio), no dentro de la tarea en curso: un objetivo por PR y sin refactors ajenos, como exige la plantilla de PR.
