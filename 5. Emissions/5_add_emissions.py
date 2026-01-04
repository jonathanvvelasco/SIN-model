# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 14:38:04 2026

@author: jonat
"""

import ixmp as ix
import message_ix
from message_ix import make_df
from timeit import default_timer as timer

# Loading modelling platform
mp = ix.Platform("default", jvmargs=["-Xmx8G"])

# %% Dados de Emissão de tC02 equivalente por MWh
emissoes = {
    "carvao_nacional": 1.11903,
    "oleo_combustivel": 0.89072,
    "oleo_diesel": 0.77512,
    "gas_natural": 0.44999
}
k_conversao = 8760*1000/1e6 # Converte tC02/MWh para MtC02/GWa

# %% Cloning the storage scenario to add emission factor
model = 'SIN Brasil expandido'
scenario='storage v.2'
base = message_ix.Scenario(mp, model, scenario= scenario)
scen = base.clone(model,'emissions_test',keep_solution=False)
scen.check_out()

# Defining sets and parameters
nodes = ['South', 'North', 'Northeast', 'Southeast']
space_level = 'province'
model_horizon = scen.set("year")
year_df = scen.vintage_and_active_years()
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

# %% Introduce the emission of CO2 and the emission category GHG
scen.add_set("emission", "CO2")
scen.add_cat("emission", "GHG", "CO2")
mp.add_unit("tCO2/kWa")
mp.add_unit("MtCO2")

tecs_emissions ={
    "bio_ppl": 0.0,
    "gas_ppl": emissoes["gas_natural"]*k_conversao,
    "gas_ppl_1": emissoes["gas_natural"]*k_conversao,
    "gas_ppl_2": emissoes["gas_natural"]*k_conversao,
    "gas_ppl_ccs": 0.2*emissoes["gas_natural"]*k_conversao,
    "gas_ppl_ccs_1": 0.2*emissoes["gas_natural"]*k_conversao,
    "gas_ppl_ccs_2": 0.2*emissoes["gas_natural"]*k_conversao,
    "coal_ppl": emissoes["carvao_nacional"]*k_conversao,
    "nuc_ppl": 0.0,
    "oil_ppl": emissoes["oleo_combustivel"]*k_conversao
}
# Build data of emissions by technology
for node in nodes:
    for tec, emission in tecs_emissions.items():
        emission_factor = make_df(
            "emission_factor",
            node_loc=node,
            year_vtg=vintage_years,
            year_act=act_years,
            mode="M1",
            unit="tCO2/kWa",
            technology=tec,
            emission="CO2",
            value=emission,
        )
        scen.add_par("emission_factor", emission_factor)

# %% Solve scenario
start = timer()
scen.solve()
end = timer()
print('Elapsed time for solving scenario:', int((end - start)/60),
              'min and', round((end - start) % 60, 2), 'sec.')

mp.close_db()