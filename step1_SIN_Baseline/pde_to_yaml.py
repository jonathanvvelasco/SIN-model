"""Converte a planilha Dados_MDI_PDE_2034_Referência.xlsm em YAML.

O arquivo gerado segue uma estrutura simples por abas, semelhante a um dump
de planilha para consumo posterior.
"""

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


INPUT_XLSM = Path(r"C:\GitHub\SIN-model\7. Brasil inputs\data EPE\Dados_MDI_PDE_2034_Referência.xlsm")
OUTPUT_YAML = Path(r"C:\GitHub\SIN-model\inputs\pde_generated_input.yaml")
# sheets explicitly requested by user
SHEETS_TO_READ = ["GERAL", "Renov Ind.", "Demanda NW"]
# base YAML to use as template
BASE_YAML = Path(r"C:\GitHub\SIN-model\inputs\pde_test_inputs.yaml")


def _clean_value(value: Any) -> Any:
	if pd.isna(value):
		return None
	if isinstance(value, pd.Timestamp):
		return value.isoformat()
	if hasattr(value, "item"):
		try:
			return value.item()
		except Exception:
			return value
	return value

def _normalize_demanda_sheet(demanda: pd.DataFrame) -> pd.DataFrame:
	"""Propagate the subsystem number through valid rows in the demand sheet."""
	if demanda.empty or demanda.shape[1] < 2:
		return demanda

	primeira_coluna = demanda.columns[0]
	segunda_coluna = demanda.columns[1]
	rows: list[pd.Series] = []
	subsistema_atual: Any = 1
	aguarda_numero_subsistema = False

	for _, row in demanda.iterrows():
		valor_segunda_coluna = row[segunda_coluna]

		if isinstance(valor_segunda_coluna, str) and valor_segunda_coluna.strip().upper() == "POS":
			aguarda_numero_subsistema = True
			continue

		if aguarda_numero_subsistema:
			if pd.notna(valor_segunda_coluna):
				subsistema_atual = _clean_value(valor_segunda_coluna)
			aguarda_numero_subsistema = False
			continue

		linha = row.copy()
		linha[primeira_coluna] = subsistema_atual
		rows.append(linha)

	return pd.DataFrame(rows, columns=demanda.columns).reset_index(drop=True)

def workbook_to_dict(xlsm_path: Path, sheets: list[str] | None = None) -> dict[str, Any]:
	"""Read specified sheets (or all if None) from workbook and return dict.

	Only the requested sheets in `sheets` will be read. Missing sheets are
	ignored.
	"""
	result: dict[str, Any] = {"source_file": str(xlsm_path), "sheets": {}}
	xls = pd.ExcelFile(xlsm_path, engine="openpyxl")

	if sheets is None:
		sheet_names = xls.sheet_names
	else:
		# keep only sheets that actually exist in the workbook
		sheet_names = [s for s in sheets if s in xls.sheet_names]

	# Aba inicial
	subsistemas_14_orig = pd.read_excel(xlsm_path, sheet_name="Inicial", skiprows=17, usecols="A:N", engine='calamine').head(1)
	subsistemas_dic = {
		# Relaciona os 14 subsistemas do PDE com os 4 subsistemas do modelo de forma agregada
		'NORDESTE': 	'Northeast',
		'IMPERATRIZ': 	'Northeast',
		'NORTE': 		'North', 
		'MAN AP BV': 'North',
		'B. MONTE': 'North',
		'XINGU': 'North',
		'SUDESTE': 'Southeast',
		'ITAIPU': 'Southeast', 
		'AC RO': 'Southeast',
		'T. PIRES': 'Southeast',
		'PARANA': 'Southeast',
		'TAPAJOS': 'Southeast',
		'SUL': 'South',
		'IVAIPORA': 'South',
	}
	subsistemas_14 = subsistemas_14_orig.replace(subsistemas_dic)
	subsistemas_por_codigo = {
		indice + 1: valor
		for indice, valor in enumerate(subsistemas_14.iloc[0].tolist())
	}
	result["sheets"]["Inicial"] = subsistemas_por_codigo

	# Aba geral
	pde_input       	= pd.read_excel(xlsm_path, sheet_name="GERAL", skiprows=14, usecols="B:P", engine='calamine').squeeze()
	pde_input.columns 	= ["technology", "lifetime", "inv_cost_brl", "ess_fix_brl", "inv_month", "O&M_fix_brl", "fix_month", "month_brl", "cvu_brl", "inflex_pdis", "inflex_ptot", "year_exp", "jdc", "teif", "ip"]
	pde_par         	= pd.read_excel(xlsm_path, sheet_name="GERAL", skiprows=3, usecols="B:C", engine='calamine').iloc[0:6].T.set_index(0)
	pde_par.columns 	= pde_par.iloc[0]
	pde_par         	= pde_par[1:].reset_index(drop=True)
	pde_config      	= pd.read_excel(xlsm_path, sheet_name="GERAL", skiprows=0, usecols="F:G", engine='calamine').iloc[0:6].T.set_index(0)
	pde_config.columns 	= pde_config.iloc[0]
	pde_config      	= pde_config[1:].reset_index(drop=True)
	result["sheets"]["GERAL"] = {"tecnologias": pde_input.to_dict(), 
								"param": pde_par.to_dict(orient="list"), 
								"config": pde_config.to_dict(orient="list")}

	# Aba Demanda
	demanda = pd.read_excel(xlsm_path, sheet_name="Demanda NW", skiprows=2, usecols="A:N", engine='calamine')
	demanda.columns = ["sistema", "ano", "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
	demanda = _differentiate_and_clean_demanda(demanda) if False else demanda
	demanda = _normalize_demanda_sheet(demanda)
	demanda['sistema'] = demanda['sistema'].map(subsistemas_por_codigo)
	result["sheets"]["Demanda NW"] = demanda.to_dict(orient="list")

	# Aba Renov Ind.
	renov_ind = pd.read_excel(xlsm_path, sheet_name="Renov Ind.", skiprows=1, usecols="A:R", engine='calamine')
	result["sheets"]["Renov Ind."] = renov_ind.to_dict(orient="list")

	return result

def _update_study_horizon(base_data, sheets_data):
	'''Atualiza o horizonte de estudo no dicionário base_data com base na aba GERAL do sheets_data.'''
	config = sheets_data['sheets']["GERAL"]["config"]
	base_data['general']['horizon'] = [i for i in range(config["Inicio da Simulação"][0].year, config["Final da Simulação"][0].year + 1)]

	return base_data

def _update_demand(base_data, sheets_data, time_frame="yearly"):
	'''Atualiza a demanda por ano e subsistema no dicionário base_data com base na aba Demanda NW do sheets_data.'''
	demanda = pd.DataFrame(sheets_data['sheets']["Demanda NW"])

	if time_frame == "yearly":
		# Fazendo demanda anual
		colunas_mensais = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
		demanda["val"] = demanda[colunas_mensais].sum(axis=1)/(730.5*len(colunas_mensais))  # From GWh to GWa
		demanda = demanda.drop(columns=colunas_mensais)
		demanda = demanda.groupby(["sistema", "ano"], as_index=False)["val"].sum()

	for node in base_data['general']['nodes']:
		demanda_node = demanda.loc[demanda["sistema"] == node]
		demanda_por_ano = demanda_node.groupby("ano")["val"].sum()
		base_data['general']['demand_per_year'][node] = [float(demanda_por_ano.get(ano, 0)) for ano in base_data['general']['horizon']]
	
	return base_data

def dados_pde_para_yaml(base_data, sheets_data: dict[str, Any]) -> dict[str, Any]:
	'''Atualiza o dicionário base_data com os dados das planilhas, mantendo a estrutura do YAML.'''

	base_data = _update_study_horizon(base_data, sheets_data)
	base_data = _update_demand(base_data, sheets_data)
	
	return base_data

def main() -> None:
	if not INPUT_XLSM.exists():
		raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_XLSM}")

	OUTPUT_YAML.parent.mkdir(parents=True, exist_ok=True)

	# load base YAML (template) if available
	base_data: dict[str, Any] = {}
	if BASE_YAML.exists():
		with BASE_YAML.open("r", encoding="utf-8") as bf:
			base_data = yaml.safe_load(bf) or {}

	# read only requested sheets from xlsm
	sheets_data = workbook_to_dict(INPUT_XLSM, sheets=SHEETS_TO_READ)

	yaml_content = yaml.dump(
		dados_pde_para_yaml(base_data, sheets_data),
		allow_unicode=True,
		sort_keys=False,
		default_flow_style=False,
	)
	
	OUTPUT_YAML.write_text(yaml_content, encoding="utf-8")

	print(f"YAML gerado em: {OUTPUT_YAML}")


if __name__ == "__main__":
	main()
