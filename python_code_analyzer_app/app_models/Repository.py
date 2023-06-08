from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
import os, shutil, stat, subprocess

from python_code_analyzer_app.app_models import tools_status

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
        return os.path.join(settings.BASE_PATH,self.folder)

    def download(self):
        print(f'Repository.donwnload - repository path {self.path}..')
        if os.path.exists(self.path):
            print(f'Repository.donwnload - The repository {self.id} already exists. It will be removed...')
            shutil.rmtree(self.path, onerror = on_rm_error)
        os.mkdir(self.path)
        cmd = "git clone {} {}".format(self.url.strip(), self.path)
        print("#####################################")
        print("Starting to clone ${}".format(self.url))
        print(cmd)
        subprocess.call(cmd, shell = True)
        print("Finshed cloning {}".format(self.url))
        print("#####################################")

    def delete_files(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path, onerror = on_rm_error)
        if os.path.isdir(self.path+"_result"):
            shutil.rmtree(self.path+"_result", onerror = on_rm_error)


    def get_last_commit(self):
        print(f'Repository.get_last_commit - repository path {self.path}..')

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
