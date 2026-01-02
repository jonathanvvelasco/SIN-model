# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 14:38:04 2026

@author: jonat
"""

import ixmp as ix
import message_ix
from timeit import default_timer as timer

# Loading modelling platform
mp = ix.Platform("default", jvmargs=["-Xmx8G"])

# %% Cloning the storage scenario to add emission factor
model = 'SIN Brasil expandido'
scenario='storage v.2'
base = message_ix.Scenario(mp, model, scenario= scenario)
scen = base.clone(model,'emissions_test',keep_solution=False)
scen.check_out()

start = timer()
scen.solve()
end = timer()
print('Elapsed time for solving scenario:', int((end - start)/60),
              'min and', round((end - start) % 60, 2), 'sec.')

mp.close_db()