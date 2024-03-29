import os
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from python_code_analyzer_app.app_layout_classes.LayoutManager import LayoutManager

from python_code_analyzer_app.app_models.TaskManager import TaskManager
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
            txt_file=os.path.join(settings.BASE_PATH,"massive.txt")
            with open(txt_file, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            task_id = TaskManager.launch_massive_upload.apply_async((txt_file,request.user.id,),countdown=5,queue='repository_queue')
            return redirect('python_code_analyzer_app:repositories')
    else:
        form = UploadFileForm()
    return render(request, 'python_code_analyzer_app/massive_upload.html', {'form': form})

@login_required
def new_analysis(request, repository_id):
    """Add a new analysis for a particular repository."""
    repository = Repository.objects.get(id=repository_id)
    all_tools = Tool.objects.all()

 
    if request.method != 'POST':
        form = AnalysisForm()
    else:
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
                    at.save()
            # launch asynchronous task
            print(f"new_analysis - launching the task")
            task_id = TaskManager.excecute_analysis.apply_async((new_analysis.id,),countdown=5)
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
    analysis = Analysis.objects.get(id=analysis_id)
    result_items=[]
    result_items=analysis.get_result()
    criteria_list = settings.CRITERIA_LIST
    result_items_ordered = LayoutManager.sort_by_multiple_criteria(result_items,criteria_list)
    context = {'analysis': analysis, 'result_items': result_items_ordered}
    return render(request, 'python_code_analyzer_app/analysis.html', context)

@login_required
def analysis_result(request, analysis_id):
    """Show a single analysis detail"""
    analysis = Analysis.objects.get(id=analysis_id)
    path_to_file = analysis.path_to_zip
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
        a.delete_files()
        a.delete()
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_all_repositories(request):
    repos = Repository.objects.filter(owner=request.user)
    for r in repos:
        r.delete_files()
        r.delete()
    return redirect(request.META['HTTP_REFERER'])