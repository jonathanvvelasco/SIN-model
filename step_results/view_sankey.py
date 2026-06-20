# import pandas as pd
import ixmp as ix # type: ignore
from message_ix import Scenario # type: ignore
from message_ix.report import Reporter # type: ignore
from genno.operator import concat # type: ignore
from message_ix.tools.sankey import map_for_sankey # type: ignore
from pyam.figures import sankey # type: ignore
import webbrowser
# import re
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

def color_sankey_by_commodity(fig):
    water_color = "rgb(0, 51, 102)"
    electricity_color = "rgb(102, 179, 255)"
    neutral_color = "rgba(180, 180, 180, 0.55)"
    water_link_color = "rgba(0, 51, 102, 0.45)"
    electricity_link_color = "rgba(102, 179, 255, 0.45)"
    neutral_link_color = "rgba(180, 180, 180, 0.30)"

    for trace in getattr(fig, "data", []):
        if getattr(trace, "type", None) != "sankey":
            continue

        node = getattr(trace, "node", None)
        link = getattr(trace, "link", None)
        if node is None or link is None:
            continue

        node_labels = getattr(node, "label", None)
        labels = list(node_labels) if node_labels is not None else []

        node_colors = []
        for label in labels:
            label_lower = str(label).lower()
            water_label = ("water" in label_lower) or ("hydro" in label_lower) or ("river" in label_lower)
            electricity_label = ("electricity" in label_lower) or ("grid" in label_lower)
            if water_label:
                node_colors.append(water_color)
            elif electricity_label:
                node_colors.append(electricity_color)
            else:
                node_colors.append(neutral_color)

        link_colors = []
        link_sources = getattr(link, "source", None)
        link_targets = getattr(link, "target", None)
        sources = list(link_sources) if link_sources is not None else []
        targets = list(link_targets) if link_targets is not None else []
        for source_index, target_index in zip(sources, targets):
            source_label = str(labels[source_index]).lower() if source_index < len(labels) else ""
            target_label = str(labels[target_index]).lower() if target_index < len(labels) else ""

            if "water" in source_label or "water" in target_label:
                link_colors.append(water_link_color)
            elif "electricity" in source_label or "electricity" in target_label:
                link_colors.append(electricity_link_color)
            else:
                link_colors.append(neutral_link_color)

        trace.update(
            node=dict(color=node_colors),
            # link=dict(color=link_colors),
        )

    return fig

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

            df_for_plot = water_m3_to_Gwa(scenario, df, mapping, subsystem, annum)

            fig = sankey(df=df_for_plot, mapping=mapping)                                 # Create the Sankey diagram
            fig = color_sankey_by_commodity(fig)
            
            fig.show()
    
            fig_to_html(fig, subsystem, annum)

    return fig

if __name__ == "__main__":
    # Loading modelling platform
    mp = ix.Platform("default", jvmargs=["-Xmx8G"])
    
    # Specifying model/scenario to be loaded from the database
    model = "SIN Brasil expandido"
    scenario = 'dados_pde'
    subsystems = ['North', 'Northeast', 'Southeast', 'South']
    annums = [2034]

    fig = view_sankey(mp, model, scenario, subsystems, annums)  
    
    # Close DB
    mp.close_db()