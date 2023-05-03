import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
# from django.htpp import StreamingHttpResponse
# from WSGIREF.UTIL import FileWrapper
from .tasks import excecute_analysis, launch_massive_upload
from python_code_analyzer.celery import app

from .models import Repository, Analysis, Tool, AnalysisTool, CeleryTaskSignal
from .forms import RepositoryForm, AnalysisForm, AnalysisToolForm, UploadFileForm

from django.core.paginator import Paginator

def index(request):
    """The home page for Python Code Analyzer."""
    return render(request, 'python_code_analyzer_app/index.html')

@login_required
def repositories(request):
    """Show all repositories."""
    #Set up pagination
    p = Paginator(Repository.objects.filter(owner=request.user).order_by('date_added'), 8)
    page = request.GET.get('page')
    repos = p.get_page(page)
    context = {'repositories': repos}
    return render(request, 'python_code_analyzer_app/repositories.html', context)

@login_required
def repository(request, repository_id):
    """Show a single repository and all its analyzes."""
    repository = Repository.objects.get(id=repository_id)
    # Make sure the repository belongs to the current user.
    if repository.owner != request.user:
        raise Http404
    analyzes = repository.analysis_set.order_by('-date_added')
    p = Paginator(repository.analysis_set.order_by('-date_added'), 8)
    page = request.GET.get('page')
    analyzes = p.get_page(page)
    context = {'repository': repository, 'analyzes': analyzes}
    return render(request, 'python_code_analyzer_app/repository.html', context)

@login_required
def new_repository(request):
    """Add a new repository."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = RepositoryForm()
    else:
        # POST data submitted; process data.
        form = RepositoryForm(data=request.POST)
        if form.is_valid():
            new_repository = form.save(commit=False)
            new_repository.owner = request.user
            new_repository.save()
            return redirect('python_code_analyzer_app:repositories')
    
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'python_code_analyzer_app/new_repository.html', context)

@login_required
def massive_upload(request):
    """Add a repositories from file."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            print(f"Nombre del archivo: {f.name}")
            with open("C:/tesis/git/massive.txt", 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            print(f"Va a mostrar el user")
            print(f"massive_upload - user id = {request.user.id}")
            task_id = launch_massive_upload.apply_async(("C:/tesis/git/massive.txt",request.user.id,),countdown=5,queue='repository_queue')
            return redirect('python_code_analyzer_app:repositories')
    else:
        form = UploadFileForm()
    return render(request, 'python_code_analyzer_app/massive_upload.html', {'form': form})

@login_required
def new_analysis(request, repository_id):
    """Add a new analysis for a particular repository."""
    repository = Repository.objects.get(id=repository_id)
    all_tools = Tool.objects.all();

 
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AnalysisForm()
        # forms = []
        # for x in all_tools:
        #     at_form = AnalysisToolForm(initial={'tool_id': x.id})
        #     forms.append(at_form)
    else:
        # POST data submitted; process data.
        form = AnalysisForm(data=request.POST)
        if form.is_valid():
            new_analysis = form.save(commit=False)
            new_analysis.repository = repository
            new_analysis.save()
            for x in all_tools:
                habilitado = request.POST.get(f"chk_enabled-{x.id}")
                if habilitado =='clicked':
                    at = AnalysisTool()
                    at.analysis = new_analysis
                    at.tool = x
                    if request.POST.get(f"chk_default-{x.id}")=='clicked':
                        at.default_parameters = True
                    else:
                        at.default_parameters = False
                        at.parameters = request.POST.get(f"parameters-{x.id}")
                    at.save()
            # launch asynchronous task
            print(f"new_analysis - launching the task")
            task_id = excecute_analysis.apply_async((new_analysis.id,),countdown=5)
            print(f"new_analysis - saving task_id = {task_id}")
            new_analysis.task_id=task_id
            new_analysis.save()
            return redirect('python_code_analyzer_app:repository', repository_id=repository_id)
    # Display a blank or invalid form.
    context = {'repository': repository, 'form': form, 'all_tools': all_tools }
    return render(request, 'python_code_analyzer_app/new_analysis.html', context)

@login_required
def analysis(request, analysis_id):
    """Show a single analysis detail"""
    list_of_charts = []
    analysis = Analysis.objects.get(id=analysis_id)
    repository = Repository.objects.get(id=analysis.repository_id)
    analysis_path = repository.path+"_result" +"/"+f"Analisis{analysis_id}"
    indicators=analysis.get_indicators()
    result_list=analysis.get_charts()
    list_of_charts=list_of_charts + result_list
    for x in list_of_charts:
        print(x.label)
    context = {'analysis': analysis, 'list_of_charts': list_of_charts, 'list_of_indicators': indicators}
    return render(request, 'python_code_analyzer_app/analysis.html', context)

@login_required
def analysis_result(request, analysis_id):
    """Show a single analysis detail"""
    analysis = Analysis.objects.get(id=analysis_id)
    repository = Repository.objects.get(id=analysis.repository_id)
    # path_to_file = os.path.join(repository.path+"_result",f"Analisis{analysis_id}.zip")
    path_to_file = repository.path+"_result" +"/"+f"Analisis{analysis_id}.zip"
    print(f"analysis_result - {path_to_file}")
    if os.path.exists(path_to_file):
        with open(path_to_file, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_to_file)
            return response
    raise Http404

@login_required
def cancel_analysis(request, analysis_id):
    print("Cancel Analysis")
    """Cancel a single analysis"""
    analysis = Analysis.objects.get(id=analysis_id)
    print(f"cancel_analysis - analysis.id: {analysis.id}")
    #Si todavia no arranco, esto cancela el task
    #revoke_result = app.control.revoke(task_id, terminate=True)
    #print(f"revoke_result: {revoke_result}")
    #analysis.cancel()
    cts = CeleryTaskSignal()
    cts.analysis = analysis
    cts.signal = CeleryTaskSignal.CANCEL_TASK

    cts.save()
    analysis.cancel("Canceled by user")
    # Redirigir a la misma página
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_analysis(request, analysis_id):
    analysis = Analysis.objects.get(id=analysis_id)
    analysis.delete_files()
    repo_id = analysis.repository_id
    analysis.delete()
    # Redirigir a la misma página
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_repository(request, repo_id):
    repo = Repository.objects.get(id=repo_id)
    repo.delete_files()
    repo.delete()
    # Redirigir a la misma página
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_all_analyzes(request, repo_id):
    repo = Repository.objects.get(id=repo_id)
    analizes = Analysis.objects.filter(repository=repo)
    for a in analizes:
        print(a.id)
        a.delete_files()
        print("archivos borrados")
        a.delete()
        print("analisis borrado")
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_all_repositories(request):
    repos = Repository.objects.filter(owner=request.user)
    for r in repos:
        print(r.id)
        r.delete_files()
        print("archivos borrados")
        r.delete()
        print("repo borrado")
    return redirect(request.META['HTTP_REFERER'])

