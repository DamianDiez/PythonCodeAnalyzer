import os, json
import contextlib
import vulture

from python_code_analyzer_app.models import Tool
from . import tools_status
from .chart_class import Chart
from .indicator_class import Indicator

# class Vulture_Tool(Tool):

# 	class Meta:
# 		managed = False
# 		db_table = 'tool'

# 	def run(self, analysis_id, repository_path, tool_name):
# 		print("Starting Vulture_Tool.run()")
# 		print(f"Vulture_Tool.run() - repository_path: {repository_path}")

# 		path_result = os.path.join(repository_path+"_result",f"Analisis{analysis_id}",f"{tool_name}")

# 		if not os.path.exists(path_result):
# 		    os.makedirs(path_result)

# 		file_result = os.path.join(path_result,"result.txt")

# 		print(f"Vulture_Tool.run() - path_result: {path_result}")

# 		try:
# 		    v = vulture.Vulture()
# 		    v.scavenge([f"{repository_path}"])
# 		    # sys.stdout = open(file_result, "w")
# 		    with open(file_result, "w") as o:
# 		        with contextlib.redirect_stdout(o):
# 		            v.report()

# 		except BaseException as err:
# 		    print(f"Vulture_Tool.run() - Unexpected {err=}, {type(err)=}")
# 		finally:
# 		    print("Vulture_Tool.run() - Finalizado")
# 		    return tools_status.FINISHED

# 	def get_charts(self, path_result):
# 		list_of_charts = []
# 		path_to_file = path_result+"/result.txt"
# 		if(not os.path.exists(path_to_file)):
# 			return list_of_charts
# 		messages=["unused method","unused variable","unused attribute","unused class","unused import","unused function"]
# 		counter = {message: 0 for message in messages}
# 		with open(path_to_file, 'r') as archivo:
# 			for line in archivo:
# 				for message in messages:
# 					if message in line:
# 						counter[message] += 1
		
# 		list_of_charts.append(Chart('Vulture-Unused-Items', 6, Chart.BAR, 'Unused Items', json.dumps(messages), counter))
				
# 		return list_of_charts
	
# 	def get_indicators(self, path_result):
# 		list_of_indicators = []
# 		path_to_file = path_result+"/result.txt"
# 		if(not os.path.exists(path_to_file)):
# 			return list_of_indicators
# 		totalUnusedItems=0
# 		with open(path_to_file) as contenido:
# 			lines = contenido.readlines()
# 			totalUnusedItems = len(lines)
				

# 		list_of_indicators.append(Indicator("vulture-unused-items", "# of Usused Items", 3, totalUnusedItems, Indicator.DEFAULT, 0, 0, 0, 0))
# 		#list_of_indicators.append(Indicator("radon-line-of-comments", "# of lines of Comments", 3, totalComments, Indicator.DEFAULT, 0, 0, 0, 0))
# 		return list_of_indicators