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
    primeira_coluna = demanda.columns[0]
    demanda[primeira_coluna] = demanda[primeira_coluna].ffill()
    result["sheets"]["Demanda NW"] = {"demanda": demanda.to_dict(orient="list")}

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
