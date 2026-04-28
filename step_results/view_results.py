# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 12:01:39 2025

@author: jonat
"""


import ixmp as ix
import message_ix
import matplotlib.pyplot as plt
import pandas as pd


def gen_plot(mp, model, scenario):
    base = message_ix.Scenario(mp, model, scenario= scenario)
    
    
    from message_ix.report import Reporter
    from message_ix.util.tutorial import prepare_plots
    
    rep = Reporter.from_scenario(base)
    prepare_plots(rep)
    
    fig_dem_ger = False
    
    filter="filter_all_tecs"
    # filter="filter_emission_tecs"
    # %% Define Filters
    
    if filter=="filter_all_tecs":
        rep.set_filters(t=["batt_4_n",
            "batt_4_ne",
            "batt_4_s",
            "batt_4_se",
            "bio_ppl",
            "gas_ppl",
             "gas_ppl_1",
             "gas_ppl_2",
             "gas_ppl_ccs",
             "gas_ppl_ccs_1",
             "gas_ppl_ccs_2",
             "coal_ppl",
             "nuc_ppl",
             "oil_ppl",
             "solar_pv_ppl",
             "hydro_4",
             "hydro_8",
             "hydro_9",
             "hydro_3",
             "hydro_1",
             "hydro_5",
             "hydro_6",
             "hydro_7",
             "hydro_10",
             "hydro_12",
             "hydro_2",
             "hydro_11",
             "pump_sphs_4",
             "pump_sphs_8",
             "pump_sphs_9",
             "pump_sphs_3",
             "pump_sphs_1",
             "pump_sphs_6",
             "pump_sphs_7",
             "pump_sphs_10",
             "pump_sphs_12",
             "pump_sphs_2",
             "pump_sphs_11",
             "wind_ppl",
             "wind_ppl_cos",
             "wind_ppl_int",
             "wind_ppl_rs",
             ])
    elif filter=="filter_emission_tecs":
        rep.set_filters(t=["bio_ppl",
            "gas_ppl",
            "gas_ppl_1",
            "gas_ppl_2",
            "gas_ppl_ccs",
            "gas_ppl_ccs_1",
            "gas_ppl_ccs_2",
            "coal_ppl",
            "nuc_ppl",
            "oil_ppl",
            ])
    else: pass
        
    # %% Report Activity and Capacity
    # rep.get("plot activity")
    # rep.get("plot capacity")
    # rep.get("plot new capacity")
    rep.set_filters(c=["electricity"]) # Somente commodity eletricidade
    # rep.get("plot prices")
    # rep.get("plot demand")
    
    # %% Compares production and demand
    out = rep.full_key("out")
    # out2 = out.drop(["yv","m","nd","c","l","h","hd"])
    out2 = out.drop("yv", "h", "hd", "m", "nd", "c", "l")
    act2 = rep.get(out2)
    act2 = act2[act2 != 0]
    
    out_br = out2.drop("nl")
    act_br = rep.get(out_br)
    act_br = act_br.rename("value").reset_index()
    
    # Load historical activity
    load_history = True
    if load_history:
        act_hist = base.par("historical_activity")
        act_hist = (
            act_hist.drop(columns=["node_loc"])
            .groupby(["technology", "year_act"], as_index=False)["value"]
            .sum()
        )
        act_hist = act_hist[~act_hist["technology"].str.startswith("grid", na=False)]
        act_hist = act_hist.rename(columns={"technology": "t", "year_act": "ya"})[["ya", "t", "value"]]
        act_br = pd.concat([act_br, act_hist], ignore_index=True)
    
    
    # Aggregate technology variants into their base technology names
    act_br["t"] = act_br["t"].replace({
        r"^gas_ppl_\d+$": "gas_ppl",
        r"^gas_ppl_ccs_\d+$": "gas_ppl_ccs",
        r"^hydro_\d+$": "hydro",
        r"^pump_sphs_\d+$": "pump_sphs",
        r"^wind_ppl_.+$": "wind_ppl",
        r"^battery.+$": "battery",
    }, regex=True)
    act_br = act_br.groupby([col for col in act_br.columns if col != "value"])["value"].sum()
    
    out_g = out2.drop("nl", "t")
    act_g = rep.get(out_g)
    act_g = act_g[act_g != 0]
    
    dem = rep.full_key("demand")
    dem_g = dem.drop("n", "c", "l", "h")
    d = rep.get(dem_g)
    
    # %% Plots
    
    #  Comparison Activity vs. Demand
    if fig_dem_ger:
        plt.figure(figsize=(12, 6))
        x = list(range(len(act_g.index)))
        width = 0.35
        plt.bar([i - width/2 for i in x], act_g.values, width=width, label='Activity', alpha=0.7)
        plt.bar([i + width/2 for i in x], d.values, width=width, label='Demand', alpha=0.7)
        plt.xlabel('Year')
        plt.ylabel('GWa')
        anos_list = act_g.index.get_level_values(0).tolist()
        plt.xticks(x, anos_list, rotation=0)
        plt.legend()
        plt.title('Comparison: Activity vs Demand')
        plt.tight_layout()
        plt.rcParams['font.size'] = 18
        plt.grid(axis='y')
        plt.show()
    
    # Generation Expansion on country level
    act_br_plot = act_br.unstack("t").fillna(0)
    act_br_plot = act_br_plot[act_br_plot.sum().sort_values(ascending=False).index]
    tech_colors = {
        "hydro": "#1f77b4",
        "wind_ppl": "#17becf",
        "solar_pv_ppl": "#f1c40f",
        "gas_ppl": "#ff7f0e",
        "gas_ppl_ccs": "#8c564b",
        "bio_ppl": "#2ca02c",
        "coal_ppl": "#4d4d4d",
        "oil_ppl": "#d62728",
        "nuc_ppl": "#9467bd",
        "pump_sphs": "#cb20ae",
        "batt_4_n": "#e377c2",
        "batt_4_ne": "#e377c2",
        "batt_4_s": "#e377c2",
        "batt_4_se": "#e377c2",
    }
    fallback_colors = plt.cm.tab20.colors
    plot_colors = [
        tech_colors.get(tech, fallback_colors[i % len(fallback_colors)])
        for i, tech in enumerate(act_br_plot.columns)
    ]
    ax = act_br_plot.plot(kind="bar", stacked=True, figsize=(12, 6), color=plot_colors)
    ax.set_xlabel('Year')
    ax.set_ylabel('GWa')
    ax.set_title(f"Geração anual por tecnologia no cenário {scenario}")
    ax.legend(title='Technology', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.rcParams['font.size'] = 18
    plt.grid(axis='y')
    plt.show()
    
    # %% Plot historical emissions
    # ha1 = rep.full_key("historical_activity")
    # ha2 = ha1.drop("h","m","nl")
    # hact = rep.get(ha2)
    # emissoes = {
    #     "coal_ppl": 1.11903*8.760,
    #     "oil_ppl": 0.89072*8.760,
    #     "gas_ppl": 0.44999*8.760
    # }
    # emiss_hist = float(hact.sum())
    # emiss = rep.get("EMISS")
 
if __name__ == "__main__":
    # Loading modelling platform
    mp = ix.Platform("default", jvmargs=["-Xmx8G"])
    
    # Specifying model/scenario to be loaded from the database
    # model = 'SIN Brasil expandido'
    # scenario='base'
    model = "SIN Brasil expandido"
    # scenario = 'emissions_test'
    # scenario = 'PDE2034'
    # scenario = 'seasonal'
    scenario = 'base'
    gen_plot(mp, model, scenario)    
    
    # Close DB
    mp.close_db()# -*- coding: utf-8 -*-




