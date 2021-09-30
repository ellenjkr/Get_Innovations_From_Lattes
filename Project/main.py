import numpy as np
import os
import pandas as pd
import re
import xml.etree.ElementTree as ET


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

for file in os.listdir('Resumes'):
	xml_file = ET.parse(f"Resumes/{file}")  # Open file
	xml_file = xml_file.getroot()

	granted_patents, requested_patents = get_granted_and_requested(xml_file, 'PATENTE', 'DADOS-BASICOS-DA-PATENTE', 'TITULO')
	granted_softwares, requested_softwares = get_granted_and_requested(xml_file, 'SOFTWARE', 'DADOS-BASICOS-DO-SOFTWARE', 'TITULO-DO-SOFTWARE')
	granted_brands, requested_brands = get_granted_and_requested(xml_file, 'MARCA', 'DADOS-BASICOS-DA-MARCA', 'TITULO')
	granted_industrial_designs, requested_industrial_designs = get_granted_and_requested(xml_file, 'DESENHO-INDUSTRIAL', 'DADOS-BASICOS-DO-DESENHO-INDUSTRIAL', 'TITULO')
	granted_integrated_circuit_topographies, requested_integrated_circuit_topographies = get_granted_and_requested(xml_file, 'TOPOGRAFIA-DE-CIRCUITO-INTEGRADO', 'DADOS-BASICOS-DA-TOPOGRAFIA-DE-CIRCUITO-INTEGRADO', 'TITULO')

	development_projects_tags = xml_file.findall(f".//PROJETO-DE-PESQUISA[@NATUREZA='DESENVOLVIMENTO'][@FLAG-POTENCIAL-INOVACAO='SIM']")
	development_projects = []
	for project in development_projects_tags:
		development_projects.append(project.attrib['NOME-DO-PROJETO'])

	cultivar = xml_file.findall(f".//CULTIVAR-PROTEGIDA/DADOS-BASICOS-DA-CULTIVAR[@FLAG-POTENCIAL-INOVACAO='SIM']")
	prototype_products = xml_file.findall(".//DADOS-BASICOS-DO-PRODUTO-TECNOLOGICO[@FLAG-POTENCIAL-INOVACAO='SIM'][@TIPO-PRODUTO='PROTOTIPO']")
	pilots_produts = xml_file.findall(".//DADOS-BASICOS-DO-PRODUTO-TECNOLOGICO[@FLAG-POTENCIAL-INOVACAO='SIM'][@TIPO-PRODUTO='PILOTO']")
	products = prototype_products + pilots_produts
	
	processes_and_techniques = xml_file.findall(".//DADOS-BASICOS-DO-PROCESSOS-OU-TECNICAS[@FLAG-POTENCIAL-INOVACAO='SIM']")

	# publications = []

	# innovations = xml_file.findall(".//*[@FLAG-POTENCIAL-INOVACAO='SIM']")
	# for publication in innovations:
	# 	publication_type = publication.tag
	# 	if "dados-basicos" in publication_type.lower():
	# 		re.findall(r'DADOS-BASICOS-D.{,2}-', publication_type)[0]
	# 		publication_type = re.sub(r'DADOS-BASICOS-D.{,2}-', '', publication_type).title()
	# 	else:
	# 		publication_type = publication_type.replace('-', ' ').title()
	# 		publication_type = publication_type.replace('De', 'de')
	# 		publication_type = publication_type.replace('E', 'e')
		
	# 	publications.append(publication_type)

	# values, counts = np.unique(publications, return_counts=True)
	# publications_counts = {'Tipo de Publicação': list(values), 'Quantidade': list(counts)}

	# publications_counts_df = pd.DataFrame(publications_counts)
	# print(publications_counts_df)

