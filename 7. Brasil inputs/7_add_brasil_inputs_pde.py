import pandas as pd
import ixmp
mp = ixmp.Platform()
from message_ix import make_df

# Load PDE inputs
pde_input       = pd.read_excel("data EPE\Dados_MDI_PDE_2034_Referência.xlsm", sheet_name="GERAL", skiprows=14, usecols="B:P", engine='calamine').squeeze()
pde_par         = pd.read_excel("data EPE\Dados_MDI_PDE_2034_Referência.xlsm", sheet_name="GERAL", skiprows=3, usecols="B:C", engine='calamine').iloc[0:6].T.set_index(0)
pde_par.columns = pde_par.iloc[0]
pde_par         = pde_par[1:].reset_index(drop=True)

# Clone existing scenario
from message_ix import Scenario
model           = 'SIN Brasil expandido'
base            = Scenario(mp, model=model, scenario='emissions_test')
scen            = base.clone(
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
# seasons = scen.set("time").tolist()
# seasons.remove("year")
# seasons.remove("winter")
# seasons.remove("summer")
mp.add_unit('MMUSD/GW')  
mp.add_unit('MMUSD/GW.a')  


# %% Update cost parameters

base_inv = {
    'name': "inv_cost",
    'unit': 'MMUSD/GW',
}

tecnologias = {
    #<tec_MESSAGE>:  <nome_MDI> 
    "solar_pv_ppl": "Fotovoltaica 1",
    "wind_ppl_int": "Eólica 4",
    "wind_ppl_cos": "Eólica 4",    
    "wind_ppl_rs": "Eólica 4",
}

for tec, pde_param in tecnologias.items():
    # Investment cost
    val_inv = pde_input["Investimento R$/kW"].loc[pde_input["Tipo"] == 
          pde_param].values[0] / pde_par["Cambio"]  # Convert from R$ to USD
    val_inv = [val_inv]*4
    
    # Fixed cost (taxes and O&M)
    val_tax = pde_input["Encargos\nR$/kW.ano"].loc[pde_input["Tipo"] == 
          pde_param].values[0] / pde_par["Cambio"]  
    val_om  = pde_input["O&M Anual em R$/kW.ano"].loc[pde_input["Tipo"] == 
          pde_param].values[0] / pde_par["Cambio"] 
    val_fix = val_tax + val_om
    val_fix = [val_fix]*9
    
    # Variable cost 
    # val_inv = pde_input["Investimento R$/kW"].loc[pde_input["Tipo"] == 
    #       tecnologias["solar_pv_ppl"]].values[0] / pde_par["Cambio"]  
    # val_inv = [val_inv]*4
    for node in nodes:
        # For the solar_pv_ppl technologies
        inv_df = make_df(
            node_loc=node, **base_inv, year_vtg=model_horizon, technology=tec, 
            value=val_inv
        )
        scen.add_par("inv_cost", inv_df)
        
        fix_df = make_df(
            node_loc=node, name="fix_cost", year_vtg=vintage_years, technology=tec, 
            value=val_fix, year_act = act_years, unit='MMUSD/GW.a'
        )
        scen.add_par("fix_cost", fix_df)
        
        
scen.commit(comment="test PDE inputs")
scen.set_as_default()
scen.solve()


mp.close_db()
    