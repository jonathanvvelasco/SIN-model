import ixmp as ix
import pandas as pd
import plotly.graph_objects as go
import webbrowser
from pathlib import Path

from message_ix import Scenario


def _label_node(node: str, commodity: str, level: str) -> str:
    return f"{node} | {commodity} | {level}"


def _label_technology(node: str, technology: str, mode: str) -> str:
    return f"{node} | {technology} | {mode}"


def _coalesce(value, fallback: str) -> str:
    return fallback if pd.isna(value) or value == "all" else str(value)


def _prepare_links(frame: pd.DataFrame, source: pd.Series, target: pd.Series) -> pd.DataFrame:
    links = frame.assign(source=source, target=target)[["source", "target", "value"]]
    links = links.dropna(subset=["source", "target", "value"])
    links = links.loc[links["value"] > 0]
    return links.groupby(["source", "target"], as_index=False)["value"].sum()


def sankey(mp, model, scenario, year: int = 2030, node: str = "Southeast"):
    scenario = Scenario(mp, model, scenario)

    if not scenario.has_solution():
        scenario.solve(quiet=True)

    input_df = scenario.par("input", {"year_act": year, "node_loc": node}).copy()
    output_df = scenario.par("output", {"year_act": year, "node_loc": node}).copy()

    if input_df.empty and output_df.empty:
        raise ValueError(f"No input/output data found for year={year} and node={node!r}")

    input_links = _prepare_links(
        input_df,
        source=input_df.apply(
            lambda row: _label_node(
                _coalesce(row.node_origin, str(row.node_loc)),
                str(row.commodity),
                str(row.level),
            ),
            axis=1,
        ),
        target=input_df.apply(
            lambda row: _label_technology(
                str(row.node_loc), str(row.technology), str(row["mode"])
            ),
            axis=1,
        ),
    )

    output_links = _prepare_links(
        output_df,
        source=output_df.apply(
            lambda row: _label_technology(
                str(row.node_loc), str(row.technology), str(row["mode"])
            ),
            axis=1,
        ),
        target=output_df.apply(
            lambda row: _label_node(
                _coalesce(row.node_dest, str(row.node_loc)),
                str(row.commodity),
                str(row.level),
            ),
            axis=1,
        ),
    )

    links = pd.concat([input_links, output_links], ignore_index=True)
    links = links.groupby(["source", "target"], as_index=False)["value"].sum()

    labels = pd.Index(pd.unique(links[["source", "target"]].to_numpy().ravel())).tolist()
    label_to_index = {label: idx for idx, label in enumerate(labels)}

    node_kind: dict[str, str] = {}
    for label in input_links["source"]:
        node_kind.setdefault(label, "commodity")
    for label in input_links["target"]:
        node_kind.setdefault(label, "technology")
    for label in output_links["source"]:
        node_kind.setdefault(label, "technology")
    for label in output_links["target"]:
        node_kind.setdefault(label, "commodity")

    node_colors = ["#4C78A8" if node_kind.get(label) == "commodity" else "#F58518" for label in labels]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=14,
                    line=dict(color="rgba(0,0,0,0.35)", width=0.5),
                    label=labels,
                    color=node_colors,
                ),
                link=dict(
                    source=links["source"].map(label_to_index),
                    target=links["target"].map(label_to_index),
                    value=links["value"],
                    hovertemplate="%{source.label} to %{target.label}: %{value}<extra></extra>",
                ),
                valueformat=",.3f",
            )
        ]
    )
    fig.update_layout(
        title_text=f"Energy Sankey for {scenario.model}/{scenario.scenario} - {node} - {year}",
        font_size=11,
    )
    return fig

if __name__ == "__main__":
    # Loading modelling platform
    mp = ix.Platform("default", jvmargs=["-Xmx8G"])
    
    # Specifying model/scenario to be loaded from the database
    model = "SIN Brasil expandido"
    scenario = 'reference'
    fig = sankey(mp, model, scenario)    
    output_path = Path(__file__).resolve().parents[1] / "Output files" / "sankey_energy.html"
    fig.write_html(output_path, include_plotlyjs="cdn", auto_open=False)
    webbrowser.open(output_path.as_uri())
    print(f"Sankey written to {output_path}")
    
    # Close DB
    mp.close_db()