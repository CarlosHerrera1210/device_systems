---
name: seguridad
description: "Use when: revisar seguridad de APIs, JWT, OAuth2, roles, permisos, password hashing, rate limiting, middleware, headers, autenticación, autorización, o validación de seguridad en FastAPI. Ideal para auditorías de endpoints, pruebas de acceso no autorizado y cumplimiento de la evidencia de seguridad."
---

# Skill de seguridad

## Objetivo
Auditar y reforzar la seguridad de una API FastAPI antes de entregar una evidencia final. Este flujo prioriza protección real, validación funcional y evidencia verificable, no suposiciones.

## Flujo recomendado
1. Revisar la arquitectura de seguridad del proyecto:
   - routers y endpoints protegidos
   - dependencias de autenticación
   - modelos de usuario y roles
   - JWT, hashing y validación de contraseñas
   - rate limiting y middleware
2. Verificar que cada endpoint tenga la protección correcta:
   - autenticación obligatoria donde aplica
   - roles y permisos explícitos
   - denegación por defecto para usuarios sin token o sin permisos
3. Confirmar la implementación técnica:
   - passwords guardadas con hash
   - tokens emitidos y decodificados correctamente
   - middleware para request ID y headers
   - manejo de errores para token inválido, faltante o prohibido
4. Validar con pruebas reales y casos límite:
   - registro
   - login
   - acceso sin token
   - token inválido
   - acceso prohibido por rol
   - rate limiting
   - CORS o headers esperados
5. Dejar evidencia objetiva:
   - capturas del comportamiento real
   - comandos ejecutados
   - resultados de pruebas y validaciones

## Puntos de decisión
- Si un endpoint requiere usuario autenticado, usar dependencia de usuario actual y no dejarlo público.
- Si hay roles distintos, definir permisos por acción y no permitir heredación implícita.
- Si se usa bcrypt o hashing, verificar que la contraseña no se guarde en texto plano.
- Si se activa rate limiting, comprobar que también aplica en rutas sensibles como login y usuarios.
- Si aparece un error de seguridad, corregir la causa raíz y volver a validar con pruebas funcionales.

## Criterios de calidad
- No hay endpoints sensibles sin autenticación.
- Los permisos se aplican por rol y no por suposición.
- Las pruebas cubren al menos registro, login, acceso no autorizado y rate limit.
- La documentación y la evidencia reflejan comportamiento real.
- No se entrega una solución que “parece segura” si no se ha verificado con ejecución real.

## Checklist final
- [ ] JWT y hashing configurados correctamente
- [ ] roles y permisos restringidos
- [ ] middleware y headers aplicados
- [ ] tests de seguridad ejecutados
- [ ] evidencia capturada sin inventar resultados
- [ ] README y documentación alineados con la implementación real
