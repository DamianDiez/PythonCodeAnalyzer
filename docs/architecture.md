# Python Code Analyzer — Arquitectura

## Propósito del sistema

Aplicación web Django que permite analizar repositorios Python con herramientas de análisis estático (Pylint, Vulture, Radon). Los usuarios registran repositorios (git clone), lanzan análisis de forma asíncrona via Celery, y visualizan resultados como indicadores numéricos y gráficos (Chart.js).

---

## Componentes principales

### `python_code_analyzer/` — Proyecto Django

| Archivo | Responsabilidad |
|---|---|
| `settings.py` | Configuración Django, Celery (broker RabbitMQ), `CRITERIA_LIST` (orden de resultados), `BASE_PATH` (ruta en disco para repositorios y resultados). Usa `BigAutoField` como default para PKs. `CELERY_RESULT_BACKEND = None` (no persiste resultados de tareas Celery). |
| `celery.py` | Configuración y auto-descubrimiento de tareas Celery |
| `urls.py` | Enrutamiento raíz: `/admin/`, `/users/`, `/` |

### `python_code_analyzer_app/app_models/` — Modelos de dominio

| Archivo / Clase | Responsabilidad |
|---|---|
| `Repository.py` / `Repository` | Representa un repositorio git. `download()` hace git clone. `get_last_commit()` obtiene el hash HEAD. `delete_files()` limpia del disco. |
| `Analysis.py` / `Analysis` | Análisis sobre un repositorio. `run()` ejecuta cada tool y empaqueta todo en ZIP. `get_result()` recolecta los `ResultItem` de todas las tools. |
| `Analysis.py` / `CeleryTaskSignal` | Mecanismo de cancelación de tareas vía polling. Definido en `Analysis.py`, no en archivo separado. Señales: `CANCEL_TASK` (usado) y `PAUSE_TASK` (definido pero nunca implementado). |
| `Tool.py` / `Tool` | Modelo base. `get_instance()` busca la subclase por nombre en `globals()`. |
| `Tool.py` / `Pylint_Tool`, `Vulture_Tool`, `Radon_Tool` | Subclases concretas que implementan `run()` y `get_result()`. Usan `managed = False` y comparten la tabla `python_code_analyzer_app_tool` — patrón multi-table inheritance sin tabla extra. |
| `AnalysisTool.py` | Join table Analysis–Tool. `run()` delega en `tool.get_instance().run()`. `get_result()` delega en `tool.get_instance().get_result()`. Tiene además `get_charts()` y `get_indicators()` como métodos separados, pero no son llamados externamente (dead code). |
| `TaskManager.py` | Tareas Celery: `excecute_analysis` (flujo completo), `launch_massive_upload` (carga masiva). |
| `tools_status.py` | Constantes de estado: PENDING, RUNNING, FINISHED, FAILED, CANCELLED. |

### `python_code_analyzer_app/tools/` — Objetos de presentación

| Archivo | Responsabilidad |
|---|---|
| `ResultItem.py` | Clase base: `id`, `label`, `size` (4/6/12 para Bootstrap grid), `plantilla` (ruta del template HTML), `tool_name`. |
| `Chart.py` | Hereda `ResultItem`. Tipos: bar, doughnut, matrix, etc. Almacena `xLabels`, `yLabels`, `data`, `height`, `display_legend`. |
| `IdicatorDefault.py` | Hereda `ResultItem`. Indicador simple con un valor numérico o texto. Nombre de archivo con typo (falta la `n`). |
| `IndicatorRating.py` | Hereda `IndicatorDefault`. Rating con umbrales (`bad`, `regular`, `good`) para colorear. |

### `python_code_analyzer_app/app_layout_classes/` — Layout

| Archivo | Responsabilidad |
|---|---|
| `Criteria.py` | Criterio de ordenamiento: `SIZE`, `TOOL_NAME` con flag ascendente/descendente. |
| `LayoutManager.py` | `sort_by_multiple_criteria(items, criteria_list)` ordena los `ResultItem` por atributos usando `sorted()` nativo. |

### `python_code_analyzer_app/forms.py` — Formularios

| Formulario | Uso |
|---|---|
| `RepositoryForm` | ModelForm para `Repository` (campo `url`). Usado en `new_repository`. |
| `AnalysisForm` | ModelForm para `Analysis` (campo `status` deshabilitado). El status siempre es PENDING inicialmente; el form se usa principalmente como vehículo CSRF para el POST. Las tools se seleccionan via checkboxes manejados manualmente en la vista y el template. |
| `AnalysisToolForm` | ModelForm para `AnalysisTool`. No se usa en vistas (dead code). |
| `UploadFileForm` | Formulario simple con `FileField` para carga masiva de repositorios desde archivo de texto. |

### `python_code_analyzer_app/views.py` — Vistas

**Control de acceso incompleto**: `@login_required` protege casi todas las vistas, pero la verificación de ownership es parcial.

| Vista | ¿Verifica ownership? |
|---|---|
| `repositories` | Sí — filtra `Repository.objects.filter(owner=request.user)` |
| `repository` | Sí — `if repository.owner != request.user: raise Http404` |
| `new_repository` | Sí — asigna `new_repository.owner = request.user` |
| `delete_all_repositories` | Sí — filtra `Repository.objects.filter(owner=request.user)` |
| `new_analysis` | **No** — cualquier usuario autenticado puede crear análisis sobre repositorios ajenos |
| `analysis` | **No** — cualquier usuario autenticado puede ver resultados ajenos |
| `analysis_result` | **No** — cualquier usuario autenticado puede descargar ZIPs ajenos |
| `cancel_analysis` | **No** — cualquier usuario autenticado puede cancelar análisis ajenos |
| `delete_analysis` | **No** — cualquier usuario autenticado puede borrar análisis ajenos |
| `delete_repository` | **No** — cualquier usuario autenticado puede borrar repositorios ajenos |
| `delete_all_analyzes` | **No** — cualquier usuario autenticado puede borrar todos los análisis de repositorio ajeno |
| `massive_upload` | Sí — asigna `new_repository.owner = request.user` al crear repos |

La única vista pública (sin `@login_required`) es `index`. El resto requiere autenticación, pero la verificación de ownership post-autenticación es parcial como muestra la tabla.

### `python_code_analyzer_app/templates/` — Templates

`base.html` extiende Bootstrap 4 (tema oscuro) con modales de confirmación para delete. `analysis.html` incluye dinámicamente el template indicado por `item.plantilla` (chart_default.html, chart_matrix.html, indicator_default.html, indicator_rating.html). Los gráficos se renderizan con Chart.js 3.9.1 y chartjs-chart-matrix.

### `users/` — Autenticación

Registro, login y logout usando `django.contrib.auth`. Sin modelos propios. Tests vacíos (`users/tests.py` solo tiene un comentario).

---

## Seed data obligatoria

`Tools Insert.sql` debe ejecutarse después de `python manage.py migrate`. Inserta los tres registros en `python_code_analyzer_app_tool`:

| name | class_name |
|---|---|
| Pylint | Pylint_Tool |
| Vulture | Vulture_Tool |
| Radon | Radon_Tool |

Sin este paso la tabla de tools está vacía, `new_analysis` no muestra herramientas para seleccionar, y toda la aplicación es funcionalmente inútil.

---

## Testing

Los tests están en `python_code_analyzer_app/tests/`:

| Archivo | Contenido |
|---|---|
| `test_domain_models.py` | Tests de `Analysis.run()`, `CeleryTaskSignal.is_task_cancelled()` |
| `test_views.py` | Tests de vistas (index, repositories, analysis, delete, cancel) |
| `test_tasks.py` | Tests de tareas Celery (`excecute_analysis`, `launch_massive_upload`) |
| `test_tool_parsing.py` | Tests de parseo de resultados: Pylint (rating, charts), Vulture (unused items), Radon (LOC, CC, MI) |
| `test_result_items.py` | Tests de `ResultItem`, `Chart`, `IndicatorDefault`, `IndicatorRating` |
| `test_layout.py` | Tests de `LayoutManager.sort_by_multiple_criteria` con múltiples criterios |

Hay fixtures de prueba en `test_fixtures/` con salidas pre-capturadas de Pylint, Vulture y Radon.

**Ejecución**: `python manage.py test` (o con `--verbosity=2` para ver nombres). No hay configuración de cobertura (`.coveragerc`).

---

## Flujo de datos básico

```
Registrar repositorio → git clone (cuando se analiza)
        │
        ▼
Crear análisis (seleccionar tools)
        │
        ▼
[ Celery: excecute_analysis ] ─── ¿Repo ya en ejecución? → cancelar (status: CANCELLED)
        │
        ├─ ¿Señal de cancelación antes de start()? → abortar (status: PENDING)
        ├─ status = RUNNING
        ├─ ¿Señal de cancelación dentro de Analysis.run()? → aborta con return sin self.save() (bug: status queda RUNNING permanentemente)
        ├─ repository.download() → git clone (subprocess.call)
        ├─ get_last_commit() → hash commit (subprocess.run, también shell=True)
        ├─ analysis.run()
        │      └─ Por cada AnalysisTool:
        │           └─ tool_instance.run()
        │              ├─ try: ejecuta herramienta, guarda archivos
        │              ├─ except BaseException: solo imprime
        │              └─ finally: return FINISHED (siempre, incluso si falló)
        ├─ Empaqueta resultado en ZIP
        └─ status = FINISHED (o FAILED si la excepción escapó de run())

Descargar ZIP desde /analysis_result/<id>/
```

### Estructura de archivos en disco

```
{BASE_PATH}/                     → analyzer_data/
  {folder}/                      → repositorio clonado (git clone)
  {folder}_result/
    Analysis{id}/
      Pylint/result.json
      Vulture/result.txt
      Radon/result_cc.txt, result_mi.json, result_raw.json
    Analysis{id}.zip              → resultado comprimido descargable
```

Nota: `get_cc_charts()` de Radon intenta leer `result_cc.json`, pero `run()` escribe `result_cc.txt`. El chart de Cyclomatic Complexity nunca se genera.

---

## Dependencias externas

| Dependencia | Versión | Uso |
|---|---|---|
| Django | 4.0.3 | Framework web. 104 migraciones (0001 a 0104) para un modelo de datos pequeño, indicador de deuda técnica. |
| Celery | 4.4.2 | Cola de tareas asíncronas. Sin result backend (`CELERY_RESULT_BACKEND = None`). |
| RabbitMQ | — | Broker de Celery |
| pylint | 2.13.5 | Análisis de calidad de código |
| vulture | 2.3 | Detección de código muerto (in-process) |
| radon | 5.1.0 | Métricas: complejidad ciclomática, MI, raw |
| bootstrap4 | — | UI responsive |
| Chart.js | 3.9.1 | Gráficos en cliente |

---

## Decisiones de diseño inferidas del código

### Base de datos SQLite

Usa SQLite por defecto de Django. No hay evidencia de que se haya evaluado otro motor. Es adecuado para desarrollo local pero no para producción con múltiples usuarios concurrentes (contención de escritura). No hay configuración para PostgreSQL ni scripts de migración.

### Resultados en archivos, no en DB

Cada herramienta guarda su salida en el sistema de archivos como JSON o TXT. Solo los metadatos (estado, commit, task_id) van a la base de datos. Esto evita almacenar grandes volúmenes de datos JSON en SQLite y permite descargar los resultados completos como ZIP. Sin embargo, no hay migración de datos si cambia la estructura de directorios, y no hay límite de espacio configurado — si el disco se llena, las operaciones de escritura fallarán sin manejo explícito.

### Instanciación dinámica de herramientas

`Tool.get_instance()` busca la clase por nombre en `globals()` del módulo `Tool.py`. Alternativa más robusta sería un registry explícito (dict). El enfoque actual es frágil: renombrar una clase o moverla a otro módulo rompe la resolución sin error visible (retorna `None`).

### Multi-table inheritance compartiendo tabla

Las subclases `Pylint_Tool`, `Vulture_Tool`, `Radon_Tool` usan `managed = False` y `db_table = 'python_code_analyzer_app_tool'`. Esto simula multi-table inheritance sobre una sola tabla: todas las subclases comparten la misma fila en DB y solo se diferencian por el `class_name` y el discriminante implícito. Alternativa: un simple `CharField` con nombre de herramienta y un dispatch explícito.

### `subprocess.call` vs `subprocess.run`

`Repository.download()` usa `subprocess.call()` (bloquea, retorna exit code). Las tools usan `subprocess.run()` (retorna `CompletedProcess`). Ambas APIs coexisten sin un criterio unificado.

### Colas de Celery

La tarea `launch_massive_upload` se encola en `repository_queue`, separada de la cola por defecto donde va `excecute_analysis`. Sin un worker Celery escuchando `repository_queue` (`-Q repository_queue`), los trabajos de carga masiva se quedan encolados indefinidamente (no hay timeout que los elimine).

---

## Puntos de cuidado al modificar código

### Parser de Pylint solo captura conventions
`Pylint_Tool._toJson()` solo chequea `elif line.startswith('C:')`. Los mensajes de tipo Warning (`W:`), Error (`E:`), Refactor (`R:`) y Fatal (`F:`) se descartan silenciosamente. El `_getType()` puede clasificar todos los tipos, pero nunca se llama para líneas que no empiecen con `C:`. Esto es un bug activo: los únicos detalles que aparecen en los resultados de Pylint son los de convention.

### Ownership checks incompletos
La mayoría de las vistas no verifican que el recurso pertenezca al usuario autenticado. Ver tabla en la sección de vistas.

### `get_cc_charts()` roto y `get_raw_charts()` huérfano
`Radon_Tool.run()` escribe `result_cc.txt`, pero `Radon_Tool.get_cc_charts()` intenta leer `result_cc.json`. El archivo nunca existe, el chart de Cyclomatic Complexity nunca se genera y no hay indicación de error.

Además, `Radon_Tool.get_charts()` solo invoca `get_cc_charts()` y `get_mi_charts()`. `get_raw_charts()` está definido y funciona correctamente (lee `result_raw.json` que sí se genera), pero nunca es llamado. El chart de Raw Metrics tampoco se muestra.

### Tools siempre retornan FINISHED + except BaseException
Las tres herramientas (`Pylint_Tool`, `Vulture_Tool`, `Radon_Tool`) envuelven su ejecución en `try/finally` y retornan `tools_status.FINISHED` en el `finally`. Si ocurre una excepción, solo se imprime y la tool igual reporta éxito. La flag `failed` en `Analysis.run()` nunca se activa, por lo que el FINISHED/FAILED de un análisis siempre es FINISHED a menos que la excepción escape completamente de `run()`.

Además, los cinco bloques `except` en las tools y en `TaskManager` usan `except BaseException`, que captura `KeyboardInterrupt`, `SystemExit` y `GeneratorExit` además de excepciones normales. En `TaskManager.excecute_analysis`, el handler tiene un segundo `try/except BaseException: pass` anidado (para el recovery de setear FAILED), que puede tragar errores silenciosamente.

### Analysis.run() no guarda estado al cancelar
Cuando `CeleryTaskSignal.is_task_cancelled()` retorna `True`, `Analysis.run()` hace `return` sin llamar a `self.save()`. El análisis queda en estado RUNNING permanentemente. Nótese la diferencia con los retornos tempranos en `TaskManager.excecute_analysis()`: esos ocurren antes de `analysis.start()`, por lo que el status sigue siendo PENDING. Solo el `return` dentro de `Analysis.run()` (después de `start()`) deja el estado en RUNNING trabado.

### `date_finished` con `auto_now=True` es semánticamente incorrecto
`Analysis.date_finished` usa `auto_now=True`, que actualiza el campo en cada `save()` del modelo. Al llamarse en `start()`, `set_commit()`, `cancel()` y `run()`, el timestamp no representa el momento en que el análisis terminó, sino la última vez que se guardó el registro. Si un análisis se cancela, `date_finished` queda con el timestamp de la cancelación. El campo no es confiable para consultas.

### Analysis.run() no genera ZIP cuando falla
Cuando `failed=True` (cualquier tool retorna distinto de FINISHED), el status se setea a FAILED pero no se genera el ZIP. La vista `analysis_result` no encontrará archivo para descargar. Esto es esperable pero no está documentado en la UI.

### AnalysisTool.run() retorna FAILED sin persistir cuando get_instance() falla
Cuando `Tool.get_instance()` retorna `None` (clase no encontrada), `AnalysisTool.run()` retorna `tools_status.FAILED` pero no actualiza `self.status` ni persiste el cambio. El registro en DB queda como PENDING mientras el caller recibe FAILED.

### `launch_massive_upload` no deduplica análisis
Por cada URL del archivo se crea un `Analysis` nuevo sin verificar si ya existe uno para ese repositorio y commit. Subir el mismo archivo dos veces crea análisis duplicados.

### `launch_massive_upload` no tiene try/except por URL
Si una URL individual falla (repo inválido, error de base de datos, etc.), la excepción propaga y aborta el procesamiento de las URLs restantes del archivo. No hay aislamiento por iteración.

### `launch_massive_upload` no implementa cancelación
Hay un `TODO` comment en la línea 67 (`# TODO: chequear si la tarea no esta cancelada`) pero nunca se implementó. A diferencia de `excecute_analysis`, que chequea `CeleryTaskSignal.is_task_cancelled()` entre pasos, `launch_massive_upload` no verifica si fue cancelada y procesa todas las URLs del archivo sin posibilidad de interrupción.

### `cancel_analysis` y views de delete crashean sin header `HTTP_REFERER`
`cancel_analysis` (line 151), `delete_analysis` (line 159), `delete_repository` (line 167), `delete_all_analyzes` (line 176) y `delete_all_repositories` (line 184) usan `request.META['HTTP_REFERER']` con subscript directo en lugar de `.get()`. Si el header `Referer` no está presente (request directo, curl, etc.), esto lanza `KeyError` y retorna un 500. El patrón correcto sería `request.META.get('HTTP_REFERER', '/')`.

### `get_cc_charts()` tiene bug lógico además del bug de extensión
`Radon_Tool.get_cc_charts()` en la línea 363 chequea `if "rank" in values:`, donde `values` es una lista de dicts. Esto evalúa si el string `"rank"` es elemento de la lista (siempre `False`). Debería ser `if "rank" in value:` (el dict individual). Incluso si el bug de extensión se arreglara (`.json` en vez de `.txt`), el chart de Cyclomatic Complexity siempre mostraría ceros.

### `format = "zip"` sombrea el built-in `format()`
`Analysis.run()` asigna `format = "zip"`, que sombrea la función `format()` de Python. No causa bugs (no se usa `format()` después), pero es un code smell.

### Inconsistencia en construcción de paths
`Repository.path` usa `os.path.join()`, pero `Repository.delete_files()` y `Analysis.path_result` / `path_to_zip` concatenan strings manualmente (`.path+"_result"` y `f"_result/Analysis{self.id}/"`). Si `Repository.path` cambiara para incluir un separador final, las concatenaciones producirían paths inválidos.

### `shell=True` en comandos del sistema
`Repository.download()`, `Repository.get_last_commit()`, `Pylint_Tool.run()` y `Radon_Tool.run()` usan `shell = True`. La URL del repositorio no se valida antes de pasarla a `git clone`, lo que permite inyección de comandos.

### Mecanismo de cancelación vía polling
`CeleryTaskSignal.is_task_cancelled()` hace UPDATE con `completed=False` y retorna si afectó filas. Las tasks chequean esto entre pasos. Si se agregan pasos nuevos sin chequeo, la cancelación puede ignorarse.

### Query duplicado en repository view
`views.py` (vista `repository`) ejecuta `repository.analysis_set.order_by('-date_added')` en la línea 39 (resultado que se descarta) y nuevamente en la línea 40 para el `Paginator`. La primera query es desperdiciada.

### `analysis_result` docstring incorrecto
La vista `analysis_result` (views.py:128) tiene el docstring `"Show a single analysis detail"` — idéntico al de `analysis`. En realidad descarga un ZIP con `HttpResponse` y content-type `force-download`. El docstring es engañoso.

### `path_result` y `path_to_zip` hacen query a DB cada vez
Ambas propiedades ejecutan `Repository.objects.get(id=self.repository_id)` en cada acceso. En `Analysis.run()` se acceden múltiples veces sin caching.

### Vulture hardcodea 6 tipos de mensajes
`Vulture_Tool.get_charts()` define manualmente `messages = ["unused method", "unused variable", ...]`. Si Vulture agrega nuevos tipos de código muerto, no aparecerán en el chart.

### Pylint escribe a disco y luego relee
`Pylint_Tool.run()` redirige stdout de pylint a un archivo `.txt` y luego `_toJson()` lo relee del disco para parsearlo a JSON. Podría capturarse stdout directamente con `subprocess.run(..., capture_output=True)`.

### No hay rate limiting ni validación de URLs
`Repository.download()` pasa la URL directamente a `git clone` sin validación. Cualquier URL maliciosa o inexistente se ejecuta. No hay límite de repositorios por usuario.

### `Repository.folder` default evaluado en import time
`folder = models.CharField(default=datetime.now().strftime(...))` — el `default` es un string evaluado una sola vez al importar el módulo, no una función invocada por fila. Todos los repositorios creados sin `folder` explícito en el mismo proceso Django reciben el mismo timestamp. `massive_upload` asigna `folder` explícitamente, pero `new_repository` no.

### `task_id` y `status_msg` usan strings `'null'` como default
`Analysis.task_id` tiene `default='null'` (string literal) y `Analysis.status_msg` tiene `default='null'`. No son `None` ni `models.NULL`, sino strings de 4 caracteres. Cualquier código que compare con `None` o use truthiness fallará. Por ejemplo, `if analysis.task_id` sería `True` incluso para análisis sin tarea asignada, porque `'null'` es truthy.

### Vulture hardcodea label con typo "# of Usused Items"
`Vulture_Tool.get_indicators()` (Tool.py:307) usa `IndicatorDefault("vulture-unused-items", "# of Usused Items", ...)`. El typo "Usused" en vez de "Unused" aparece en la UI del usuario.

### Vulture in-process vs subprocess
Vulture se ejecuta in-process (`vulture.Vulture().scavenge()`) mientras Pylint y Radon se ejecutan como subprocess. Diferencias en manejo de memoria, errores y aislamiento.

### Tipografía `excecute_analysis`
El nombre de la tarea Celery tiene typo: `excecute` en vez de `execute`. Aparece en `TaskManager.py` y en `views.py`. Si se renombra, tasks encoladas con el nombre antiguo perderían su destino.

### Métodos dead code
- `PAUSE_TASK`: definido en `CeleryTaskSignal` pero nunca utilizado.
- `was_excecuted()`: definido en `Analysis`, tiene tests, pero nunca se llama en producción.
- `mark_completed()`: definido en `CeleryTaskSignal`, no se usa en el flujo de cancelación (el `is_task_cancelled` usa `update` directamente).
- `AnalysisToolForm`: importado pero nunca instanciado.
- `get_raw_charts()`: definido en `Radon_Tool`, funciona correctamente, pero `get_charts()` nunca lo invoca.
- `AnalysisTool.get_charts()` y `AnalysisTool.get_indicators()`: definidos en `AnalysisTool`, pero `get_result()` llama directamente a `instancia.get_result()` del Tool, no a estos métodos. Sólo se usarían si alguien los invocara explícitamente.
- `AnalysisTool.status`: el campo se actualiza en `run()` (line 17-18) pero ningún código lo consulta posteriormente.

### Archivos temporales sin limpieza
`massive_upload` crea archivos `{BASE_PATH}/massive_{userId}_{uuid}.txt` que `launch_massive_upload` lee pero nunca elimina.

### Paths Windows en Radon
`Radon_Tool.get_mi_charts()` y `get_raw_charts()` usan `rsplit('\\', 1)` para extraer nombres de archivo del JSON. En Linux esto no funciona.

### Gestión de logging inexistente
Todo el código usa `print()` en lugar de logging estructurado. No hay `logging.getLogger()` en ningún módulo.

### Debtas técnicas observables
- 104 migraciones (0001 a 0104) para un modelo de datos pequeño.
- Sin Docker / docker-compose (solo `readme.txt` con instrucciones manuales).
- Sin REST API (toda la interacción es server-side rendering).
- Sin configuración de cobertura de tests.
