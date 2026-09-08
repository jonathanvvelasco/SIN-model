# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 12:01:39 2025

@author: jonat
"""


import ixmp as ix
import message_ix
import matplotlib.pyplot as plt
import pandas as pd
from message_ix.report import Reporter
from message_ix.util.tutorial import prepare_plots


def gen_plot(mp, model, scenario):
    base = message_ix.Scenario(mp, model, scenario= scenario)
    
    rep = Reporter.from_scenario(base)
    prepare_plots(rep)
    
    fig_dem_ger = False
        
    # %% Report Activity and Capacity
    # rep.get("plot activity")
    # rep.get("plot capacity")
    # rep.get("plot new capacity")
    rep.set_filters(c=["electricity"]) # Somente commodity eletricidade
    # rep.get("plot prices")
    # rep.get("plot demand")
    allowed_t = [t for t in rep.get("t") if not t.startswith("grid")]
    rep.set_filters(t=allowed_t)
    
    # %% Test emissions
    emis = rep.full_key("EMISS")
    emis_node = emis.drop("type_tec")
    emis_node = rep.get(emis_node)
    emis_node = emis_node.rename("value").reset_index()
    emis_node = emis_node[~emis_node["n"].isin(["World", "Brazil"])]
    emis_plot = emis_node.pivot(index="y", columns="n", values="value").fillna(0)
    ax = emis_plot.plot(kind='bar', stacked=True, figsize=(12, 6), linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Mton CO2")
    ax.legend(title='Node', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_title("Emissions per node")
    plt.show()
    
    # %% Capacity per node
    cap = rep.full_key("CAP")
    cap_node = cap.drop("yv")
    cap_node = rep.get(cap_node)
    cap_node = cap_node.rename("value").reset_index()
    for node in rep.get("n"):
        if node == 'World' or node == 'Brazil':
            continue
        cap_plot = cap_node[cap_node["nl"]==node]
        cap_plot = cap_plot.pivot(index="ya", columns="t", values="value").fillna(0)
        ax = cap_plot.plot(kind="bar", stacked=True, figsize=(12, 6), linewidth=2)
        ax.set_xlabel("Year")
        ax.set_ylabel("GW")
        ax.set_title(f"Capacity in {node}")
        ax.legend(title='Technology', bbox_to_anchor=(1.05, 1), loc='upper left')
        # plt.xticks(rotation=0)
        plt.tight_layout()
        plt.show()
    
    # %% Capacity
    cap = rep.full_key("CAP")
    cap_tot = cap.drop("nl", "yv")
    cap_tot = rep.get(cap_tot)
    cap_tot=cap_tot.rename("value").reset_index()
    
    # Aggregate technology variants into their base technology names
    cap_tot["t"] = cap_tot["t"].replace({
        r"^gas_.+$": "gas_ppl",
        r"^hydro_.+$": "hydro",
        r"^pump_sphs_\d+$": "pump_sphs",
        r"^wind_ppl_.+$": "wind_ppl",
        r"^battery.+$": "battery",
    }, regex=True)
    cap_tot = cap_tot.groupby([col for col in cap_tot.columns if col != "value"])["value"].sum()
    
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
        r"^gas_.+$": "gas_ppl",
        # r"^hydro_\d+$": "hydro",
        r"^hydro_.+$": "hydro",
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
        # plt.rcParams['font.size'] = 18
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
    # ax = act_br_plot.plot(kind="area", stacked=True, figsize=(12, 6), color=plot_colors)
    ax.set_xlabel('Year')
    ax.set_ylabel('GWa')
    ax.set_title(f"Geração anual no cenário {scenario}")
    ax.legend(title='Technology', bbox_to_anchor=(1.05, 1), loc='upper left')
    # plt.xticks(rotation=0)
    # plt.tight_layout()
    plt.rcParams['font.size'] = 12
    plt.grid(axis='y')
    plt.show()

    # Capacity Total on country level
    cap_plot = cap_tot.unstack("t").fillna(0)
    cap_plot = cap_plot[cap_plot.sum().sort_values(ascending=False).index]
    tech_colors = {
        "hydro": "#1f77b4",
        "wind_ppl": "#17becf",
        "solar_pv_ppl": "#f1c40f",
        "gas_ppl": "#ff7f0e",
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
        for i, tech in enumerate(cap_plot.columns)
    ]
    ax = cap_plot.plot(kind="bar", stacked=True, figsize=(12, 6), color=plot_colors)
    # ax = cap_plot.plot(kind="area", stacked=True, figsize=(12, 6), color=plot_colors)
    ax.set_xlabel('Year')
    ax.set_ylabel('GW')
    ax.set_title(f"Capacidade total no cenário {scenario}")
    ax.legend(title='Technology', bbox_to_anchor=(1.05, 1), loc='upper left')
    # plt.xticks(rotation=0)
    # plt.tight_layout()
    plt.rcParams['font.size'] = 12
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
    scenario = 'dados_pde'
    gen_plot(mp, model, scenario)    
    
    # Close DB
    mp.close_db()# -*- coding: utf-8 -*-




