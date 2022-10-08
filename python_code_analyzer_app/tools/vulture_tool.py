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