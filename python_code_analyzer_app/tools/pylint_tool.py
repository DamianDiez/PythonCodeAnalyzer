import os
from . import tools_status
import pylint
from pylint import lint


class Pylint_Tool:
	def run(self, analysis_id, repository_path, tool_name):
		print("Pylint_Tool.run()")
		print(f"Pylint_Tool.run() - repository_path: {repository_path}")
		path_result = os.path.join(repository_path+"_result",f"Analisis{analysis_id}",f"{tool_name}")

		if not os.path.exists(path_result):
		    os.makedirs(path_result)

		file_result = os.path.join(path_result,"result.json")

		print(f"Pylint_Tool.run() - path_result: {path_result}")
		# ejemplo
		# options = ["--recursive=y","--output-format=json:C:/tesis/git/result.json","C:/tesis/git/a3657248f44443498e74ba57bef673d8"]
		options = ["--recursive=y",f"--output-format=json:{file_result}",f"{repository_path}"]

		try:
		    pylint.lint.Run(options)
		except BaseException as err:
		    print(f"Pylint_Tool.run() - Unexpected {err=}, {type(err)=}")
		finally:
		    print("Pylint_Tool.run() - Finalizado")
		    return tools_status.FINISHED