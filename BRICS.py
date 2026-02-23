import json
import time
import warnings
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio

# I'm ignoring warnings here because the WB API sometimes throws harmless ones.
warnings.filterwarnings("ignore")


class BRICSDataCollector:
    """Handles collecting all macro‑level indicators for BRICS countries."""

    def __init__(self):
        # ISO2 codes – mainly for display or future API integrations.
        self.brics_countries = {
            "Brazil": "BR",
            "Russia": "RU",
            "India": "IN",
            "China": "CN",
            "South Africa": "ZA",
        }

        # ISO3 codes – these are what the World Bank API expects.
        self.wb_codes = {
            "Brazil": "BRA",
            "Russia": "RUS",
            "India": "IND",
            "China": "CHN",
            "South Africa": "ZAF",
        }

        # Bucket all indicators by themes so the rest of the code stays neat.
        self.indicators = {
            "economic": {
                "GDP": "NY.GDP.MKTP.CD",
                "GDP_growth": "NY.GDP.MKTP.KD.ZG",
                "GDP_per_capita": "NY.GDP.PCAP.CD",
                "Trade_GDP": "NE.TRD.GNFS.ZS",
                "Exports": "NE.EXP.GNFS.CD",
                "Imports": "NE.IMP.GNFS.CD",
                "FDI_inflow": "BX.KLT.DINV.CD.WD",
                "Current_account": "BN.CAB.XOKA.CD",
                "Inflation": "FP.CPI.TOTL.ZG",
                "Unemployment": "SL.UEM.TOTL.ZS",
            },
            "resources": {
                "Energy_use": "EG.USE.PCAP.KG.OE",
                "Oil_consumption": "EG.USE.PETE.KT.OE",
                "Natural_gas": "EG.USE.GASF.KT.OE",
                "Coal_consumption": "EG.USE.COAL.KT.OE",
                "Renewable_energy": "EG.FEC.RNEW.ZS",
                "Agricultural_land": "AG.LND.AGRI.ZS",
                "Arable_land": "AG.LND.ARBL.ZS",
                "Forest_area": "AG.LND.FRST.ZS",
            },
            "defense_security": {
                "Military_expenditure": "MS.MIL.XPND.GD.ZS",
                "Military_expenditure_USD": "MS.MIL.XPND.CD",
                "Armed_forces": "MS.MIL.TOTL.P1",
                "Arms_imports": "MS.MIL.MPRT.KD",
            },
            "social_development": {
                "Population": "SP.POP.TOTL",
                "Urban_population": "SP.URB.TOTL.IN.ZS",
                "Education_expenditure": "SE.XPD.TOTL.GD.ZS",
                "Health_expenditure": "SH.XPD.CHEX.GD.ZS",
                "Life_expectancy": "SP.DYN.LE00.IN",
                "Internet_users": "IT.NET.USER.ZS",
            },
            "governance": {
                "Government_expenditure": "NE.CON.GOVT.ZS",
                "Tax_revenue": "GC.TAX.TOTL.GD.ZS",
                "Rule_of_law": "RL.EST",
                "Control_corruption": "CC.EST",
            },
        }

        # Keeping all API endpoints in one place makes life easier later.
        self.base_urls = {
            "worldbank": "https://api.worldbank.org/v2/country",
            "un_comtrade": "https://comtradeapi.un.org/data/v1/get",
            "imf": "http://dataservices.imf.org/REST/SDMX_JSON.svc",
        }

        self.all_data = {}

    def collect_worldbank_data(self, start_year=2010, end_year=2023):
        """Pulls indicator data from the World Bank API for all BRICS."""
        wb_data = {}

        for country, code in self.wb_codes.items():
            country_data = {}

            for category, indicators in self.indicators.items():
                category_data = {}

                for ind_name, ind_code in indicators.items():
                    try:
                        # Build the WB endpoint for each indicator
                        url = (
                            f"{self.base_urls['worldbank']}/"
                            f"{code}/indicator/{ind_code}"
                        )
                        params = {
                            "format": "json",
                            "date": f"{start_year}:{end_year}",
                            "per_page": 1000,
                        }

                        # Request the data
                        resp = requests.get(url, params=params, timeout=10)

                        if resp.status_code == 200:
                            data = resp.json()

                            # WB returns [metadata, values]
                            if len(data) > 1 and data[1]:
                                values = {
                                    item["date"]: float(item["value"])
                                    for item in data[1]
                                    if item["value"] is not None
                                }
                                category_data[ind_name] = values

                        # A tiny pause so we don’t hammer the API
                        time.sleep(0.1)

                    except Exception as exc:
                        print(f"Error collecting {ind_name}: {exc}")

                country_data[category] = category_data

            wb_data[country] = country_data

        return wb_data

    def collect_trade_data(self, start_year=2010, end_year=2022):
        """Simulated Comtrade values – temporary placeholders"""
        trade_data = {}

        for country in self.brics_countries:
            # Adding a bit of noise -> more realistic
            country_trade = {
                "total_exports": {
                    str(y): float(np.random.normal(100000, 20000))
                    for y in range(start_year, end_year + 1)
                },
                "total_imports": {
                    str(y): float(np.random.normal(90000, 15000))
                    for y in range(start_year, end_year + 1)
                },
            }

            trade_data[country] = country_trade

        return trade_data

    def collect_all_data(self):
        """Runs all collection routines and bundles everything."""
        print("🔄 Starting comprehensive BRICS data collection...\n")

        # Adding timestamps makes the dataset self‑describing
        self.all_data["collection_timestamp"] = datetime.utcnow().isoformat()
        self.all_data["valid_until"] = (
            datetime.utcnow() + timedelta(days=1)
        ).isoformat()

        self.all_data["worldbank"] = self.collect_worldbank_data()
        print("✅ World Bank data collected.\n")

        self.all_data["trade"] = self.collect_trade_data()
        print("✅ Trade data collected.\n")

        return self.all_data

    def save_data(self, filename="brics_data.json"):
        """Saves the full dataset to disk so other modules can use it."""
        with open(filename, "w") as f:
            json.dump(self.all_data, f, indent=2)


class BRICSVisualizer:
    """Generates dashboards and comparison plots for BRICS indicators."""

    def __init__(self, data):
        self.data = data

        # Custom colors so each country stays consistent across plots
        self.colors = {
            "Brazil": "#009739",
            "Russia": "#0033A0",
            "India": "#FF9933",
            "China": "#DE2910",
            "South Africa": "#000000",
        }

        # Global plotting theme
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

    def create_country_dashboard(self, country, filename=None):
        """Builds a 3×3 country dashboard – GDP + whatever else I add later."""
        fig = make_subplots(rows=3, cols=3)
        country_data = self.data["worldbank"][country]
        color = self.colors[country]

        # --- GDP Growth plot ---
        gdp = country_data["economic"].get("GDP_growth")

        if gdp:
            years = sorted(gdp)
            vals = [gdp[y] for y in years]

            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=vals,
                    line=dict(color=color),
                    name="GDP Growth (%)"
                ),
                row=1, col=1,
            )

            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="GDP Growth (%)", row=1, col=1)

        # I can add more indicators here as needed (kept minimal for now)

        fig.update_layout(
            height=1200,
            title=dict(
                text=f"{country} Dashboard: GDP Growth and Key Indicators",
                x=0.5,
                font=dict(size=20)
            ),
            showlegend=True,
            template="plotly_white",
        )

        # Small reference note at the bottom
        fig.add_annotation(
            text=(
                "Source: World Bank (2024). Available at:"
                "https://data.worldbank.org"
            ),
            xref="paper",
            yref="paper",
            x=0,
            y=-0.12,
            showarrow=False,
            font=dict(size=10),
            align="left"
        )

        # Save or show
        if filename:
            pio.write_html(fig, file=filename, auto_open=False)
        else:
            fig.show()

    def create_sector_comparison(self, sector="economic", filename=None):
        """Compares countries within a sector (economic, resources, etc.)."""
        # Basic validation
        if sector not in self.data["worldbank"]["Brazil"]:
            print("Invalid sector.")
            return

        indicators = list(self.data["worldbank"]["Brazil"][sector])

        # Layout: 2×2 grid – enough to quickly scan four indicators
        fig = make_subplots(rows=2, cols=2)
        pos = [(1, 1), (1, 2), (2, 1), (2, 2)]

        for idx, ind in enumerate(indicators[:4]):
            r, c = pos[idx]

            for country in self.data["worldbank"]:
                vals = self.data["worldbank"][country][sector].get(ind)
                if not vals:
                    continue

                years = sorted(vals)

                fig.add_trace(
                    go.Scatter(
                        x=years,
                        y=[vals[y] for y in years],
                        name=country,
                        line=dict(color=self.colors[country]),
                        showlegend=True,
                    ),
                    row=r,
                    col=c,
                )

            fig.update_xaxes(title_text="Year", row=r, col=c)
            fig.update_yaxes(
                title_text=ind.replace("_", " ").title(),
                row=r,
                col=c
            ),

        fig.update_layout(
            height=800,
            title=dict(
                text=f"BRICS {sector.title()} Sector Comparison",
                x=0.5,
                font=dict(size=18)
            ),
            template="plotly_white",
        )

        # Again adding data source note
        fig.add_annotation(
            text=(
                "Source: World Bank (2024). Available at:"
                "https://data.worldbank.org"
            ),
            xref="paper",
            yref="paper",
            x=0,
            y=-0.12,
            showarrow=False,
            font=dict(size=10),
            align="left"
        )

        if filename:
            pio.write_html(fig, file=filename, auto_open=False)
        else:
            fig.show()

    def create_comprehensive_heatmap(self):
        """Builds a heatmap that shows indicator trends for all countries."""
        rows = []

        for country, sectors in self.data["worldbank"].items():
            for sector, indicators in sectors.items():
                for ind, values in indicators.items():
                    if not values:
                        continue

                    # Only looking at the last 5 years to gauge recent trends
                    yrs = sorted(values)[-5:]
                    if len(yrs) < 3:
                        continue

                    yvals = [values[y] for y in yrs]
                    xvals = list(range(len(yvals)))

                    # If all values identical, trend = 0
                    if len(set(yvals)) > 1:
                        slope = np.polyfit(xvals, yvals, 1)[0]
                        trend = (slope / np.mean(yvals)) * 100
                    else:
                        trend = 0

                    rows.append({
                        "Country": country,
                        "Indicator": f"{sector}_{ind}",
                        "Trend": trend,
                    })

        df = pd.DataFrame(rows)
        if df.empty:
            print("No data for heatmap.")
            return

        # Transform into pivot table so seaborn can read it
        pivot = df.pivot_table(
            values="Trend",
            index="Indicator",
            columns="Country",
            aggfunc="mean"
        )

        plt.figure(figsize=(12, 14))
        sns.heatmap(pivot, cmap="RdYlBu_r", center=0)
        plt.show()


def export_data_to_csv(data, output_dir="brics_csv_exports"):
    """Exports all indicator data as country‑sector CSV files."""
    import os

    os.makedirs(output_dir, exist_ok=True)

    for country, sectors in data["worldbank"].items():
        for sector, indicators in sectors.items():
            rows = []

            # Flatten nested structure into clean tabular rows
            for ind, values in indicators.items():
                for year, value in values.items():
                    rows.append({
                        "Country": country,
                        "Sector": sector,
                        "Indicator": ind,
                        "Year": year,
                        "Value": value,
                    })

            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(f"{output_dir}/{country}_{sector}.csv", index=False)


if __name__ == "__main__":
    # Kick off the full pipeline
    collector = BRICSDataCollector()
    data = collector.collect_all_data()
    collector.save_data()

    visualizer = BRICSVisualizer(data)

    # Saving plots so I can embed them in the dashboard later
    visualizer.create_sector_comparison(
        "economic", filename="brics_economic_comparison.html"
    )

    visualizer.create_comprehensive_heatmap()
