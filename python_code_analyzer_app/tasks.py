from celery import shared_task
from .models import Repository, Analysis, AnalysisTool, CeleryTaskSignal, Tool
from time import sleep
from datetime import datetime




@shared_task
def excecute_analysis(analysis_id):

    #chequear que no haya corriendo un analisis para el mismo repositorio
    print('start excecute_analysis - getting analysis...')
    analysis = Analysis.objects.get(id=analysis_id)
    print('excecute_analysis - getting repository...')
    repository = Repository.objects.get(id=analysis.repository_id)
    
    
    if(repository.is_being_analyzed()):
        #loguear que se esta ejecutando otro analisis
        print(f'excecute_analysis - an analysis is already executing for this repository {repository.id}...')
        #cancelar la ejecucion de este
        analysis.cancel()
        return False

    print(f"excecute_analysis - start - analysis: {analysis} ")
    if (CeleryTaskSignal.is_task_cancelled(analysis)):
        print(f"excecute_analysis - is_task_cancelled True")
        return False
    #Cambiar el estado del analisis a ejecutandose
    analysis.start()

    print(f"excecute_analysis - download repository - analysis: {analysis} ")
    if (CeleryTaskSignal.is_task_cancelled(analysis)):
        print(f"excecute_analysis - is_task_cancelled True")
        return False
    #try:
    #descargar el repositorio
    repository.download()

    print(f"excecute_analysis - run - analysis: {analysis} ")
    if (CeleryTaskSignal.is_task_cancelled(analysis)):
        print(f"excecute_analysis - is_task_cancelled True")
        return False
    #ejecutar el analisis
    analysis.run()
    
    return True
    # except:
    #     print(f"excecute_analysis - error downloading the repository {repository.id}...")
    #     analysis.cancel()
    #     return False

@shared_task
def launch_massive_upload(filename):
    print(f"launch_massive_upload - Begin. File {filename}")
    url=""
    with open(filename) as archivo:
        print("launch_massive_upload - Va a leer una linea del archivo")
        for url in archivo:
            # TODO: chequear si la tarea no esta cancelada
            
            print(f"launch_massive_upload - url: {url}")
            
            #me fijo si existe el repositorio
            print("launch_massive_upload - Chequeo si existe el repositorio")
            repositories = Repository.objects.filter(url=url)
            repository = None
            repository = Repository()
            if len(repositories) > 0:
                print("launch_massive_upload - Existe el repositorio")
                repository = repositories.first()
            else:
                # crear el repo si no existe
                print("launch_massive_upload - No existe el repositorio, lo creo")
                repository.url=url
                repository.folder = datetime.now().strftime("%Y%m%d%H%M%S%f")
                repository.save()

            #agrego un analisis
            print("launch_massive_upload - Busco todas las tools")
            all_tools = Tool.objects.all();
            print("launch_massive_upload - Creo el analysis")
            new_analysis = Analysis()
            new_analysis.repository = repository
            new_analysis.save()
            print("launch_massive_upload - Agrego las tools al analisis")
            for x in all_tools:
                at = AnalysisTool()
                at.analysis = new_analysis
                at.tool = x
                at.default_parameters = True
                at.save()
            # lanzar el analisis
            # launch asynchronous task
            print(f"launch_massive_upload - launching the task")
            task_id = excecute_analysis.apply_async((new_analysis.id,),countdown=5)
            print(f"launch_massive_upload - saving task_id = {task_id}")
            new_analysis.task_id=task_id
            print(f"launch_massive_upload - Guardo el analisis")
            new_analysis.save()
        
    print("launch_massive_upload - End")
