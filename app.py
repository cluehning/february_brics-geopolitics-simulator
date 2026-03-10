import json
import requests

import dash
from dash import html, dcc, Output, Input, State
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate

from BRICS_GT import BRICS_GT
from news_ai import fetch_news
from knowledge_graph import load_graph

from flask import Flask, jsonify
from risk_model import iran_escalation_scenario

from global_risk_data import load_global_risk_data
from risk_data_collector import RiskDataCollector

collector = RiskDataCollector()
BRICS = ["Brazil", "Russia", "India", "China", "South Africa"]
DATA = collector.load_all(BRICS)

HORMUZ = DATA["logistics"]
SUEZ   = DATA["trade"]


# ================================================================
# LOAD INTELLIGENCE DATA
# ================================================================

news_articles = fetch_news()
graph_state = load_graph()
gt = BRICS_GT()

# ================================================================
# LOAD OPEN-SOURCE GLOBAL RISK DATA (FSI / WGI)
# ================================================================

FSI_DATA = load_global_risk_data()   # <-- echte Daten, nicht hardcoded


# ================================================================
# HELPERS
# ================================================================

def apply_font(fig):
    fig.update_layout(font={"family": "TT Norms Pro"})
    return fig


# ================================================================
# NEWS TAB
# ================================================================

def news_tab():
    items = []
    for art in news_articles:
        card = html.Div(
            [
                html.H3(art.get("title", "")),
                html.Div(art.get("source", ""), style={"color": "#444"}),
                html.Div(art.get("published", ""), style={"color": "gray"}),
                html.A("Read article", href=art.get("link", "#"),
                       target="_blank"),
                html.Hr(),
            ],
            style={"marginBottom": "25px"},
        )
        items.append(card)
    return html.Div(items, style={"padding": "20px"})


# ================================================================
# BRICS WORLD MAP
# ================================================================

def brics_world_map():
    brics = [
        "Brazil", "Russia", "India", "China", "South Africa",
        "Egypt", "Ethiopia", "Iran", "United Arab Emirates",
        "Indonesia",
    ]

    high = ["Saudi Arabia", "Türkiye", "United States"]
    medium = ["Kazakhstan", "Nigeria", "Belarus", "Argentina", "Thailand"]
    low = ["Cuba", "Bolivia"]

    frame = px.data.gapminder().query("year == 2007")[["country", "iso_alpha"]]
    frame["value"] = 0.0

    def set_val(names, val):
        for name in names:
            frame.loc[frame["country"] == name, "value"] = val

    set_val(brics, 1.0)
    set_val(high, 0.75)
    set_val(medium, 0.5)
    set_val(low, 0.25)

    fig = px.choropleth(
        frame,
        locations="iso_alpha",
        color="value",
        hover_name="country",
        projection="natural earth",
        title="BRICS Membership and Global Influence",
        color_continuous_scale=[
            (0.00, "#ECF0F1"),
            (0.25, "#F1C40F"),
            (0.50, "#E67E22"),
            (0.75, "#E74C3C"),
            (1.00, "#2ECC71"),
        ],
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="black",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="white"
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=40),
        coloraxis_showscale=False,
        font={"family": "TT Norms Pro"}
    )

    return fig


# ================================================================
# GLOBAL RISK MAP (FSI + SCENARIO)
# ================================================================

def combine_risk(fsi_data, scenario_data):
    fsi_values = list(fsi_data.values())
    fmin, fmax = min(fsi_values), max(fsi_values)

    combined = {}
    for country, fsi in fsi_data.items():
        base = (fsi - fmin) / (fmax - fmin) if fmax != fmin else 0.0  # small correction to avoid div-by-zero
        scen = scenario_data.get(country, 0)
        combined[country] = 0.6 * base + 0.4 * scen
    return combined


def risk_world_map(country_risk):
    frame = px.data.gapminder().query("year == 2007")[["country", "iso_alpha"]]
    frame["risk"] = frame["country"].map(country_risk).fillna(0)

    fig = px.choropleth(
        frame,
        locations="iso_alpha",
        color="risk",
        hover_name="country",
        projection="natural earth",
        title="Global Geopolitical Risk Map",
        color_continuous_scale="Reds",
        range_color=(0, 1),
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="black",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="white"
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=40),
        coloraxis_colorbar=dict(title="Risk Level"),
        font={"family": "TT Norms Pro"}
    )

    return fig


# ================================================================
# PRECOMPUTED FIGURES
# ================================================================

tariff_fig, tariff_summary = gt.trade_figure_with_summary()
tariff_fig = apply_font(tariff_fig)

energy_fig, energy_summary = gt.energy_figure_with_summary()
energy_fig = apply_font(energy_fig)

arms_fig, arms_summary = gt.arms_race_figure_with_summary()
arms_fig = apply_font(arms_fig)


# ================================================================
# SCENARIO REGISTRY + RISK BUILDERS (ADDED)
# ================================================================

# Placeholders for additional scenarios; return dict {"countries": {<ISO3 or name>: score in [0,1], ...}}

def hormuz_closure_scenario():
    # TODO: implement with oil-import dependency, shipping reliance via Hormuz, etc.
    return {"countries": HORMUZ}

def suez_disruption_scenario():
    # TODO: implement with container throughput reliance, Red Sea exposure, reroute elasticity, etc.
    return {"countries": SUEZ}

SCENARIO_REGISTRY = {
    "iran_escalation": {
        "label": "Iran Escalation",
        "loader": lambda: iran_escalation_scenario().get("countries", {}),
    },
    "hormuz_closure": {
        "label": "Hormuz Closure",
        "loader": lambda: hormuz_closure_scenario().get("countries", {}),
    },
    "suez_disruption": {
        "label": "Suez Disruption",
        "loader": lambda: suez_disruption_scenario().get("countries", {}),
    },
}


# Optional open-source layers (stubs); return dict {ISO3 or name: score in [0,1]}

def load_wef_global_risks():
    # TODO: wire to WEF signals you select and normalize to [0,1]
    return {}

def load_wgi_risk_proxy():
    # TODO: derive proxy from WGI (e.g., invert Stability), normalize to [0,1]
    return {}


# Canonical world index from Plotly — used to align different datasets to ISO3

COUNTRY_IDX = px.data.gapminder().query("year == 2007")[["country", "iso_alpha"]].rename(
    columns={"iso_alpha": "iso3"}
)

def _to_iso_indexed(series_like):
    """
    Accepts a dict keyed by country names OR ISO3 codes.
    Returns a pandas Series indexed by ISO3 codes, aligned to COUNTRY_IDX.iso3.
    """
    s = pd.Series(series_like, dtype=float)

    # If keys look like ISO3, map directly by iso3 -> iso3
    if len(s.index) and all(isinstance(k, str) and len(k) == 3 for k in s.index):
        df = COUNTRY_IDX.merge(s.rename("val"), left_on="iso3", right_index=True, how="left")
    else:
        # Assume keys are country names, map via country -> iso3
        df = COUNTRY_IDX.merge(s.rename("val"), left_on="country", right_index=True, how="left")

    # Return Series indexed by iso3
    return df.set_index("iso3")["val"].fillna(0.0)

def _minmax(x: pd.Series, eps: float = 1e-9) -> pd.Series:
    xmin, xmax = float(x.min()), float(x.max())
    rng = xmax - xmin
    if rng < eps:
        # avoid division by zero → no information
        return pd.Series(0.0, index=x.index)
    return (x - xmin) / rng

def build_risk_frame(
    base_fsi_dict: dict,
    scenario_key: str,
    base_weight: float = 0.6,
    include_wef: bool = False,
    include_wgi: bool = False,
    wef_weight: float = 0.2,
    wgi_weight: float = 0.2,
):
    """
    Compose normalized risk = w_base*FSI + w_scen*Scenario [+ optional WEF/WGI].
    Weights auto-renormalize if some components are disabled.
    Returns a DataFrame with columns: iso3, country, fsi, scenario, wef, wgi, risk
    """

    # base FSI
    fsi = _to_iso_indexed(base_fsi_dict)
    fsi_n = _minmax(fsi)

    # scenario
    loader = SCENARIO_REGISTRY.get(scenario_key, {}).get("loader")
    if not loader:
        raise ValueError(f"Unknown scenario '{scenario_key}'")
    scen_raw = loader()
    scen = _to_iso_indexed(scen_raw)
    scen_n = _minmax(scen)

    # optional layers
    wef_n = pd.Series(0.0, index=fsi.index)
    wgi_n = pd.Series(0.0, index=fsi.index)
    components = [("base", base_weight, fsi_n), ("scenario", 1 - base_weight, scen_n)]

    if include_wef:
        wef = _to_iso_indexed(load_wef_global_risks())
        wef_n = _minmax(wef)
        components.append(("wef", wef_weight, wef_n))

    if include_wgi:
        wgi = _to_iso_indexed(load_wgi_risk_proxy())
        wgi_n = _minmax(wgi)
        components.append(("wgi", wgi_weight, wgi_n))

    # renormalize weights so they sum to 1 for enabled components
    total_w = sum(w for _, w, _ in components)
    components = [(name, (w / total_w if total_w > 0 else 0.0), vec) for name, w, vec in components]

    # weighted sum
    risk = sum(w * vec for _, w, vec in components)

    df = COUNTRY_IDX.copy()
    df["fsi"] = fsi_n.reindex(df["iso3"]).values
    df["scenario"] = scen_n.reindex(df["iso3"]).values
    df["wef"] = wef_n.reindex(df["iso3"]).values
    df["wgi"] = wgi_n.reindex(df["iso3"]).values
    df["risk"] = risk.reindex(df["iso3"]).values

    return df

def risk_world_map_df(df: pd.DataFrame, title: str = "Scenario Risk Map"):
    fig = px.choropleth(
        df,
        locations="iso3",
        color="risk",
        hover_name="country",
        projection="natural earth",
        color_continuous_scale="Reds",
        range_color=(0, 1),
        title=title,
        hover_data={
            "iso3": True,
            "risk": ":.2f",
            "fsi": ":.2f",
            "scenario": ":.2f",
            "wef": ":.2f",
            "wgi": ":.2f",
        },
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="black",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="white",
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=40),
        coloraxis_colorbar=dict(title="Risk"),
        font={"family": "TT Norms Pro"},
    )
    return fig


# ================================================================
# FLASK + DASH APP
# ================================================================

server = Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    assets_folder="assets"
)
app.title = "BRICS Dashboard"


summary_style = {
    "padding": "20px",
    "fontSize": "16px",
    "lineHeight": "1.5",
    "maxWidth": "900px",
}

# Scenario Risk Map tab (ADDED)
scenario_tab = dcc.Tab(
    label="Scenario Risk Map",
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Scenario", style={"fontWeight": 600}),
                        dcc.RadioItems(
                            id="scenario-chooser",
                            options=[{"label": v["label"], "value": k} for k, v in SCENARIO_REGISTRY.items()],
                            value="iran_escalation",
                            inputStyle={"marginRight": "6px"},
                            labelStyle={
                                "display": "inline-block",
                                "padding": "6px 12px",
                                "border": "1px solid #ccc",
                                "borderRadius": "16px",
                                "marginRight": "8px",
                                "cursor": "pointer",
                            },
                            style={"marginBottom": "10px"},
                        ),
                    ],
                    style={"marginBottom": "8px"},
                ),
                html.Div(
                    [
                        html.Label("Blend weight (Base FSI ↔ Scenario)", style={"fontWeight": 600}),
                        dcc.Slider(
                            id="base-weight",
                            min=0.0, max=1.0, step=0.05, value=0.6,
                            tooltip={"placement": "bottom", "always_visible": False},
                            marks={
                                0.0: {"label": "0% FSI"},
                                0.5: "50/50",
                                1.0: {"label": "100% FSI"},
                            },
                        ),
                    ],
                    style={"marginBottom": "8px"},
                ),
                html.Div(
                    [
                        dcc.Checklist(
                            id="extra-sources",
                            options=[
                                {"label": "Include WEF signals", "value": "wef"},
                                {"label": "Include WGI proxy", "value": "wgi"},
                            ],
                            value=[],
                            labelStyle={"marginRight": "18px"},
                        )
                    ],
                    style={"marginBottom": "10px"},
                ),
                html.Div(
                    [
                        html.Button("Refresh", id="refresh-map", n_clicks=0, style={"marginRight": "10px"}),
                        html.Button("Download CSV", id="download-csv", n_clicks=0),
                        dcc.Download(id="download-csv-target"),
                        dcc.Store(id="risk-df-store", storage_type="memory"),
                    ],
                    style={"marginBottom": "12px"},
                ),
                dcc.Graph(id="scenario-risk-map", style={"width": "100%", "height": "80vh", "minHeight": "600px"}),
            ],
            style={"padding": "12px"},
        )
    ],
)


# ================================================================
# LAYOUT
# ================================================================

app.layout = html.Div(
    style={"fontFamily": "TT Norms Pro"},
    children=[
        html.H1("BRICS Game‑Theory Dashboard", style={"textAlign": "center"}),

        dcc.Tabs(
            style={"fontFamily": "TT Norms Pro"},
            children=[

                # 1 — BRICS World Map
                dcc.Tab(
                    label="BRICS World Map",
                    children=[
                        dcc.Graph(
                            figure=brics_world_map(),
                            config={"responsive": True},
                            style={"width": "100%", "height": "80vh",
                                   "minHeight": "600px"}
                        )
                    ],
                ),

                # 2 — Tariff Game
                dcc.Tab(
                    label="Tariff Game (Dynamic)",
                    children=[
                        dcc.Graph(figure=tariff_fig),
                        dcc.Markdown(tariff_summary, style=summary_style)
                    ],
                ),

                # 3 — Energy Coordination
                dcc.Tab(
                    label="Energy Coordination",
                    children=[
                        dcc.Graph(figure=energy_fig),
                        dcc.Markdown(energy_summary, style=summary_style)
                    ],
                ),

                # 4 — Arms Race Simulation
                dcc.Tab(
                    label="Arms Race Simulation",
                    children=[
                        dcc.Graph(figure=arms_fig),
                        dcc.Markdown(arms_summary, style=summary_style)
                    ],
                ),

                # 5 — Live News Feed
                dcc.Tab(
                    label="Live News Feed",
                    children=[html.Div(news_tab())],
                ),

                # 6 — Scenario Risk Map (ADDED)
                scenario_tab,
            ]
        ),
    ]
)


# ================================================================
# API ROUTE
# ================================================================

@server.route("/api/risk/iran-escalation")
def api_iran_escalation():
    try:
        result = iran_escalation_scenario()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================================================
# CALLBACKS
# ================================================================

@app.callback(
    Output("scenario-risk-map", "figure"),
    Output("risk-df-store", "data"),
    Input("refresh-map", "n_clicks"),
    Input("scenario-chooser", "value"),
    Input("base-weight", "value"),
    Input("extra-sources", "value"),
)
def update_scenario_map(n_clicks, scenario_key, base_weight, extra_sources):
    if scenario_key is None:
        raise PreventUpdate

    include_wef = "wef" in (extra_sources or [])
    include_wgi = "wgi" in (extra_sources or [])

    df = build_risk_frame(
        base_fsi_dict=FSI_DATA,
        scenario_key=scenario_key,
        base_weight=float(base_weight or 0.6),
        include_wef=include_wef,
        include_wgi=include_wgi,
        wef_weight=0.2,
        wgi_weight=0.2,
    )

    title = f"Scenario Risk Map — {SCENARIO_REGISTRY[scenario_key]['label']} (FSI weight={base_weight:.0%})"
    fig = risk_world_map_df(df, title)
    return fig, df.to_dict(orient="records")


@app.callback(
    Output("download-csv-target", "data"),
    Input("download-csv", "n_clicks"),
    State("risk-df-store", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, records):
    if not n_clicks or not records:
        raise PreventUpdate
    df = pd.DataFrame.from_records(records)
    return dcc.send_data_frame(df.to_csv, "scenario_risk_map.csv", index=False)


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    app.run(debug=False)
