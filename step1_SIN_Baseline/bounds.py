
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

def bound_activity_up(scenario, dados):
    '''Add Bound Activity up'''

    base_act_up = {
        'year_act': dados['general']['horizon'],
        'time': 'year',
        'mode':'M1',
        'unit': 'GWa',
    }

    for tec, val in dados['bound']['activity_up']['North'].items():
        df = make_df(base_act_up, node_loc='North', technology=tec, value=val) 
        scenario.add_par('bound_activity_up', df)

    for tec, val in dados['bound']['activity_up']['Northeast'].items():
        df = make_df(base_act_up, node_loc='Northeast', technology=tec, value=val) 
        scenario.add_par('bound_activity_up', df)

    for tec, val in dados['bound']['activity_up']['Southeast'].items():
        df = make_df(base_act_up, node_loc='Southeast', technology=tec, value=val) 
        scenario.add_par('bound_activity_up', df)
        
    for tec, val in dados['bound']['activity_up']['South'].items():
        df = make_df(base_act_up, node_loc='South', technology=tec, value=val) 
        scenario.add_par('bound_activity_up', df)

    return scenario

def bound_activity_low(scenario, dados):
    '''Add Bound Activity low'''

    base_act_low = {
        'year_act': dados['general']['horizon'],
        # 'year_act': [2029],
        'time': 'year',
        'mode':'M1',
        'unit': 'GWa',
    }

    try:
        for node, par in dados['bound']['activity_low'].items():
            try:
                for tec, val in par.items():
                    df = make_df(base_act_low, node_loc=node, technology=tec, value=val) 
                    scenario.add_par('bound_activity_lo', df)
            except AttributeError:
                print(f"Warning: No activity_low bound in node {node}")
    except KeyError:
        print("Warning: No activity_low bound in the input data")
        pass


    return scenario

def bound_total_capacity_up(scenario, dados):
    '''Add Bound Capacity up'''
        
    base_cap = {
        'year_act': dados['general']['horizon'],
        'unit': 'GW',
    }

    for tec, val in dados['bound']['total_capacity_up']['North'].items():
        df = make_df(base_cap, node_loc='North', technology=tec, value=val)
        scenario.add_par('bound_total_capacity_up', df)

    for tec, val in dados['bound']['total_capacity_up']['Northeast'].items():
        df = make_df(base_cap, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('bound_total_capacity_up', df)

    for tec, val in dados['bound']['total_capacity_up']['Southeast'].items():
        df = make_df(base_cap, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('bound_total_capacity_up', df)

    for tec, val in dados['bound']['total_capacity_up']['South'].items():
        df = make_df(base_cap, node_loc='South', technology=tec, value=val)
        scenario.add_par('bound_total_capacity_up', df)

    return scenario

def bound_new_capacity_up(scenario, dados):
    '''Add Bound New Capacity up'''

    base_new_cap = {
        'year_vtg': dados['general']['horizon'],
        'unit': 'GW',
    }
    try:
        for tec, val in dados['bound']['new_capacity_up']['North'].items():
            df = make_df(base_new_cap, node_loc='North', technology=tec, value=val)
            scenario.add_par('bound_new_capacity_up', df)
    except:
        print("Warning: No new capacity bound for North")
        pass

    # try:
    for tec, val in dados['bound']['new_capacity_up']['Northeast'].items():
        df = make_df(base_new_cap, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('bound_new_capacity_up', df)
    # except:
    #     print("Warning: No new capacity bound for Northeast")
    #     pass

    try:
        for tec, val in dados['bound']['new_capacity_up']['Southeast'].items():
            df = make_df(base_new_cap, node_loc='Southeast', technology=tec, value=val)
            scenario.add_par('bound_new_capacity_up', df)
    except:
        print("Warning: No new capacity bound for Southeast")
        pass

    try:
        for tec, val in dados['bound']['new_capacity_up']['South'].items():
            df = make_df(base_new_cap, node_loc='South', technology=tec, value=val)
            scenario.add_par('bound_new_capacity_up', df)
    except:
        print("Warning: No new capacity bound for South")
        pass

    return scenario

def bound_growth_capacity_up(scenario, dados, growth_cap=0.1):
    '''Add Bound Growth Capacity up'''

    for node in dados['general']['nodes']:
        for tec in scenario.set("technology"):
            try:
                df = make_df(
                "growth_activity_up",
                node_loc=node,
                year_act=dados['general']['horizon'],
                time="year",
                unit="-",
                technology=tec,
                value=growth_cap,
                )
                scenario.add_par("growth_activity_up", df)
            except:
                pass

    return scenario

