---
name: codificacion
description: "Use when: desarrollar o corregir funcionalidad en FastAPI, seguir una arquitectura por capas, implementar endpoints, pruebas, autenticación, modelos, validaciones o migraciones. Ideal para trabajo de codificación incremental y verificación técnica antes de concluir."
---

# Skill de codificación

## Objetivo
Implementar soluciones de forma ordenada, siguiendo la arquitectura del proyecto y validando cada cambio con pruebas o ejecución real.

## Flujo recomendado
1. Entender el requisito funcional o la guía a cumplir.
2. Identificar la capa afectada:
   - model
   - schema
   - route
   - service
   - dependency
   - database/migration
   - test
3. Implementar con enfoque mínimo y correcto:
   - respetar la arquitectura vigente
   - evitar cambios fuera del alcance
   - mantener consistencia en nombres y validaciones
4. Verificar funcionalidad con pruebas reales:
   - ejecutar pytest si aplica
   - probar endpoints con cliente HTTP o Swagger
   - revisar errores de validación o permisos
5. Documentar solo lo necesario y cerrar con evidencia.

## Puntos de decisión
- Si falla una prueba o un caso de negocio, localizar la causa en la capa correcta antes de corregir.
- Si cambia la base de datos, revisar también la migración y su estado real.
- Si agregas seguridad, completar roles, dependencias y pruebas asociadas.
- Si el cambio afecta una ruta existente, revisar también el README y la evidencia del comportamiento.

## Criterios de calidad
- Cada cambio tiene una razón clara y se ajusta a la arquitectura existente.
- Se valida la funcionalidad con ejecución real o pruebas automatizadas.
- No se entregan cambios incompletos sin verificar.
- La implementación es consistente con el estado del proyecto y la guía de entrega.

## Checklist final
- [ ] requisito entendido
- [ ] capa correcta modificada
- [ ] validación ejecutada
- [ ] pruebas o casos reales revisados
- [ ] errores de seguridad o permisos comprobados
- [ ] documentación o evidencia actualizada si aplica
