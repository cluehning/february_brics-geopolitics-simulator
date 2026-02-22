import dash
from dash import html, dcc
import plotly.express as px

from BRICS_GT import BRICS_GT
from news_ai import fetch_news
from knowledge_graph import load_graph


def apply_font(fig):
    fig.update_layout(font={"family": "TT Norms Pro"})
    return fig

# ================================================================
# LOAD INTELLIGENCE DATA
# ================================================================


news_articles = fetch_news()
graph_state = load_graph()
gt = BRICS_GT()

# ================================================================
# NEWS TAB
# ================================================================


def news_tab():
    """Return HTML cards for live news."""
    items = []

    for art in news_articles:
        card = html.Div(
            [
                html.H3(art.get("title", "")),
                html.Div(art.get("source", ""), style={"color": "#444"}),
                html.Div(art.get("published", ""), style={"color": "gray"}),
                html.A(
                    "Read article",
                    href=art.get("link", "#"),
                    target="_blank"
                ),
                html.Hr(),
            ],
            style={"marginBottom": "25px"},
        )
        items.append(card)

    return html.Div(items, style={"padding": "20px"})


# ================================================================
# WORLD MAP — RESPONSIVE VERSION
# ================================================================
def brics_world_map():
    """Responsive BRICS influence world map."""
    brics = [
        "Brazil", "Russia", "India", "China", "South Africa",
        "Egypt", "Ethiopia", "Iran", "United Arab Emirates",
        "Indonesia",
    ]

    high = ["Saudi Arabia", "Türkiye", "United States"]
    medium = ["Kazakhstan", "Nigeria", "Belarus",
              "Argentina", "Thailand"]
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

    # KEY FIXES FOR RESPONSIVENESS
    fig.update_layout(
        autosize=True,
        height=None,  # Let Dash Graph handle height
        margin=dict(l=0, r=0, t=40, b=40),
        coloraxis_showscale=False,
    )

    fig.update_layout(font={"family": "TT Norms Pro"})

    return fig


# ================================================================
# WORLD MAP LEGEND
# ================================================================
def world_map_legend():
    """Legend for BRICS map (responsive)."""

    def box(color):
        return html.Div(
            style={
                "display": "inline-block",
                "width": "18px",
                "height": "18px",
                "backgroundColor": color,
                "marginRight": "10px",
                "border": "1px solid black",
            }
        )

    style = {
        "padding": "10px",
        "margin": "20px auto 0 auto",
        "maxWidth": "480px",
        "backgroundColor": "#f8f8f8",
        "borderRadius": "8px",
        "border": "1px solid #ccc",
        "fontSize": "14px",
    }

    return html.Div(
        [
            html.H4("Legend", style={"marginBottom": "10px"}),
            html.Div([box("#2ECC71"), "BRICS Members"]),
            html.Div([box("#E74C3C"), "High Influence"]),
            html.Div([box("#E67E22"), "Medium Influence"]),
            html.Div([box("#F1C40F"), "Low Influence"]),
            html.Div([box("#ECF0F1"), "Neutral"]),
        ],
        style=style
    )


# ================================================================
# PRECOMPUTED FIGURES + SUMMARIES
# ================================================================
tariff_fig, tariff_summary = gt.trade_figure_with_summary()
tariff_fig = apply_font(tariff_fig)

energy_fig, energy_summary = gt.energy_figure_with_summary()
energy_fig = apply_font(energy_fig)

arms_fig, arms_summary = gt.arms_race_figure_with_summary()
arms_fig = apply_font(arms_fig)

# ================================================================
# DASH APP LAYOUT
# ================================================================
app = dash.Dash(
    __name__,
    assets_folder="assets"
)
app.title = "BRICS Dashboard"

summary_style = {
    "padding": "20px",
    "fontSize": "16px",
    "lineHeight": "1.5",
    "maxWidth": "900px",
}


app.layout = html.Div(
    style={"fontFamily": "TT Norms Pro"},
    children=[
        html.H1(
            "BRICS Game‑Theory Dashboard",
            style={"textAlign": "center"},
        ),

        dcc.Tabs(
            style={"fontFamily": "TT Norms Pro"},
            children=[
                # ------------------- TARIFF GAME -------------------
                dcc.Tab(
                    label="Tariff Game (Dynamic)",
                    style={"fontFamily": "TT Norms Pro"},
                    children=[
                        dcc.Graph(
                            figure=tariff_fig,
                            style={"width": "100%"}
                        ),
                        dcc.Markdown(
                            tariff_summary,
                            style=summary_style
                        )
                    ],
                ),

                # ------------------- ENERGY GAME -------------------
                dcc.Tab(
                    label="Energy Coordination",
                    style={"fontFamily": "TT Norms Pro"},
                    children=[
                        dcc.Graph(
                            figure=energy_fig,
                            style={"width": "100%"}
                        ),
                        dcc.Markdown(
                            energy_summary,
                            style=summary_style
                        )
                    ],
                ),

                # ------------------- ARMS RACE ----------------------
                dcc.Tab(
                    label="Arms Race Simulation",
                    style={"fontFamily": "TT Norms Pro"},
                    children=[
                        dcc.Graph(
                            figure=arms_fig,
                            style={"width": "100%"}
                        ),
                        dcc.Markdown(
                            arms_summary,
                            style=summary_style
                        )
                    ],
                ),

                # ------------------- LIVE NEWS ----------------------
                dcc.Tab(
                    label="Live News Feed",
                    children=[
                        html.Div(news_tab())
                    ],
                ),

                # ------------------- WORLD MAP (RESPONSIVE) --------
                dcc.Tab(
                    label="BRICS World Map",
                    style={"fontFamily": "TT Norms Pro"},
                    children=[
                        html.Div(
                            dcc.Graph(
                                figure=brics_world_map(),
                                config={"responsive": True},
                                style={
                                    "width": "100%",
                                    "height": "80vh",
                                    "minHeight": "600px"
                                }
                            ),
                            style={"padding": "0 10px"}
                        ),
                        html.Div(
                            world_map_legend()
                        )
                    ],
                ),
            ]
        ),
    ]
)

# ================================================================
# RUN SERVER
# ================================================================
if __name__ == "__main__":
    app.run(debug=True)
