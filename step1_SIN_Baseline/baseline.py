# -*- coding: utf-8 -*-
"""
Created on Thrus Jan 19 09:13 2023

@authors: Natalia & Fernando
@contributor: Jonathan
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

    technologies = (
        dados['technology']['plants'] +
        dados['technology']['north_hydro'] +
        dados['technology']['northeast_hydro'] +
        dados['technology']['southeast_hydro'] +
        dados['technology']['south_hydro'] +
        dados['technology']['north_pump'] +
        dados['technology']['northeast_pump'] +
        dados['technology']['southeast_pump'] +
        dados['technology']['south_pump'] +
        dados['technology']['north_res'] +
        dados['technology']['northeast_res'] +
        dados['technology']['southeast_res'] +
        dados['technology']['south_res'] +
        dados['technology']['northeast_wind'] +
        dados['technology']['south_wind'] +
        dados['technology']['brazil_wind'] +
        dados['technology']['final_energy_techs'] +
        dados['technology']['north_wat'] +
        dados['technology']['northeast_wat'] +
        dados['technology']['southeast_wat'] +
        dados['technology']['south_wat'] +
        dados['technology']['battery_n'] +
        dados['technology']['battery_ne'] +
        dados['technology']['battery_se'] +
        dados['technology']['battery_s']
    )
    scenario.add_set("technology", technologies)

    scenario.add_par("interestrate", dados['general']['horizon'], value=dados['general']['int_rate'], unit='-') #EPE

    # Adding electricity demand
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

    # %% Add Technology hydro_ppl       (input and output)

    # North hydro ==================================================================
    for h_plant, val in dados['hydro']['North']['out'].items():
        h_plant_out_n = make_df(output_n, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_out_n['year_act'] < h_plant_out_n['year_vtg'] + dados['lifetimes']['North'][h_plant] 
        h_plant_out_n = h_plant_out_n.loc[condition] 

        scenario.add_par('output', h_plant_out_n)
        
    for h_plant, val in dados['hydro']['North']['out_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_out_n_2 = make_df(output_n, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_n_2['year_act'] < h_plant_out_n_2['year_vtg'] + dados['lifetimes']['North'][h_plant] 
        h_plant_out_n_2 = h_plant_out_n_2.loc[condition]
        
        scenario.add_par('output', h_plant_out_n_2)
        
    for h_plant, val in dados['hydro']['North']['in_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_in_n = make_df(input_n, technology= h_plant, commodity= wat, 
                    level='primary', value= val, unit="m^3/s")

        # Removing extra years based on lifetime 
        condition = h_plant_in_n['year_act'] < h_plant_in_n['year_vtg'] + dados['lifetimes']['North'][h_plant] 

        h_plant_in_n = h_plant_in_n.loc[condition]
        scenario.add_par('input', h_plant_in_n)
        
    for river in dados['technology']['north_res']:
        riv = 'water_' + river.split('river')[1]  
        river_out_n = make_df(output_n, technology= river, commodity= riv, 
                    level='primary', value=val, unit="m^3/s")
        scenario.add_par('output', river_out_n)

    # REE 3 Northeast ========================================================

    for h_plant, val in dados['hydro']['Northeast']['out'].items():
        h_plant_out_ne = make_df(output_ne, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value=val, unit="GWa")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_ne['year_act'] < h_plant_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 
        h_plant_out_ne = h_plant_out_ne.loc[condition] 
        scenario.add_par('output', h_plant_out_ne)
        
    for h_plant, val in dados['hydro']['Northeast']['out_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_out_ne_2 = make_df(output_ne, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_ne_2['year_act'] < h_plant_out_ne_2['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 
        h_plant_out_ne_2 = h_plant_out_ne_2.loc[condition]
        
        scenario.add_par('output', h_plant_out_ne_2)

    for h_plant, val in dados['hydro']['Northeast']['in_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_in_ne = make_df(input_ne, technology= h_plant, commodity= wat, 
                    level='primary', value= val, unit="m^3/s")
        scenario.add_par('input', h_plant_in_ne)
        
    for river in dados['technology']['northeast_res']:
        riv = 'water_' + river.split('river')[1]  
        river_out_ne = make_df(output_ne, technology= river, commodity= riv, 
                    level='primary', value=val, unit="m^3/s")
        scenario.add_par('output', river_out_ne)

    # Hydro Southeast ========================================================

    for h_plant, val in dados['hydro']['Southeast']['out'].items():
        h_plant_out_se = make_df(output_se, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value=val, unit="GWa")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_se['year_act'] < h_plant_out_se['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 
        h_plant_out_se = h_plant_out_se.loc[condition]
        scenario.add_par('output', h_plant_out_se)
        
    for h_plant, val in dados['hydro']['Southeast']['out_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_out_se_2 = make_df(output_se, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_se_2['year_act'] < h_plant_out_se_2['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 
        h_plant_out_se_2 = h_plant_out_se_2.loc[condition]
        scenario.add_par('output', h_plant_out_se_2)

    for h_plant, val in dados['hydro']['Southeast']['in_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_in_se = make_df(input_se, technology= h_plant, commodity= wat, 
                    level='primary', value= val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_in_se['year_act'] < h_plant_in_se['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 
        h_plant_in_se = h_plant_in_se.loc[condition]
        scenario.add_par('input', h_plant_in_se)
        
    for river in dados['technology']['southeast_res']:
        riv = 'water_' + river.split('river')[1]  
        river_out_se = make_df(output_se, technology= river, commodity= riv, 
                    level='primary', value=val, unit="m^3/s") 
        scenario.add_par('output', river_out_se)

    # South hydro ==================================================================

    for h_plant, val in dados['hydro']['South']['out'].items():
        h_plant_out_s = make_df(output_s, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value=val, unit="GWa")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_s['year_act'] < h_plant_out_s['year_vtg'] + dados['lifetimes']['South'][h_plant] 
        h_plant_out_s = h_plant_out_s.loc[condition]
        scenario.add_par('output', h_plant_out_s)
        
    for h_plant, val in dados['hydro']['South']['out_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_out_s_2 = make_df(output_s, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_s_2['year_act'] < h_plant_out_s_2['year_vtg'] + dados['lifetimes']['South'][h_plant] 
        h_plant_out_s_2 = h_plant_out_s_2.loc[condition]
        scenario.add_par('output', h_plant_out_s_2)

    for h_plant, val in dados['hydro']['South']['in_water'].items():
        wat = 'water_' + h_plant.split('hydro_')[1]  
        h_plant_in_s = make_df(input_s, technology= h_plant, commodity= wat, 
                    level='primary', value= val, unit="m^3/s")
        # Removing extra years based on lifetime 
        condition = h_plant_in_s['year_act'] < h_plant_in_s['year_vtg'] + dados['lifetimes']['South'][h_plant] 
        h_plant_in_s = h_plant_in_s.loc[condition]
        scenario.add_par('input', h_plant_in_s)
        
    for river in dados['technology']['south_res']:
        riv = 'water_' + river.split('river')[1]  
        river_out_s = make_df(output_s, technology= river, commodity= riv, 
                    level='primary', value=val, unit="m^3/s")
        scenario.add_par('output', river_out_s)

    # %% Add Technology sphs_ppl        (input and output)

    # SPSH North ==================================================================
    for h_plant, val in dados['sphs']['North']['out'].items():
        h_plant_out_n_3 = make_df(output_n, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_out_n_3['year_act'] < h_plant_out_n_3['year_vtg'] + dados['lifetimes']['North'][h_plant] 
        h_plant_out_n_3 = h_plant_out_n_3.loc[condition] 

        scenario.add_par('output', h_plant_out_n_3)
        
    for h_plant, val in dados['sphs']['North']['out_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_out_n_4 = make_df(output_n, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_n_4['year_act'] < h_plant_out_n_4['year_vtg'] + dados['lifetimes']['North'][h_plant] 
        h_plant_out_n_4 = h_plant_out_n_4.loc[condition]
        
        scenario.add_par('output', h_plant_out_n_4)
        
    for h_plant, val in dados['sphs']['North']['in_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_in_n_2 = make_df(input_n, technology= h_plant, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")

        # Removing extra years based on lifetime 
        condition = h_plant_in_n_2['year_act'] < h_plant_in_n_2['year_vtg'] + dados['lifetimes']['North'][h_plant] 

        h_plant_in_n_2 = h_plant_in_n_2.loc[condition]
        scenario.add_par('input', h_plant_in_n_2)
            
    for h_plant, val in dados['sphs']['North']['in'].items():
        h_plant_in_n_3 = make_df(input_n, technology= h_plant, commodity= 'electricity', 
                        level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_in_n_3['year_act'] < h_plant_in_n_3['year_vtg'] + dados['lifetimes']['North'][h_plant] 

        h_plant_in_n_3 = h_plant_in_n_3.loc[condition]
        scenario.add_par('input', h_plant_in_n_3)

    # SPSH Northeast ===============================================================
    for h_plant, val in dados['sphs']['Northeast']['out'].items():
        h_plant_out_ne_3 = make_df(output_ne, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_out_ne_3['year_act'] < h_plant_out_ne_3['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 
        h_plant_out_ne_3 = h_plant_out_ne_3.loc[condition] 

        scenario.add_par('output', h_plant_out_ne_3)
        
    for h_plant, val in dados['sphs']['Northeast']['out_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_out_ne_4 = make_df(output_ne, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_ne_4['year_act'] < h_plant_out_ne_4['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 
        h_plant_out_ne_4 = h_plant_out_ne_4.loc[condition]
        
        scenario.add_par('output', h_plant_out_ne_4)
        
    for h_plant, val in dados['sphs']['Northeast']['in_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_in_ne_2 = make_df(input_ne, technology= h_plant, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")

        # Removing extra years based on lifetime 
        condition = h_plant_in_ne_2['year_act'] < h_plant_in_ne_2['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 

        h_plant_in_ne_2 = h_plant_in_ne_2.loc[condition]
        scenario.add_par('input', h_plant_in_ne_2)
            
    for h_plant, val in dados['sphs']['Northeast']['in'].items():
        h_plant_in_ne_3 = make_df(input_ne, technology= h_plant, commodity= 'electricity', 
                        level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_in_ne_3['year_act'] < h_plant_in_ne_3['year_vtg'] + dados['lifetimes']['Northeast'][h_plant] 

        h_plant_in_ne_3 = h_plant_in_ne_3.loc[condition]
        scenario.add_par('input', h_plant_in_ne_3)

    # SPSH Southeast ===============================================================

    for h_plant, val in dados['sphs']['Southeast']['out'].items():
        h_plant_out_se_3 = make_df(output_se, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_out_se_3['year_act'] < h_plant_out_se_3['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 
        h_plant_out_se_3 = h_plant_out_se_3.loc[condition] 

        scenario.add_par('output', h_plant_out_se_3)
        
    for h_plant, val in dados['sphs']['Southeast']['out_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_out_se_4 = make_df(output_se, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_se_4['year_act'] < h_plant_out_se_4['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 
        h_plant_out_se_4 = h_plant_out_se_4.loc[condition]
        
        scenario.add_par('output', h_plant_out_se_4)
        
    for h_plant, val in dados['sphs']['Southeast']['in_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_in_se_2 = make_df(input_se, technology= h_plant, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")

        # Removing extra years based on lifetime 
        condition = h_plant_in_se_2['year_act'] < h_plant_in_se_2['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 

        h_plant_in_se_2 = h_plant_in_se_2.loc[condition]
        scenario.add_par('input', h_plant_in_se_2)
            
    for h_plant, val in dados['sphs']['Southeast']['in'].items():
        h_plant_in_se_3 = make_df(input_se, technology= h_plant, commodity= 'electricity', 
                        level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_in_se_3['year_act'] < h_plant_in_se_3['year_vtg'] + dados['lifetimes']['Southeast'][h_plant] 

        h_plant_in_se_3 = h_plant_in_se_3.loc[condition]
        scenario.add_par('input', h_plant_in_se_3)

    # SPSH South ==================================================================
    for h_plant, val in dados['sphs']['South']['out'].items():
        h_plant_out_s_3 = make_df(output_s, technology= h_plant, commodity= 'electricity', 
                    level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_out_s_3['year_act'] < h_plant_out_s_3['year_vtg'] + dados['lifetimes']['South'][h_plant] 
        h_plant_out_s_3 = h_plant_out_s_3.loc[condition] 

        scenario.add_par('output', h_plant_out_s_3)
        
    for h_plant, val in dados['sphs']['South']['out_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_out_s_4 = make_df(output_s, technology= h_plant, commodity= wat, 
                    level='secondary', value=val, unit="m^3/s")
        
        # Removing extra years based on lifetime 
        condition = h_plant_out_s_4['year_act'] < h_plant_out_s_4['year_vtg'] + dados['lifetimes']['South'][h_plant] 
        h_plant_out_s_4 = h_plant_out_s_4.loc[condition]
        
        scenario.add_par('output', h_plant_out_s_4)
        
    for h_plant, val in dados['sphs']['South']['in_water'].items():
        wat = 'water_' + h_plant.split('sphs_')[1]  
        h_plant_in_s_2 = make_df(input_s, technology= h_plant, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")

        # Removing extra years based on lifetime 
        condition = h_plant_in_s_2['year_act'] < h_plant_in_s_2['year_vtg'] + dados['lifetimes']['South'][h_plant] 

        h_plant_in_s_2 = h_plant_in_s_2.loc[condition]
        scenario.add_par('input', h_plant_in_s_2)
            
    for h_plant, val in dados['sphs']['South']['in'].items():
        h_plant_in_s_3 = make_df(input_s, technology= h_plant, commodity= 'electricity', 
                        level='secondary', value= val, unit="GWa")

        # Removing extra years based on lifetime 
        condition = h_plant_in_s_3['year_act'] < h_plant_in_s_3['year_vtg'] + dados['lifetimes']['South'][h_plant] 

        h_plant_in_s_3 = h_plant_in_s_3.loc[condition]
        scenario.add_par('input', h_plant_in_s_3)

        

    # %% Add Technology Battery         (input and output)
    # Battery in North
    for tech in dados['technology']['battery_n']:
        tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + dados['lifetimes']['North'][tech] 
        tech_out_n = tech_out_n.loc[condition] 
        scenario.add_par('output', tech_out_n)
        
    for tech in dados['technology']['battery_n']:
        tech_in_n = make_df(input_n, technology=tech, commodity='electricity', 
                    level='secondary', value=dados['efficiency']['battery'], unit="GWa")
        # Removing extra years based on lifetime 
        condition = tech_in_n['year_act'] < tech_in_n['year_vtg'] + dados['lifetimes']['North'][tech] 
        tech_in_n = tech_in_n.loc[condition] 
        scenario.add_par('input', tech_in_n)

    # Battery in Northeast
    for tech in dados['technology']['battery_ne']:
        tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
        tech_out_ne = tech_out_ne.loc[condition] 
        scenario.add_par('output', tech_out_ne)
        
    for tech in dados['technology']['battery_ne']:
        tech_in_ne = make_df(input_ne, technology=tech, commodity='electricity', 
                    level='secondary', value=dados['efficiency']['battery'], unit="GWa")
        # Removing extra years based on lifetime 
        condition = tech_in_ne['year_act'] < tech_in_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
        tech_in_ne = tech_in_ne.loc[condition] 
        scenario.add_par('input', tech_in_ne)

    # Battery in Southeast
    for tech in dados['technology']['battery_se']:
        tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
        tech_out_se = tech_out_se.loc[condition] 
        scenario.add_par('output', tech_out_se)
        
    for tech in dados['technology']['battery_se']:
        tech_in_se = make_df(input_se, technology=tech, commodity='electricity', 
                    level='secondary', value=dados['efficiency']['battery'], unit="GWa")
        # Removing extra years based on lifetime 
        condition = tech_in_se['year_act'] < tech_in_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
        tech_in_se = tech_in_se.loc[condition] 
        scenario.add_par('input', tech_in_se)

    # Battery in South
    for tech in dados['technology']['battery_s']:
        tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + dados['lifetimes']['South'][tech] 
        tech_out_s = tech_out_s.loc[condition] 
        scenario.add_par('output', tech_out_s)
        
    for tech in dados['technology']['battery_s']:
        tech_in_s = make_df(input_s, technology=tech, commodity='electricity', 
                    level='secondary', value=dados['efficiency']['battery'], unit="GWa")
        # Removing extra years based on lifetime 
        condition = tech_in_s['year_act'] < tech_in_s['year_vtg'] + dados['lifetimes']['South'][tech] 
        tech_in_s = tech_in_s.loc[condition] 
        scenario.add_par('input', tech_in_s)

        
    # %% Add Other Technologies         (input and output)
    # Techs in North
    for tech in dados['technology']['brazil_wind']:
        tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        # condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + dados['lifetimes']['North'][tech] 
        # tech_out_n = tech_out_n.loc[condition]
        
        scenario.add_par('output', tech_out_n)
        
    for tech in dados['technology']['plants']:
        tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")

        # Removing extra years based on lifetime 
        # condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + dados['lifetimes']['North'][tech] 
        # tech_out_n = tech_out_n.loc[condition] 
        scenario.add_par('output', tech_out_n)

    # Techs in Northeast
    for tech in dados['technology']['plants']:
        tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
        # tech_out_ne = tech_out_ne.loc[condition]
        scenario.add_par('output', tech_out_ne)

    for tech in dados['technology']['northeast_wind']:
        tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
        # tech_out_ne = tech_out_ne.loc[condition]
        scenario.add_par('output', tech_out_ne)

    # Techs in Southeast
    for tech in dados['technology']['brazil_wind']:
        tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
        # tech_out_se = tech_out_se.loc[condition]
        scenario.add_par('output', tech_out_se)

    for tech in dados['technology']['plants']:
        tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
        # tech_out_se = tech_out_se.loc[condition]
        scenario.add_par('output', tech_out_se)

    # Techs in South
    for tech in dados['technology']['plants']:
        tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + dados['lifetimes']['South'][tech] 
        # tech_out_s = tech_out_s.loc[condition]
        scenario.add_par('output', tech_out_s)

    for tech in dados['technology']['south_wind']:
        tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                    level='secondary', value=1., unit="GWa")
        # Removing extra years based on lifetime 
        # condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + dados['lifetimes']['South'][tech] 
        # tech_out_s = tech_out_s.loc[condition]
        scenario.add_par('output', tech_out_s)

    # %% Add Technology Water Supply    (input and output) 

    # Water supply North ==================================================================
    for w_supply, val in dados['water_supply']['North']['out'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1] 
        w_supply_out_n = make_df(output_n, technology= w_supply, commodity= wat, 
                    level='final', value= val, unit="m^3/s")
        scenario.add_par('output', w_supply_out_n)
        
    for w_supply, val in dados['water_supply']['North']['in'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1]  
        w_supply_in_n = make_df(input_n, technology= w_supply, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")
        scenario.add_par('input', w_supply_in_n)

    # Water supply Northeast ===============================================================
    for w_supply, val in dados['water_supply']['Northeast']['out'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1] 
        w_supply_out_ne = make_df(output_ne, technology= w_supply, commodity= wat, 
                    level='final', value= val, unit="m^3/s")
        scenario.add_par('output', w_supply_out_ne)

    for w_supply, val in dados['water_supply']['Northeast']['in'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1]  
        w_supply_in_ne = make_df(input_ne, technology= w_supply, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")
        scenario.add_par('input', w_supply_in_ne)

        # Water supply Southeast ===============================================================
    for w_supply, val in dados['water_supply']['Southeast']['out'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1] 
        w_supply_out_se = make_df(output_se, technology= w_supply, commodity= wat, 
                    level='final', value= val, unit="m^3/s") 
        scenario.add_par('output', w_supply_out_se)
        
    for w_supply, val in dados['water_supply']['Southeast']['in'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1]  
        w_supply_in_se = make_df(input_se, technology= w_supply, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")
        scenario.add_par('input', w_supply_in_se)

    # Water supply South ==================================================================

    for w_supply, val in dados['water_supply']['South']['out'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1] 
        w_supply_out_s = make_df(output_s, technology= w_supply, commodity= wat, 
                    level='final', value= val, unit="m^3/s")
        scenario.add_par('output', w_supply_out_s)
        
    for w_supply, val in dados['water_supply']['South']['in'].items():
        wat = 'water_' + w_supply.split('water_supply_')[1]  
        w_supply_in_s = make_df(input_s, technology= w_supply, commodity= wat, 
                    level='secondary', value= val, unit="m^3/s")
        scenario.add_par('input', w_supply_in_s)
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
        # Removing extra years based on lifetime
        condition = df['year_act'] < df['year_vtg'] + dados['lifetimes']['North'][tec]
        df = df.loc[condition]
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

if __name__ == "__main__":
    # Open input data
    with open ("baseline_inputs.yaml", "r") as f:
        dados = yaml.safe_load(f)
    
    # Create a new scenario
    mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])
    model = "SIN Brasil expandido"
    scen = "base"
    scenario = message_ix.Scenario(mp, model, scen, version = 'new')

    # Add data to the model
    scenario = start_model(scenario, dados)   # Creates a new scenario
    scenario = technical_lifetime(scenario, dados)
    scenario = technologies(scenario, dados)
    scenario = capacity_factors_and_historical_capacity(scenario, dados)
    scenario = costs(scenario, dados)
    scenario = historical_activity(scenario, dados)
    scenario = bound_activity_up(scenario, dados)
    scenario = bound_total_capacity_up(scenario, dados)
    # scenario = bound_growth_capacity_up(scenario, dados, growth_cap=0.3) # Growth capacity bound to 30%

    # solving the model
    scenario.commit(comment='Brazilian_base')       ## Commit the datastructure and solve the model
    scenario.solve()
    scenario.var('OBJ')['lvl']
    scenario.set_as_default()
    scenario.version
    # scenario.to_excel('SIN expandido base.xlsx')

    mp.close_db()    
