"""Converte a planilha Dados_MDI_PDE_2034_Referência.xlsm em YAML.

O arquivo gerado segue uma estrutura simples por abas, semelhante a um dump
de planilha para consumo posterior.
"""

from __future__ import annotations

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

    # Aba geral
    pde_input       = pd.read_excel(xlsm_path, sheet_name="GERAL", skiprows=14, usecols="B:P", engine='calamine').squeeze()
    pde_par         = pd.read_excel(xlsm_path, sheet_name="GERAL", skiprows=3, usecols="B:C", engine='calamine').iloc[0:6].T.set_index(0)
    pde_par.columns = pde_par.iloc[0]
    pde_par         = pde_par[1:].reset_index(drop=True)
    result["sheets"]["GERAL"] = {"tecnologias": pde_input.to_dict(), "param": pde_par.to_dict(orient="list")}

    # Aba Demanda
    demanda = pd.read_excel(xlsm_path, sheet_name="Demanda NW", skiprows=2, usecols="A:N", engine='calamine')
    demanda = _normalize_demanda_sheet(demanda)
    result["sheets"]["Demanda NW"] = demanda.to_dict(orient="list")

    # Aba Renov Ind.
    renov_ind = pd.read_excel(xlsm_path, sheet_name="Renov Ind.", skiprows=1, usecols="A:R", engine='calamine')
    result["sheets"]["Renov Ind."] = renov_ind.to_dict(orient="list")

    return result


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

	# attach sheets under a dedicated key so base structure is preserved
	base_data.setdefault("pde_sheets", {})
	base_data["pde_sheets"].update(sheets_data.get("sheets", {}))

	with OUTPUT_YAML.open("w", encoding="utf-8") as f:
		yaml.safe_dump(
			base_data,
			f,
			allow_unicode=True,
			sort_keys=False,
			default_flow_style=False,
		)

	print(f"YAML gerado em: {OUTPUT_YAML}")


if __name__ == "__main__":
	main()
