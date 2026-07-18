# Engineering Guidelines

## 1. Objetivo

Este documento define las reglas de ingeniería que guían todo el ciclo de desarrollo de features en el proyecto. Aplica desde la planificación inicial hasta la integración final, cubriendo especificación, diseño del plan, implementación, testing y revisión de código.

Sirve como fuente de verdad para todas las sesiones de trabajo. Cualquier persona que planifique, implemente o revise una feature debe seguir estas directrices.

Si una especificación de feature contradice este documento, la especificación tiene prioridad para esa feature. Las guidelines definen el marco general; la spec define el alcance concreto.

---

## 2. Reglas obligatorias y recomendaciones

Las reglas de este documento se expresan con distintos niveles de formalidad:

- **Obligatorias:** Las reglas formuladas con "debe", "no debe" y "siempre" son de cumplimiento obligatorio. No admiten excepciones salvo que el documento lo indique explícitamente.
- **Recomendaciones:** Las reglas formuladas con "preferir", "cuando sea viable", "como guía general" o expresiones similares son recomendaciones que pueden adaptarse según la naturaleza de la feature, el contexto técnico o las restricciones del proyecto. Deben justificarse cuando no se sigan.

---

## 3. Alcance

Estas guidelines aplican a todas las features desarrolladas en este proyecto y cubren:

* elaboración y revisión de especificaciones;
* elaboración y revisión de planes de implementación;
* implementación;
* testing;
* code review.

Este documento define principios generales de ingeniería. Las especificaciones de cada feature pueden complementar estas reglas, pero no deberían contradecirlas.

---

## 4. Prioridad de documentos

Cuando existan reglas en múltiples documentos, el orden de precedencia es el siguiente:

1. **Especificación de la feature.** Máxima prioridad. Define el alcance concreto y los requisitos que debe cumplir la implementación.
2. **docs/architecture.md.** Describe la estructura actual del sistema, componentes, modelos y decisiones de diseño existentes.
3. **docs/engineering-guidelines.md.** Establece principios generales de ingeniería, procesos y estándares de calidad.
4. **AGENTS.md.** Instrucciones operativas para sesiones de trabajo.

Un documento de menor prioridad nunca debe contradecir uno de mayor prioridad. Si existe un conflicto, prevalece el documento con mayor precedencia.

---

## 5. Principios Generales

Todo el desarrollo se rige por estos principios:

- **Simplicidad sobre sofisticación.** Preferir la solución más simple que funcione. No agregar abstracciones, patrones o mecanismos que no resuelvan un problema real e inmediato.

- **Cambios pequeños e incrementales.** Dividir el trabajo en unidades mínimas verificables. Evitar macros-features que dificultan el review, el testing y el rollback.

- **Consistencia permanente.** El proyecto debe funcionar en todo momento. No commitear código que rompa tests existentes, que deje el sistema en estado inconsistente o que requiera pasos manuales no documentados para recuperar la funcionalidad.

- **Evitar deuda técnica innecesaria.** No introducir atajos que generen problemas futuros. Si un cambio requiere un refactor previo para ser implementado correctamente, ese refactor debe formar parte del plan.

- **No agregar funcionalidades fuera del alcance.** Implementar exclusivamente lo que la spec define. Si durante la implementación se descubre una mejora posible, documentarla como task separada para abordarla después.

- **No modificar comportamiento existente salvo que la spec lo requiera.** El código que funciona no debe ser alterado. Si un refactor o cambio de comportamiento es necesario para la feature, debe estar explicitado en la especificación o en el plan aprobado.

- **Mínimo impacto.** Toda implementación debe minimizar el impacto sobre el código existente. Antes de modificar componentes estables, debe evaluarse si la funcionalidad puede agregarse mediante cambios localizados que no alteren la estructura ni el comportamiento previo del sistema.

---

## 6. Roles y Responsabilidades

Cada etapa del proceso tiene un rol asignado con un alcance definido. La separación de responsabilidades evita que un rol invada el territorio de otro.

### 6.1 Spec Editor

**Objetivo:** Redactar una especificación clara, completa y sin ambigüedades.

- Define el objetivo, el contexto, los requisitos funcionales, los no objetivos y los criterios de aceptación.
- Asegura que cada requisito tenga al menos un criterio de aceptación asociado.
- Verifica que no existan contradicciones entre secciones.
- Indica los archivos posiblemente afectados (opcional).

**No debe:**
- Incluir detalles de implementación.
- Proponer soluciones técnicas o arquitectónicas.
- Definir nombres de clases, métodos o atributos.

### 6.2 Spec Reviewer

**Objetivo:** Detectar problemas funcionales en la especificación antes de que se invierta tiempo en planificar o implementar.

- Evalúa ambigüedades, contradicciones, comportamientos no definidos y edge cases.
- Verifica la consistencia entre Objetivo, Contexto, Requisitos, No Objetivos y Criterios de Aceptación.
- Comprueba que cada requisito funcional tenga al menos un criterio de aceptación que lo valide.
- Comprueba que no existan criterios de aceptación que agreguen comportamiento no definido en los requisitos.
- Comprueba que todos los escenarios importantes tengan cobertura en los criterios de aceptación.
- Clasifica las observaciones por severidad (crítica, mayor, menor).

**No debe:**
- Revisar implementación, diseño interno o decisiones de arquitectura existentes.
- Proponer refactors o mejoras de código.
- Revisar nombres de clases, métodos o variables.

### 6.3 Plan Editor

**Objetivo:** Traducir la spec aprobada en un conjunto de tareas concretas, verificables y ordenadas.

- Divide el trabajo en tareas pequeñas e independientes.
- Define objetivo, archivos afectados, dependencias y riesgos para cada tarea.
- Ordena las tareas para minimizar el riesgo de regresiones.
- Asegura que cada tarea deje el proyecto en un estado consistente.

**No debe:**
- Agregar funcionalidades que no estén en la spec.
- Proponer cambios de arquitectura no requeridos.
- Mezclar responsabilidades en una misma tarea.

### 6.4 Plan Reviewer

**Objetivo:** Evaluar la viabilidad y calidad del proceso de implementación propuesto.

- Verifica la separación de responsabilidades entre tareas.
- Evalúa el tamaño de cada tarea.
- Valida que el orden de implementación minimice regresiones.
- Comprueba que los tests aparezcan en un momento adecuado del plan.
- Valida que cada tarea deje el proyecto en un estado consistente.
- Comprueba que sea posible hacer un commit al finalizar cada tarea.
- Verifica que una tarea pueda revertirse sin romper el resto del trabajo.
- Evalúa si las dependencias, riesgos y estrategia de testing están bien definidos.

**No debe:**
- Proponer implementación alternativa.
- Reescribir el plan.
- Cuestionar decisiones de arquitectura existentes.

### 6.5 Implementador

**Objetivo:** Ejecutar el plan aprobado respetando la spec, la arquitectura y las convenciones del proyecto.

- Sigue exactamente los requisitos de la spec.
- Implementa tarea por tarea, en el orden definido por el plan.
- Ejecuta los tests después de cada tarea.
- Mantiene el proyecto en un estado funcional en todo momento.

**No debe:**
- Agregar funcionalidades fuera del alcance de la spec.
- Modificar comportamiento existente sin que la spec lo requiera.
- Hacer refactors no planificados.
- Commitear código que rompa tests existentes.

### 6.6 Code Reviewer

**Objetivo:** Verificar que el código cumple la spec, es correcto, legible y no introduce regresiones.

- Evalúa cumplimiento de la spec, simplicidad, legibilidad, bugs y cobertura de tests.
- Verifica consistencia con la arquitectura y convenciones del proyecto.
- Detecta posibles regresiones o efectos colaterales.

**No debe:**
- Solicitar refactors innecesarios.
- Imponer preferencias personales de estilo.
- Bloquear un merge por diferencias de opinión que no afecten la funcionalidad.

---

## 7. Especificaciones (Specs)

La especificación es el punto de partida de toda feature. Define qué debe hacer el sistema sin detallar cómo se logrará.

### 7.1 Estructura requerida

Toda spec debe contener, como mínimo:

| Sección | Descripción |
|---|---|
| **Objetivo** | Qué problema resuelve la feature. Una oración clara y concisa. |
| **Contexto** | Información relevante para entender el problema: estado actual, restricciones, dependencias. |
| **Requisitos funcionales** | Qué debe hacer el sistema. Lista de comportamientos esperados, ordenados y sin ambigüedad. |
| **No objetivos** | Qué NO se incluye en esta feature. Debe ser explícito para evitar scope creep durante la implementación. |
| **Criterios de aceptación** | Condiciones verificables que deben cumplirse para considerar la feature completa. Cada criterio debe ser testeable de forma independiente. |
| **Archivos posiblemente afectados** | (Opcional) Lista orientativa de módulos, modelos, vistas o templates que la feature podría impactar. Útil para el plan pero no es definitiva. |

### 7.2 Reglas de redacción

- La spec describe **qué**, nunca **cómo**. No debe incluir detalles de implementación.
- Debe ser suficientemente precisa para que un implementador pueda trabajar sin interpretar requisitos ambiguos.
- Los criterios de aceptación deben poder verificarse con tests o con observación directa del comportamiento.
- Si un requisito depende de otro, establecer la relación explícitamente.
- Los requisitos funcionales y los criterios de aceptación deben describir únicamente comportamiento observable del sistema y no depender de detalles de implementación.

### 7.3 Prohibido en una spec

- Detalles de implementación (librerías, frameworks, herramientas específicas)
- Algoritmos o estructuras de datos
- Nombres de métodos, clases o atributos
- Patrones de diseño
- Refactors del código existente
- Decisiones de arquitectura nuevas

Estos elementos corresponden a la fase de plan e implementación, no a la especificación.

---

## 8. Revisión de Specs

El reviewer de una spec debe evaluar exclusivamente la calidad funcional del documento. El objetivo es detectar problemas antes de que se invierta tiempo en implementar algo incompleto o ambiguo.

### 8.1 Qué buscar

| Tipo de problema | Ejemplo |
|---|---|
| Ambigüedad | "El sistema debe responder rápido" — ¿cuánto es rápido? |
| Contradicción | Un requisito dice que el campo es obligatorio; otro dice que es opcional. |
| Comportamiento no definido | ¿Qué pasa si el usuario cancela durante el procesamiento? |
| Edge cases relevantes | ¿Qué ocurre con entradas vacías, límites extremos, errores de red? |
| Criterios de aceptación incompletos | Falta validar un escenario descrito en los requisitos. |
| Requisitos inconsistentes | Dos requisitos apuntan a resultados incompatibles. |

Una **ambigüedad** existe únicamente cuando dos implementadores razonables podrían producir comportamientos funcionales distintos cumpliendo literalmente la especificación. Diferencias de estilo, implementación o estructura interna no constituyen ambigüedades funcionales.

Un **edge case relevante** es aquel que:

- produce un comportamiento observable distinto;
- puede cambiar el resultado funcional;
- impide implementar correctamente la feature.

Detalles internos de implementación, límites técnicos del modelo, optimizaciones o restricciones del código existente no constituyen edge cases funcionales salvo que la spec los mencione explícitamente.

### 8.2 Consistencia entre secciones

El reviewer debe comprobar además:

- Que cada requisito funcional tenga al menos un criterio de aceptación que lo valide.
- Que no existan criterios de aceptación que agreguen comportamiento no definido en los requisitos.
- Que todos los escenarios importantes tengan cobertura en los criterios de aceptación.
- Que exista consistencia entre Objetivo, Contexto, Requisitos, No Objetivos y Criterios de Aceptación.

### 8.3 Criterio para reportar observaciones

Antes de reportar una observación, el reviewer debe evaluar si realmente produce una diferencia funcional. Antes de reportar una observación el reviewer debe responder:

- ¿Dos implementadores razonables podrían implementar comportamientos distintos siguiendo la spec?
- ¿La diferencia afecta el comportamiento observable?
- ¿El problema puede verificarse mediante un criterio de aceptación?
- ¿La observación pertenece realmente a la revisión funcional y no a implementación, arquitectura o code review?

Si alguna respuesta es negativa, la observación normalmente no debe reportarse.

### 8.4 Qué NO revisar

- Implementación del código
- Refactors o mejoras de estructura
- Diseño interno
- Nombres de clases, métodos o variables
- Decisiones de arquitectura existentes
- Rendimiento (salvo que sea un requisito explícito de la spec)

### 8.5 Fuera del alcance de una revisión

Los siguientes aspectos no deben ser sugeridos en una revisión de spec salvo que la spec los requiera explícitamente:

- Refactors
- Mejoras de arquitectura
- Deuda técnica
- Cambios de naming
- Optimizaciones
- Mejoras de performance
- Internacionalización
- Accesibilidad
- Cambios de estilo
- Mejoras futuras

### 8.6 Formato de feedback

Toda observación debe clasificarse por severidad:

| Severidad | Cuándo aplicar |
|---|---|
| **Crítica** | Impide implementar correctamente la feature. Produce un comportamiento incorrecto. Debe resolverse antes de continuar. |
| **Mayor** | Puede producir implementaciones funcionalmente distintas. Puede dejar requisitos sin validar. Debería resolverse antes del plan. |
| **Menor** | Mejora la claridad o completitud. No cambia el comportamiento observable. Puede resolverse posteriormente. |

---

## 9. Plan de Implementación

El plan traduce la spec en pasos concretos y verificables. Es un documento de trabajo que facilita la implementación, el review y el testing.

### 9.1 Estructura de cada tarea

Cada tarea del plan debe especificar:

| Campo | Descripción |
|---|---|
| **Objetivo** | Qué logra esta tarea en una oración. |
| **Archivos afectados** | Qué archivos se crearán, modificarán o eliminarán. |
| **Dependencias** | Qué tareas deben completarse antes. |
| **Riesgos** | Qué podría fallar o qué efectos colaterales podría tener. |

### 9.2 Características de una buena tarea

- **Un solo objetivo.** No mezclar responsabilidades que puedan separarse.
- **Pocos archivos.** Una tarea típica afecta entre 1 y 4 archivos.
- **Independiente.** Puede completarse y testearse de forma aislada.
- **Fácil de revisar.** Un reviewer puede evaluarla en menos de 30 minutos.
- **Commit independiente.** Cada tarea genera un commit que deja el proyecto en estado funcional.

### 9.3 Reglas adicionales

- Si una tarea crece más de lo esperado, dividirla en subtareas.
- Las dependencias deben ser explícitas, no implícitas.
- Los riesgos deben ser realistas y no teóricos.
- Si una tarea requiere un cambio de comportamiento existente, debe indicarlo explícitamente.
- Una tarea no debe combinar implementación de la feature, refactors, limpieza de código y mejoras no relacionadas. Cada tarea debe perseguir un único objetivo funcional.

### 9.4 Orden recomendado de las tareas

Cuando sea posible, el plan debería seguir aproximadamente este orden:

1. **Preparación / refactor necesario.** Migraciones, configuraciones, modelos base, fixtures, o refactors que habiliten la feature.
2. **Tests.** Escribir o adaptar tests. Test first cuando sea viable.
3. **Implementación del dominio.** Modelos, reglas de negocio, lógica pura.
4. **Implementación de servicios / lógica.** Tareas Celery, procesamiento, integraciones.
5. **Implementación de interfaz.** Vistas, templates, formularios.
6. **Limpieza.** Eliminar código muerto temporal, verificar imports, revisar consistencia.
7. **Ejecución de toda la suite de tests.** Verificar que nada se rompió.

Este orden puede variar dependiendo de la naturaleza de la feature, pero debe justificarse cuando cambie significativamente.

---

## 10. Testing

El testing es parte integral del desarrollo, no una actividad posterior.

### 10.1 Principios

- **Test First cuando sea viable.** Definir los tests antes de la implementación fuerza a pensar en la interfaz pública del código y reduce el acoplamiento.
- **Validar comportamiento observable.** Los tests deben verificar qué hace el sistema, no cómo lo hace internamente.
- **Evitar acoplamiento a detalles internos.** Si un test rompe al refactorizar pero el comportamiento externo es el mismo, el test estaba mal diseñado.
- **Ejecutar regresión completa antes de finalizar.** Todo el suite de tests existente debe pasar después de cada cambio.

### 10.2 Cobertura

- Toda funcionalidad nueva debe quedar cubierta por tests.
- Los tests existentes deben seguir pasando después de cada cambio.
- Si un cambio requiere modificar tests existentes, esos cambios deben incluirse en la misma tarea.

### 10.3 Calidad

- Reutilizar fixtures existentes cuando sea posible.
- Evitar duplicación de setup y datos de prueba.
- Mantener nombres descriptivos que comuniquen la intención del test.
- Un test debe validar un único comportamiento.
- No testear implementación; testear resultado observable.
- Mantener los tests limpios y legibles, como código de producción.
- Los tests deben escribirse al nivel adecuado (unidad, integración o vista según corresponda), priorizando validar comportamiento y evitando duplicar innecesariamente la misma cobertura en distintos niveles.

### 10.4 Ejecución

- Ejecutar `python manage.py test` antes de finalizar cada tarea.
- Ejecutar la suite completa antes del commit final.
- Si un test falla, investigar la causa antes de asumir que es un problema del entorno.

---

## 11. Tamaño de Tareas

Una tarea adecuada se mide por su capacidad de ser revisada, testada y commitada de forma independiente.

### 11.1 Criterios

- **Un solo objetivo claro.** Si una tarea tiene un "y además", probablemente debe dividirse.
- **Pocos archivos.** Entre 1 y 4 archivos es lo típico. Más de 5 sugiere que la tarea es demasiado grande.
- **Commit independiente.** El proyecto debe funcionar correctamente después de aplicar el commit.
- **Fácilmente revisable.** Un reviewer debe poder evaluarla sin contexto adicional significativo.
- **Testeable de forma aislada.** La funcionalidad agregada o modificada debe poder validarse sin ejecutar toda la aplicación.

### 11.2 Cómo dividir

Si una tarea tiene múltiples responsabilidades, separarla en subtareas secuenciales. Cada subtarea deja el proyecto en un estado funcional y consistente.

Ejemplo de división:

- Tarea original: "Agregar validación de URL y log de intentos de clone"
- Subtarea A: "Agregar validación de URL en Repository"
- Subtarea B: "Agregar log de intentos de clone"

---

## 12. Revisión del Plan

El reviewer del plan debe evaluar la viabilidad y calidad del proceso de implementación propuesto, no la implementación en sí.

### 12.1 Qué evaluar

| Criterio | Pregunta clave |
|---|---|
| Separación de responsabilidades | ¿Cada tarea tiene un objetivo único y claro? |
| Tamaño de tareas | ¿Son revisiones viables en tiempo razonable? |
| Orden de implementación | ¿Minimiza el riesgo de regresión? |
| Dependencias | ¿Son correctas y están bien explícitas? |
| Riesgos | ¿Son realistas y están mitigados? |
| Estrategia de testing | ¿Cada tarea tiene una forma de validarse? |
| Commits | ¿Cada tarea genera un commit pequeño e independiente? |
| Tests en momento adecuado | ¿Los tests aparecen en el paso correcto del plan? |
| Estado consistente | ¿Cada tarea deja el proyecto en un estado funcional? |
| Estado integrable | ¿Cada tarea deja el proyecto en un estado funcional e integrable? |
| Reversibilidad | ¿Se podría revertir una tarea sin romper el resto del trabajo? |

### 12.2 Qué NO hacer

- No sugerir implementación alternativa.
- No proponer refactors no relacionados con la feature.
- No cuestionar decisiones de arquitectura existentes.
- No reescribir el plan; solo señalar problemas y sugerir mejoras puntuales.

---

## 13. Implementación

Durante la implementación, las reglas son claras:

- **Seguir exactamente la spec aprobada.** No interpretar requisitos de forma creativa.
- **No agregar funcionalidades.** Si se descubre una mejora, documentarla y abordarla después.
- **No eliminar comportamiento existente.** A menos que la spec lo requiera explícitamente.
- **Respetar la arquitectura.** Seguir las convenciones de estructura, naming y patrones existentes.
- **Mantener el estilo del proyecto.** Código nuevo debe ser consistente con lo que ya existe.
- **No commitear código que rompa tests existentes.** Si un cambio afecta tests anteriores, adaptarlos como parte de la misma tarea.
- **No hacer refactors no planificados.** Si un refactor es necesario, debe estar en el plan aprobado.

---

## 14. Scope Creep

Durante la implementación pueden detectarse bugs, mejoras o necesidades no relacionadas con la feature en curso. Salvo que bloqueen directamente la implementación:

- no deben resolverse en la misma rama;
- deben registrarse como nuevas tareas o nuevas specs;
- no deben ampliar el alcance de la feature aprobada.

El alcance de una feature se define en su especificación y no debe modificarse durante la implementación sin una revisión formal del plan.

---

## 15. Code Review

El code review es la última línea de defensa antes de integrar cambios.

### 15.1 Qué revisar

| Criterio | Qué buscar |
|---|---|
| Cumplimiento de la spec | ¿El código implementa lo que la spec describe? |
| Simplicidad | ¿La solución es lo más simple posible? ¿Hay código innecesario? |
| Legibilidad | ¿Es claro para alguien que no escribió el código? |
| Bugs | ¿Hay lógica incorrecta, edge cases no manejados, errores potenciales? |
| Cobertura de tests | ¿La funcionalidad nueva está testada? ¿Los tests son relevantes? |
| Regresiones | ¿Podría este cambio romper funcionalidad existente? |
| Consistencia | ¿Sigue la arquitectura y convenciones del proyecto? |

### 15.2 Reglas para reviewers

- No solicitar refactors innecesarios durante el review de una feature.
- Enfocarse en correctness, no en preferencias personales de estilo.
- Si se detecta un problema de diseño importante, proponerlo como nota pero no bloquear el merge si no afecta la funcionalidad.
- Ser específico: indicar archivo, línea y problema concreto.
- Las observaciones deben basarse en requisitos, riesgos técnicos, bugs, mantenibilidad o consistencia, evitando bloquear cambios por preferencias personales de estilo o diseño.

---

## 16. Definition of Done

Una feature se considera terminada cuando cumple **todas** estas condiciones:

| # | Condición |
|---|---|
| 1 | Cumple con todos los requisitos de la spec. |
| 2 | Cumple con todos los criterios de aceptación definidos. |
| 3 | Los tests nuevos pasan. |
| 4 | Los tests existentes siguen pasando. |
| 5 | No introduce regresiones conocidas. |
| 6 | La implementación respeta la arquitectura del proyecto. |
| 7 | Puede integrarse mediante un único merge sin trabajo adicional. |
| 8 | Cada tarea del plan fue completada y validada. |
| 9 | El plan aprobado fue respetado, o cualquier desviación quedó documentada y justificada. |

Ninguna de estas condiciones es negociable. Si alguna no se cumple, la feature vuelve al backlog o se continúa el trabajo hasta alcanzar el estado completo.
