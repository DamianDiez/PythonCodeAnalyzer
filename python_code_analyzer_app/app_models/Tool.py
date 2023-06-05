import contextlib
import re
from django.db import models
import json
import os
import subprocess
import vulture
from python_code_analyzer_app.app_models import tools_status
from python_code_analyzer_app.tools.IdicatorDefault import IndicatorDefault
from python_code_analyzer_app.tools.IndicatorRating import IndicatorRating
from python_code_analyzer_app.tools.ResultItem import SizeOptions, Template
from python_code_analyzer_app.tools.chart_class import Chart


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

    def get_result(self, analysis_tool):
        pass


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
                    detail['message'] = detail['message'] + line
                

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
        chart=Chart('Pylint-types', SizeOptions.MEDIUM, Template.CHART_DEFAULT, Tool.PYLINT, Chart.BAR, '# of Messages by Type', tipos, valores)
        return chart

    def __get_number_of_msg_type_by_module(self, msg_type, datos, modulos):
        #cantidad de elementos de cada tipo
        valores = []
        for modulo in modulos:
            valores.append( sum(x['type']==msg_type and x['module'] ==modulo for x in datos) )
        return valores

    def __get_messages_by_module(self, datos):
        charts = []
        tipos = [x['type'] for x in datos]
        tipos=sorted(list(set(tipos)),key=str.lower)
        modulos = [x['module'] for x in datos]
        modulos=sorted(list(set(modulos)),key=str.lower)
        all_values = []
        for tipo in tipos:
            valores = self.__get_number_of_msg_type_by_module( tipo, datos, modulos)		
            for i in range(len(modulos)):
                all_values.append({"x": modulos[i], "y": tipo, "v": valores[i]})
        charts.insert(0,Chart(f"Pylint-heatmap-module", SizeOptions.LARGE, Template.CHART_MATRIX, Tool.PYLINT, Chart.MATRIX, f'Heatmap by Module', modulos, all_values,100, 'false', tipos))
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
        list_of_indicators.append(IndicatorRating("pylint-rating", "Rating", SizeOptions.SMALL, rating["current"], Tool.PYLINT, 10, 4.0, 7.0, 9.0))
        details = datos['details']
        modulos = [x['module'] for x in details]
        modulos=sorted(list(set(modulos)),key=str.lower)
        list_of_indicators.append(IndicatorDefault("pylint-modules", "# of Modules", SizeOptions.SMALL, len(modulos), Tool.PYLINT))
        
        return list_of_indicators
    
    def get_result(self, analysis_tool):
        result_items=[]
        result_items+=self.get_indicators(analysis_tool)
        result_items+=self.get_charts(analysis_tool)
        
        return result_items
    
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
        if(not os.path.exists(path_to_file)):
            return list_of_charts
        messages=["unused method","unused variable","unused attribute","unused class","unused import","unused function"]
        counter = {message: 0 for message in messages}
        with open(path_to_file, 'r') as archivo:
            for line in archivo:
                for message in messages:
                    if message in line:
                        counter[message] += 1
        
        list_of_charts.append(Chart('Vulture-Unused-Items', SizeOptions.MEDIUM, Template.CHART_DEFAULT, Tool.VULTURE, Chart.BAR, 'Unused Items', json.dumps(messages), counter))

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
                

        list_of_indicators.append(IndicatorDefault("vulture-unused-items", "# of Usused Items", SizeOptions.SMALL, totalUnusedItems, Tool.VULTURE))
        return list_of_indicators
    
    def get_result(self, analysis_tool):
        result_items=[]
        result_items+=self.get_indicators(analysis_tool)
        result_items+=self.get_charts(analysis_tool)
        
        return result_items


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
        chart=Chart('Radon-CC', SizeOptions.MEDIUM, Template.CHART_DEFAULT, Tool.RADON, Chart.DOUGHNUT, 'Cyclomatic Complexity', json.dumps(labels), ranks)
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
        chart=Chart('Radon-MI', SizeOptions.LARGE, Template.CHART_DEFAULT, Tool.RADON, Chart.BAR, 'Modificability Index by Module', json.dumps(files), mis, 150)
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
        chart=Chart('Radon-RAW', SizeOptions.MEDIUM, Template.CHART_DEFAULT, Tool.RADON, Chart.BAR, 'Radon - RAW', json.dumps(files), comments)
        list_of_charts.append(chart)
        return list_of_charts

    def get_charts(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_charts = []
        list_of_charts += self.get_cc_charts(path_result)
        list_of_charts += self.get_mi_charts(path_result)
        
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

        list_of_indicators.append(IndicatorDefault("radon-line-of-code", "# of lines of Code", SizeOptions.SMALL, totalLOC, Tool.RADON))
        list_of_indicators.append(IndicatorDefault("radon-line-of-comments", "# of lines of Comments", SizeOptions.SMALL, totalComments, Tool.RADON))
        
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
            list_of_indicators.append(IndicatorDefault("radon-cyclomatic-complexity", "Cyclomatic Complexity", SizeOptions.SMALL, rank+' ('+str(value)+')', Tool.RADON))
        
        return list_of_indicators

    def get_indicators(self, analysis_tool):
        path_result = analysis_tool.get_path_result_analysis()+self.name
        list_of_indicators = []
        
                
        list_of_indicators+=self._get_raw_indicators(path_result)
        list_of_indicators+=self._get_cc_indicators(path_result)
        
        return list_of_indicators
    
    def get_result(self, analysis_tool):
        result_items=[]
        result_items+=self.get_indicators(analysis_tool)
        result_items+=self.get_charts(analysis_tool)
        
        return result_items