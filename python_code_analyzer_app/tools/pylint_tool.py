import os, json, subprocess, re
from . import tools_status
import pylint
from pylint import lint
from .chart_class import Chart
from .indicator_class import Indicator



class Pylint_Tool:


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

			#message = re.match(r"^(.*?)\s*\(", msg).group(1)
			#category = re.search(r"\(([\w-]+)\)$", msg).group(1)
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
				rating = {"current": float(resultados[0]), "previous": float(resultados[1])}
			elif line.startswith('------------------------------------'):
				None
			else:#el caso de que sea la continuación del mensaje
				if line != "":
					detail['message'] = detail['message'] + line;
				

		result = {'details': details, 
				'rating': rating}

		with open(fileJson, 'w') as file:
			json.dump(result, file, indent=4)

	def run(self, analysis_id, repository_path, tool_name):
		print("Pylint_Tool.run()")
		print(f"Pylint_Tool.run() - repository_path: {repository_path}")
		path_result = os.path.join(repository_path+"_result",f"Analisis{analysis_id}",f"{tool_name}")

		if not os.path.exists(path_result):
		    os.makedirs(path_result)
		
		file_result_json = os.path.join(path_result,"result.json")
		file_result_text = os.path.join(path_result,"result.txt")

		print(f"Pylint_Tool.run() - path_result: {path_result}")
		# ejemplo
		# options = ["--recursive=y","--output-format=json:C:/tesis/git/result.json","C:/tesis/git/a3657248f44443498e74ba57bef673d8"]
		#options = ["--recursive=y",f"--output-format=text:{file_result}",f"{repository_path}"]

		try:
		    with open(file_result_text,"wb") as out:
		        result = subprocess.run(["pylint","--recursive=y", repository_path], stdout=out, shell=True)
			
		    self._toJson(file_result_text,file_result_json)
		    #pylint.lint.Run(options)
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
		chart=Chart('Pylint-types', 6, Chart.BAR, 'Pylint - Tipos de mensaje', tipos, valores)
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
		
		
		charts.insert(0,Chart(f"Pylint-heatmap-module", 12, Chart.MATRIX, f'Pylint - Heatmap by module', modulos, all_values,100, 'false', tipos))
			

		return charts

	def get_charts(self, path_result):
		list_of_charts = []
		path_to_file = path_result+"/result.json"
		if(not os.path.exists(path_to_file)):
			return list_of_charts

		with open(path_to_file) as contenido:
			datos = json.load(contenido)

		details = datos['details']
		list_of_charts+=self.__get_messages_by_module(details)
		list_of_charts.append(self.__get_number_of_messages_by_type(details))
		list_of_charts.append(self.__get_number_of_messages_by_symbol(details))
		
		return list_of_charts

	
	def get_indicators(self, path_result):
		list_of_indicators = []
		path_to_file = path_result+"/result.json"
		if(not os.path.exists(path_to_file)):
			return list_of_indicators

		with open(path_to_file) as contenido:
			datos = json.load(contenido)
		
		rating = datos['rating']
		list_of_indicators.append(Indicator("pylint-rating", "Rating", 3, rating["current"], Indicator.RATING, 10, 4.0, 7.0, 9.0))
		
		return list_of_indicators