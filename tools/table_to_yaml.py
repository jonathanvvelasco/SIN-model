"""Converte a planilha Dados_MDI_PDE_2034_Referência.xlsm em YAML.

O arquivo gerado segue uma estrutura simples por abas, semelhante a um dump
de planilha para consumo posterior.
"""

from pathlib import Path
from typing import Any

import pandas as pd
import yaml



INPUT_TABLE = path = Path(__file__).resolve().parent.parent / "tools" / "technology_table.csv"
OUTPUT_YAML = Path(__file__).resolve().parent.parent / "inputs" / "pde_generated_input.yaml"
BASE_YAML = Path(__file__).resolve().parent.parent / "inputs" / "pde_test_inputs.yaml"

def table_to_df(table_path: Path) -> pd.DataFrame:
	"""Read specified sheets (or all if None) from workbook and return dict.

	Only the requested sheets in `sheets` will be read. Missing sheets are
	ignored.
	"""
	result: dict[str, Any] = {"source_file": str(table_path), "sheets": {}}
	tab = pd.read_csv(table_path)

	return tab

def _update_param(base_data: dict, table_data: pd.DataFrame, param: str):
	'''Atualiza a demanda por ano e subsistema no dicionário base_data com base na aba Demanda NW do table_data.'''

	for node in base_data['general']['nodes']:
		table_node = table_data.loc[table_data["system"] == node]
		tecs_to_read = table_node["technology"].unique()
		for technology in tecs_to_read:
			base_data[param][node][technology] = float(table_node.loc[table_node["technology"] == technology, param].values[0])
	
	return base_data

def _update_costs(base_data, table_data):
	'''Atualiza os custos de investimento e operação no dicionário base_data com base na aba GERAL do table_data.'''
	tecnologias = table_data['sheets']["GERAL"]["tecnologias"]
	cambio = table_data['sheets']["GERAL"]["param"]["Cambio"][0]
	horas = table_data['sheets']["GERAL"]["config"]["Horas no mês"][0]
	mwh2Gwa = horas / 1000  # From MWh to GWa

	for node, tecs in dic_t.items():
		for tec, tec_pde in tecs.items():
			inv_cost = tecnologias[tecnologias["technology"]==tec_pde]["inv_cost_brl"].values[0] if not pd.isna(tecnologias[tecnologias["technology"]==tec_pde]["inv_cost_brl"].values[0]) else 9999
			
			om_cost = tecnologias[tecnologias["technology"]==tec_pde]["O&M_fix_brl"].values[0] if not pd.isna(tecnologias[tecnologias["technology"]==tec_pde]["O&M_fix_brl"].values[0]) else 9999
			ess_cost = tecnologias[tecnologias["technology"]==tec_pde]["ess_fix_brl"].values[0] if not pd.isna(tecnologias[tecnologias["technology"]==tec_pde]["ess_fix_brl"].values[0]) else 9999	
			fix_cost = om_cost + ess_cost
			
			var_cost = tecnologias[tecnologias["technology"]==tec_pde]["cvu_brl"].values[0] if not pd.isna(tecnologias[tecnologias["technology"]==tec_pde]["cvu_brl"].values[0]) else 0

			base_data['costs']['inv_cost'][node][tec] = int(inv_cost/cambio)
			base_data['costs']['fix_cost'][node][tec] = int(fix_cost/cambio)
			base_data['costs']['var_cost'][node][tec] = int(var_cost*mwh2Gwa/cambio)

	return base_data

def dados_pde_para_yaml(base_data, table_data: dict[str, Any]) -> dict[str, Any]:
	'''Atualiza o dicionário base_data com os dados das planilhas, mantendo a estrutura do YAML.'''

	# base_data = _update_capacity_factor(base_data, table_data)
	base_data = _update_param(base_data, table_data, "capacity_factor")
	# base_data = _update_costs(base_data, table_data)
	
	return base_data

def main() -> None:
	if not INPUT_TABLE.exists():
		raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_TABLE}")

	OUTPUT_YAML.parent.mkdir(parents=True, exist_ok=True)

	# load base YAML (template) if available
	base_data: dict[str, Any] = {}
	if BASE_YAML.exists():
		with BASE_YAML.open("r", encoding="utf-8") as bf:
			base_data = yaml.safe_load(bf) or {}

	# read only requested sheets from xlsm
	table_data = table_to_df(INPUT_TABLE)

	yaml_content = yaml.dump(
		dados_pde_para_yaml(base_data, table_data),
		allow_unicode=True,
		sort_keys=False,
		default_flow_style=False,
	)
	
	OUTPUT_YAML.write_text(yaml_content, encoding="utf-8")

	print(f"YAML gerado em: {OUTPUT_YAML}")


if __name__ == "__main__":
	main()
