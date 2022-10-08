import os
import subprocess
from . import tools_status

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