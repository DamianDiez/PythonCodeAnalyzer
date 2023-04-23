import os
import subprocess
import contextlib
import vulture
from . import tools_status

class Vulture_Tool:
	def run(self, analysis_id, repository_path, tool_name):
		print("Starting Vulture_Tool.run()")
		print(f"Vulture_Tool.run() - repository_path: {repository_path}")

		path_result = os.path.join(repository_path+"_result",f"Analisis{analysis_id}",f"{tool_name}")

		if not os.path.exists(path_result):
		    os.makedirs(path_result)

		file_result = os.path.join(path_result,"result.txt")

		print(f"Vulture_Tool.run() - path_result: {path_result}")

		try:
		    v = vulture.Vulture()
		    v.scavenge([f"{repository_path}"])
		    # sys.stdout = open(file_result, "w")
		    with open(file_result, "w") as o:
		        with contextlib.redirect_stdout(o):
		            v.report()

		except BaseException as err:
		    print(f"Vulture_Tool.run() - Unexpected {err=}, {type(err)=}")
		finally:
		    print("Vulture_Tool.run() - Finalizado")
		    return tools_status.FINISHED

	def get_charts(self, path_result):
		list_of_charts = []
		# path_result = path_to_file+"/Radon/result_cc.json"
		# ranks=[0,0,0,0,0,0]
		# with open(path_result) as contenido:
		#     clases = json.load(contenido)
		#     for clase in clases:
		#         values = clases[clase]
		#         # print(values)
		#         for value in values:
		#             _type=value["type"]
		#             if(value["rank"]=='A'):
		#                 ranks[0]+=1
		#             if(value["rank"]=='B'):
		#                 ranks[1]+=1
		#             if(value["rank"]=='C'):
		#                 ranks[2]+=1
		#             if(value["rank"]=='D'):
		#                 ranks[3]+=1
		#             if(value["rank"]=='E'):
		#                 ranks[4]+=1
		#             if(value["rank"]=='F'):
		#                 ranks[5]+=1
		# chart=Chart('chart1', 0, 'pie', 'Cyclomatic Complexity', json.dumps(["A","B","C","D","E","F"]), ranks)
		# list_of_charts.append(chart)
		return list_of_charts
	
	def get_indicators(self, path_result):
		list_of_indicators = []
		return list_of_indicators