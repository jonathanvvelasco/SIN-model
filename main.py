import yaml
import ixmp
import message_ix

import step1_SIN_Baseline
import step_results


# %% Inputs
input_file = "baseline_inputs.yaml"
model = "SIN Brasil expandido"
scen = "base"


# %% Model 

# Open input data
path = f"inputs/{input_file}"
with open (path, "r") as f:
    dados = yaml.safe_load(f)

# Create a new scenario
mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])
scenario = message_ix.Scenario(mp, model, scen, version = 'new')

mp.add_unit('m^3/s')  
mp.add_unit('MMUSD/GW')

# Add data to the model
scenario = step1_SIN_Baseline.start_model(scenario, dados)   # Creates a new scenario
scenario = step1_SIN_Baseline.technical_lifetime(scenario, dados)
scenario = step1_SIN_Baseline.technologies(scenario, dados)
scenario = step1_SIN_Baseline.capacity_factors_and_historical_capacity(scenario, dados)
scenario = step1_SIN_Baseline.costs(scenario, dados)
scenario = step1_SIN_Baseline.historical_activity(scenario, dados)
scenario = step1_SIN_Baseline.bound_activity_up(scenario, dados)
scenario = step1_SIN_Baseline.bound_total_capacity_up(scenario, dados)
# scenario = step1_SIN_Baseline.bound_growth_capacity_up(scenario, dados, growth_cap=0.3) # Growth capacity bound to 30%

# solving the model
scenario.commit(comment='Brazilian_base')       ## Commit the datastructure and solve the model
scenario.solve()
scenario.var('OBJ')['lvl']
scenario.set_as_default()
scenario.version
# scenario.to_excel('SIN expandido base.xlsx')
mp.close_db()    

# Generate plots
mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])
step_results.gen_plot(mp, model, scen)
mp.close_db() 
