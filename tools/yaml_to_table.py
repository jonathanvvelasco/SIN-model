from pathlib import Path

import yaml
import pandas as pd

input_file = "pde_generated_input.yaml"
# input_file = "pde_test_inputs.yaml"

# Open input data relative to this script, not the current working directory.
path = Path(__file__).resolve().parent.parent / "inputs" / input_file
with path.open("r", encoding="utf-8") as f:
    dados = yaml.safe_load(f)


def nested_get(data, *keys):
    value = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
        if value is None:
            return None
    return value


rows = []

tecs = dados['technology']
systems = tecs.keys()
for system in systems:
    tecs_i = tecs[system]
    if isinstance(tecs_i, dict):
        for level, tecs_ii in tecs_i.items():
            tecs_iii = tecs_ii.keys()
            for tec_x in tecs_iii:
                rows.append(
                    {
                        "technology": tec_x,
                        "system": system,
                        "level": level,
                        "lifetime": nested_get(dados, "lifetimes", system, tec_x),
                        "CF": nested_get(dados, "capacity_factor", system, tec_x),
                        "inv cost": nested_get(dados, "costs", "inv_cost", system, tec_x),
                        "fix cost": nested_get(dados, "costs", "fix_cost", system, tec_x),
                        "var cost": nested_get(dados, "costs", "var_cost", system, tec_x),
                    }
                )
    else:
        for tecs_ii in tecs_i:
            rows.append(
                {
                    "technology": tecs_ii,
                    "system": system,
                    "level": "final",
                    "lifetime": None,
                    "CF": None,
                    "inv cost": None,
                    "fix cost": None,
                    "var cost": None,
                }
            )

df = pd.DataFrame(rows, columns=["technology", "system", "level", "lifetime", "CF", "inv cost", "fix cost", "var cost"])

output_path = Path(__file__).resolve().parent / "technology_table.csv"
df.to_csv(output_path, index=False)

print(df)
print(f"CSV saved to: {output_path}")