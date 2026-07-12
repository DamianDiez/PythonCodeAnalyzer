# Mostrar el estado del último análisis en la lista de repositorios

## Objetivo

Permitir que el usuario conozca, desde la lista de repositorios, el estado del último análisis ejecutado para cada repositorio.

## Contexto

Actualmente la lista de repositorios solo muestra información básica. Para conocer el estado de un análisis es necesario ingresar al detalle del repositorio, lo que dificulta identificar rápidamente qué repositorios tienen análisis pendientes, en ejecución, finalizados o con errores.

## Requisitos funcionales

- Mostrar el estado del último análisis de cada repositorio en la lista principal.
- Se considera "último análisis" al análisis más recientemente creado para ese repositorio, independientemente de su estado.
- Si el repositorio nunca fue analizado, indicar claramente que no existen análisis.
- El estado debe representarse de forma visual mediante un badge por cada estado posible.
- La columna de estado se ubica entre "Url" y "Actions".
- El badge es únicamente informativo; no es clickeable.

## Mapeo visual de estados

| Estado | Texto del badge | Clase de badge |
|---|---|---|
| Sin análisis | Sin análisis | `badge-light` |
| PENDING | Pendiente | `badge-secondary` |
| RUNNING | En ejecución | `badge-primary` |
| FINISHED | Finalizado | `badge-success` |
| FAILED | Fallido | `badge-danger` |
| CANCELLED | Cancelado | `badge-warning` |

## No objetivos

- No modificar el proceso de ejecución de análisis.
- No agregar nuevos estados de análisis.
- No cambiar el modelo de datos existente.
- No modificar la lógica de creación de análisis.

## Criterios de aceptación

- Dado un repositorio con un análisis `FINISHED`, el badge muestra `Finalizado`.
- Dado un repositorio con múltiples análisis de distinto estado, el badge muestra el estado del análisis más reciente.
- Dado un repositorio sin análisis, se muestra el badge `Sin análisis`.
- Dado un repositorio con análisis en estado `RUNNING`, el badge muestra `En ejecución` independientemente de si existen análisis previos finalizados.
- El badge se muestra correctamente en todas las páginas del paginador.
- Se agregan pruebas que verifican el comportamiento definido en esta especificación.
- Los tests existentes continúan pasando.
