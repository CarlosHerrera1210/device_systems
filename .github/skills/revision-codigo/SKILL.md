---
name: revision-codigo
description: "Use when: revisar el código del proyecto, validar endpoints, detectar brechas de integración, validar dependencias, revisar arquitectura, o comprobar que el proyecto cumple la guía de evidencia. Ideal para análisis de calidad, checks de implementación y revisión previa a entrega."
---

# Skill de revisión de código

## Objetivo
Revisar el proyecto como si fuera una auditoría técnica antes de cerrar una evidencia o entrega. El enfoque es encontrar inconsistencias entre la guía, el código y la ejecución real.

## Flujo recomendado
1. Leer la guía o requisito que debe cumplirse.
2. Mapear el proyecto por capas:
   - modelos
   - schemas
   - routes
   - services
   - dependencies
   - middleware
   - database / migrations
   - tests
3. Comparar cada característica con la evidencia posible:
   - existe endpoint
   - existe autenticación
   - existe validación de permisos
   - existe manejo de errores
   - existe prueba automatizada
   - existe migración o ajuste relevante
4. Buscar brechas comunes:
   - routes públicas que deberían estar protegidas
   - permisos incompletos
   - dependencias rotas
   - tests inconclusos
   - README desactualizado
   - evidencia visual incompleta o inventada
5. Corregir primero la causa raíz y luego validar.

## Puntos de decisión
- Si el código no coincide con la guía, priorizar cumplir la guía con evidencia real.
- Si un comportamiento no está probado, no asumir que funciona; verificarlo ejecutando la API o pytest.
- Si el README menciona algo que no está en el código, corregir la documentación antes de cerrar.
- Si la evidencia no se puede producir con una ejecución real, no inventar y documentar la limitación.

## Criterios de calidad
- El proyecto cumple la guía funcional y técnica.
- El código está coherente entre rutas, validaciones y servicios.
- Las pruebas ejecutadas respaldan lo que se entrega.
- El README refleja el estado real del repositorio.
- Se evita la entrega de trabajo “aparente” sin verificación.

## Checklist final
- [ ] requisitos revisados
- [ ] endpoints verificados
- [ ] roles y permisos inspeccionados
- [ ] pruebas ejecutadas
- [ ] migraciones comprobadas
- [ ] documentación alineada
- [ ] evidencia real disponible
