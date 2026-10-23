# -*- coding: utf-8 -*-
"""
Created on Thrus Jan 19 09:13 2023

@author: Jonathan V. Velasco
"""
# load required packages 
#import itertools
import pandas as pd
import yaml
import ixmp
import message_ix
from message_ix.utils import make_df


def start_model(scenario, dados):
    # Set model attributes
    # Check scenario metadata and input data
    if dados['general']['model'] != scenario.model or dados['general']['scen'] != scenario.scenario:
        input("The scenario name does not match the input data. Press Enter to continue or Ctrl+C to stop:")

    # Adding units to the library
    # mp.add_unit('m^3/s')  
    # mp.add_unit('MMUSD/GW')

    scenario.add_horizon(
        year= dados['general']['history'] + dados['general']['horizon'],
        firstmodelyear=dados['general']['horizon'][0]
    )

    scenario.add_spatial_sets({'country': dados['general']['country']})
    space_level = 'province'
    scenario.add_set('lvl_spatial', space_level)
    for node in dados['general']['nodes']:
        scenario.add_set('node', node)
        scenario.add_set('map_spatial_hierarchy', [space_level, node, dados['general']['country']])

    scenario.add_set("commodity", dados['general']['commodities'])
    scenario.add_set("level", dados['general']['energy_lvl'])
    scenario.add_set('mode', dados['general']['modes'])

    tec_new = []
    for node in dados['general']['nodes']:
        try:
            for tec in dados['technology'][node]['primary'].keys():
                tec_new.append(tec)
        except KeyError:
            pass
        try:
            for tec in dados['technology'][node]['secondary'].keys():
                tec_new.append(tec)
        except KeyError:
            pass

    technologies = (
        dados['technology']['final_energy_techs'] +
        tec_new
    )
    scenario.add_set("technology", technologies)

    scenario.add_par("interestrate", dados['general']['horizon'], value=dados['general']['int_rate'], unit='-') #EPE

    # Demand of Electricity
    if len(dados['general']['demand_per_year']) > 1:
        # Demand input is explicit per year
        for node, dem in dados['general']['demand_per_year'].items():
            demand_data = pd.DataFrame({
                    'node': node,
                    'commodity': 'electricity',
                    'level': 'final',
                    'year': dados['general']['horizon'],
                    'time': 'year',
                    'value': dem,
                    'unit': 'GWa',
                })
            scenario.add_par("demand", demand_data)
    else:
        # Demand input as a growth rate
        elec_growth = pd.Series(dados['general']['dem_growth'], index=pd.Index(dados['general']['horizon'], name='Time'))   # centralized demand
        for node, dem in dados['general']['demand_per_year'].items():
            demand_data = pd.DataFrame({
                    'node': node,
                    'commodity': 'electricity',
                    'level': 'final',
                    'year': dados['general']['horizon'],
                    'time': 'year',
                    'value': dem * elec_growth, #retirada a multiplicação por demanda regional por esta ser incluída posteriormente. Caso se deseje voltar para o estágio anterior, é só colocar dem * na parte do value.
                    'unit': 'GWa',
                })
            scenario.add_par("demand", demand_data)

    # [x for x in scenario.par_list() if 'mode' in scenario.idx_sets(x)]
    return scenario

def technical_lifetime(scenario, dados):
    base_technical_lifetime = {
        'year_vtg': dados['general']['history'] + dados['general']['horizon'],
        'unit': 'y',
    }

    for tec, val in dados['lifetimes']['North'].items():
        df_n = make_df(base_technical_lifetime, node_loc='North', technology=tec, value=val)
        scenario.add_par('technical_lifetime', df_n)

    for tec, val in dados['lifetimes']['Northeast'].items():
        df_ne = make_df(base_technical_lifetime, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('technical_lifetime', df_ne)

    for tec, val in dados['lifetimes']['Southeast'].items():
        df_se = make_df(base_technical_lifetime, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('technical_lifetime', df_se)

    for tec, val in dados['lifetimes']['South'].items():
        df_s = make_df(base_technical_lifetime, node_loc='South', technology=tec, value=val)
        scenario.add_par('technical_lifetime', df_s)

    return scenario

def technologies(scenario, dados):
    ''' 
    Adding technology inputs and outputs
    '''
    
    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

    # %% Add Technology grid            (input and output)

    output_base = {
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }
    
    input_base = {
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    # North grid
    base_input_n1 = {
        'node_loc': 'North',
        'node_origin': 'North',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'n-to-ne',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_n1 = {
        'node_loc': 'North',
        'node_dest': 'Northeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'n-to-ne',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    base_input_n2 = {
        'node_loc': 'North',
        'node_origin': 'Northeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'ne-to-n',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_n2 = {
        'node_loc': 'North',
        'node_dest': 'North',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'ne-to-n',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    #grids
    grid_out_n1 = make_df(base_output_n1, technology='grid1', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_n1)

    grid_in_n1 = make_df(base_input_n1, technology='grid1', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_n1)

    grid_out_n2 = make_df(base_output_n2, technology='grid1', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_n2)

    grid_in_n2 = make_df(base_input_n2, technology='grid1', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_n2)

    input_n = {
        'node_loc': 'North',
        'node_origin': 'North',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }
    output_n = {
        'node_loc': 'North',
        'node_dest': 'North',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }
    grid_out_n = make_df(output_n, technology='grid_n', commodity='electricity', 
                    level='final', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_n)
    grid_in_n = make_df(input_n, technology='grid_n', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['distribution'], unit="GWa")
    scenario.add_par('input', grid_in_n)

    # Northeast grid

    base_input_ne1 = {
        'node_loc': 'Northeast',
        'node_origin': 'Northeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'ne-to-se',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_ne1 = {
        'node_loc': 'Northeast',
        'node_dest': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'ne-to-se',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    base_input_ne2 = {
        'node_loc': 'Northeast',
        'node_origin': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-ne',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_ne2 = {
        'node_loc': 'Northeast',
        'node_dest': 'Northeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-ne',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    #grids

    grid_out_ne1 = make_df(base_output_ne1, technology='grid2', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_ne1)

    grid_in_ne1 = make_df(base_input_ne1, technology='grid2', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_ne1)

    grid_out_ne2 = make_df(base_output_ne2, technology='grid2', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_ne2)

    grid_in_ne2 = make_df(base_input_ne2, technology='grid2', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_ne2)

    input_ne = {
        'node_loc': 'Northeast',
        'node_origin': 'Northeast',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    output_ne = {
        'node_loc': 'Northeast',
        'node_dest': 'Northeast',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    # regional grid
    grid_out_ne = make_df(output_ne, technology='grid_ne', commodity='electricity', 
                    level='final', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_ne)

    grid_in_ne = make_df(input_ne, technology='grid_ne', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['distribution'], unit="GWa")
    scenario.add_par('input', grid_in_ne)

    # Southeast grid

    base_input_se1 = {
        'node_loc': 'Southeast',
        'node_origin': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-n',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_se1 = {
        'node_loc': 'Southeast',
        'node_dest': 'North',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-n',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    base_input_se2 = {
        'node_loc': 'Southeast',
        'node_origin': 'North',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'n-to-se',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_se2 = {
        'node_loc': 'Southeast',
        'node_dest': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'n-to-se',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    #grids

    grid_out_se1 = make_df(base_output_se1, technology='grid3', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_se1)

    grid_in_se1 = make_df(base_input_se1, technology='grid3', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_se1)

    grid_out_se2 = make_df(base_output_se2, technology='grid3', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_se2)

    grid_in_se2 = make_df(base_input_se2, technology='grid3', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_se2)

    input_se = {
        'node_loc': 'Southeast',
        'node_origin': 'Southeast',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    output_se = {
        'node_loc': 'Southeast',
        'node_dest': 'Southeast',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    # regional grid

    grid_out_se = make_df(output_se, technology='grid_se', commodity='electricity', 
                    level='final', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_se)

    grid_in_se = make_df(input_se, technology='grid_se', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['distribution'], unit="GWa")
    scenario.add_par('input', grid_in_se)

    # South grid

    base_input_s1 = {
        'node_loc': 'South',
        'node_origin': 'South',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 's-to-se',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_s1 = {
        'node_loc': 'South',
        'node_dest': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 's-to-se',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    base_input_s2 = {
        'node_loc': 'South',
        'node_origin': 'Southeast',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-s',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    base_output_s2 = {
        'node_loc': 'South',
        'node_dest': 'South',
        'commodity': 'electricity',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'se-to-s',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    #grids

    grid_out_s1 = make_df(base_output_s1, technology='grid4', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_s1)

    grid_in_s1 = make_df(base_input_s1, technology='grid4', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_s1)

    grid_out_s2 = make_df(base_output_s2, technology='grid4', commodity='electricity', 
                    level='secondary', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_s2)

    grid_in_s2 = make_df(base_input_s2, technology='grid4', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['transmission'], unit="GWa")
    scenario.add_par('input', grid_in_s2)

    input_s = {
        'node_loc': 'South',
        'node_origin': 'South',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_origin': 'year',
        'unit': '-',
    }

    output_s = {
        'node_loc': 'South',
        'node_dest': 'South',
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'time_dest': 'year',
        'unit': '-',
    }

    # regional grid
    grid_out_s = make_df(output_s, technology='grid_s', commodity='electricity', 
                    level='final', value=1.0, unit="GWa")
    scenario.add_par('output', grid_out_s)

    grid_in_s = make_df(input_s, technology='grid_s', commodity='electricity',
                    level='secondary', value=1/dados['efficiency']['distribution'], unit="GWa")
    scenario.add_par('input', grid_in_s)

    # %% Add Technologies               (input and output)
    
    for node in dados['general']['nodes']:
        try:
            for tec, par in dados['technology'][node]['primary'].items():
                tec_out = make_df(output_base, node_loc=node, node_dest=node, technology=tec, 
                                  commodity=par['output_commodity'], level='primary', value=1., unit=par['output_unit'])
                scenario.add_par('output', tec_out)
        except KeyError:
            pass

    for node in dados['general']['nodes']:
        for tec, par in dados['technology'][node]['secondary'].items():
            tec_out = make_df(output_base, node_loc=node, node_dest=node, technology=tec, 
                              commodity=par['output_commodity'], level='secondary', value=1., unit=par['output_unit'])
            scenario.add_par('output', tec_out)

            try:
                tec_in = make_df(input_base, node_loc=node, node_origin=node, technology=tec, 
                                 commodity=par['input_commodity'], level='primary', value=par['input'], unit=par['input_unit'])
                scenario.add_par('input', tec_in)
            except KeyError:
                pass
        # %% Return 
    return scenario

def capacity_factors_and_historical_capacity(scenario, dados):
    '''Add Capacity Factors and Historical Capacity'''

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

    base_capacity_factor = {
        'year_vtg': vintage_years,
        'year_act': act_years,
        'time': 'year',
        'unit': '-',
    }
    
    base_capacity = {
        'year_vtg': dados['general']['history'],
        'time': 'year',
        'unit': 'GW',
    }

    # Capacity Factor for North
    for tec, val in dados['capacity_factor']['North'].items():
        df = make_df(base_capacity_factor, node_loc='North', technology=tec, value=val)
        scenario.add_par('capacity_factor', df)
    # Capacity dados['general']['history'] for North
    for tec, val in dados['historical_new_capacity']['North'].items():
        df = make_df(base_capacity, node_loc='North', technology=tec, value=val/dados['historical_new_capacity']['times'])
        scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

    # Capacity Factor for Northeast
    for tec, val in dados['capacity_factor']['Northeast'].items():
        df = make_df(base_capacity_factor, node_loc='Northeast', technology=tec, value=val)
        # Removing extra years based on lifetime 
        condition = df['year_act'] < df['year_vtg'] + dados['lifetimes']['Northeast'][tec] 
        df = df.loc[condition] 
        scenario.add_par('capacity_factor', df)
    # Capacity dados['general']['history'] for Northeast
    for tec, val in dados['historical_new_capacity']['Northeast'].items():
        df = make_df(base_capacity, node_loc='Northeast', technology=tec, value=val/dados['historical_new_capacity']['times'])
        scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

    # Capacity Factor for Southeast
    for tec, val in dados['capacity_factor']['Southeast'].items():
        df = make_df(base_capacity_factor, node_loc='Southeast', technology=tec, value=val)
        # Removing extra years based on lifetime 
        condition = df['year_act'] < df['year_vtg'] + dados['lifetimes']['Southeast'][tec] 
        df = df.loc[condition] 
        scenario.add_par('capacity_factor', df)
    # Capacity dados['general']['history'] for Southeast
    for tec, val in dados['historical_new_capacity']['Southeast'].items():
        df = make_df(base_capacity, node_loc='Southeast', technology=tec, value=val/dados['historical_new_capacity']['times'])
        scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

    # Capacity Factor for South
    for tec, val in dados['capacity_factor']['South'].items():
        df = make_df(base_capacity_factor, node_loc='South', technology=tec, value=val)
        # Removing extra years based on lifetime 
        condition = df['year_act'] < df['year_vtg'] + dados['lifetimes']['South'][tec] 
        df = df.loc[condition] 
        scenario.add_par('capacity_factor', df)

    for tec, val in dados['historical_new_capacity']['South'].items():
        df = make_df(base_capacity, node_loc='South', technology=tec, value=val/dados['historical_new_capacity']['times'])
        scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

    return scenario

def costs(scenario, dados):
    '''Add Costs (investment, fixed and variable)'''

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

    base_inv_cost = {
        'year_vtg': dados['general']['horizon'],
        'unit': 'MMUSD/GW',
    }

    base_fix_cost = {
        'year_vtg': vintage_years,
        'year_act': act_years,
        'unit': 'MMUSD/GW',
    }

    var_cost = {
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'M1',
        'time': 'year',
        'unit': 'MMUSD/GWa',
    }

    # of North
    for tec, val in dados['costs']['inv_cost']['North'].items():
        df = make_df(base_inv_cost, node_loc='North', technology=tec, value=val)
        scenario.add_par('inv_cost', df)

    for tec, val in dados['costs']['fix_cost']['North'].items():
        df = make_df(base_fix_cost, node_loc='North', technology=tec, value=val)
        scenario.add_par('fix_cost', df)

    for tec, val in dados['costs']['var_cost']['North'].items():                                     # Adding variable cost = fuel cost to thermal power dados['technology']['plants']
        df = make_df(var_cost, node_loc='North', technology=tec, value=val)
        scenario.add_par('var_cost', df)

    # of Northeast
    for tec, val in dados['costs']['inv_cost']['Northeast'].items():
        df = make_df(base_inv_cost, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('inv_cost', df)

    for tec, val in dados['costs']['fix_cost']['Northeast'].items():
        df = make_df(base_fix_cost, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('fix_cost', df)

    for tec, val in dados['costs']['var_cost']['Northeast'].items():
        df = make_df(var_cost, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('var_cost', df)

    # of Southeast
    for tec, val in dados['costs']['inv_cost']['Southeast'].items():
        df = make_df(base_inv_cost, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('inv_cost', df)

    for tec, val in dados['costs']['fix_cost']['Southeast'].items():
        df = make_df(base_fix_cost, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('fix_cost', df)

    for tec, val in dados['costs']['var_cost']['Southeast'].items():
        df = make_df(var_cost, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('var_cost', df)

    # of South
    for tec, val in dados['costs']['inv_cost']['South'].items():
        df = make_df(base_inv_cost, node_loc='South', technology=tec, value=val)
        scenario.add_par('inv_cost', df)

    for tec, val in dados['costs']['fix_cost']['South'].items():
        df = make_df(base_fix_cost, node_loc='South', technology=tec, value=val)
        scenario.add_par('fix_cost', df)

    for tec, val in dados['costs']['var_cost']['South'].items():
        df = make_df(var_cost, node_loc='South', technology=tec, value=val)
        scenario.add_par('var_cost', df)

    return scenario

def historical_activity(scenario, dados):
    '''Add Historical Acitvity'''

    base_activity = {
        'year_act': dados['general']['history'],
        'mode': 'M1',
        'time': 'year',
        'unit': 'GWa',
    }

    base_activity_grid = {
        'year_act': dados['general']['history'],
        'time': 'year',
        'unit': 'GWa',
    }

    ### 1.1) North baseline and growth parameters
    for tec, val in dados['historical_activity']['North']['old_activity'].items():
        df = make_df(base_activity, node_loc='North', technology=tec, value=val)
        scenario.add_par('historical_activity', df)
        
    for tec, val in dados['historical_activity']['North']['old_activity_1'].items():    
        df = make_df(base_activity_grid, node_loc='North', mode='n-to-ne', technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    for tec, val in dados['historical_activity']['North']['old_activity_2'].items(): 
        df = make_df(base_activity_grid, node_loc='North', mode='ne-to-n', technology=tec, value=val)
        scenario.add_par('historical_activity', df)
        

    ### 2.2) Northeast base and growth
    for tec, val in dados['historical_activity']['Northeast']['old_activity'].items():
        df = make_df(base_activity, node_loc='Northeast', technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    for tec, val in dados['historical_activity']['Northeast']['old_activity_1'].items():
        df = make_df(base_activity_grid, node_loc='Northeast', mode='ne-to-se', technology=tec, value=val)
        scenario.add_par('historical_activity', df)
        
    for tec, val in dados['historical_activity']['Northeast']['old_activity_2'].items():
        df = make_df(base_activity_grid, node_loc='Northeast', mode='se-to-ne', technology=tec, value=val)
        scenario.add_par('historical_activity', df)


    ### 3.1) Southeast base and growth
    for tec, val in dados['historical_activity']['Southeast']['old_activity'].items():
        df = make_df(base_activity, node_loc='Southeast', technology=tec, value=val)
        scenario.add_par('historical_activity', df)
        
    for tec, val in dados['historical_activity']['Southeast']['old_activity_1'].items():
        df = make_df(base_activity_grid, node_loc='Southeast', mode='n-to-se' , technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    for tec, val in dados['historical_activity']['Southeast']['old_activity_2'].items():
        df = make_df(base_activity_grid, node_loc='Southeast', mode='se-to-n', technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    ### 4) South base and growth
    for tec, val in dados['historical_activity']['South']['old_activity'].items():
        df = make_df(base_activity, node_loc='South', technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    for tec, val in dados['historical_activity']['South']['old_activity_1'].items():
        df = make_df(base_activity_grid, node_loc='South', mode='se-to-s', technology=tec, value=val)
        scenario.add_par('historical_activity', df)
        
    for tec, val in dados['historical_activity']['South']['old_activity_2'].items():
        df = make_df(base_activity_grid, node_loc='South', mode='s-to-se', technology=tec, value=val)
        scenario.add_par('historical_activity', df)

    return scenario

def yearly_to_season(scenario, parameter, data, filters=None):
    '''A function for adding sub-annual data to a parameter'''
    if filters:
        old = scenario.par(parameter, filters)
    else:
        old = scenario.par(parameter)
    scenario.remove_par(parameter, old)
    
    # Finding "time" related indexes
    time_idx = [x for x in scenario.idx_names(parameter) if 'time' in x]
    for h in data.keys():
        new = old.copy()
        for time in time_idx:
            new[time] = h
        new['value'] = data[h] * old['value']
        scenario.add_par(parameter, new)

def represent_blocks(scenario, dados):
    '''Add Blocks ou patamares de carga'''

    # Adding sub-annual time blocks
    time_blocks = ['ponta','pesada','media','leve']
    scenario.add_set('time', time_blocks)

    # Defining a new temporal level
    time_level = ['blocks']
    scenario.add_set('lvl_temporal', time_level)

    # Adding temporal hierarchy
    for t in time_blocks:
        scenario.add_set('map_temporal_hierarchy', ['blocks', t, 'year'])

        # All parameters with at least one sub-annual time index
    parameters = [p for p in scenario.par_list() if 'time' in scenario.idx_sets(p)]

    # Those parameters with "time" index that are not empty in our model
    nonempty = [p for p in parameters if not scenario.par(p).empty]
    # print(nonempty)
    # print(scenario.set('time'))
    # print(scenario.set('lvl_temporal'))
    # print(scenario.set('map_temporal_hierarchy'))
    # print(scenario.par('duration_time'))

    # Adding duration time
    duration_blocks = {
        'ponta': 0.0137,
        'pesada': 0.3367,
        'media': 0.4796,
        'leve': 0.1700
    }
    for t in time_blocks:
        scenario.add_par('duration_time', [t], duration_blocks[t], '-')

    # Modifying demand for each season
    demand_data = {
        'ponta':0.01885,
        'pesada':0.38417,
        'media':0.45992,
        'leve':0.13689,
    }

    fixed_data = {'ponta':1,'pesada':1,'media':1,'leve':1}
    test_data = {'ponta':0,'pesada':0,'media':1,'leve':1}
    
    data_to_demand =  {
        "demand",
        'bound_activity_up',
        'bound_activity_lo',
        'historical_activity'
    }

    data_to_fixed = {
        "output",
        'input',
        'bound_total_capacity_up',
        'capacity_factor',
        'historical_activity',
        'var_cost'
    }

    for p in data_to_demand:
        yearly_to_season(scenario, p, demand_data)

    for p in data_to_fixed:
        yearly_to_season(scenario, p, fixed_data)

    yearly_to_season(scenario, 'flexibility_factor', test_data)

    return scenario

if __name__ == "__main__":
    # Open input data
    with open ("baseline_inputs.yaml", "r") as f:
        dados = yaml.safe_load(f)
    
    # Create a new scenario
    mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])
    model = "SIN Brasil expandido"
    scenario = "base"
    scenario = message_ix.Scenario(mp, model, scenario, version = 'new')

    # Add data to the model
    scenario = start_model(scenario, dados)   # Creates a new scenario
    scenario = technical_lifetime(scenario, dados)
    scenario = technologies(scenario, dados)
    scenario = capacity_factors_and_historical_capacity(scenario, dados)
    scenario = costs(scenario, dados)
    scenario = historical_activity(scenario, dados)
    # scenario = bound_activity_up(scenario, dados)
    # scenario = bound_total_capacity_up(scenario, dados)
    # scenario = bound_new_capacity_up(scenario, dados)
    # scenario = emissions(scenario, dados)
    # scenario = bound_growth_capacity_up(scenario, dados, growth_cap=0.3) # Growth capacity bound to 30%

    # solving the model
    scenario.commit(comment='Brazilian_base')       ## Commit the datastructure and solve the model
    scenario.solve()
    scenario.var('OBJ')['lvl']
    scenario.set_as_default()
    scenario.version
    # scenario.to_excel('SIN expandido base.xlsx')

    mp.close_db()    
