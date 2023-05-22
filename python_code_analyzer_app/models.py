from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os, shutil, stat, json, subprocess, re, contextlib
from time import sleep
from python_code_analyzer_app.tools.chart_class import Chart
from python_code_analyzer_app.tools.indicator_class import Indicator
from .tools import tools_status
import vulture


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

    def get_instance(self):
        instancia_clase_hija = globals()[self.class_name]()
        return instancia_clase_hija

    
    
    class Meta:
        abstract = False
        db_table = 'python_code_analyzer_app_tool'
        
    def run(self, analysis_tool):
        pass

    def get_charts(self, analysis_tool):
        pass
    
    def get_indicators(self, analysis_tool):
        pass

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

    def get_charts(self):
        tools = self.analysistool_set.all()
        charts=[]
        for tool in tools:
            print(tool)
            charts += tool.get_charts()
        return charts
    
    def get_indicators(self):
        tools = self.analysistool_set.all()
        indicators=[]
        for tool in tools:
            indicators += tool.get_indicators()
        return indicators

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
    
    def get_path_result_analysis(self):
        analysis = Analysis.objects.get(id=self.analysis.id)
        return analysis.path_result
    
    def get_path_repository(self):
        analysis = Analysis.objects.get(id=self.analysis.id)
        repo = Repository.objects.get(id=analysis.repository.id)
        return repo.path

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

# region Tools
class Pylint_Tool(Tool):

    def __init__(self):
        """init"""
        self.name="Pylint"
        self.class_name="Pylint_Tool"

    class Meta:
        managed = False
        db_table = 'python_code_analyzer_app_tool'
    
    def _add(self,details,detail):
        if(detail != None):
            details.append(detail)
            msg = detail["message"].rstrip()
            index = msg.rfind('(')
            # Si no se encuentra el carácter '(', lanzamos una excepción
            if index == -1:
                raise ValueError("No se encontró el carácter '(' en la cadena")
            # Obtener el mensaje y la categoría del mensaje usando rebanado de cadenas
            message = msg[:index].strip()
            category = msg[index+1:-1]
            detail["symbol"]=category
            detail["message"] = message
            detail = None

    def _getType(self,message_id):
        if message_id.startswith("C"):
            return "convention"
        if message_id.startswith("E"):
            return "error"
        if message_id.startswith("W"):
            return "warning"
        if message_id.startswith("R"):
            return "refactor"
        if message_id.startswith("I"):
            return "information"
        if message_id.startswith("F"):
            return "fatal"

    def _toJson(self,fileTxt,fileJson):
        with open(fileTxt, 'r') as file:
            lines = file.readlines()

        details = []
        detail = None
        for line in lines:
            message=""        
            if line.startswith('*************'):
                x, y, module = line.split()
            elif line.startswith('C:'):
                self._add(details,detail)
                line_split=line.split(':')
                disc=line_split[0]
                path=line_split[1]
                line=line_split[2]
                column=line_split[3]
                message_id=line_split[4]
                for item in line_split[4:]:
                    message=message + item
                message = message.strip()
                detail={
                    'type': self._getType(message_id.strip()),
                    'module': module,
                    'obj': "",
                    'line': int(line),
                    'column': int(column),
                    'endLine': int(line),
                    'endColumn': int(column),
                    'path': disc+":"+path,
                    'symbol': None,
                    'message': message,
                    'message-id': message_id.strip()
                }
            elif line.startswith('Your code has been rated at'):
                self._add(details,detail)
                resultados = re.findall(r'\d+\.\d+(?=/10)', line)
                current=-1.0
                previous=-1.0
                if len(resultados) >= 1:
                    current=float(resultados[0])
                if len(resultados) >= 2:
                    previous=float(resultados[1])
                rating = {"current": current, "previous": previous}
            elif line.startswith('------------------------------------'):
                None
            else:#el caso de que sea la continuación del mensaje
                if line != "":
                    detail['message'] = detail['message'] + line;
                

        result = {'details': details, 
                'rating': rating}

        with open(fileJson, 'w') as file:
            json.dump(result, file, indent=4)

    def run(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        repository_path = analysis_tool.get_path_repository()

        if not os.path.exists(path_result):
            os.makedirs(path_result)
        
        file_result_json = os.path.join(path_result,"result.json")
        file_result_text = os.path.join(path_result,"result.txt")

        # ejemplo
        # options = ["--recursive=y","--output-format=json:C:/tesis/git/result.json","C:/tesis/git/a3657248f44443498e74ba57bef673d8"]
        #options = ["--recursive=y",f"--output-format=text:{file_result}",f"{repository_path}"]

        try:
            with open(file_result_text,"wb") as out:
                result = subprocess.run(["pylint","--recursive=y", repository_path], stdout=out, shell=True)
            
            self._toJson(file_result_text,file_result_json)
        except BaseException as err:
            print(f"Pylint_Tool.run() - Unexpected {err=}, {type(err)=}")
        finally:
            print("Pylint_Tool.run() - Finalizado")
            return tools_status.FINISHED

    def __get_number_of_messages_by_type(self,datos):
        tipos = [x['type'] for x in datos]
        tipos=sorted(list(set(tipos)),key=str.lower)
        #cantidad de elementos de cada tipo
        valores = []
        for tipo in tipos:
            valores.append( sum(x['type']==tipo for x in datos) )
        chart=Chart('Pylint-types', 6, Chart.BAR, '# of Messages by Type', tipos, valores)
        return chart

    def __get_number_of_messages_by_symbol(self,datos):
        symbols = [x['symbol'] for x in datos]
        symbols=sorted(list(set(symbols)),key=str.lower)
        #cantidad de elementos de cada tipo
        valores = []
        for symbol in symbols:
            valores.append( sum(x['symbol']==symbol for x in datos) )
        display_legend = True
        if len(symbol)>10:
            display_legend = 'false'
        chart=Chart('Pylint-symbols', 6, Chart.PIE, 'Pylint - Tipos de mensaje', symbols, valores, 400, display_legend)
        return chart

    def __get_number_of_msg_type_by_module(self, msg_type, datos, modulos):
        #cantidad de elementos de cada tipo
        valores = []
        for modulo in modulos:
            valores.append( sum(x['type']==msg_type and x['module'] ==modulo for x in datos) )
        # chart=Chart(f"Pylint-{msg_type}-module", 1, Chart.BAR, f'Pylint - {msg_type}s by module', modulos, valores)
        return valores

    def __get_messages_by_module(self, datos):
        charts = []
        tipos = [x['type'] for x in datos]
        tipos=sorted(list(set(tipos)),key=str.lower);
        modulos = [x['module'] for x in datos]
        modulos=sorted(list(set(modulos)),key=str.lower);
        all_values = []
        for tipo in tipos:
            valores = self.__get_number_of_msg_type_by_module( tipo, datos, modulos)		
            for i in range(len(modulos)):
                all_values.append({"x": modulos[i], "y": tipo, "v": valores[i]})
            
            # chart=Chart(f"Pylint-{tipo}-module", 1, Chart.BAR, f'Pylint - {tipo}s by module', modulos, valores)
            # charts.append(chart)
        
        
        charts.insert(0,Chart(f"Pylint-heatmap-module", 12, Chart.MATRIX, f'Heatmap by Module', modulos, all_values,100, 'false', tipos))
            

        return charts

    def get_charts(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_charts = []
        path_to_file = path_result+"/result.json"
        if(not os.path.exists(path_to_file)):
            return list_of_charts

        with open(path_to_file) as contenido:
            datos = json.load(contenido)

        details = datos['details']
        list_of_charts+=self.__get_messages_by_module(details)
        list_of_charts.append(self.__get_number_of_messages_by_type(details))
        #list_of_charts.append(self.__get_number_of_messages_by_symbol(details))
        
        return list_of_charts

    
    def get_indicators(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_indicators = []
        path_to_file = path_result+"/result.json"
        if(not os.path.exists(path_to_file)):
            return list_of_indicators

        with open(path_to_file) as contenido:
            datos = json.load(contenido)
        
        rating = datos['rating']
        list_of_indicators.append(Indicator("pylint-rating", "Rating", 3, rating["current"], Indicator.RATING, 10, 4.0, 7.0, 9.0))
        details = datos['details']
        modulos = [x['module'] for x in details]
        modulos=sorted(list(set(modulos)),key=str.lower);
        list_of_indicators.append(Indicator("pylint-modules", "# of Modules", 3, len(modulos), Indicator.DEFAULT, 10, 4.0, 7.0, 9.0))
        
        return list_of_indicators

class Vulture_Tool(Tool):

    def __init__(self):
        """init"""
        self.name="Vulture"
        self.class_name="Vulture_Tool"

    class Meta:
        managed = False
        db_table = 'python_code_analyzer_app_tool'

    def run(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        repository_path = analysis_tool.get_path_repository()
        if not os.path.exists(path_result):
            os.makedirs(path_result)
        file_result = os.path.join(path_result,"result.txt")
        try:
            v = vulture.Vulture()
            v.scavenge([f"{repository_path}"])
            with open(file_result, "w") as o:
                with contextlib.redirect_stdout(o):
                    v.report()

        except BaseException as err:
            print(f"Vulture_Tool.run() - Unexpected {err=}, {type(err)=}")
        finally:
            print("Vulture_Tool.run() - Finalizado")
            return tools_status.FINISHED

    def get_charts(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_charts = []
        path_to_file = path_result+"/result.txt"
        print(f"path to file: {path_to_file}")
        if(not os.path.exists(path_to_file)):
            return list_of_charts
        messages=["unused method","unused variable","unused attribute","unused class","unused import","unused function"]
        counter = {message: 0 for message in messages}
        with open(path_to_file, 'r') as archivo:
            for line in archivo:
                for message in messages:
                    if message in line:
                        counter[message] += 1
        
        list_of_charts.append(Chart('Vulture-Unused-Items', 6, Chart.BAR, 'Unused Items', json.dumps(messages), counter))
                
        return list_of_charts
    
    def get_indicators(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_indicators = []
        path_to_file = path_result+"/result.txt"
        if(not os.path.exists(path_to_file)):
            return list_of_indicators
        totalUnusedItems=0
        with open(path_to_file) as contenido:
            lines = contenido.readlines()
            totalUnusedItems = len(lines)
                

        list_of_indicators.append(Indicator("vulture-unused-items", "# of Usused Items", 3, totalUnusedItems, Indicator.DEFAULT, 0, 0, 0, 0))
        #list_of_indicators.append(Indicator("radon-line-of-comments", "# of lines of Comments", 3, totalComments, Indicator.DEFAULT, 0, 0, 0, 0))
        return list_of_indicators

class Radon_Tool(Tool):

    def __init__(self):
        """init"""
        self.name="Radon"
        self.class_name="Radon_Tool"
    class Meta:
        managed = False
        db_table = 'python_code_analyzer_app_tool'

    def run(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        repository_path = analysis_tool.get_path_repository()
        if not os.path.exists(path_result):
            os.makedirs(path_result)
        file_result_cc = os.path.join(path_result,"result_cc.txt")
        file_result_mi = os.path.join(path_result,"result_mi.json")
        file_result_raw = os.path.join(path_result,"result_raw.json")

        try:
            with open(file_result_cc,"wb") as out:
                result = subprocess.run(["radon","cc", '-s', '-a', repository_path], stdout=out, shell=True)
            with open(file_result_mi,"wb") as out:
                result = subprocess.run(["radon","mi", '-s', '-j', repository_path], stdout=out, shell=True)
            with open(file_result_raw,"wb") as out:
                result = subprocess.run(["radon","raw", '-s', '-j', repository_path], stdout=out, shell=True)

        except BaseException as err:
            print(f"Radon_Tool.run() - Unexpected {err=}, {type(err)=}")
        finally:
            print("Radon_Tool.run() - Finalizado")
            return tools_status.FINISHED

    def get_cc_charts(self, path_result):
        list_of_charts = []
        path_to_file = path_result+"/result_cc.json"
        if(not os.path.exists(path_to_file)):
            return list_of_charts
        ranks=[0,0,0,0,0,0]
        labels = ["A","B","C","D","E","F"]
        with open(path_to_file) as contenido:
            clases = json.load(contenido)
            for clase in clases:
                values = clases[clase]
                for value in values:
                    if "rank" in values:
                        ranks[labels.index(value["rank"])]+=1
        chart=Chart('Radon-CC', 6, Chart.DOUGHNUT, 'Cyclomatic Complexity', json.dumps(labels), ranks)
        list_of_charts.append(chart)
        return list_of_charts

    def get_mi_charts(self, path_result):
        list_of_charts = []
        path_to_file = path_result+"/result_mi.json"
        if(not os.path.exists(path_to_file)):
            return list_of_charts
        files=[]
        mis=[]
        with open(path_to_file) as contenido:
            datos = json.load(contenido)
            for dato in datos:
                files.append(dato.rsplit('\\', 1)[1])
                values = datos[dato]
                if "mi" in values:
                    mis.append(values["mi"])
                #mis.append(values.get("mi"))
        chart=Chart('Radon-MI', 12, Chart.BAR, 'Modificability Index by Module', json.dumps(files), mis, 150)
        list_of_charts.append(chart)
        return list_of_charts

    def get_raw_charts(self, path_result):
        list_of_charts = []
        path_to_file = path_result+"/result_raw.json"
        if(not os.path.exists(path_to_file)):
            return list_of_charts
        files=[]
        comments=[]
        with open(path_to_file) as contenido:
            datos = json.load(contenido)
            for dato in datos:
                files.append(dato.rsplit('\\', 1)[1])
                values = datos[dato]
                if "comments" in values:
                    comments.append(values["comments"])
        chart=Chart('Radon-RAW', 6, Chart.BAR, 'Radon - RAW', json.dumps(files), comments)
        list_of_charts.append(chart)
        return list_of_charts

    def get_charts(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_charts = []
        list_of_charts += self.get_cc_charts(path_result)
        list_of_charts += self.get_mi_charts(path_result)
        #list_of_charts += self.get_raw_charts(path_result)
        
        return list_of_charts
    
    def _get_raw_indicators(self, path_result):
        list_of_indicators = []
        path_to_file = path_result+"/result_raw.json"
        if(not os.path.exists(path_to_file)):
            return list_of_indicators
        totalLOC=0
        totalComments=0
        with open(path_to_file) as contenido:
            datos = json.load(contenido)
            for dato in datos:
                values = datos[dato]
                if "loc" in values:
                    totalLOC+=values["loc"]
                if "multi" in values and "single_comments" in values:
                    totalComments+=values["multi"] + values["single_comments"]

        list_of_indicators.append(Indicator("radon-line-of-code", "# of lines of Code", 3, totalLOC, Indicator.DEFAULT, 0, 0, 0, 0))
        list_of_indicators.append(Indicator("radon-line-of-comments", "# of lines of Comments", 3, totalComments, Indicator.DEFAULT, 0, 0, 0, 0))
        
        return list_of_indicators
    
    def _get_cc_indicators(self, path_result):
        list_of_indicators = []
        path_to_file = path_result+"/result_cc.txt"
        if(not os.path.exists(path_to_file)):
            return list_of_indicators
        with open(path_to_file, "r") as f:
            content = f.read()

        match = re.search(r"Average complexity: ([A-Z]) \((\d+\.\d+)\)", content)
        if match:
            rank = match.group(1)
            value = round(float(match.group(2)), 2)
            # list_of_indicators.append(Indicator("radon-cyclomatic-complexity", "Cyclomatic Complexity", 3, '<h1 style="color: red;">'+rank+' ('+str(value)+')<h1>' , "color: red;"))
            list_of_indicators.append(Indicator("radon-cyclomatic-complexity", "Cyclomatic Complexity", 3, rank+' ('+str(value)+')', Indicator.DEFAULT, 0, 0, 0, 0))
        
        return list_of_indicators

    def get_indicators(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_indicators = []
        
                
        list_of_indicators+=self._get_raw_indicators(path_result)
        list_of_indicators+=self._get_cc_indicators(path_result)
        
        return list_of_indicators