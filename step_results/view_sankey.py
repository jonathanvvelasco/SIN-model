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
            # Adjust values: for flows with commodity 'water', divide by the
            # input value of the corresponding 'hydro' technology at the
            # same node and year.
            try:
                input_par = scenario.par("input").copy()
                # Sum hydro inputs by node and year
                hydro_inputs = (
                    input_par[input_par["technology"].str.startswith("hydro", na=False)]
                    .groupby(["node_loc", "year_act"], as_index=False)["value"]
                    .sum()
                    .rename(columns={"value": "hydro_input"})
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

                    print(f"DEBUG: total rows in iam df: {len(pdf)}")
                    print(f"DEBUG: total mapping entries: {len(mapping)}; water candidate vars: {len(water_vars)}")
                    if len(water_vars) > 10:
                        print("DEBUG: sample water vars:", water_vars[:10])
                    else:
                        print("DEBUG: water vars:", water_vars)

                    if water_vars:
                        # for this filtered df we only have one year (annum) and one region (subsystem)
                        hydro_sum = 0.0
                        try:
                            hrow = hydro_inputs.loc[
                                (hydro_inputs["node_loc"] == subsystem) & (hydro_inputs["year_act"] == annum)
                            ]
                            hydro_sum = float(hrow["hydro_input"].sum())/12 if not hrow.empty else 0.0
                        except Exception as e:
                            print(f"DEBUG: error finding hydro inputs: {e}")
                            hydro_sum = 0.0

                        print(f"DEBUG: hydro_input sum for {subsystem} {annum} = {hydro_sum}")

                        if hydro_sum > 0:
                            before_sum = float(pdf.loc[pdf["variable"].isin(water_vars), "value"].sum())
                            print(f"DEBUG: sum of water variables BEFORE adjustment = {before_sum}")

                            pdf.loc[pdf["variable"].isin(water_vars), "value"] = (
                                pdf.loc[pdf["variable"].isin(water_vars), "value"] / hydro_sum
                            )

                            after_sum = float(pdf.loc[pdf["variable"].isin(water_vars), "value"].sum())
                            print(f"DEBUG: sum of water variables AFTER adjustment = {after_sum}")

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
                            print("DEBUG: hydro_sum is zero, skipping adjustment")
                            df_for_plot = df
                    else:
                        print("DEBUG: no water_vars found in mapping; skipping adjustment")
                        df_for_plot = df
                else:
                    df_for_plot = df
            except Exception as e:
                print(f"Failed to adjust water values: {e}")
                df_for_plot = df

            fig = sankey(df=df_for_plot, mapping=mapping)                                 # Create the Sankey diagram
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