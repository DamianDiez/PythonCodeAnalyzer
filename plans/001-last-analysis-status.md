# Plan de implementación — 001-last-analysis-status.md

## Enfoque técnico

Separar en dos responsabilidades claras dentro de `Repository`:

1. **`last_analysis`** — retorna el objeto `Analysis` más reciente (o `None`).
2. **`last_analysis_badge`** — traduce el estado del análisis a `(texto, clase_css)` usando un dict lookup. Esto es un método estático o función auxiliar, no depende del `self` del repo (solo del status).

En el template se llama a `repo.last_analysis_badge`.

---

## Tarea 1 — Tests de la property `last_analysis` (~20 min)

**Objetivo:** Definir el contrato de la property `last_analysis` antes de implementarla.

**Archivos a modificar:**
- `python_code_analyzer_app/tests/test_domain_models.py`

**Tests:**

| Test | Escenario |
|---|---|
| `test_repo_without_analysis_returns_none` | Repo sin análisis → `None` |
| `test_repo_with_single_analysis_returns_it` | Repo con 1 análisis → ese análisis |
| `test_repo_with_multiple_analyses_returns_most_recent` | Repo con 3 análisis de fechas distintas → el de `date_added` más grande |
| `test_repo_with_analysis_in_different_states` | Los análisis tienen distintos statuses; retorna el del más reciente, no el de mejor estado |

**Dependencias:** Ninguna.

**Riesgos:** Ninguno. Solo se leen archivos existentes para entender el patrón de tests.

---

## Tarea 2 — Implementar `last_analysis` en Repository (~15 min)

**Objetivo:** Hacer pasar los tests de la Tarea 1.

**Archivos a modificar:**
- `python_code_analyzer_app/app_models/Repository.py` — agregar property `last_analysis`:
  ```python
  @property
  def last_analysis(self):
      return self.analysis_set.order_by('-date_added').first()
  ```

**Dependencias:** Tarea 1.

**Riesgos:**
- N+1 queries al iterar repos en el template. Con 8 items/página es despreciable.
- No requiere migración (es una property, no un campo de DB).

---

## Tarea 3 — Tests de la property `last_analysis_badge` (~20 min)

**Objetivo:** Definir el contrato de la función de mapeo status → badge.

**Archivos a modificar:**
- `python_code_analyzer_app/tests/test_domain_models.py`

**Tests:**

| Test | Entrada | Salida esperada |
|---|---|---|
| `test_badge_sin_analisis` | `None` | `('Sin análisis', 'badge-light')` |
| `test_badge_pending` | `PENDING` | `('Pendiente', 'badge-secondary')` |
| `test_badge_running` | `RUNNING` | `('En ejecución', 'badge-primary')` |
| `test_badge_finished` | `FINISHED` | `('Finalizado', 'badge-success')` |
| `test_badge_failed` | `FAILED` | `('Fallido', 'badge-danger')` |
| `test_badge_cancelled` | `CANCELLED` | `('Cancelado', 'badge-warning')` |

**Dependencias:** Ninguna.

**Riesgos:** Ninguno.

---

## Tarea 4 — Implementar `last_analysis_badge` en Repository (~15 min)

**Objetivo:** Hacer pasar los tests de la Tarea 3.

**Archivos a modificar:**
- `python_code_analyzer_app/app_models/Repository.py` — agregar property `last_analysis_badge` que delega en `self.last_analysis` y aplica el dict de mapeo.

**Lógica:**

```python
BADGE_MAP = {
    tools_status.PENDING:    ('Pendiente', 'badge-secondary'),
    tools_status.RUNNING:    ('En ejecución', 'badge-primary'),
    tools_status.FINISHED:   ('Finalizado', 'badge-success'),
    tools_status.FAILED:     ('Fallido', 'badge-danger'),
    tools_status.CANCELLED:  ('Cancelado', 'badge-warning'),
}

@property
def last_analysis_badge(self):
    analysis = self.last_analysis
    if analysis is None:
        return ('Sin análisis', 'badge-light')
    return self.BADGE_MAP.get(analysis.status, ('Sin análisis', 'badge-light'))
```

`BADGE_MAP` como class-level dict (no instance), para no redefinirlo por cada repo.

**Dependencias:** Tarea 3, Tarea 2.

**Riesgos:** Ninguno.

---

## Tarea 5 — Tests de la vista `repositories` con badge (~25 min)

**Objetivo:** Verificar que la vista renderiza el badge correctamente en el HTML de respuesta.

**Archivos a modificar:**
- `python_code_analyzer_app/tests/test_views.py` — agregar tests en `RepositoriesViewTest`

**Tests:**

| Test | Verificación |
|---|---|
| `test_repositories_shows_badge_for_repo_with_finished_analysis` | `assertContains(response, "badge-success")` y `assertContains(response, "Finalizado")` |
| `test_repositories_shows_badge_without_analysis` | `assertContains(response, "badge-light")` y `assertContains(response, "Sin análisis")` |
| `test_repositories_shows_most_recent_status_over_older` | Con análisis PENDING (viejo) y RUNNING (nuevo) → badge `En ejecución`, no `Pendiente` |
| `test_repositories_badge_on_second_page` | 9 repos (8 en page 1, 1 en page 2) → GET `?page=2` → badge visible en el repo de page 2 |

**Dependencias:** Tareas 2 y 4 (implementación del modelo).

**Riesgos:**
- Test de paginación: requiere crear 9 repos + análisis para forzar segunda página.
- Seguir el patrón existente de `setUp` con `User.objects.create_user` + `self.client.login`.

---

## Tarea 6 — Actualizar template `repositories.html` (~15 min)

**Objetivo:** Agregar columna "Status" con badge entre "Url" y "Actions".

**Archivos a modificar:**
- `python_code_analyzer_app/templates/python_code_analyzer_app/repositories.html`

**Cambios:**

1. `<thead>`: agregar `<th>Status</th>` después de `<th>Url</th>`.
2. `<tbody>`, dentro del `{% for repo in repositories %}`:
   ```html
   <td>
       {% with badge=repo.last_analysis_badge %}
       <span class="badge {{ badge.1 }}">{{ badge.0 }}</span>
       {% endwith %}
   </td>
   ```
3. `<tbody>` del `{% empty %}`: cambiar `colspan="3"` → `colspan="4"`.

**Dependencias:** Tareas 2 y 4.

**Riesgos:**
- Los classes `badge-*` de Bootstrap 4 ya están disponibles vía `{% bootstrap_css %}`.
- No romper el layout existente de la tabla.

---

## Tarea 7 — Verificación y self-review (~15 min)

**Objetivo:** Ejecutar tests completos y hacer una revisión manual del cambio.

**Acciones:**

1. Ejecutar `python manage.py test`.
2. Self-review:

| Pregunta | Criterio |
|---|---|
| ¿Se respetó la spec? | Columna entre Url y Actions; mapeo de estados; badge no es clickeable; sin cambios al modelo de datos ni al flujo de análisis |
| ¿Se modificaron archivos innecesariamente? | Solo `Repository.py`, `repositories.html`, `test_domain_models.py`, `test_views.py` |
| ¿Hay código duplicado? | El dict `BADGE_MAP` está en un solo lugar; no se repite lógica de mapeo |
| ¿Hay oportunidades de simplificación? | Verificar que la property `last_analysis` no se llama dos veces por repo en el template |
| ¿Los tests existentes pasan? | `python manage.py test` sin fallos nuevos |

**Dependencias:** Todas las anteriores.

**Riesgos:**
- Tests que fallaban antes del cambio (bugs conocidos). Documentar cuáles eran preexistentes.

---

## Resumen

| # | Tarea | Duración | Dependencias |
|---|---|---|---|
| 1 | Tests de `last_analysis` | ~20 min | — |
| 2 | Implementar `last_analysis` | ~15 min | T1 |
| 3 | Tests de `last_analysis_badge` | ~20 min | — |
| 4 | Implementar `last_analysis_badge` | ~15 min | T2, T3 |
| 5 | Tests de la vista con badge | ~25 min | T2, T4 |
| 6 | Actualizar template | ~15 min | T2, T4 |
| 7 | Verificación y self-review | ~15 min | T1–T6 |
| | **Total estimado** | **~125 min** | |

## Archivos que se modifican

| Archivo | Tarea | Motivo |
|---|---|---|
| `app_models/Repository.py` | T2, T4 | Agregar properties `last_analysis` y `last_analysis_badge` |
| `templates/.../repositories.html` | T6 | Columna Status con badge |
| `tests/test_domain_models.py` | T1, T3 | Tests de ambas properties |
| `tests/test_views.py` | T5 | Tests de vista con badge |

## Archivos que NO se modifican

- `Analysis.py` — sin cambios al modelo ni lógica de análisis
- `tools_status.py` — las constantes ya son correctas
- `views.py` — la vista `repositories` no necesita cambios
- `TaskManager.py` — sin cambios al flujo de ejecución
- Migraciones — no hay cambios al schema de la base de datos
