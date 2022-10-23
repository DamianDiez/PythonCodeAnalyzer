import os, json
from . import tools_status
import pylint
from pylint import lint
from .chart_class import Chart



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

	def __get_number_of_messages_by_type(self,datos):
		print("get_amount_of_messages_by_type")
		
		tipos = [x['type'] for x in datos]
		tipos=list(set(tipos))
		#cantidad de elementos de cada tipo
		valores = []
		for tipo in tipos:
		    valores.append( sum(x['type']==tipo for x in datos) )
		chart=Chart('Pylint-types', 1, Chart.BAR, 'Pylint - Tipos de mensaje', tipos, valores)
		return chart

	def __get_number_of_messages_by_symbol(self,datos):
		print("get_amount_of_messages_by_type")
		
		symbols = [x['symbol'] for x in datos]
		symbols=list(set(symbols))
		#cantidad de elementos de cada tipo
		valores = []
		for symbol in symbols:
		    valores.append( sum(x['symbol']==symbol for x in datos) )
		display_legend = True
		if len(symbol)>10:
			display_legend = 'false'
		chart=Chart('Pylint-symbols', 1, Chart.PIE, 'Pylint - Tipos de mensaje', symbols, valores, display_legend)
		return chart

	def __get_number_of_msg_type_by_module(self, msg_type, datos):
		print("get_amount_of_messages_by_type")
		
		modulos = [x['module'] for x in datos]
		modulos=list(set(modulos))
		#cantidad de elementos de cada tipo
		valores = []
		for modulo in modulos:
		    valores.append( sum(x['type']==msg_type and x['module'] ==modulo for x in datos) )
		chart=Chart(f"Pylint-{msg_type}-module", 1, Chart.BAR, f'Pylint - {msg_type}s by module', modulos, valores)
		return chart

	def __get_messages_by_module(self, datos):
		charts = []
		tipos = [x['type'] for x in datos]
		tipos=list(set(tipos))
		for tipo in tipos:
			charts.append(self.__get_number_of_msg_type_by_module(tipo,datos))
		return charts

	def get_charts(self, path_result):
		print("Pylint_Tool.get_charts()")
		list_of_charts = []
		path_to_file = path_result+"/result.json"
		if(not os.path.exists(path_to_file)):
			return list_of_charts

		with open(path_to_file) as contenido:
			datos = json.load(contenido)
		list_of_charts.append(self.__get_number_of_messages_by_type(datos))
		list_of_charts.append(self.__get_number_of_messages_by_symbol(datos))
		list_of_charts+=self.__get_messages_by_module(datos)
		
		return list_of_charts

	