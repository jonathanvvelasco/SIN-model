# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 12:04:52 2026

@author: jonat
"""

import ixmp
mp = ixmp.Platform()
from message_ix import make_df

from message_ix import Scenario
model = 'SIN Brasil expandido'
base = Scenario(mp, model=model, scenario='emissions_test')
scen = base.clone(
    model,
    "flexibility_gen",
    "flexible-generation constraint",
    keep_solution=False,
)
scen.check_out()

nfi_brasil = {
    "multicombustivel_oleo":0.80,
    "diesel":	            0.96,
    "oleo":	                0.99,
    "gas":	                0.81,
    "nuclear":	            0.51,
    "outras_multi":	        0.82,
    "biomassa":	            0.69,
    "hidro":	            0.64,
    "residuos":	            0.56,
    "carvao":	            0.71,
    "eolica":	           -0.64,
    "solar":	           -0.94,
    "demanda":	           -0.39
}

# Retrieve parameters
year_df = scen.vintage_and_active_years()
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
model_horizon = scen.set("year")
country = "Brazil"
nodes = ['South', 'North', 'Northeast', 'Southeast']

seasons = scen.set("time").tolist()
seasons.remove("year")
seasons.remove("winter")
seasons.remove("summer")

# Decidi não definir Rating Bins, como no exemplo do Git Hub. Para isso seria necessário avaliação 
# de requisito de flexibilidade em função da penetração de renováveis.

# Cria dicionário para o parâmetro de flexibilidade
base_flexibility_factor = dict(
    commodity="electricity",
    level="secondary",
    mode="M1",
    unit="-",
    year_vtg=vintage_years,
    year_act=act_years,
)

name = "flexibility_factor"

tecs = scen.set("technology")

# For the load (`grid`)
for season in seasons:
    flexibility_factor_n = make_df(
        name, **base_flexibility_factor, node_loc="North", time=season, 
        technology="grid_n", rating="unrated", value=nfi_brasil["demanda"]
        )
    flexibility_factor_ne = make_df( 
        name, **base_flexibility_factor, node_loc="Northeast", time=season,
        technology="grid_ne", rating="unrated", value=nfi_brasil["demanda"]
        )
    flexibility_factor_se = make_df( 
        name, **base_flexibility_factor, node_loc="Southeast", time=season,
        technology="grid_se", rating="unrated", value=nfi_brasil["demanda"]
        )
    flexibility_factor_s = make_df( 
        name, **base_flexibility_factor, node_loc="South", time=season,
        technology="grid_s", rating="unrated", value=nfi_brasil["demanda"]
        )
scen.add_par(name, flexibility_factor_n)
scen.add_par(name, flexibility_factor_ne)
scen.add_par(name, flexibility_factor_se)
scen.add_par(name, flexibility_factor_s)


for node in nodes:
    for season in seasons:
        # For the wind_ppl technologies
        tecs_wind = tecs[tecs.str.startswith("wind_ppl")]
        for tec in tecs_wind:
            flexibility_factor = make_df(
                name, node_loc=node, **base_flexibility_factor, time=season,
                technology=tec, rating="unrated", value=nfi_brasil["eolica"]
            )
            scen.add_par(name, flexibility_factor)

        # For the hydro technologies
        tecs_hydro = tecs[tecs.str.startswith("hydro")]
        for tec in tecs_hydro:
            flexibility_factor = make_df(
                name, node_loc=node, **base_flexibility_factor, time=season,
                technology=tec, rating="unrated", value=nfi_brasil["hidro"]
            )
            scen.add_par(name, flexibility_factor)

        # For the gas technologies
        tecs_gas = tecs[tecs.str.startswith("gas")]
        for tec in tecs_gas:
            flexibility_factor = make_df(
                name, node_loc=node, **base_flexibility_factor, time=season,
                technology=tec, rating="unrated", value=nfi_brasil["gas"]
            )
            scen.add_par(name, flexibility_factor)

        # For the sphs technologies
        tecs_sphs = tecs[tecs.str.startswith("pump_sphs")]
        for tec in tecs_sphs:
            flexibility_factor = make_df(
                name, node_loc=node, **base_flexibility_factor, time=season,
                technology=tec, rating="unrated", value=1.0
            )
            scen.add_par(name, flexibility_factor)

        # For the battery technologies
        tecs_sphs = tecs[tecs.str.startswith("battery_4")]
        for tec in tecs_sphs:
            flexibility_factor = make_df(
                name, node_loc=node, **base_flexibility_factor, time=season,# mode="Dis",
                technology=tec, rating="unrated", value=1.0
            )
            scen.add_par(name, flexibility_factor)

    # For `coal_ppl`
        flexibility_factor = make_df(
            name, node_loc=node, **base_flexibility_factor, time=season,
            technology='coal_ppl', rating="unrated", value=nfi_brasil["carvao"]
        )
        scen.add_par(name, flexibility_factor)

    # For the bio_ppl technologies
        flexibility_factor = make_df(
            name, node_loc=node, **base_flexibility_factor, time=season,
            technology='bio_ppl', rating="unrated", value=nfi_brasil["biomassa"]
        )
        scen.add_par(name, flexibility_factor)

    # For the solar_pv_ppl technologies
        flexibility_factor = make_df(
            name, node_loc=node, **base_flexibility_factor, time=season,
            technology="solar_pv_ppl", rating="unrated", value=nfi_brasil["solar"]
        )
        scen.add_par(name, flexibility_factor)

    # For oil_ppl
        flexibility_factor = make_df(
            name, node_loc=node, **base_flexibility_factor, time=season,
            technology='oil_ppl', rating="unrated", value=nfi_brasil["oleo"]
        )
        scen.add_par(name, flexibility_factor)
    
    # For nuclear_ppl
        flexibility_factor = make_df(
            name, node_loc=node, **base_flexibility_factor, time=season,
            technology='nuc_ppl', rating="unrated", value=nfi_brasil["nuclear"]
        )
        scen.add_par(name, flexibility_factor)

scen.commit(comment="add flexibility factors")
scen.set_as_default()

scen.solve()

mp.close_db()


