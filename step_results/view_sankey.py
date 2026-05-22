import pandas as pd
import ixmp as ix # type: ignore
from message_ix import Scenario # type: ignore
from message_ix.report import Reporter # type: ignore
from genno.operator import concat # type: ignore
from message_ix.tools.sankey import map_for_sankey # type: ignore
from pyam.figures import sankey # type: ignore
import webbrowser
import re
from pathlib import Path

def water_m3_to_Gwa(scenario, df, mapping, subsystem, annum):
    # Adjust values: for flows with commodity 'water', divide by the
    # input value of the corresponding 'hydro' technology at the
    # same node and year.
    try:
        input_par = scenario.par("input").copy()
        # Sum hydro inputs by node, technology suffix, and year
        hydro_inputs = (
            input_par[input_par["technology"].str.startswith("hydro", na=False)]
            .groupby(["node_loc", "technology", "year_act"], as_index=False)["value"]
            .mean()
        )

        # Convert iam df to long pandas DataFrame (try common APIs)
        pdf = None
        try:
            if hasattr(df, "data"):
                pdf = df.data.reset_index()
            elif hasattr(df, "dataframe"):
                pdf = df.dataframe().reset_index()
            elif hasattr(df, "to_dataframe"):
                pdf = df.to_dataframe().reset_index()
        except Exception:
            pdf = None

        if pdf is not None and "variable" in pdf.columns and "value" in pdf.columns:
            # Identify variables whose mapped source/target contains 'water'
            water_vars = [
                v
                for v, (s, t) in mapping.items()
                if (isinstance(s, str) and "water" in s.lower()) or (isinstance(t, str) and "water" in t.lower())
            ]

            if water_vars:
                hrow = hydro_inputs.loc[
                    (hydro_inputs["node_loc"] == subsystem) & (hydro_inputs["year_act"] == annum)
                ]
                
                
                for water_var in water_vars:
                    try: 
                        pdf_var = pdf.loc[pdf["variable"] == water_var, "variable"].iloc[0]
                        pdf_hyd = "_".join(["hydro", pdf_var.split("|")[2].split("_")[1]])
                        inp_hyd = hrow.loc[hrow["technology"] == pdf_hyd, "value"].iloc[0]
                        wat_val = pdf.loc[pdf["variable"] == pdf_var, "value"].iloc[0] / inp_hyd
                        # val_ant = pdf.loc[pdf["variable"]==pdf_var, "value"].iloc[0]
                        pdf.loc[pdf["variable"] == pdf_var, "value"] = wat_val
                        # print(f"O valor passou de {val_ant} para {wat_val}")
                    except:
                        print("Deu ruim.")
                # Recreate an IamDataFrame from the modified pandas DF
                try:
                    import pyam

                    # Keep only columns pyam expects to avoid issues
                    expected = ["model", "scenario", "region", "variable", "unit", "year", "value"]
                    keep = [c for c in expected if c in pdf.columns]
                    if "variable" not in keep or "value" not in keep:
                        raise ValueError("modified dataframe missing required columns for pyam")
                    pdf2 = pdf[keep].copy()
                    new_df = pyam.IamDataFrame(pdf2)
                    df_for_plot = new_df
                except Exception as e:
                    print(f"DEBUG: failed to recreate IamDataFrame: {e}")
                    df_for_plot = df
            else:
                print("DEBUG: no water_vars found in mapping; skipping adjustment")
                df_for_plot = df
        else:
            df_for_plot = df
    except Exception as e:
        print(f"Failed to adjust water values: {e}")
        df_for_plot = df

    return df_for_plot

def fig_to_html(fig, subsystem, annum):
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

def apply_sankey_node_positions(fig, node_positions=None, arrangement="snap"):
    if not node_positions:
        return fig

    for trace in getattr(fig, "data", []):
        if getattr(trace, "type", None) != "sankey":
            continue

        node = getattr(trace, "node", None)
        node_labels = getattr(node, "label", None)
        labels = list(node_labels) if node_labels is not None else []

        node_x = getattr(node, "x", None)
        node_y = getattr(node, "y", None)
        x_positions = list(node_x) if node_x is not None else [None] * len(labels)
        y_positions = list(node_y) if node_y is not None else [None] * len(labels)

        for key, position in node_positions.items():
            if isinstance(key, int):
                node_index = key
            else:
                try:
                    node_index = labels.index(key)
                except ValueError:
                    continue

            if node_index < 0 or node_index >= len(labels):
                continue

            if isinstance(position, dict):
                if "x" in position:
                    x_positions[node_index] = position["x"]
                if "y" in position:
                    y_positions[node_index] = position["y"]
            elif isinstance(position, (tuple, list)) and len(position) >= 2:
                x_positions[node_index], y_positions[node_index] = position[0], position[1]

        trace.node.x = x_positions
        trace.node.y = y_positions
        trace.arrangement = arrangement

    fig.update_layout(uirevision="sankey-default-node-positions")
    return fig

def view_sankey(mp, model, scenario, subsystems, annums, node_positions=None):
    
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

            df_for_plot = water_m3_to_Gwa(scenario, df, mapping, subsystem, annum)

            fig = sankey(df=df_for_plot, mapping=mapping)                                 # Create the Sankey diagram
            fig = apply_sankey_node_positions(fig, node_positions=node_positions)

            fig.show()
    
            fig_to_html(fig, subsystem, annum)

    return fig

if __name__ == "__main__":
    # Loading modelling platform
    mp = ix.Platform("default", jvmargs=["-Xmx8G"])
    
    # Specifying model/scenario to be loaded from the database
    model = "SIN Brasil expandido"
    scenario = 'reference'
    subsystems = ['North']
    annums = [2030] # [2025, 2030, 2035]
    node_positions = {
        "river9|M1": (0.02, 0.20),
        "river4|M1": (0.02, 0.50),
        "river8|M1": (0.02, 0.80),
        "primary|water_4": (0.02, 0.35),
        "primary|water_8": (0.02, 0.65),
        "primary|water_9": (0.02, 0.90),

        "water_supply_9|M1": (0.12, 0.10),
        "water_supply_4|M1": (0.12, 0.25),
        "water_supply_8|M1": (0.12, 0.40),

        "hydro_4|M1": (0.28, 0.20),
        "hydro_8|M1": (0.28, 0.35),
        "hydro_9|M1": (0.28, 0.50),

        "wind_ppl|M1": (0.42, 0.08),
        "solar_pv_ppl|M1": (0.42, 0.18),
        "nuc_ppl|M1": (0.42, 0.28),
        "bio_ppl|M1": (0.42, 0.38),
        "oil_ppl|M1": (0.42, 0.48),
        "gas_ppl|M1": (0.42, 0.58),
        "gas_ppl_1|M1": (0.42, 0.68),
        "gas_ppl_2|M1": (0.42, 0.78),
        "gas_ppl_ccs|M1": (0.42, 0.88),
        "gas_ppl_ccs_1|M1": (0.42, 0.95),
        "gas_ppl_ccs_2|M1": (0.42, 1.00),
        "coal_ppl|M1": (0.42, 0.98),

        "batt_n|M1": (0.58, 0.18),
        "sphs_4|M1": (0.58, 0.32),
        "sphs_8|M1": (0.58, 0.46),
        "sphs_9|M1": (0.58, 0.60),

        "secondary|water_4": (0.76, 0.20),
        "secondary|water_8": (0.76, 0.35),
        "secondary|water_9": (0.76, 0.50),
        "secondary|electricity": (0.76, 0.68),

        "grid1|n-to-ne": (0.88, 0.55),
        "grid1|ne-to-n": (0.88, 0.72),

        "final|water_4": (0.98, 0.20),
        "final|water_8": (0.98, 0.35),
        "final|water_9": (0.98, 0.50),
        "final|electricity": (0.98, 0.68),
    }
    fig = view_sankey(mp, model, scenario, subsystems, annums, node_positions=node_positions)  
    
    # Close DB
    mp.close_db()