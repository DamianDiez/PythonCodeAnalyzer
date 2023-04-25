import os, json, subprocess
from . import tools_status
from .chart_class import Chart
from .indicator_class import Indicator

#a function to calculate fibonacci sucecion?

class Radon_Tool:
	def run(self, analysis_id, repository_path, tool_name):
		print("Starting Radon_Tool.run()")
		print(f"Starting Radon_Tool.run() - analysis_id: {analysis_id}")
		print(f"Starting Radon_Tool.run() - tool_name: {tool_name}")
		print(f"Radon_Tool.run() - repository_path: {repository_path}")
		path_result = os.path.join(repository_path+"_result",f"Analisis{analysis_id}",f"{tool_name}")
		if not os.path.exists(path_result):
		    os.makedirs(path_result)
		file_result_cc = os.path.join(path_result,"result_cc.json")
		file_result_mi = os.path.join(path_result,"result_mi.json")
		file_result_raw = os.path.join(path_result,"result_raw.json")

		try:
		    with open(file_result_cc,"wb") as out:
		        result = subprocess.run(["radon","cc", '-s', '-j', repository_path], stdout=out, shell=True)
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
		print("Radon_Tool.get_cc_charts")
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
					ranks[labels.index(value["rank"])]+=1
		chart=Chart('Radon-CC', 6, Chart.DOUGHNUT, 'Cyclomatic Complexity', json.dumps(labels), ranks)
		list_of_charts.append(chart)
		return list_of_charts

	def get_mi_charts(self, path_result):
		print("Radon_Tool.get_mi_charts")
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
				mis.append(values["mi"])
				#mis.append(values.get("mi"))
		chart=Chart('Radon-MI', 6, Chart.BAR, 'Radon - MI', json.dumps(files), mis)
		list_of_charts.append(chart)
		return list_of_charts

	def get_raw_charts(self, path_result):
		print("Radon_Tool.get_raw_charts")
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
				comments.append(values["comments"])
		chart=Chart('Radon-RAW', 6, Chart.BAR, 'Radon - RAW', json.dumps(files), comments)
		list_of_charts.append(chart)
		return list_of_charts

	def get_charts(self, path_result):

		list_of_charts = []
		list_of_charts += self.get_cc_charts(path_result)
		list_of_charts += self.get_mi_charts(path_result)
		list_of_charts += self.get_raw_charts(path_result)
		
		return list_of_charts
	
	def get_indicators(self, path_result):
		list_of_indicators = []
		path_to_file = path_result+"/result_raw.json"
		if(not os.path.exists(path_to_file)):
			return list_of_indicators
		comments=[]
		totalLOC=0
		totalComments=0
		with open(path_to_file) as contenido:
			datos = json.load(contenido)
			for dato in datos:
				values = datos[dato]
				comments.append(values["comments"])
				totalLOC+=values["loc"]
				totalComments+=values["multi"] + values["single_comments"]
				

		list_of_indicators.append(Indicator("radon-line-of-code", "# of lines of Code", 3, totalLOC, Indicator.DEFAULT, 0, 0, 0, 0))
		#list_of_indicators.append(Indicator("radon-line-of-comments", "# of lines of Comments", 3, totalComments, Indicator.DEFAULT, 0, 0, 0, 0))
		return list_of_indicators