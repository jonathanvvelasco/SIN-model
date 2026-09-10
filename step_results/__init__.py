try:
    from .view_results import *
except ImportError:
    print("Failed to import view_results. In case of issues, check if the necessary modules are installed.")
try:
    from .view_sankey import *
except ImportError:
    print("Failed to import view_sankey. In case of issues, check if the necessary modules are installed.")