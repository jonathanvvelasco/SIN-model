import pandas as pd
import ixmp
mp = ixmp.Platform()
from message_ix import make_df

pde_input   = pd.read_excel("data EPE\Dados_MDI_PDE_2034_Referência.xlsm", sheet_name="GERAL", skiprows=14, usecols="B:P", engine='calamine').squeeze()
pde_par     = pd.read_excel("data EPE\Dados_MDI_PDE_2034_Referência.xlsm", sheet_name="GERAL", skiprows=3, usecols="B:C", engine='calamine').iloc[0:6].T.set_index(0)
pde_par.columns = pde_par.iloc[0]
pde_par     = pde_par[1:].reset_index(drop=True)

from message_ix import Scenario
model = 'SIN Brasil expandido'
base = Scenario(mp, model=model, scenario='emissions_test')
scen = base.clone(
    model,
    "PDE2034",
    "Brazil inputs for PDE2034",
    keep_solution=False,
)
scen.check_out()

# Retrieve parameters
year_df = scen.vintage_and_active_years()
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
model_horizon = scen.set("year")
country = "Brazil"
nodes = ['South', 'North', 'Northeast', 'Southeast']
tecs = scen.set("technology")
seasons = scen.set("time").tolist()
seasons.remove("year")
seasons.remove("winter")
seasons.remove("summer")


# %% Update cost parameters

base_inv = {
    'name': "inv_cost",
    'unit': 'MMUSD/GWa',
}

for node in nodes:
    # For the solar_pv_ppl technologies
    inv_df = make_df(
        node_loc=node, **base_inv, year_vtg=model_horizon, technology="solar_pv_ppl", 
        value=pde_input["Investimento R$/kW"].loc[pde_input["Tipo"] == "Fotovoltaica 1"].values[0] / pde_par["Cambio"]  # Convert from R$ to USD
    )
    scen.add_par("inv_cost", inv_df)



mp.close_db()