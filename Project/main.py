import os
import pandas as pd
import xml.etree.ElementTree as ET

from excel import Excel


def build_production_dict(productions, production_type, weight):
	production_dict = {'Título': productions}
	production_df = pd.DataFrame(production_dict)
	production_df['Tipo de Produção'] = production_type
	production_df['Peso'] = weight
	production_df['Comprovado'] = 0
	production_df['Pontos'] = ''

	production_df = production_df[['Tipo de Produção', 'Título', 'Peso', 'Comprovado', 'Pontos']]  # Rearrange columns
	
	return production_df


def get_granted_and_requested(xml_file, xml_path, basic_data_path, title_attrib_name):
	granted_patents = []
	requested_patents = []

	patents = xml_file.findall(f".//{xml_path}")
	for patent in patents:
		if patent.findall(f".//{basic_data_path}[@FLAG-POTENCIAL-INOVACAO='SIM']") != []:
			title = patent.findall(f".//{basic_data_path}")[0].attrib[title_attrib_name]
			if patent.findall(".//REGISTRO-OU-PATENTE") != []:
				register = patent.findall(".//REGISTRO-OU-PATENTE")[0]
				if register.attrib['DATA-DE-CONCESSAO'] != '':
					granted_patents.append(title)
				elif register.attrib['DATA-PEDIDO-DE-DEPOSITO'] != '' or register.attrib['DATA-DEPOSITO-PCT'] != '':
					requested_patents.append(title)
				else:
					all_status = patent.findall(".//HISTORICO-SITUACOES-PATENTE")
					if all_status != []:
						granted = True if patent.findall(".//HISTORICO-SITUACOES-PATENTE[@DESCRICAO-SITUACAO-PATENTE='Concessão']") != [] else False

						if granted is True:
							granted_patents.append(title)
						else:
							requested_patents.append(title)

	return (granted_patents, requested_patents)


def get_proudctions(xml_path, title_attrib_name):
	productions_tags = xml_file.findall(f".//{xml_path}[@FLAG-POTENCIAL-INOVACAO='SIM']")
	productions = []
	for production in productions_tags:
		productions.append(production.attrib[title_attrib_name])

	return productions

innovation_productions = {'Researcher': [], 'Productions': []}
for file in os.listdir('Resumes'):
	xml_file = ET.parse(f"Resumes/{file}")  # Open file
	xml_file = xml_file.getroot()

	granted_patents, requested_patents = get_granted_and_requested(xml_file, 'PATENTE', 'DADOS-BASICOS-DA-PATENTE', 'TITULO')
	granted_patents_df = build_production_dict(granted_patents, 'Patente concedida', 120)
	requested_patents_df = build_production_dict(requested_patents, 'Patente solicitada', 40)

	granted_brands, requested_brands = get_granted_and_requested(xml_file, 'MARCA', 'DADOS-BASICOS-DA-MARCA', 'TITULO')
	granted_brands_df = build_production_dict(granted_brands, 'Marca concedida', 40)
	requested_brands_df = build_production_dict(requested_brands, 'Marca solicitada', 20)

	granted_softwares, requested_softwares = get_granted_and_requested(xml_file, 'SOFTWARE', 'DADOS-BASICOS-DO-SOFTWARE', 'TITULO-DO-SOFTWARE')
	granted_softwares_df = build_production_dict(granted_softwares, 'Programa de computador registrado', 60)

	granted_industrial_designs, requested_industrial_designs = get_granted_and_requested(xml_file, 'DESENHO-INDUSTRIAL', 'DADOS-BASICOS-DO-DESENHO-INDUSTRIAL', 'TITULO')
	granted_industrial_designs_df = build_production_dict(granted_industrial_designs, 'Desenho industrial registrado', 40)
	requested_industrial_designs_df = build_production_dict(requested_industrial_designs, 'Desenho industrial solicitado', 20)

	cultivar = get_proudctions("CULTIVAR-PROTEGIDA/DADOS-BASICOS-DA-CULTIVAR", 'DENOMINACAO')
	cultivar_df = build_production_dict(cultivar, 'Cultivar protegida', 120)

	granted_integrated_circuit_topographies, requested_integrated_circuit_topographies = get_granted_and_requested(xml_file, 'TOPOGRAFIA-DE-CIRCUITO-INTEGRADO', 'DADOS-BASICOS-DA-TOPOGRAFIA-DE-CIRCUITO-INTEGRADO', 'TITULO')
	granted_integrated_circuit_topographies_df = build_production_dict(granted_integrated_circuit_topographies, 'Topografia de circuito integrado registrado', 50)

	prototype_products = get_proudctions("DADOS-BASICOS-DO-PRODUTO-TECNOLOGICO[@TIPO-PRODUTO='PROTOTIPO']", 'TITULO-DO-PRODUTO')
	pilots_produts = get_proudctions("DADOS-BASICOS-DO-PRODUTO-TECNOLOGICO[@TIPO-PRODUTO='PILOTO']", 'TITULO-DO-PRODUTO')
	products = prototype_products + pilots_produts
	products_df = build_production_dict(products, 'Produtos (protótipos e pilotos)', 40)

	processes_and_techniques = get_proudctions("DADOS-BASICOS-DO-PROCESSOS-OU-TECNICAS", 'TITULO-DO-PROCESSO')
	processes_and_techniques_df = build_production_dict(processes_and_techniques, 'Processos ou técnicas', 40)

	development_projects = get_proudctions("PROJETO-DE-PESQUISA[@NATUREZA='DESENVOLVIMENTO']", 'NOME-DO-PROJETO')
	development_projects_df = build_production_dict(development_projects, 'Projeto de desenvolvimento tecnológico', 40)

	all_productions = pd.concat([granted_patents_df, requested_patents_df, granted_brands_df, requested_brands_df, granted_softwares_df, granted_industrial_designs_df, requested_industrial_designs_df, cultivar_df, granted_integrated_circuit_topographies_df, products_df, processes_and_techniques_df, development_projects_df])

	innovation_productions['Researcher'].append(file.replace('.xml', ''))
	innovation_productions['Productions'].append(all_productions)

excel = Excel(innovation_productions)
excel.build_file()
excel.save('inovações.xlsx')