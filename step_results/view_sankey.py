import pandas as pd
import ixmp as ix # type: ignore
from message_ix import Scenario # type: ignore
from message_ix.report import Reporter # type: ignore
from genno.operator import concat # type: ignore
from message_ix.tools.sankey import map_for_sankey # type: ignore
from pyam.figures import sankey # type: ignore
import webbrowser
from pathlib import Path

def view_sankey(mp, model, scenario, subsystems, annums):
    
    scenario = Scenario(mp, model, scenario)
    
    if not scenario.has_solution():
        scenario.solve(quiet=True)    # Load the scenario

    for subsystem in subsystems:
        for annum in annums:
            # Create Sankey diagram for each subsystem and year
            rep = Reporter.from_scenario(scenario, units={"replace": {"-": ""}}) # Remove "-" from units
            df_all = concat(rep.get("in::pyam"), rep.get("out::pyam"))           # Concatenate input and output dataframes
            df = df_all.filter(year=annum, region=subsystem+'|'+subsystem)       # Filter for the year and subsystem
            mapping = map_for_sankey(df, node=subsystem,)                        # Map the data for Sankey diagram
            fig = sankey(df=df, mapping=mapping)                                 # Create the Sankey diagram
            fig.show()
    
            output_dir = Path(__file__).resolve().parents[1] / "Output files"
            output_dir.mkdir(parents=True, exist_ok=True)
            html_path = output_dir / f"sankey_energy_messageix_{subsystem}_{annum}.html"
            png_path = output_dir / f"sankey_energy_messageix_{subsystem}_{annum}.png"
            txt_path = output_dir / f"sankey_energy_messageix_{subsystem}_{annum}.txt"

            written = False

            # 1) Plotly figure with write_html
            if hasattr(fig, "write_html"):
                try:
                    fig.write_html(html_path, include_plotlyjs="cdn", auto_open=False)
                    webbrowser.open(html_path.as_uri())
                    print(f"Sankey written to {html_path}")
                    written = True
                except Exception as e:
                    print(f"plotly.write_html failed: {e}")

            # 2) Try plotly.io.to_html (handles dicts or plotly-compatible objects)
            if not written:
                try:
                    import plotly.io as pio  # type: ignore

                    html = pio.to_html(fig, include_plotlyjs="cdn")
                    html_path.write_text(html, encoding="utf-8")
                    webbrowser.open(html_path.as_uri())
                    print(f"Sankey written to {html_path}")
                    written = True
                except Exception as e:
                    print(f"plotly.io.to_html failed: {e}")

            # 3) If it's a Matplotlib figure, save as PNG
            if not written:
                try:
                    from matplotlib.figure import Figure  # type: ignore

                    if isinstance(fig, Figure):
                        fig.savefig(png_path, dpi=200)
                        webbrowser.open(png_path.as_uri())
                        print(f"Sankey written to {png_path}")
                        written = True
                except Exception as e:
                    print(f"matplotlib save failed: {e}")

            # 4) Fallback: dump repr() to a text file
            if not written:
                try:
                    txt_path.write_text(repr(fig), encoding="utf-8")
                    print(f"Sankey object dumped to {txt_path}; inspect contents manually.")
                except Exception as e:
                    print(f"Failed to write sankey object: {e}")

    return fig

if __name__ == "__main__":
    # Loading modelling platform
    mp = ix.Platform("default", jvmargs=["-Xmx8G"])
    
    # Specifying model/scenario to be loaded from the database
    model = "SIN Brasil expandido"
    scenario = 'reference'
    subsystems = ['North']
    annums = [2030] # [2025, 2030, 2035]
    fig = view_sankey(mp, model, scenario, subsystems, annums)  
    
    # Close DB
    mp.close_db()