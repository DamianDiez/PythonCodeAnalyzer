import os
import shutil
from django.db import models

from python_code_analyzer_app.app_models.Repository import Repository
from python_code_analyzer_app.app_models.Tool import Tool
from python_code_analyzer_app.app_models import tools_status

class Analysis(models.Model):
    """Analisis de un repositorio"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices = tools_status.STATUS_OPTIONS, default=tools_status.PENDING)
    herramientas = models.ManyToManyField(Tool, through='AnalysisTool')
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

    @property
    def path_result(self):
        repository = Repository.objects.get(id=self.repository_id)
        path_result = repository.path+f"_result/Analysis{self.id}/"
        return path_result
    
    @property
    def path_to_zip(self):
        repository = Repository.objects.get(id=self.repository_id)
        path_result = repository.path+f"_result/Analysis{self.id}.zip"
        return path_result
    
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
            path_result = self.path_result
            if path_result.endswith('/'):
                path_result = path_result[:-1]
            format = "zip"
            shutil.make_archive(path_result, format, path_result)
            self.status = tools_status.FINISHED
        self.save()

    def cancel(self, status_msg):
        self.status = tools_status.CANCELLED
        self.status_msg=status_msg
        self.save()

    def delete_files(self):
        path_result = self.path_result
        path_result_zip = self.path_to_zip
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
    
    def get_result(self):
        tools = self.analysistool_set.all()
        result_items=[]
        for tool in tools:
            result_items += tool.get_result()
        return result_items
    

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
        if(cts):
            cts.completed = True
            return True
        return False

    def mark_completed(self, save=True):
        self.completed = True

        if save:
            self.save()

    class Meta:
        ordering = ('modified_on',)