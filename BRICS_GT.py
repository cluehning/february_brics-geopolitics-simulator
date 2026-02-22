import json
import os
import textwrap
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser


# ============================================================
# Utility Functions
# ============================================================

def safe_load(path, default):
    """Safely load JSON with fallback."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception:
        return default
    return default


def sigmoid(x_val):
    """Sigmoid helper."""
    return 1.0 / (1.0 + np.exp(-x_val))


def save_html_with_summary(fig, filename, summary_html):
    """
    Save graph + summary into an HTML file.
    Not used by Dash; optional export feature.
    """
    graph_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn"
    )

    full_html = (
        "<html><body>"
        + graph_html +
        "<div style='margin-top:30px; font-size:16px; line-height:1.5; "
        "width:85%; font-family:Arial;'>"
        + summary_html +
        "</div></body></html>"
    )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(full_html)

    webbrowser.open(filename)


# ============================================================
# BRICS Game Theory Engine
# ============================================================

class BRICS_GT:
    """
    Multi‑model game‑theory engine:
    - Adaptive tariff game
    - Energy coordination game
    - Richardson escalation model
    """

    def __init__(self):
        print(">>> Loaded BRICS_GT")

        self.data = safe_load("data/brics_data.json", {})
        self.news = safe_load("data/news_cache.json", {})

        default_graph = {
            "USA": {"tariff_aggression": 5},
            "China": {"coordination": 5},
            "Russia": {"coordination": 6},
            "India": {"alignment": 3},
            "Brazil": {"alignment": 2},
            "South Africa": {"alignment": 2},
        }

        self.graph = safe_load("data/graph_state.json", default_graph)

        self.tariff_intensity = self.graph["USA"]["tariff_aggression"]
        self.coord_intensity = (
            self.graph["China"]["coordination"]
            + self.graph["Russia"]["coordination"]
        ) / 2.0

    # ============================================================
    # MODEL‑BASED SUMMARY ENGINE (Option A)
    # ============================================================

    def generate_summary_from_fig(self, model_type, fig):
        """
        Generate a clean, model-driven summary based ONLY on the
        numerical graph data.
        """

        y = fig.data[0].y
        slope = y[-1] - y[0]

        # Determine mathematical trend category
        if slope > 5:
            trend = "a strong upward trajectory"
            expectation = "continued acceleration"
        elif slope > 1:
            trend = "a moderate upward trend"
            expectation = "further gradual increases"
        elif slope > -1:
            trend = "a stable, near‑flat pattern"
            expectation = "stabilization around current levels"
        elif slope > -5:
            trend = "a moderate downward trend"
            expectation = "continued mild decline"
        else:
            trend = "a sharp downward trajectory"
            expectation = "further contraction"

        # Model-specific language
        if model_type == "tariff":
            text = (
                f"The cumulative BRICS payoff curve exhibits {trend}.  \n"
                f"Based on the model's trajectory, the most likely "
                f"outcome is {expectation}."
            )

        elif model_type == "energy":
            text = (
                f"The payoff curve demonstrates {trend}.  \n"
                f"This implies BRICS coordination is likely to experience "
                f"{expectation} if cooperation remains similar."
            )

        else:  # arms_race
            text = (
                f"The tariff escalation paths show {trend}.  \n"
                f"Model behavior suggests {expectation} rather than "
                f"uncontrolled escalation."
            )

        # Convert textwrap to Markdown with real line breaks
        wrapped = textwrap.wrap(text, width=75)
        return "  \n".join(wrapped)

    # ============================================================
    # 1 — Adaptive Tariff Game
    # ============================================================

    def trade_tariff_game(self, filename=None, return_figure=False):
        rounds = 40
        t_arr = np.arange(rounds)

        last_usa = 0
        last_brics = 0

        usa_probs = []
        brics_probs = []
        brics_scores = []

        payoff = {
            (1, 1): (-1, -1),
            (1, 0): (4, -2),
            (0, 1): (-2, 4),
            (0, 0): (3, 3),
        }

        for _ in t_arr:
            usa_def = sigmoid(
                0.4 * self.tariff_intensity +
                0.7 * last_brics
            )
            brics_def = sigmoid(
                0.35 * self.tariff_intensity +
                0.6 * last_usa
            )

            usa_probs.append(usa_def)
            brics_probs.append(brics_def)

            usa_move = int(np.random.rand() < usa_def)
            brics_move = int(np.random.rand() < brics_def)

            last_usa = usa_move
            last_brics = brics_move

            score, _ = payoff[(brics_move, usa_move)]
            brics_scores.append(score)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_arr,
            y=np.cumsum(brics_scores),
            mode="lines",
            name="BRICS Payoff"
        ))
        fig.add_trace(go.Scatter(
            x=t_arr,
            y=brics_probs,
            mode="lines",
            name="BRICS Defection Probability"
        ))

        fig.update_layout(
            title="Adaptive Tariff Game",
            template="plotly_white",
            xaxis_title="Round",
            yaxis_title="Value",
            height=650
        )

        if return_figure:
            return fig

        if filename:
            summary = self.generate_summary_from_fig("tariff", fig)
            save_html_with_summary(fig, filename, summary)

        return fig

    # ============================================================
    # 2 — Energy Coordination Game
    # ============================================================

    def energy_coordination_game(self, filename=None, return_figure=False):
        coalition = np.arange(1, 6)

        base = (coalition ** 1.2) * 4.0
        bonus = coalition * (self.coord_intensity * 0.6)
        penalty = np.linspace(5.0, 45.0, 5)

        net = base + bonus - penalty

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=coalition,
            y=net,
            mode="lines+markers",
            name="Net Payoff"
        ))

        fig.update_layout(
            title="Energy & Currency Coordination",
            template="plotly_white",
            xaxis_title="Cooperating States",
            yaxis_title="Net Payoff",
            height=600
        )

        if return_figure:
            return fig

        if filename:
            summary = self.generate_summary_from_fig("energy", fig)
            save_html_with_summary(fig, filename, summary)

        return fig

    # ============================================================
    # 3 — Richardson Tariff Arms Race
    # ============================================================

    def tariff_arms_race(self, filename=None, return_figure=False):
        t_arr = np.linspace(0, 20, 200)
        dt = t_arr[1] - t_arr[0]

        usa = np.zeros_like(t_arr)
        brics = np.zeros_like(t_arr)

        usa[0] = 10
        brics[0] = 7

        k1 = 0.6 + self.tariff_intensity * 0.05
        k2 = 0.5 + self.tariff_intensity * 0.04

        c1 = 0.2
        c2 = 0.25

        s1 = 0.5
        s2 = 0.4

        for i in range(1, len(t_arr)):
            usa[i] = (
                usa[i - 1] +
                dt * (k1 * brics[i - 1] - c1 * usa[i - 1] + s1)
            )
            brics[i] = (
                brics[i - 1] +
                dt * (k2 * usa[i - 1] - c2 * brics[i - 1] + s2)
            )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_arr,
            y=usa,
            mode="lines",
            name="USA Tariff"
        ))
        fig.add_trace(go.Scatter(
            x=t_arr,
            y=brics,
            mode="lines",
            name="BRICS Tariff"
        ))

        fig.update_layout(
            title="Tariff Arms Race (Richardson Model)",
            template="plotly_white",
            xaxis_title="Time",
            yaxis_title="Tariff Index",
            height=600
        )

        if return_figure:
            return fig

        if filename:
            summary = self.generate_summary_from_fig("arms_race", fig)
            save_html_with_summary(fig, filename, summary)

        return fig

    # ============================================================
    # Dash Helper Methods
    # ============================================================

    def trade_figure_with_summary(self):
        fig = self.trade_tariff_game(return_figure=True)
        return fig, self.generate_summary_from_fig("tariff", fig)

    def energy_figure_with_summary(self):
        fig = self.energy_coordination_game(return_figure=True)
        return fig, self.generate_summary_from_fig("energy", fig)

    def arms_race_figure_with_summary(self):
        fig = self.tariff_arms_race(return_figure=True)
        return fig, self.generate_summary_from_fig("arms_race", fig)
