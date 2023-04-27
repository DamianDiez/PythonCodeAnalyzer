from asgiref.sync import sync_to_async
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os, shutil, stat
import contextlib
import subprocess
import sys
from time import sleep

from .tools.pylint_tool import Pylint_Tool
from .tools.radon_tool import Radon_Tool
from .tools.vulture_tool import Vulture_Tool
from .tools import tools_status

BASE_PATH = "C:/tesis/git/"

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

class Repository(models.Model):
    """Un repositorio a ser analizado"""
    url = models.CharField(max_length=256)
    folder = models.CharField(max_length=256, default=datetime.now().strftime("%Y%m%d%H%M%S%f"))
    date_added = models.DateTimeField(auto_now_add=True) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'repositories'
    def __str__(self):
        """Return a string representation of the model."""
        return self.url

    @property
    def path(self):
        return os.path.join(BASE_PATH,self.folder)

    def download(self):
        print(f'Repository.donwnload - repository path {self.path}..')
        if os.path.exists(self.path):
            print(f'Repository.donwnload - The repository {self.id} already exists. It will be removed...')
            shutil.rmtree(self.path, onerror = on_rm_error)
            # os.rmdir(self.path)
        os.mkdir(self.path)
        cmd = "git clone {} {}".format(self.url.strip(), self.path)
        print("#####################################")
        print("Starting to clone ${}".format(self.url))
        print(cmd)
        # os.system(cmd)
        subprocess.call(cmd, shell = True)
        print("Finshed cloning {}".format(self.url))
        print("#####################################")

    def delete_files(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path, onerror = on_rm_error)
        if os.path.isdir(self.path+"_result"):
            shutil.rmtree(self.path+"_result", onerror = on_rm_error)


    def getLastCommit(self):
        print(f'Repository.getLastCommit - repository path {self.path}..')

        result = subprocess.run(["git","-C", self.path, "rev-parse", "HEAD"], capture_output=True,shell=True)
        commit = result.stdout.strip()
        print(f"Repository.donwnload - commit: {commit}")
        return commit

    def is_being_analyzed(self):
        analyzes = self.analysis_set.filter(status=tools_status.RUNNING)
        if len(analyzes) > 0:
            return True
        else:
            return False

class Tool(models.Model):
    """Herramienta"""
    PYLINT = 'Pylint'
    PYSMELL = 'Pysmell'
    PYREF = 'PyRef'
    VULTURE = 'Vulture'
    RADON = 'Radon'
    TOOL_OPTIONS = (
        (PYLINT, 'pylint'),
        (PYSMELL, 'pysmell'),
        (PYREF, 'pyref'),
        (VULTURE, 'vulture'),
        (RADON, 'radon'),
    )
    parameters = models.CharField(max_length=256, null=True)
    name = models.CharField(
        max_length=20,
        choices=TOOL_OPTIONS,
        default=PYLINT,
    )
    class_name = models.CharField(max_length=256, null=False, default="")

    def __str__(self):
        """Return a string representation of the model."""
        return self.name

    def run(self, analysis_tool):
        print('Tool.run')
        analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
        repository = Repository.objects.get(id=analysis.repository_id)
        tool_class = globals()[self.class_name]()
        print(f"Tool.run() - tool_class: {tool_class}")
        return tool_class.run(analysis.id, repository.path, self.name)

    def get_charts(self, analysis_tool):
        analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
        repository = Repository.objects.get(id=analysis.repository_id)
        tool_class = globals()[self.class_name]()
        path_result=repository.path+f"_result/Analisis{analysis.id}/{self.name}"
        return tool_class.get_charts(path_result)
    
    def get_indicators(self, analysis_tool):
        analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
        repository = Repository.objects.get(id=analysis.repository_id)
        tool_class = globals()[self.class_name]()
        path_result=repository.path+f"_result/Analisis{analysis.id}/{self.name}"
        return tool_class.get_indicators(path_result)

class Analysis(models.Model):
    """Analisis de un repositorio"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices = tools_status.STATUS_OPTIONS, default=tools_status.PENDING)
    herramientas = models.ManyToManyField(Tool, through='AnalysisTool')
    result = models.CharField(max_length=256)
    date_added = models.DateTimeField(auto_now_add=True) 
    date_finished = models.DateTimeField(auto_now = True, null=True, blank=True)
    task_id = models.CharField(max_length=50, null=False, blank=False, default='null')
    commit = models.CharField(max_length=40, null=False, blank=False, default='null')
    status_msg = models.CharField(max_length=256, default='null')

    class Meta:
        verbose_name_plural = 'analyzes'
    def __str__(self):
        """Return a string representation of the model."""
        return f'Analysis {self.id}'

    def start(self):
        self.status = tools_status.RUNNING
        self.save()

    def run(self):
        failed=False
        tools = self.analysistool_set.all()
        for tool in tools:
            if (CeleryTaskSignal.is_task_cancelled(self.id)):
                print(f"Analysis.run - Tarea Cancelada {self.id}")
                return
            if (tool.run()!=tools_status.FINISHED):
                failed = True
        if(failed):
            self.status = tools_status.FAILED
        else:
            path_result = os.path.join(self.repository.path+"_result",f"Analisis{self.id}")
            format = "zip"
            shutil.make_archive(path_result, format, path_result)
            self.status = tools_status.FINISHED
        self.save()

    def cancel(self, status_msg):
        self.status = tools_status.CANCELLED
        self.status_msg=status_msg
        self.save()

    def delete_files(self):
        path_result = os.path.join(self.repository.path+"_result",f"Analisis{self.id}")
        path_result_zip = os.path.join(self.repository.path+"_result",f"Analisis{self.id}.zip")
        if os.path.isdir(path_result):
            shutil.rmtree(path_result)
        if os.path.isfile(path_result_zip):
            os.remove(path_result_zip)

    def set_commit(self,commit):
        self.commit=commit
        self.save()

    def was_excecuted(self):
        analysis_related = Analysis.objects.filter(commit=self.commit, status=tools_status.FINISHED)
        return len(analysis_related) > 0

    def get_charts(self):
        tools = self.analysistool_set.all()
        charts=[]
        for tool in tools:
            charts += tool.get_charts()
        # for index in range(len(charts)):
        #     charts[index].position=index
        return charts
    
    def get_indicators(self):
        tools = self.analysistool_set.all()
        indicators=[]
        for tool in tools:
            indicators += tool.get_indicators()
        # for index in range(len(indicators)):
        #     indicators[index].position=index
        return indicators

class AnalysisTool(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    default_parameters = models.BooleanField(default=True)
    parameters = models.CharField(max_length=256, default=None, null=True)
    status = models.CharField(max_length=15, choices = tools_status.STATUS_OPTIONS, default=tools_status.PENDING)
    result = models.CharField(max_length=256, default='')


    def run(self):
        xstatus = self.tool.run(self)
        print(f"AnalysisTool.run() - status {xstatus}")
        self.status=xstatus
        self.save()
        return xstatus

    def get_charts(self):
        charts = self.tool.get_charts(self)
        return charts
    
    def get_indicators(self):
        indicators = self.tool.get_indicators(self)
        return indicators

class CeleryTaskSignal(models.Model):   
    CANCEL_TASK = 'cancel_task'
    PAUSE_TASK = 'pause_task'
    SIGNAL_CHOICES = (
        (CANCEL_TASK, 'Cancel Task'),
        (PAUSE_TASK, 'Pause Task'),
    )

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    signal = models.CharField(max_length=25, choices=SIGNAL_CHOICES, null=True)
    completed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True) 
    modified_on = models.DateTimeField(auto_now = True, null=True, blank=True)

    @staticmethod
    def is_task_cancelled(analysis):
        #chequear que el analisis no se haya cancelado
        cts = CeleryTaskSignal.objects.filter(signal=CeleryTaskSignal.CANCEL_TASK,
            completed=False,
            analysis = analysis)
        print(f"is_task_cancelled - cts: {cts}")
        if(cts):
            print(f"is_task_cancelled - entra al if")
            cts.completed = True
            print(f"is_task_cancelled - retorna True")
            return True
        print(f"is_task_cancelled - retorna falso")
        return False

    def mark_completed(self, save=True):
        self.completed = True

        if save:
            self.save()

    class Meta:
        ordering = ('modified_on',)

