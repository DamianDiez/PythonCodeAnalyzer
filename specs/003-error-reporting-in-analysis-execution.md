# Reporte de errores en la ejecución de herramientas de análisis

## Objetivo

Que el sistema acumule y describa correctamente los errores que ocurren durante la ejecución de herramientas de análisis, para que esa información esté disponible para consultas posteriores.

## Contexto

Actualmente las herramientas de análisis (`Pylint`, `Vulture`, `Radon`) siempre reportan estado `FINISHED` incluso si ocurre una excepción durante su ejecución. Los errores se imprimen por consola pero no se persisten en la base de datos.

El campo `status_msg` del modelo de análisis existe pero no se popula cuando la ejecución falla. Como resultado, el campo queda con su valor por defecto y no contiene información útil sobre lo ocurrido.

## Requisitos funcionales

- Cuando una herramienta de análisis falla durante su ejecución, debe reportar un estado de error en lugar de `FINISHED`.
- Cuando al menos una herramienta falla, el análisis completo debe quedar en estado `FAILED`.
- El campo `status_msg` del análisis debe contener los mensajes de error de **todas** las herramientas que fallaron. Cada mensaje debe tener el formato `<Nombre de la herramienta>: <mensaje de error>`.
- Cuando múltiples herramientas fallan, cada entrada se concatena utilizando un salto de línea (`\n`) como separador.
- Si múltiples herramientas fallan, el usuario debe poder identificar cuáles fallaron a partir del contenido de `status_msg`.
- Si la herramienta no pudo instanciarse, el error debe registrarse en `status_msg` con un mensaje que incluya el nombre de la herramienta cuya instanciación falló.
- El comportamiento de cancelación existente no debe modificarse: `status_msg` ya se establece correctamente al cancelar.

## No objetivos

- No modificar la interfaz de usuario ni los templates.
- No agregar nuevos estados de análisis.
- No cambiar el modelo de datos existente (ya tiene `status_msg`).
- No modificar la lógica de paginación.
- No modificar la lógica de creación de análisis.
- No modificar la lógica de cancelación de análisis.

## Criterios de aceptación

- Dado un análisis con una herramienta que falla, el campo `status_msg` contiene el mensaje de error de esa herramienta en el formato `<Nombre de la herramienta>: <mensaje de error>`.
- Dado un análisis con dos herramientas que fallan, el campo `status_msg` contiene los mensajes de ambas herramientas separados por un salto de línea.
- Dado un análisis con tres herramientas donde una falla, el campo `status_msg` contiene el mensaje de la herramienta que falló.
- Dado un análisis donde todas las herramientas fallan, el campo `status_msg` contiene los mensajes de todas ellas separados por un salto de línea.
- Dado un análisis donde la herramienta no pudo instanciarse, el campo `status_msg` contiene un mensaje que permite identificar la herramienta cuya instanciación falló.
- Dado un análisis con una herramienta que falla, el estado del análisis es `FAILED` independientemente de que otras herramientas finalicen correctamente.
- Dado un análisis donde todas las herramientas finalizan correctamente, el estado del análisis es `FINISHED`.
- Dado un análisis donde todas las herramientas finalizan correctamente, el campo `status_msg` no se modifica.
- Los cambios no afectan el comportamiento visible de la interfaz de usuario.
- Se agregan pruebas que verifican el comportamiento definido en esta especificación.
- Los tests existentes continúan pasando.

## Archivos posiblemente afectados

| Archivo | Descripción |
|---------|-------------|
| `python_code_analyzer_app/app_models/Analysis.py` | Modelo de análisis con lógica de ejecución. |
| `python_code_analyzer_app/app_models/Tool.py` | Herramientas de análisis y sus subclases. |
| `python_code_analyzer_app/tests/test_domain_models.py` | Tests de modelos de dominio. |
