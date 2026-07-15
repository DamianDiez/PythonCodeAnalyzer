# Reglas para opencode

## Antes de comenzar

1. Leer `docs/architecture.md` para entender el proyecto.
2. Comprender el problema a resolver.
3. Si el requerimiento no está completamente claro, hacer preguntas.
4. Proponer un plan de implementación.
5. Esperar aprobación antes de modificar archivos.

## Durante la implementación

- Seguir la estructura existente de `app_models/`. Los modelos de dominio van ahí, no en `models.py`.
- Nombres en inglés. PascalCase para clases, snake_case para funciones y variables.
- No agregar dependencias nuevas sin consultar.
- Templates: Django + Bootstrap 4. No agregar frameworks CSS/JS.
- Paths de archivos: usar `settings.BASE_PATH`. No hardcodear rutas absolutas.
- En tests, usar `unittest.mock.patch` para subprocess y operaciones de disco.
- No commitear secretos. `settings.py` tiene SECRET_KEY de desarrollo; no replicar este patrón.
- Realizar cambios pequeños y enfocados. Evitar modificar código no relacionado con la tarea.

## Antes de finalizar una tarea

- Explicar qué archivos fueron modificados.
- Explicar por qué fueron modificados.
- Enumerar posibles riesgos.
- Indicar si quedaron tareas pendientes.
- Ejecutar los tests relevantes: `python manage.py test`
- Realizar una validación manual de la funcionalidad.
- No asumir que los tests garantizan que la UI funciona correctamente.
- Realizar una self-review del cambio antes de dar la tarea por terminada.
