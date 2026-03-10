from dash import Dash, html, dcc, Output, Input
import json
import requests
from BRICS_GT import BRICS_GT

# Load your game‑theory engine
engine = BRICS_GT()

# Create Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("BRICS Dashboard"),

    html.H2("Geopolitical Risk Engine"),
    html.Button("Run Iran Escalation Scenario", id="run-scenario-btn"),
    html.Pre(id="risk-output", style={"whiteSpace": "pre-wrap"}),

    html.H2("Game Theory Models"),
    dcc.Dropdown(
        id="model-select",
        options=[
            {"label": "Adaptive Tariff Game", "value": "tariff"},
            {"label": "Energy Coordination", "value": "energy"},
            {"label": "Tariff Arms Race", "value": "arms"},
        ],
        value="tariff"
    ),
    dcc.Graph(id="model-graph"),
    html.Pre(id="model-summary", style={"whiteSpace": "pre-wrap"})
])

# Risk Engine Callback


@app.callback(
    Output("risk-output", "children"),
    Input("run-scenario-btn", "n_clicks")
)
def run_scenario(n):
    if not n:
        return "Click the button to run the scenario."

    res = requests.get("http://127.0.0.1:5000/api/risk/iran-escalation")
    data = res.json()
    return json.dumps(data, indent=2)

# Model Callback


@app.callback(
    Output("model-graph", "figure"),
    Output("model-summary", "children"),
    Input("model-select", "value")
)
def update_model(model):
    if model == "tariff":
        fig, summary = engine.trade_figure_with_summary()
    elif model == "energy":
        fig, summary = engine.energy_figure_with_summary()
    else:
        fig, summary = engine.arms_race_figure_with_summary()

    return fig, summary


if __name__ == "__main__":
    app.run(debug=True)
