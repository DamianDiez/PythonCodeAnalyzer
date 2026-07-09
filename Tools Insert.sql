-- Herramientas disponibles para análisis de código Python.
-- Correr después de python manage.py migrate.
-- Solo incluye herramientas con implementación en python_code_analyzer_app/app_models/Tool.py.
-- Compatible con el modelo posterior a la migración 0103 (se eliminó el campo parameters).
INSERT INTO [python_code_analyzer_app_tool] ([name],[class_name]) VALUES ('Pylint','Pylint_Tool');
INSERT INTO [python_code_analyzer_app_tool] ([name],[class_name]) VALUES ('Vulture','Vulture_Tool');
INSERT INTO [python_code_analyzer_app_tool] ([name],[class_name]) VALUES ('Radon','Radon_Tool');
