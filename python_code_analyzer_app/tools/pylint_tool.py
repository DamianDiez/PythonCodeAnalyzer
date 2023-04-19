import os, json
from . import tools_status
import pylint
from pylint import lint
from .chart_class import Chart, Cell



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
		tipos = [x['type'] for x in datos]
		tipos=sorted(list(set(tipos)),key=str.lower)
		#cantidad de elementos de cada tipo
		valores = []
		for tipo in tipos:
		    valores.append( sum(x['type']==tipo for x in datos) )
		chart=Chart('Pylint-types', 1, Chart.BAR, 'Pylint - Tipos de mensaje', tipos, valores)
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
		chart=Chart('Pylint-symbols', 1, Chart.PIE, 'Pylint - Tipos de mensaje', symbols, valores, display_legend)
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
		
		
		charts.insert(0,Chart(f"Pylint-heatmap-module", 1, Chart.MATRIX, f'Pylint - Heatmap by module', modulos, all_values, 'false', tipos))
			

		return charts

	def get_charts(self, path_result):
		list_of_charts = []
		path_to_file = path_result+"/result.json"
		if(not os.path.exists(path_to_file)):
			return list_of_charts

		with open(path_to_file) as contenido:
			datos = json.load(contenido)
		
		list_of_charts+=self.__get_messages_by_module(datos)
		list_of_charts.append(self.__get_number_of_messages_by_type(datos))
		list_of_charts.append(self.__get_number_of_messages_by_symbol(datos))
		
		return list_of_charts

	