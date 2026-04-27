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

mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])


model = "SIN Brasil expandido"
scen = "base"

with open ("baseline_inputs.yaml", "r") as f:
    dados = yaml.safe_load(f)
# =============================================================================
# :check %% Inputs
# =============================================================================

# General Inputs
# Scenario id


# Include sets
# country     = 'Brazil'
# nodes       = ['South', 'North', 'Northeast', 'Southeast']  # Spacial sets
# commodities = ["electricity", "water_1", "water_2", "water_3", "water_4",
#                                "water_5", "water_6","water_7", "water_8",
#                                "water_9", "water_10", "water_11", "water_12"]     # commoditie sets #ion commodities are storage especifications for batteries
# energy_lvl  = ["primary" , "secondary", "final"] # Energy level
# modes       = ['n-to-ne', 'ne-to-n', 'n-to-se', 'se-to-n', 'ne-to-se', 
#                'se-to-ne', 'se-to-s', 's-to-se', 'M1','M2'] # Technology modes

# demand_per_year = {
#         'South': 11.67, # electricity demand GWa BEN year 2019
#         'North': 5.57,
#         'Northeast': 11.05,
#         'Southeast': 39.55,
#         }

# :check %% Tecnhology sets

# Overall echnologies
# dados['technology']['plants'] = [
#     "bio_ppl",
#     "gas_ppl",
#     "gas_ppl_1",
#     "gas_ppl_2",
#     "gas_ppl_ccs",
#     "gas_ppl_ccs_1",
#     "gas_ppl_ccs_2",
#     "coal_ppl",
#     "nuc_ppl",
#     "oil_ppl",
#     "solar_pv_ppl"
# ]

# Battery technologies
# dados['technology']['battery_n'] = ['batt_n']
# dados['technology']['battery_ne'] = ['batt_ne']
# dados['technology']['battery_se'] = ['batt_se']
# dados['technology']['battery_s'] = ['batt_s']

# Wind technologies
# brazil_wind = ["wind_ppl"]
# northeast_wind = ["wind_ppl_cos", "wind_ppl_int"]
# south_wind = ["wind_ppl_rs"]
#wind_ppl_cos means wind_ppl on the coast of northeast of Brazil. To obtain it's parameters, it was considered data from RN and CE states.
#wind_ppl_int means wind_ppl on inlands of northeast of Brazil. To obtain it's parameters, it was considered data from BA and PI states.
#wind_ppl_rs means wind_ppl on Rio Grande do Sul state. To obtain it's parameters, it was considered data from RS state.
#wind_ppl means wind on the rest of the country

# Hidro technologies
# north_hydro = ["hydro_4", "hydro_8", "hydro_9"]     # REE Norte, Belo Monte e Amazonas
# northeast_hydro = ["hydro_3"]                       # REE Nordeste
#                 # REE Sudeste, Itaipu, Madeira, Teles Pires, Paraná e Paranapanema
# southeast_hydro = ["hydro_1", "hydro_5", "hydro_6", "hydro_7", "hydro_10", "hydro_12"]
# south_hydro = ["hydro_2", "hydro_11"]               # REE Sul e Iguaçu
        
# north_pump = ["sphs_4", "sphs_8", "sphs_9"]
# northeast_pump = ["sphs_3"]
# southeast_pump = ["sphs_1", "sphs_6", "sphs_7", "sphs_10", "sphs_12"]
# south_pump = ["sphs_2", "sphs_11"]

# north_res = [ "river4", "river8", "river9"]
# northeast_res = ["river3"]
# southeast_res = ["river1", "river5", "river6", "river7", "river10", "river12" ]
# south_res = ["river2", "river11"]

# north_wat = [ "water_supply_4", "water_supply_8", "water_supply_9"]
# northeast_wat = ["water_supply_3"]
# southeast_wat = ["water_supply_1", "water_supply_5", "water_supply_6", "water_supply_7", "water_supply_10", "water_supply_12" ]
# south_wat = ["water_supply_2", "water_supply_11"]

# # Transmission and Distribution technologies 
# final_energy_techs = ["grid1", "grid2", "grid3", "grid4", "grid_n", "grid_ne", "grid_se", "grid_s"]


# :check %% Technology lifetimes

# dados['lifetimes']['North'] = { # considering NREL COST utility scale for batteries
#     "hydro_4": 60, "hydro_8": 60, "hydro_9": 60, "sphs_4": 60, "sphs_8": 60, "sphs_9": 60,
#     "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1":20, "gas_ppl_2":20, "wind_ppl": 20,  
#     "coal_ppl": 25, "batt_n": 15, "gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, 
#     "gas_ppl_ccs_2": 20, "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
#     "grid1": 25, "grid_n": 25,"river4":1000, "river8":1000, "river9":1000,
#     "water_supply_4":1000, "water_supply_8":1000, "water_supply_9":1000,
# } 

# dados['lifetimes']['Northeast'] = {
#     "hydro_3": 60, "sphs_3": 60, "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1": 20, 
#     "gas_ppl_2": 20, "gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20,
#     "wind_ppl_int": 20, "wind_ppl_cos": 20, "coal_ppl": 25, "nuc_ppl": 60,
#     "solar_pv_ppl":20,  "oil_ppl": 20, "batt_ne": 15,
#     "grid2": 25, "grid_ne": 25, "river3":1000,"water_supply_3":1000,
# }

# dados['lifetimes']['Southeast'] = {
#     "hydro_1": 60, "hydro_5": 60, "hydro_6": 60, "hydro_7": 60, "hydro_10": 60, "hydro_12": 60,
#     "sphs_1": 60, "sphs_6": 60, "sphs_7": 60, "sphs_10": 60, "sphs_12": 60,
#     "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1": 20, "gas_ppl_2": 20, "gas_ppl_ccs": 20, 
#     "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20,"wind_ppl": 20,  "coal_ppl": 25, "batt_se": 15,
#     "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,"grid3": 25, "grid_se": 25, "river1":1000, 
#     "river5":1000, "river6":1000, "river7":1000, "river10":1000, "river12":1000, "water_supply_1":1000, 
#     "water_supply_5":1000, "water_supply_6":1000, "water_supply_7":1000, "water_supply_10":1000, "water_supply_12":1000
# }

# dados['lifetimes']['South'] = {
#     "hydro_2": 60, "hydro_11": 60, "sphs_2": 60, "sphs_11": 60, "bio_ppl": 20, 
#     "gas_ppl": 20, "gas_ppl_1": 20, "gas_ppl_2": 20,"gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, 
#     "gas_ppl_ccs_2": 20, "wind_ppl_rs": 20, "coal_ppl": 25, "nuc_ppl": 60, 
#     "solar_pv_ppl":20,  "oil_ppl": 20, "batt_s": 15, "grid4": 25, "grid_s": 25, 
#     "river2":1000, "river11":1000,"water_supply_2":1000, "water_supply_11":1000
# }

# :check %% Technology Capacity Factor

# # Capacity Factors for North
# capacity_factor_n = {
#     "hydro_4": 0.9, #EPE
#     "hydro_8": 0.9, #EPE
#     "hydro_9": 0.9, #EPE
#     "sphs_4": 0.7, #EPE
#     "sphs_8": 0.7, #EPE
#     "sphs_9": 0.7, #EPE
#     "bio_ppl": 0.33, #EPE
#     "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "wind_ppl": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
#     "coal_ppl": 0.69,#EPE
#     "nuc_ppl": 0.85, #EPE - eff 33%
#     "solar_pv_ppl":0.3,
#     "oil_ppl": 0.75,
#     "grid1": 0.8,
#     "batt_n": 0.85,
#     "grid_n": 0.8,
# }

# # Capacity Factors for Northeast
# capacity_factor_ne = {
#     "hydro_3": 0.9,#EPE 
#     "sphs_3": 0.7,#EPE 
#     "bio_ppl": 0.33, #EPE
#     "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "wind_ppl_cos": 0.47,#For now, the EPE data of 0.47 in North and Northeast is maintained.
#     "wind_ppl_int": 0.47,#For now, the EPE data of 0.47 in North and Northeast is maintained.
#     "coal_ppl": 0.69,#EPE
#     "nuc_ppl": 0.85, #EPE - eff 33%
#     "solar_pv_ppl":0.3,
#     "oil_ppl": 0.75, #EPE
#     "grid2": 0.8,
#     "batt_ne": 0.85,
#     "grid_ne": 0.8,
# }

# # Capacity Factors for Southeast
# capacity_factor_se = {
#     "hydro_1": 0.9, #EPE
#     "hydro_5": 0.9,#EPE
#     "hydro_6": 0.9,#EPE
#     "hydro_7": 0.9,#EPE
#     "hydro_10": 0.9,#EPE
#     "hydro_12": 0.9,#EPE
#     "sphs_1": 0.7, #EPE
#     "sphs_6": 0.7,#EPE
#     "sphs_7": 0.7,#EPE
#     "sphs_10": 0.7,#EPE
#     "sphs_12": 0.7,#EPE    
#     "bio_ppl": 0.33, #EPE
#     "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "wind_ppl": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
#     "coal_ppl": 0.69,#EPE
#     "nuc_ppl": 0.85, #EPE - eff 33%
#     "solar_pv_ppl":0.29,
#     "oil_ppl": 0.75, #EPE
#     "grid3": 0.8,
#     "batt_se": 0.85,
#     "grid_se": 0.8,
# }

# # Capacity Factors for South

# capacity_factor_s = {
#     "hydro_2": 0.9,#EPE 
#     "hydro_11": 0.9,#EPE 
#     "sphs_2": 0.7,#EPE 
#     "sphs_11": 0.7,#EPE 
#     "bio_ppl": 0.33, #EPE
#     "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
#     "wind_ppl_rs": 0.4,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
#     "coal_ppl": 0.69,#EPE
#     "nuc_ppl": 0.85, #EPE - eff 33%
#     "solar_pv_ppl":0.29,
#     "oil_ppl": 0.75, #EPE
#     "grid4": 0.8,
#     "batt_s": 0.85,
#     "grid_s": 0.8,
# }


# :check %% Technology Historical New Capacity
#base capacity [GW] in 07/2019 according to CCEE historical operation for each subsystem [North, Northeast, SE/MW, South]
#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]

# Capacity for North
# times = 10. # Assumption Built in last 10 years
# thermal_capacity_n = 3.87 
# hydro_capacity_n = 22.12
# transmission_capacity_n = 5.02
# transmission_internal_capacity_n = 6.59

# # Capacity for Northeast
# thermal_capacity_ne = 8.40
# hydro_capacity_ne = 11.0
# transmission_capacity_ne = 2.51
# transmission_internal_capacity_ne = 13.23

# # Capacity for Southeast
# thermal_capacity_se = 18.69 
# hydro_capacity_se = 65.2
# transmission_capacity_se = 9.46
# transmission_internal_capacity_se = 51.2

# # Capacity for South
# thermal_capacity_s = 4.72
# transmission_capacity_s = 11.22
# transmission_internal_capacity_s = 18.0
# hydro_capacity_s = 17.0


# base_cap_n = {
#     "hydro_4": 9.6, 
#     "hydro_8": 11.03, 
#     "hydro_9": 1.2, 
#     "sphs_4": 0., 
#     "sphs_8": 0., 
#     "sphs_9": 0., 
#     "bio_ppl": 0.42957,     #thermal_capacity_n*0.111,  
#     "gas_ppl": 2.41101,     #thermal_capacity_n*0.623,
#     "gas_ppl_1": 0.,        #thermal_capacity_n*0.,
#     "gas_ppl_2": 0.,        #thermal_capacity_n*0.,
#     "gas_ppl_ccs": 0.,
#     "gas_ppl_ccs_1": 0.,
#     "gas_ppl_ccs_2": 0.,
#     "wind_ppl": 0.33, 
#     "coal_ppl": thermal_capacity_n*0.093, 
#     "nuc_ppl": 0., 
#     "solar_pv_ppl": 0.05,
#     "oil_ppl": thermal_capacity_n*0.173,
#     "grid1": transmission_capacity_n,
#     "batt_n": 0.,
#     "grid_n": transmission_internal_capacity_n,
# }

# base_cap_ne = {
#     "hydro_3": 8.3/times, 
#     "sphs_3": 0./times, 
#     "bio_ppl": thermal_capacity_ne*0.164/times,  
#     "gas_ppl": thermal_capacity_ne*0.359/times,
#     "gas_ppl_1": thermal_capacity_ne*0./times,
#     "gas_ppl_2": thermal_capacity_ne*0./times,
#     "gas_ppl_ccs": 0./times,
#     "gas_ppl_ccs_1": 0./times,
#     "gas_ppl_ccs_2": 0./times,
#     "wind_ppl_cos": 6.2/times, 
#     "wind_ppl_int": 5.94/times, 
#     "coal_ppl": thermal_capacity_ne*0.129/times, 
#     "nuc_ppl": 0./times, 
#     "solar_pv_ppl": 1.4/times,
#     "oil_ppl": thermal_capacity_ne*0.348/times,
#     "grid2": transmission_capacity_ne/times,
#     "batt_ne": 0./times,
#     "grid_ne": transmission_internal_capacity_ne/times,
# }

# base_cap_se = {
#     "hydro_1": 6.4/times, 
#     "hydro_5": 14./times, 
#     "hydro_6": 7.3/times, 
#     "hydro_7": 3.2/times,
#     "hydro_10": 27.6/times,
#     "hydro_12": 2.4/times,
#     "sphs_1": 0./times, 
#     "sphs_6": 0./times, 
#     "sphs_7": 0./times,
#     "sphs_10": 0./times,
#     "sphs_12": 0./times,
#     "bio_ppl": thermal_capacity_se*0.552/times,  
#     "gas_ppl": thermal_capacity_se*0.364/times,
#     "gas_ppl_1": thermal_capacity_se*0./times,
#     "gas_ppl_2": thermal_capacity_se*0./times,
#     "gas_ppl_ccs": 0./times,
#     "gas_ppl_ccs_1": 0./times,
#     "gas_ppl_ccs_2": 0./times,
#     "wind_ppl": 0.03/times, 
#     "coal_ppl": thermal_capacity_se*0.0/times, 
#     "nuc_ppl": 2.0/times, 
#     "solar_pv_ppl": 0.74/times,
#     "oil_ppl": thermal_capacity_se*0.084/times,
#     "grid3": transmission_capacity_se/times,
#     "batt_se": 0./times,
#     "grid_se": transmission_internal_capacity_se/times,
# }


# base_cap_s = {
#     "hydro_2": 6.9/times,
#     "hydro_11": 7.3/times,
#     "sphs_2": 0./times,
#     "sphs_11": 0./times,
#     "bio_ppl": thermal_capacity_s*0.266/times,  
#     "gas_ppl": thermal_capacity_s*0.291/times,
#     "gas_ppl_1": thermal_capacity_s*0./times,
#     "gas_ppl_2": thermal_capacity_s*0./times,
#     "gas_ppl_ccs": 0./times,
#     "gas_ppl_ccs_1": 0./times,
#     "gas_ppl_ccs_2": 0./times,
#     "wind_ppl_rs": 2.07/times,        
#     "coal_ppl": thermal_capacity_s*0.438/times, 
#     "nuc_ppl": 0./times, 
#     "solar_pv_ppl": 0.004/times,
#     "oil_ppl": thermal_capacity_s*0.005/times,
#     "grid4": transmission_capacity_s/times,
#     "batt_s": 0./times,
#     "grid_s": transmission_internal_capacity_s/times,
# }


# :check %% Technology Historical Activity

# Historical activity in North
# thermal_act_n = 1.82
# hydro_act_s_n = 7.53
# transmission_act_1_s_n = 0.43*transmission_capacity_n
# transmission_act_2_n = 0.40*transmission_capacity_n
# transmission_internal_act_n = 0.41*transmission_internal_capacity_n

# # Historical activity in Northeast
# thermal_act_ne = 1.98
# hydro_act_s_ne = 2.47
# transmission_act_1_s_ne = 0.49*transmission_capacity_ne
# transmission_act_2_ne = 0.24*transmission_capacity_ne
# transmission_internal_act_ne = 0.42*transmission_internal_capacity_ne

# # Historical activity in Southeast
# thermal_act_se = 5.11
# hydro_act_s_se = 28.93
# transmission_act_1_s_se = 0.48*transmission_capacity_se
# transmission_act_2_se = 0.05*transmission_capacity_se
# transmission_internal_act_se = 0.48*transmission_internal_capacity_se

# # Historical activity in South
# thermal_act_s = 1.05
# hydro_act_s = 7.45
# transmission_act_1_s = 0.47*transmission_capacity_s
# transmission_act_2_s = 0.11*transmission_capacity_s
# transmission_internal_act_s = 0.42*transmission_internal_capacity_s


# old_activity_n = {                                      #old activity basen on 2019 BEN
#     "hydro_4": 0.35*9.6, 
#     "hydro_8": 0.35*11.03, 
#     "hydro_9": 0.35*1.2, 
#     'bio_ppl': thermal_act_n *0.09,
#     'gas_ppl': thermal_act_n *0.81,
#     'gas_ppl_1': 0., 
#     'gas_ppl_2': 0.,
#     'gas_ppl_ccs': 0.,
#     'gas_ppl_ccs_1': 0.,
#     'gas_ppl_ccs_2': 0.,
#     'wind_ppl': 0.13,
#     'coal_ppl': thermal_act_n *0.09, 
#     'nuc_ppl': 0.,
#     'solar_pv_ppl': 0.001,
#     'oil_ppl': thermal_act_n *0.01,
#     'grid_n': transmission_internal_act_n,
#     }
# old_activity_n_1 = {'grid1': transmission_act_1_s_n,}     # Adding the old activity of transmission sistem in both modes
# old_activity_n_2 = {'grid1': transmission_act_2_n,}

# old_activity_ne = {
#     "hydro_3": 0.3*8.3, 
#     'bio_ppl': thermal_act_ne*0.102,
#     'gas_ppl': thermal_act_ne*0.493,
#     'gas_ppl_1': thermal_act_ne*0.,
#     'gas_ppl_2': thermal_act_ne*0.,
#     'gas_ppl_ccs': 0.,
#     'gas_ppl_ccs_1': 0.,
#     'gas_ppl_ccs_2': 0.,    
#     'wind_ppl_cos': 2.86,#Based on 2019 BEN 5.54 GWa informed, using percentages of generation from 2018 in RN and CE compared to the total amount of Northeast region. 
#     'wind_ppl_int': 2.68,#Based on 2019 BEN 5.54 GWa informed, using percentages of generation from 2018 in BA and PI compared to the total amount of Northeast region. 
#     'coal_ppl': thermal_act_ne*0.335, 
#     'nuc_ppl': 0. ,
#     'solar_pv_ppl': 0.37,
#     'oil_ppl': thermal_act_ne *0.071,
#     'grid_ne': transmission_internal_act_ne,
# }
# old_activity_ne_1 = {'grid2': transmission_act_1_s_ne,}
# old_activity_ne_2 = {'grid2': transmission_act_2_ne,}


# old_activity_se = {
#     "hydro_1": 0.48*6.4, 
#     "hydro_5": 0.48*14, 
#     "hydro_6": 0.48*7.3, 
#     "hydro_7": 0.48*3.2,
#     "hydro_10": 0.48*27.6,
#     "hydro_12": 0.48*2.4,
#     'bio_ppl': thermal_act_se*0.445,
#     'gas_ppl': thermal_act_se*0.522,
#     'gas_ppl_1': thermal_act_se*0.,
#     'gas_ppl_2': thermal_act_se*0.,
#     'gas_ppl_ccs': 0., 
#     'gas_ppl_ccs_1': 0.,
#     'gas_ppl_ccs_2': 0.,
#     'wind_ppl': 0.007,
#     'coal_ppl': thermal_act_se*0.0, 
#     'nuc_ppl': 1.841,
#     'solar_pv_ppl': 0.19,
#     'oil_ppl': thermal_act_se *0.033,
#     'grid_se': transmission_internal_act_se,
# }
# old_activity_se_1 = {'grid3': transmission_act_1_s_se,}
# old_activity_se_2 = {'grid3': transmission_act_2_se,}

# old_activity_s = {
#     "hydro_2": 0.52*6.9,
#     "hydro_11": 0.52*7.3,
#     "bio_ppl": 0.24*thermal_act_s,  
#     "gas_ppl": 0.023*thermal_act_s,
#     "gas_ppl_1": 0.0*thermal_act_s,
#     "gas_ppl_2": 0.0*thermal_act_s,
#     "gas_ppl_ccs": 0.,
#     "gas_ppl_ccs_1": 0.,
#     "gas_ppl_ccs_2": 0.,
#     "wind_ppl_rs": 0.7, 
#     "coal_ppl": 0.717*thermal_act_s, 
#     "nuc_ppl": 0.0, 
#     "solar_pv_ppl": 0.01,
#     "oil_ppl": 0.019*thermal_act_s,
#     'grid_s': transmission_internal_act_s,
# }
# old_activity_1_s = { 'grid4': transmission_act_1_s,}
# old_activity_2_s = {'grid4': transmission_act_2_s,}


# :check %% Bound Activity Up
# Bound activities of hydros based on this source peak generation between 2018-2020 for the subsistem in order to keep the historical production from this source

# North activity up bound
# dados['bound']['activity_up']['North'] = {
#     "hydro_4": 3.41,
#     "hydro_8": 3.91,
#     "hydro_9": 0.43,
# }

# # Northeast activity up bound
# bound_act_up_ne = {
#     "hydro_3": 4.33, 
# }

# # Southeast activity up bound
# bound_act_up_se = {
#     "hydro_1": 3.15, 
#     "hydro_5": 6.89,
#     "hydro_6": 3.59,
#     "hydro_7": 1.58,
#     "hydro_10": 13.58,
#     "hydro_12": 1.18, 
# }

# # South activity up bound
# bound_act_up_s = {
#     "hydro_2": 3.66,
#     "hydro_11": 3.87,
# }


# :check %% Bound Capacity Up

# North capacity up bound
# total_cap_n = {
#     'hydro_4': 9.6,
#     'hydro_8': 11.03,
#     'hydro_9': 1.2,
#     #'sphs_4': 1.,
#     #'sphs_8': 1.,
#     #'sphs_9': 1.,
#     'wind_ppl': 0.18,
#     'nuc_ppl':0.,
#     'gas_ppl':1.5*thermal_capacity_n*0.623,
#     'gas_ppl_1':2*thermal_capacity_n*0.623,
#     'gas_ppl_ccs':1.5*thermal_capacity_n*0.623,
#     'gas_ppl_ccs_1':2*thermal_capacity_n*0.623,
#     "bio_ppl": 3.,
#     'solar_pv_ppl': 5.,
#     'coal_ppl': 2.9,
#     'oil_ppl': 0.6, # oil ppl won't be able to raise up it's capacity on the country, considering the environmental restrictions related to this resource.
#     #"batt_n": 10.,
# }

# # Northeast capacity up bound
# total_cap_ne = {
#     'hydro_3': 8.3,
#     #'sphs_3': 1.,
#     'wind_ppl_cos': 80,
#     'wind_ppl_int': 80,
#     'solar_pv_ppl': 10,
#     "gas_ppl": 4.71,
#     "gas_ppl_1": 16,                   
#     "gas_ppl_ccs": 4.71,
#     "gas_ppl_ccs_1": 16,
#     'nuc_ppl': 0.,
#     "bio_ppl": 5.,
#     'coal_ppl': 7.0, 
#     'oil_ppl': 2.9,#oil ppl won't be able to raise up it's capacity on the country, considering the environmental restrictions related to this resource
#     #"batt_ne": 20,
# }

# # Southeast capacity up bound
# total_cap_se = { 
#     "hydro_1": 6.4,
#     "hydro_5": 14.,
#     "hydro_6": 7.3,
#     "hydro_7": 3.2,
#     "hydro_10": 27.6,
#     "hydro_12": 2.4,
#     #"sphs_1": 1.,
#     #"sphs_6": 1.,
#     #"sphs_7": 1.,
#     #"sphs_10": 1.,
#     #"sphs_12": 1.,
#     "coal_ppl": 7.0,
#     "bio_ppl": 17.,
#     "oil_ppl": 3,
#     "gas_ppl": 12.24,
#     "gas_ppl_1": 30,
#     "gas_ppl_ccs": 12.24,
#     "gas_ppl_ccs_1": 30,
#     "nuc_ppl": 5.,
#     "wind_ppl": 0.03,
#     "solar_pv_ppl": 25.,
#     #"batt_se": 50.,       
# }

# # South capacity up bound
# total_cap_s = {
#     "hydro_2": 6.9,
#     "hydro_11": 7.3,
#     #"sphs_2": 1.,
#     #"sphs_11": 1.,
#     "coal_ppl": 7.0,
#     "oil_ppl": 0.13,
#     "gas_ppl": 1.5*thermal_capacity_n*0.291,
#     "gas_ppl_1": 16,
#     "gas_ppl_ccs": 1.5*thermal_capacity_n*0.291,
#     "gas_ppl_ccs_1": 16,
#     'nuc_ppl':0.,
#     "bio_ppl": 5.,
#     "wind_ppl_rs": 70.0,
#     "solar_pv_ppl": 10.0,
#     #"batt_s": 20.,
# }

# :check %% Technology efficiency and water consumption

# # Grid efficiency
# dados['efficiency']['transmission'] = 0.95
# dados['efficiency']['distribution'] = 0.95

# # Battery efficiency
# dados['efficiency']['battery'] = 1.2 # losses to store 1 GWa of energy. eg.: 20%

# :check %% Hydro
# Hydro North
# n_hydro_out      = {"hydro_4": 1,       # GWa generated
#                     "hydro_8": 1,
#                     "hydro_9": 1}
# n_hydro_out_2    = {"hydro_4": 1558.6,  # m^3/s of water outflow to generate 1 GWa
#                     "hydro_8": 1317.0,
#                     "hydro_9": 4898.5}
# n_hydro_in       = {"hydro_4": 1558.6,  # m^3/s of water inflow to generate 1 GWa
#                     "hydro_8": 1317.0,
#                     "hydro_9": 4898.5}

# # Hydro Northeast
# ne_hydro_out     = {"hydro_3": 1.}      # GWa generated
# ne_hydro_out_2   = {"hydro_3": 595.1}   # m^3/s of water outflow to generate 1 GWa
# ne_hydro_in      = {"hydro_3": 595.1}   # m^3/s of water inflow to generate 1 GWa

# # Hydro Southeast
# se_hydro_out     = {"hydro_1": 1,
#                     "hydro_5": 1.,
#                     "hydro_6": 1., 
#                     "hydro_7": 1.,
#                     "hydro_10": 1., 
#                     "hydro_12": 1.,
#                     }
# se_hydro_out_2   = {"hydro_1": 456.0,
#                     "hydro_5": 968.0,
#                     "hydro_6": 3793.4, 
#                     "hydro_7": 1205.3,
#                     "hydro_10": 560.6, 
#                     "hydro_12": 1004.9,
#                     }
# se_hydro_in      = {"hydro_1": 456.0,
#                     "hydro_5": 968.0,
#                     "hydro_6": 3793.4, 
#                     "hydro_7": 1205.3,
#                     "hydro_10": 560.6, 
#                     "hydro_12": 1004.9,
#                     }

# # Hydro South
# s_hydro_out      = {"hydro_2": 1.,
#                     "hydro_11": 1.}
# s_hydro_out_2    = {"hydro_2": 431.4,  # m^3/s of water outflow to generate 1 GWa
#                     "hydro_11": 457.4}
# s_hydro_in       = {"hydro_2": 431.4,  # m^3/s of water inflow to generate 1 GWa
#                     "hydro_11": 457.4}

# :check %% SPHS

# SPHS North
# n_sphs_out       = {"sphs_4": 1,       # GWa generated
#                     "sphs_8": 1,
#                     "sphs_9": 1}
# n_sphs_out_2     = {"sphs_4": 73.,     # m^3/s of water outflow to generate 1 GWa
#                     "sphs_8": 86.,
#                     "sphs_9": 23.}
# n_sphs_in        = {"sphs_4": 73.,     # m^3/s of water inflow to generate 1 GWa
#                     "sphs_8": 86.,
#                     "sphs_9": 23.}
# n_sphs_in_2      = {"sphs_4": 1.2,     # losses to store 1 GWa of energy. eg.: 20%
#                     "sphs_8": 1.2,
#                     "sphs_9": 1.2}

# # SPHS Northeast
# ne_sphs_out = {"sphs_3": 1,}        # GWa generated
# ne_sphs_out_2 = {"sphs_3": 190.}    # m^3/s of water outflow to generate 1 GWa
# ne_sphs_in = {"sphs_3": 190.}       # m^3/s of water inflow to generate 1 GWa
# ne_sphs_in_2 = {"sphs_3": 1.2}      # losses to store 1 GWa of energy. eg.: 20%

# # SPHS Southeast
# se_sphs_out = {"sphs_1": 1,
#                "sphs_6": 1,
#                "sphs_7": 1,
#                "sphs_10": 1,
#                "sphs_12": 1
#            }
# se_sphs_out_2 =  {"sphs_1": 248,
#                "sphs_6": 30,
#                "sphs_7": 94,
#                "sphs_10": 202,
#                "sphs_12": 112
#               }
# se_sphs_in = {"sphs_1": 248,
#                "sphs_6": 30,
#                "sphs_7": 94,
#                "sphs_10": 202,
#                "sphs_12": 112
#               }
# se_sphs_in_2 = {"sphs_1": 1.2,
#                     "sphs_6": 1.2,
#                     "sphs_7": 1.2, 
#                     "sphs_10": 1.2, 
#                     "sphs_12": 1.2,
#                     }

# # SPHS South
# s_sphs_out = {"sphs_2": 1,
#               "sphs_11": 1,
#                }
# s_sphs_out_2 =  {"sphs_2": 263,
#               "sphs_11": 247,
#               }
# s_sphs_in = {"sphs_2": 263,
#               "sphs_11": 247,
#               }
# s_sphs_in_2 = {"sphs_2": 1.2,     # losses to store 1 GWa of energy. eg.: 20%
#                 "sphs_11": 1.2,
#                 }

# :check %% Water supply

# Water supply North
# n_water_out      = {"water_supply_4": 1558.6,   # water to final use
#                     "water_supply_8": 1317.0,
#                     "water_supply_9": 4898.5}
# n_water_in       = {"water_supply_4": 1558.6,   # water comming from river
#                     "water_supply_8": 1317.0,
#                     "water_supply_9": 4898.5}

# # Water supply Northeast
# ne_water_out     = {"water_supply_3": 595.1,}
# ne_water_in      = {"water_supply_3": 595.1,}

# # Water supply Southeast
# se_water_out = {"water_supply_1": 456.0,
#                 "water_supply_5": 968.0,
#                 "water_supply_6": 3793.4, 
#                 "water_supply_7": 1205.3,
#                 "water_supply_10": 560.6, 
#                 "water_supply_12": 1004.9,
#                  }
# se_water_in = {"water_supply_1": 456.0,
#                 "water_supply_5": 968.0,
#                 "water_supply_6": 3793.4, 
#                 "water_supply_7": 1205.3,
#                 "water_supply_10": 560.6, 
#                 "water_supply_12": 1004.9,
#                  }

# # Water supply South
# s_water_out = {"water_supply_2": 431.4,
#                 "water_supply_11": 457.4,
#               }
# s_water_in = {"water_supply_2": 431.4,
#                 "water_supply_11": 457.4,
#               }


# :check %% Technology costs :check 
'''
- inv cost in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
- fix cost in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M costs based on the size of the plant, e.g. lightening, labor, scheduled maintenance, etc.)
- var cost in $ / MWh (variable cost of generation, considering fuel costs, variable O&M costs, etc.)
'''

# Costs for North
# dados['cost']['inv_cost']['North'] = {
#     "hydro_4": 1352, #EPE mean value for UHE
#     "hydro_8": 1352, #EPE mean value for UHE
#     "hydro_9": 1352,#EPE mean value for UHE
#     "sphs_4": 1500,#EPE
#     "sphs_8": 1500,#EPE
#     "sphs_9": 1500,#EPE
#     "bio_ppl": 1200,#EPE 
#     "gas_ppl": 900, #EPE mean value
#     "gas_ppl_1": 1000, #EPE mean value
#     "gas_ppl_2": 1000, #EPE mean value
#     "gas_ppl_ccs": 1.8*900, #PNE value
#     "gas_ppl_ccs_1": 1.8*1000, #PNE value
#     "gas_ppl_ccs_2": 1.8*1000, #PNE value
#     "wind_ppl": 1200,#EPE mean value
#     "coal_ppl": 2500, #EPE
#     "nuc_ppl": 5000,#EPE
#     "solar_pv_ppl":1100, #min value in EPE, max value is 1350
#     "oil_ppl": 1100,
#     'grid1': 359,
#     "batt_n": 1271,#NREL study
#     'grid_n': 205,
# }
# fix_cost_n = {
#     "hydro_4": 12.8, #EPE
#     "hydro_8": 12.8, #EPE 
#     "hydro_9": 12.8,#EPE 
#     "sphs_4": 20.5, #EPE
#     "sphs_8": 20.5, #EPE 
#     "sphs_9": 20.5,#EPE 
#     "bio_ppl": 30.8, #EPE
#     "gas_ppl": 43.6,#EPE
#     "gas_ppl_1": 43.6,#EPE
#     "gas_ppl_2": 43.6,#EPE
#     "gas_ppl_ccs": 43.6,#PNE
#     "gas_ppl_ccs_1": 43.6,#PNE
#     "gas_ppl_ccs_2": 43.6,#PNE
#     "wind_ppl": 25.6,#EPE
#     "coal_ppl": 89.7,#EPE
#     "nuc_ppl": 83.3, #EPE
#     "solar_pv_ppl":16.7, #EPE
#     "oil_ppl": 56.4,
#     "batt_n": 31.8, #NREL
# }
# var_cost_n = {
#     "gas_ppl": 219.8, #Considering Gas cost of 4 US$/MMBtu
#     "gas_ppl_1": 329.8, #Considering Gas cost of 6 US$/MMBtu
#     "gas_ppl_2": 439.7, #Considering Gas cost of 8 US$/MMBtu
#     "gas_ppl_ccs": 219.8, #Considering Gas cost of 4 US$/MMBtu
#     "gas_ppl_ccs_1": 329.8, #Considering Gas cost of 6 US$/MMBtu
#     "gas_ppl_ccs_2": 439.7, #Considering Gas cost of 8 US$/MMBtu
#     "coal_ppl": 298.7, #EPE
#     "oil_ppl": 898,
#     "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
# }

# # Costs for Northeast
# inv_cost_ne = {
#     "hydro_3": 1352,#EPE mean value for UHE
#     "sphs_3": 1500,#EPE
#     "bio_ppl": 1200,#EPE 
#     "gas_ppl": 900, #EPE mean value
#     "gas_ppl_1": 1000, #EPE mean value
#     "gas_ppl_2": 1000, #EPE mean value
#     "gas_ppl_ccs": 1.8*900, #PNE
#     "gas_ppl_ccs_1": 1.8*1000, #PNE
#     "gas_ppl_ccs_2": 1.8*1000, #PNE
#     "wind_ppl_cos": 1200,#It will be considered same values. The only difference will be capacity factor
#     "wind_ppl_int": 1200,#It will be considered same values. The only difference will be capacity factor
#     "coal_ppl": 2500, #EPE
#     "nuc_ppl": 5000,#EPE
#     "solar_pv_ppl":1100, #min value in EPE, max value is 1350
#     "oil_ppl": 1100,
#     'grid2': 359,
#     "batt_ne": 1271, #NREL study
#     'grid_ne': 205,
# }
# fix_cost_ne = {
#     "hydro_3": 12.8,#EPE
#     "sphs_3": 20.5,#EPE
#     "bio_ppl": 30.8, #EPE
#     "gas_ppl": 43.6,#EPE
#     "gas_ppl_1": 43.6,#EPE
#     "gas_ppl_2": 43.6,#EPE
#     "gas_ppl_ccs": 43.6,#EPE
#     "gas_ppl_ccs_1": 43.6,#EPE
#     "gas_ppl_ccs_2": 43.6,#EPE
#     "wind_ppl_cos": 25.6,#EPE
#     "wind_ppl_int": 25.6,#EPE
#     "coal_ppl": 89.7,#EPE
#     "nuc_ppl": 83.3, #EPE
#     "solar_pv_ppl":16.7, #EPE
#     "oil_ppl": 56.4,
#     "batt_ne": 31.8,#NREL
# }
# var_cost_ne = {
#     "gas_ppl": 219.8, #EPE mean value
#     "gas_ppl_1": 329.8, #EPE mean value
#     "gas_ppl_2": 439.7, #EPE mean value
#     "gas_ppl_ccs": 219.8, #EPE mean value
#     "gas_ppl_ccs_1": 329.8, #EPE mean value
#     "gas_ppl_ccs_2": 439.7, #EPE mean value
#     "coal_ppl": 298.7, #EPE
#     "oil_ppl": 898,
#     "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
# }

# # Costs for Southeast
# inv_cost_se = {
#     "hydro_1": 1352,#EPE mean value for UHE
#     "hydro_5": 1352,#EPE mean value for UHE
#     "hydro_6": 1352,#EPE mean value for UHE
#     "hydro_7": 1352,#EPE mean value for UHE
#     "hydro_10": 1352,#EPE mean value for UHE
#     "hydro_12": 1352,#EPE mean value for UHE
#     "sphs_1": 1500,#EPE
#     "sphs_6": 1500,#EPE
#     "sphs_7": 1500,#EPE
#     "sphs_10": 1500,#EPE
#     "sphs_12": 1500,#EPE
#     "bio_ppl": 1200,#EPE 
#     "gas_ppl": 900, #EPE mean value
#     "gas_ppl_1": 1000, #EPE mean value
#     "gas_ppl_2": 1000, #EPE mean value
#     "gas_ppl_ccs": 1.8*900, #EPE mean value
#     "gas_ppl_ccs_1": 1.8*1000, #EPE mean value
#     "gas_ppl_ccs_2": 1.8*1000, #EPE mean value
#     "wind_ppl": 1200,#EPE mean value
#     "coal_ppl": 2500, #EPE
#     "nuc_ppl": 5000,#EPE
#     "solar_pv_ppl":1100, #min value in EPE, max value is 1350
#     "oil_ppl": 1100,
#     'grid3': 462,
#     "batt_se": 1271, #NREL study
#     'grid_se': 205,
# }
# fix_cost_se = {
#     "hydro_1": 12.8,
#     "hydro_5": 12.8,
#     "hydro_6": 12.8,
#     "hydro_7": 12.8,
#     "hydro_10": 12.8,
#     "hydro_12": 12.8,
#     "sphs_1": 20.5,#EPE
#     "sphs_6": 20.5,#EPE
#     "sphs_7": 20.5,#EPE
#     "sphs_10": 20.5,#EPE
#     "sphs_12": 20.5,#EPE   
#     "bio_ppl": 30.8, #EPE
#     "gas_ppl": 43.6,#EPE
#     "gas_ppl_1": 43.6,#EPE
#     "gas_ppl_2": 43.6,#EPE
#     "gas_ppl_ccs": 43.6,#EPE
#     "gas_ppl_ccs_1": 43.6,#EPE
#     "gas_ppl_ccs_2": 43.6,#EPE
#     "wind_ppl": 25.6,#EPE
#     "coal_ppl": 89.7,#EPE
#     "nuc_ppl": 83.3, #EPE
#     "solar_pv_ppl":16.7, #EPE
#     "oil_ppl": 56.4,
#     "batt_se": 31.8, #NREL
# }
# var_cost_se = {
#     "gas_ppl": 219.8, #EPE mean value
#     "gas_ppl_1": 329.8, #EPE mean value
#     "gas_ppl_2": 439.7, #EPE mean value
#     "gas_ppl_ccs": 219.8, #EPE mean value
#     "gas_ppl_ccs_1": 329.8, #EPE mean value
#     "gas_ppl_ccs_2": 439.7, #EPE mean value
#     "coal_ppl": 298.7, #EPE
#     "oil_ppl": 898,
#     "nuc_ppl": 53.3,
#     "bio_ppl":0.000001, #Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
# }

# # Costs for South
# inv_cost_s = {
#     "hydro_2": 1352,#EPE mean value for UHE
#     "hydro_11": 1352,
#     "sphs_2": 1500,#EPE mean value for UHE
#     "sphs_11": 1500,
#     "bio_ppl": 1200,#EPE 
#     "gas_ppl": 900, #EPE mean value
#     "gas_ppl_1": 1000, #EPE mean value
#     "gas_ppl_2": 1000, #EPE mean value
#     "gas_ppl_ccs": 1.8*900, #PNE
#     "gas_ppl_ccs_1": 1.8*1000, #PNE
#     "gas_ppl_ccs_2": 1.8*1000, #PNE
#     "wind_ppl_rs": 1200,#EPE mean value
#     "coal_ppl": 2100, #EPE
#     "nuc_ppl": 5000,#EPE
#     "solar_pv_ppl":1100, #min value in EPE, max value is 1350
#     "oil_ppl": 1100,
#     'grid4': 205,#EPE NT pr 007/2018
#     "batt_s": 1271,#NREL study
#     'grid_s': 205,
#   }
# fix_cost_s = {
#     "hydro_2": 12.8,#EPE
#     "hydro_11": 12.8,#EPE
#     "sphs_2": 20.5,#EPE
#     "sphs_11": 20.5,#EPE
#     "bio_ppl": 30.8, #EPE
#     "gas_ppl": 43.6,#EPE
#     "gas_ppl_1": 43.6,#EPE
#     "gas_ppl_2": 43.6,#EPE
#     "gas_ppl_ccs": 43.6,#EPE
#     "gas_ppl_ccs_1": 43.6,#EPE
#     "gas_ppl_ccs_2": 43.6,#EPE
#     "wind_ppl_rs": 25.6,#EPE
#     "coal_ppl": 89.7,#EPE
#     "nuc_ppl": 83.3, #EPE
#     "solar_pv_ppl":16.7, #EPE
#     "oil_ppl": 56.4,
#     "batt_s": 31.8, #NREL
# }
# var_cost_s = {
#     "gas_ppl": 219.8, #EPE mean value
#     "gas_ppl_1": 329.8, #EPE mean value
#     "gas_ppl_2": 439.7, #EPE mean value
#     "gas_ppl_ccs": 219.8, #EPE mean value
#     "gas_ppl_ccs_1": 329.8, #EPE mean value
#     "gas_ppl_ccs_2": 439.7, #EPE mean value
#     "coal_ppl": 136.6, #EPE national coal
#     "oil_ppl": 898,
#     "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
# }


# %% =============================== Start Model ===============================

scenario = message_ix.Scenario(mp, model, scen, version = 'new')

# Adding units to the library
mp.add_unit('m^3/s')  
mp.add_unit('MMUSD/GW')

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


year_df = scenario.vintage_and_active_years()
vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

[x for x in scenario.par_list() if 'mode' in scenario.idx_sets(x)]

# %% Technical lifetime
base_technical_lifetime = {
    'year_vtg': dados['general']['horizon'],
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
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + dados['lifetimes']['North'][tech] 
     tech_out_n = tech_out_n.loc[condition]
     
     scenario.add_par('output', tech_out_n)
     
for tech in dados['technology']['plants']:
     tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")

     # Removing extra years based on lifetime 
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + dados['lifetimes']['North'][tech] 
     tech_out_n = tech_out_n.loc[condition] 
     scenario.add_par('output', tech_out_n)

# Techs in Northeast
for tech in dados['technology']['plants']:
     tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
      # Removing extra years based on lifetime 
     condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
     tech_out_ne = tech_out_ne.loc[condition]
     scenario.add_par('output', tech_out_ne)

for tech in dados['technology']['northeast_wind']:
     tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
      # Removing extra years based on lifetime 
     condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + dados['lifetimes']['Northeast'][tech] 
     tech_out_ne = tech_out_ne.loc[condition]
     scenario.add_par('output', tech_out_ne)

# Techs in Southeast
for tech in dados['technology']['brazil_wind']:
     tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
     tech_out_se = tech_out_se.loc[condition]
     scenario.add_par('output', tech_out_se)

for tech in dados['technology']['plants']:
     tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + dados['lifetimes']['Southeast'][tech] 
     tech_out_se = tech_out_se.loc[condition]
     scenario.add_par('output', tech_out_se)

# Techs in South
for tech in dados['technology']['plants']:
     tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + dados['lifetimes']['South'][tech] 
     tech_out_s = tech_out_s.loc[condition]
     scenario.add_par('output', tech_out_s)

for tech in dados['technology']['south_wind']:
     tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + dados['lifetimes']['South'][tech] 
     tech_out_s = tech_out_s.loc[condition]
     scenario.add_par('output', tech_out_s)


# %% Add Capacity Factors and Historical Capacity

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
    df = make_df(base_capacity, node_loc='Southeast', technology=tec, value=val)
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

# Capacity Factor for South
for tec, val in dados['capacity_factor']['South'].items():
    df = make_df(base_capacity_factor, node_loc='South', technology=tec, value=val)
    # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + dados['lifetimes']['South'][tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)

for tec, val in dados['historical_new_capacity']['South'].items():
    df = make_df(base_capacity, node_loc='South', technology=tec, value=val)
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?


# %% Add Costs                      (investment, fixed and variable)

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


# %% Add Historical Acitvity

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

# %% Add Bound Activity up

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

    
# %% Add Bound Capacity up
       
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

# %% solving the model

## Commit the datastructure and solve the model

scenario.commit(comment='Brazilian_base')

scenario.solve()
scenario.var('OBJ')['lvl']
scenario.set_as_default()
scenario.version
# scenario.to_excel('SIN expandido base.xlsx')

mp.close_db()



      
