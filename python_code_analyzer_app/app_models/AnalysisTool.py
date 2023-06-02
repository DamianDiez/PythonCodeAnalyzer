from django.db import models
from python_code_analyzer_app.app_models.Analysis import Analysis
from python_code_analyzer_app.app_models.Repository import Repository
from python_code_analyzer_app.app_models.Tool import Tool
from python_code_analyzer_app.tools import tools_status

class AnalysisTool(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    default_parameters = models.BooleanField(default=True)
    parameters = models.CharField(max_length=256, default=None, null=True)
    status = models.CharField(max_length=15, choices = tools_status.STATUS_OPTIONS, default=tools_status.PENDING)
    result = models.CharField(max_length=256, default='')

    def run(self):
        instancia = self.tool.get_instance()
        if(instancia == None):
            return tools_status.FAILED
        xstatus = instancia.run(self)
        self.status=xstatus
        self.save()
        return xstatus

    def get_charts(self):
        instancia = self.tool.get_instance()
        if(instancia == None):
            return []
        charts = instancia.get_charts(self)
        return charts
    
    def get_indicators(self):
        instancia = self.tool.get_instance()
        if(instancia == None):
            return []
        indicators = instancia.get_indicators(self)
        return indicators
    
    def get_result(self):
        instancia = self.tool.get_instance()
        if(instancia == None):
            return []
        result_items = instancia.get_result(self)
        return result_items
    
    def get_path_result_analysis(self):
        analysis = Analysis.objects.get(id=self.analysis.id)
        return analysis.path_result
    
    def get_path_repository(self):
        analysis = Analysis.objects.get(id=self.analysis.id)
        repo = Repository.objects.get(id=analysis.repository.id)
        return repo.path