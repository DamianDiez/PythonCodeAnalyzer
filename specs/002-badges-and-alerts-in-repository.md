# Badges de estado y alerts de error en la página del repositorio

## Objetivo

Permitir que el usuario identifique visualmente, desde la página de detalle del repositorio, el estado de cada análisis y el motivo cuando falla o se cancela.

## Contexto

Actualmente la página de detalle del repositorio muestra el estado de cada análisis como texto plano (ej: `FAILED`, `FINISHED`). No hay distinción visual entre estados. Cuando un análisis falla o se cancela, no se muestra ningún mensaje explicativo, aunque el campo `status_msg` del modelo ya existe y puede contener esa información.

Esto obliga al usuario a hacer clic en "View results" para descubrir que un análisis falló, sin obtener información útil sobre la causa.

## Requisitos funcionales

- Reemplazar el texto plano de estado por un **badge colorido** en la columna "Status" de la tabla de análisis.
- El esquema de colores por estado es el siguiente:

| Estado | Texto del badge | Color |
|---|---|---|
| PENDING | Pendiente | Gris |
| RUNNING | En ejecución | Azul |
| FINISHED | Finalizado | Verde |
| FAILED | Fallido | Rojo |
| CANCELLED | Cancelado | Amarillo |

- Cuando un análisis tiene estado `FAILED` o `CANCELLED`, y su campo `status_msg` contiene un mensaje informativo, mostrar un **alert banner** debajo de la fila de la tabla con ese mensaje. Los alerts no son dismissibles (no incluyen botón de cierre).
- El alert utiliza el mismo esquema de colores que el badge del estado correspondiente: rojo para `FAILED`, amarillo para `CANCELLED`.
- Los alerts **solo** se muestran para `FAILED` y `CANCELLED`. Para `PENDING`, `RUNNING` y `FINISHED` no se renderiza alert independientemente del valor de `status_msg`. Los mensajes informativos en `status_msg` para análisis exitosos (`FINISHED`) se ignoran intencionalmente en esta iteración.
- Un alert se considera no informativo cuando `status_msg` es el string `'null'` (valor por defecto del campo), `None`, una cadena vacía o una cadena que contiene solo whitespace. En estos casos no se renderiza alert.
- El contenido de `status_msg` se muestra completo sin truncamiento. En pantallas estrechas, el texto hace wrap dentro del alert.

## No objetivos

- No modificar la lógica de ejecución de herramientas de análisis.
- No modificar cómo se populate el campo `status_msg`.
- No agregar nuevos estados de análisis.
- No cambiar el modelo de datos existente.
- No modificar la lógica de paginación.
- No modificar la lógica de creación de análisis.
- No modificar la lógica de cancelación de análisis.

## Criterios de aceptación

- Dado un análisis con estado `PENDING`, se muestra un badge gris con texto `Pendiente`.
- Dado un análisis con estado `RUNNING`, se muestra un badge azul con texto `En ejecución`.
- Dado un análisis con estado `FINISHED`, se muestra un badge verde con texto `Finalizado` y no se muestra ningún alert.
- Dado un análisis con estado `FAILED`, se muestra un badge rojo con texto `Fallido`.
- Dado un análisis con estado `FAILED` y `status_msg = "Tool Vulture raised an exception"`, se muestra un alert rojo con ese mensaje debajo de la fila.
- Dado un análisis con estado `FAILED` y `status_msg = "null"`, se muestra el badge pero no se muestra alert.
- Dado un análisis con estado `FAILED` y `status_msg` vacío, se muestra el badge pero no se muestra alert.
- Dado un análisis con estado `FAILED` y `status_msg` con solo whitespace, se muestra el badge pero no se muestra alert.
- Dado un análisis con estado `CANCELLED`, se muestra un badge amarillo con texto `Cancelado`.
- Dado un análisis con estado `CANCELLED` y `status_msg = "Canceled by user"`, se muestra un alert amarillo con ese mensaje debajo de la fila.
- Dado un análisis con estado `CANCELLED` y `status_msg = "null"`, se muestra el badge amarillo y no se muestra ningún alert.
- Dado un análisis con estado `CANCELLED` y `status_msg` vacío, se muestra el badge amarillo y no se muestra ningún alert.
- Dado un análisis con estado `CANCELLED` y `status_msg` con solo whitespace, se muestra el badge amarillo y no se muestra ningún alert.
- Dado un análisis con estado `PENDING` o `RUNNING`, no se muestra alert independientemente del valor de `status_msg`.
- Dado un análisis en la página 2 del paginador con estado `FAILED` y `status_msg` informativo, se muestra el badge rojo y el alert con el mensaje.
- Se agregan tests de vista que verifican:
  - el badge correspondiente para cada estado;
  - la presencia del alert para `FAILED` y `CANCELLED` con `status_msg` informativo;
  - la ausencia del alert cuando `status_msg` no es informativo;
  - el comportamiento en una página distinta del paginador.
- Los tests existentes continúan pasando.

## Archivos posiblemente afectados

| Archivo | Descripción |
|---------|-------------|
| `python_code_analyzer_app/templates/python_code_analyzer_app/repository.html` | Template de la página de detalle del repositorio. |
| `python_code_analyzer_app/tests/test_views.py` | Tests de la vista de detalle del repositorio. |
