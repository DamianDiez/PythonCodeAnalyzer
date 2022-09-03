1) Instalar python con ADD python path
2) Bajarse el proyecto desde github
3) Abrir un command line y pararse en la carpeta del proyecto 
4) Dentro de la carpeta del proyecto crear un virtual env (a la altura de donde está el archivo requirements.txt)
	python -m venv pca_env
5) Iniciar el virtual env
	pca_env\Scripts\activate
6) En la misma consola instalar los requerimientos:
	pip install requirements.txt
7) Correr las migraciones para crear la base de datos:
	python manage.py migrate
8) Correr los inserts de las tools en la base de datos: 
	Tools Insert.sql
9) Instalar RabbitMQ. Con Docker se puede usar la siguiente imagen:
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management
10) En la consola del virtual env poner a correr el servidor:
	python manage.py runserver
11) Abrir otra consola como administrador, ir a la carpeta del proyecto, iniciar el virtual env y correr Celery:
	celery -A python_code_analyzer worker -l info --pool=solo
12) Crear un super user
	python manage.py createsuperuser
	Pide nombre de usuario y password. Recordarlo para poder entrar como administrador y porder crear mas usuarios, configurar tools, etc.
