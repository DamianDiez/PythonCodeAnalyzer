from asgiref.sync import sync_to_async
from django.db import models
from datetime import datetime
import os, shutil, stat
import pylint
import vulture
# import sys
import contextlib
import subprocess
import sys
from radon.cli import Config
from radon.cli.harvest import CCHarvester
from pylint import lint
from time import sleep


PENDING = 'PENDING'
RUNNING = 'RUNNING'
FINISHED = 'FINISHED'
FAILED = 'FAILED'
CANCELLED = 'CANCELLED'
STATUS_OPTIONS = (
    (PENDING, 'PENDING'),
    (RUNNING, 'RUNNING'),
    (FINISHED, 'FINISHED'),
    (FAILED, 'FAILED'),
    (CANCELLED, 'CANCELLED'),
)

BASE_PATH = "C:/tesis/git/"

def paylint_tool_excecute(tool, analysis_tool):
    print("Starting paylint_tool_excecute")
    analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
    repository = Repository.objects.get(id=analysis.repository_id)
    print(f"paylint_tool_excecute - repository.path: {repository.path}")
    path_result = os.path.join(repository.path+"_result",f"Analisis{analysis.id}",f"{tool.name}")
    
    if not os.path.exists(path_result):
        os.makedirs(path_result)

    file_result = os.path.join(path_result,"result.json")

    print(f"paylint_tool_excecute - path_result: {path_result}")
    # ejemplo
    # options = ["--recursive=y","--output-format=json:C:/tesis/git/result.json","C:/tesis/git/a3657248f44443498e74ba57bef673d8"]
    options = ["--recursive=y",f"--output-format=json:{file_result}",f"{repository.path}"]

    try:
        pylint.lint.Run(options)
    except BaseException as err:
        print(f"paylint_tool_excecute - Unexpected {err=}, {type(err)=}")
    finally:
        print("Finalizado")
        return FINISHED

def pysmell_tool_excecute(tool, analysis_tool):
    print("Starting pysmell_tool_excecute")
    analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
    repository = Repository.objects.get(id=analysis.repository_id)
    print(f"pysmell_tool_excecute - repository.path: {repository.path}")
    return FINISHED

def pyRef_tool_excecute(tool, analysis_tool):
    print("Starting pyRef_tool_excecute")
    analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
    repository = Repository.objects.get(id=analysis.repository_id)
    print(f"pyRef_tool_excecute - repository.path: {repository.path}")
    return FINISHED

def vulture_tool_excecute(tool, analysis_tool):
    print("Starting vulture_tool_excecute")
    analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
    repository = Repository.objects.get(id=analysis.repository_id)
    print(f"vulture_tool_excecute - repository.path: {repository.path}")

    path_result = os.path.join(repository.path+"_result",f"Analisis{analysis.id}",f"{tool.name}")
    
    if not os.path.exists(path_result):
        os.makedirs(path_result)

    file_result = os.path.join(path_result,"result.txt")

    print(f"vulture_tool_excecute - path_result: {path_result}")

    try:
        v = vulture.Vulture()
        v.scavenge([f"{repository.path}"])
        # sys.stdout = open(file_result, "w")
        with open(file_result, "w") as o:
            with contextlib.redirect_stdout(o):
                v.report()
        
    except BaseException as err:
        print(f"vulture_tool_excecute - Unexpected {err=}, {type(err)=}")
    finally:
        print("Finalizado")
        return FINISHED

def radon_tool_excecute(tool, analysis_tool):
    print("Starting radon_tool_excecute")
    analysis = Analysis.objects.get(id=analysis_tool.analysis.id)
    repository = Repository.objects.get(id=analysis.repository_id)
    print(f"radon_tool_excecute - repository.path: {repository.path}")
    path_result = os.path.join(repository.path+"_result",f"Analisis{analysis.id}",f"{tool.name}")
    if not os.path.exists(path_result):
        os.makedirs(path_result)
    file_result_cc = os.path.join(path_result,"result_cc.txt")
    file_result_mi = os.path.join(path_result,"result_mi.txt")
    file_result_raw = os.path.join(path_result,"result_raw.txt")
    file_result_hal = os.path.join(path_result,"result_hal.txt")

    try:
        # process = subprocess.Popen(['radon', 'cc', repository.path],
        #                            stdout=subprocess.PIPE,
        #                            stderr=subprocess.STDOUT)
        # returncode = process.wait()
        # print('ping returned {0}'.format(returncode))
        # with open(file_result_cc, "w") as o:
        #     with contextlib.redirect_stdout(o):
        #         print(process.stdout)
        with open(file_result_cc,"wb") as out:
            subprocess.Popen(['radon', 'cc', repository.path],stdout=out,stderr=subprocess.STDOUT)
        with open(file_result_mi,"wb") as out:
            subprocess.Popen(['radon', 'mi', repository.path],stdout=out,stderr=subprocess.STDOUT)
        with open(file_result_raw,"wb") as out:
            subprocess.Popen(['radon', 'raw', repository.path],stdout=out,stderr=subprocess.STDOUT)
        with open(file_result_hal,"wb") as out:
            subprocess.Popen(['radon', 'hal', repository.path],stdout=out,stderr=subprocess.STDOUT)
        # config = Config(
        #     exclude=None,
        #     ignore=None,
        #     order='SCORE',
        #     no_assert=False,
        #     show_closures=False,
        #     min='A',
        #     max='F',
        # )
        # print(f"radon_tool_excecute - config created")
        # h = CCHarvester([repository.path], config)
        # # h = CCHarvester(["C:/Tesis/git/6123410c37094547b6567f2b94960e40/example.py"], config)
        # print(f"radon_tool_excecute - CCHarvester created")
        # results = h.as_json()
        # print(f"radon_tool_excecute - h._to_dicts() executed")
        # print(results)
        # print(f"radon_tool_excecute - result printed")
        # print(r)
        # r.as_json()
        # v.scavenge([f"{repository.path}"])
        # # sys.stdout = open(file_result, "w")
        # with open(file_result, "w") as o:
        #     with contextlib.redirect_stdout(o):
        #         v.report()
        
    except BaseException as err:
        print(f"radon_tool_excecute - Unexpected {err=}, {type(err)=}")
    finally:
        print("Finalizado")
        return FINISHED

TOOL_FUNCTIONS={
    'Pylint': paylint_tool_excecute,
    'Pysmell': pysmell_tool_excecute,
    'PyRef': pyRef_tool_excecute,
    'Vulture': vulture_tool_excecute,
    'Radon': radon_tool_excecute}

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

class Repository(models.Model):
    """Un repositorio a ser analizado"""
    url = models.CharField(max_length=256)
    # path = models.CharField(max_length=256, default=os.path.join(BASE_PATH,datetime.now().strftime("%Y%m%d%H%M%S%f")))
    folder = models.CharField(max_length=256, default=datetime.now().strftime("%Y%m%d%H%M%S%f"))
    date_added = models.DateTimeField(auto_now_add=True) 
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
        # cmd = "git clone {} {}".format(self.url, "C:/tesis/git/test")
        print("#####################################")
        print("Starting to clone ${}".format(self.url))
        print(cmd)
        # os.system(cmd)
        subprocess.call(cmd, shell = True)
        print("Finshed cloning {}".format(self.url))
        print("#####################################")
    
    def is_being_analyzed(self):
        analyzes = self.analysis_set.filter(status=RUNNING)
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
    def __str__(self):
        """Return a string representation of the model."""
        return self.name

    def run(self, analysis_tool):
        return TOOL_FUNCTIONS[self.name](self,analysis_tool)

class Analysis(models.Model):
    """Analisis de un repositorio"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices = STATUS_OPTIONS, default=PENDING)
    herramientas = models.ManyToManyField(Tool, through='AnalysisTool')
    result = models.CharField(max_length=256)
    date_added = models.DateTimeField(auto_now_add=True) 
    date_finished = models.DateTimeField(auto_now = True, null=True, blank=True)
    task_id = models.CharField(max_length=50, null=False, blank=False, default='null')
    
    class Meta:
        verbose_name_plural = 'analyzes'
    def __str__(self):
        """Return a string representation of the model."""
        return f'Analysis {self.id}'

    def start(self):
        self.status = RUNNING
        self.save()

    def run(self):
        failed=False
        tools = self.analysistool_set.all()
        for tool in tools:
            if (CeleryTaskSignal.is_task_cancelled(self.id)):
                print(f"Analysis.run - Tarea Cancelada {self.id}")
                return
            if (tool.run()!=FINISHED):
                failed = True
        if(failed):
            self.status = FAILED
        else:
            path_result = os.path.join(self.repository.path+"_result",f"Analisis{self.id}")
            filename = "result"
            format = "zip"
            shutil.make_archive(path_result, format, path_result)
            self.status = FINISHED
        self.save()

    def cancel(self):
        self.status = CANCELLED
        self.save()

class AnalysisTool(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    default_parameters = models.BooleanField(default=True)
    parameters = models.CharField(max_length=256, default=None, null=True)
    status = models.CharField(max_length=15, choices = STATUS_OPTIONS, default=PENDING)
    result = models.CharField(max_length=256, default='')


    def run(self):
        xstatus = self.tool.run(self)
        print(f"AnalysisTool.run() - status {xstatus}")
        self.status=xstatus
        self.save()
        return xstatus

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

