
# -*- coding: utf-8 -*-
"""
Created on Wednesday Oct 21 14:28 2026

@author: Jonathan V. Velasco
"""

import pandas as pd
import yaml
import ixmp
import message_ix
from message_ix.utils import make_df

def emissions(scenario, dados):
    '''Add Emissions'''

    # Introduce the emission of CO2 and the emission category GHG
    scenario.add_set("emission", "CO2")
    scenario.add_cat("emission", "GHG", "CO2")

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    # Build data of emissions by technology
    for node in dados['general']['nodes']:
        for tec, val in dados['emissions'][node].items():
            emission_factor = make_df(
                "emission_factor",
                node_loc=node,
                year_vtg=vintage_years,
                year_act=act_years,
                mode="M1",
                unit="tCO2/kWa",
                technology=tec,
                emission="CO2",
                value=val,
            )
            scenario.add_par("emission_factor", emission_factor)

    return scenario

def emissions_tax(scenario, dados):
    '''Add Emissions Tax'''

    # year_df = scenario.vintage_and_active_years()
    # vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    scenario.add_set("emission", "CO2")
    scenario.add_cat("emission", "GHG", "CO2")
    scenario.add_set('type_year', dados['general']['horizon'])

    # Build data of emissions tax by technology
    for node, val in dados['emission_tax'].items():
        if isinstance(val, (int, float)):
            val = [val] * len(dados['general']['horizon'])
        elif len(val) == 1:
            val = val * len(dados['general']['horizon'])
        emission_tax = make_df(
            "tax_emission",
            node=node,
            type_year=dados['general']['horizon'],
            unit="USD/tCO2",
            type_tec="all",
            type_emission="GHG",
            value=val,
        )
        scenario.add_par("tax_emission", emission_tax)

    return scenario

def flexibility(scenario, dados):
    '''Add Flexibility'''

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    base_flexibility_factor = dict(
        commodity="electricity",
        mode="M1",
        unit="-",
        year_vtg=vintage_years,
        year_act=act_years,
)
    for node, info in dados['flexibility'].items():
        for level, info_i in info.items():
            for tec, val in info_i.items():
                flexibility_factor = make_df(
                    "flexibility_factor", node_loc=node, **base_flexibility_factor, time='year',
                    level=level, technology=tec, rating="unrated", value=val
                )
                scenario.add_par("flexibility_factor", flexibility_factor)

    return scenario

def storage(scenario, dados):
    '''Add Storage'''
    
    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    scenario.add_set("level", "storage")
    scenario.add_set("level_storage", "storage")
    
    for node, tec in dados['technology_storage'].items():
        base_storage = dict(
            commodity="electricity",
            node_loc=node,
            node_origin=node,
            node_dest=node,
            year_vtg=vintage_years,
            year_act=act_years,
            time='year',
            time_origin='year',
            time_dest='year',
            value=1,
            unit="GWa",
        )

        s_tec = list(tec.keys())[0]
        s_tec_storage = s_tec + "_storage"
        scenario.add_set("technology", [s_tec, s_tec_storage])
        scenario.add_set("storage_tec", s_tec_storage)
        scenario.add_set("map_tec_storage",[node, s_tec, "M1", s_tec_storage, "M1", "storage", "electricity", "year"])
        scenario.add_set("map_tec_storage",[node, s_tec, "M2", s_tec_storage, "M2", "storage", "electricity", "year"])

        storage_df = make_df(base_storage, technology=s_tec, mode="M1", level='secondary')  # input to storage
        scenario.add_par("input", storage_df)
        storage_df = make_df(base_storage, technology=s_tec, mode="M2", level='storage')    # input from storage
        scenario.add_par("input", storage_df)
        storage_df = make_df(base_storage, technology=s_tec_storage, mode="M1", level='storage') # time-coupling
        scenario.add_par("input", storage_df)
        storage_df = make_df(base_storage, technology=s_tec, mode="M1", level='storage')    # output to storage
        scenario.add_par("output", storage_df)
        storage_df = make_df(base_storage, technology=s_tec, mode="M2", level='secondary')  # output from storage
        scenario.add_par("output", storage_df)
        storage_df = make_df(base_storage, technology=s_tec_storage, mode="M1", level='storage') # time-coupling
        scenario.add_par("output", storage_df)

    # base_storage = dict(
    #     node_loc=dados['general']['nodes'],
    #     year_vtg=vintage_years,
    #     year_act=act_years,
    #     mode="M1",
    #     time="year",
    #     unit="-",
    # )
    # for node, info in dados['storage'].items():
    #     for tec, val in info.items():
    #         storage_factor = make_df(
    #             "storage_factor", node_loc=node, **base_storage, technology=tec, value=val
    #         )
    #         scenario.add_par("storage_factor", storage_factor)

    return scenario

