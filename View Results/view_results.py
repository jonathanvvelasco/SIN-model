# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 12:01:39 2025

@author: jonat
"""


import ixmp as ix
import message_ix
import matplotlib as plt


# Loading modelling platform
mp = ix.Platform("default", jvmargs=["-Xmx8G"])

# Specifying model/scenario to be loaded from the database
# model = 'SIN Brasil expandido'
# scenario='base'
model = "SIN Brasil expandido"
scenario = 'storage v.2'
nodes = ['South', 'North', 'Northeast', 'Southeast']
base = message_ix.Scenario(mp, model, scenario= scenario)


from message_ix.report import Reporter
from message_ix.util.tutorial import prepare_plots

rep = Reporter.from_scenario(base)
prepare_plots(rep)

# %% Report Activity and Capacity
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
                    "wind_ppl_rs"
                    ])
rep.get("plot activity")
rep.get("plot capacity")
rep.get("plot new capacity")

rep.set_filters(c=["electricity"]) # Somente commodity eletricidade
rep.get("plot prices")
rep.get("plot demand")
# plt.show()

act = rep.get("ACT")

mp.close_db()# -*- coding: utf-8 -*-




