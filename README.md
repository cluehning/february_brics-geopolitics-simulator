# BRICS Game Theory — Modeling Strategy, Incentives, and the Geometry of Power

**Geopolitics behaves like a dynamical system.**

BRICS nations interact through incentives, feedback loops, and structural dependencies that resemble mathematical systems more than political narratives.  
So I built a computational pipeline that treats geopolitics as something **computable** — something that can be mapped, simulated, and visualized.

The result is a multi‑layered intelligence system:

- macro‑economic data ingestion  
- real‑time news signal extraction  
- a persistent geopolitical knowledge graph  
- adaptive game‑theory models  
- differential‑equation escalation dynamics  
- a fully interactive Dash dashboard  

Each layer feeds the next.  
The code is intentionally **cumulative** — every module builds on the previous one.
Esseentially, a computational geopolitics engine combining real‑time news signals, macro‑economic data, game‑theory models, and scenario‑driven risk simulations — visualized in an interactive global dashboard.

---
## Quickstart
Run the BRICS Geopolitics Simulator locally in under one minute.

1 | Clone the repository

      git clone https://github.com/cluehning/february_brics-geopolitics-simulator.git
      cd february_brics-geopolitics-simulator

2 | Install dependencies
Python 3.11+ recommended.

      pip install -r requirements.txt

3 | Pull and preprocess data
This updates news signals, risk exposures, and BRICS indicators.

      python update_data.py

4 | Launch the dashboard
Runs the Dash app with the global risk map and scenario engine.

      python app.py

Then open your browser at:

      http://127.0.0.1:8050

You now have the full computational geopolitics engine running locally — including real‑time signals, the BRICS model, the game‑theory engine, and the global scenario map.

---

## Repository Structure

      |   app.py
      |   BRICS.py
      |   brics_data.json
      |   brics_economic_comparison.html
      |   BRICS_GT.py
      |   dashboard.py
      |   global_risk_data.py
      |   knowledge_graph.py
      |   news_ai.py
      |   risk_data_collector.py
      |   risk_data_loader.py
      |   risk_model.py
      |   update_data.py
      |
      +---assets
      |   |   font_v3.css
      |   |
      |   \---fonts
      |           TTNormsPro-Medium.ttf
      |           TTNormsPro-Regular.ttf
      |
      +---data
      |       brics_data.json
      |       graph_state.json
      |       hormuz_exposure.csv
      |       news_cache.json
      |       suez_exposure.csv
      |
      +---etl
      |       build_hormuz_exposure.py
      |       build_suez_exposure.py
      |       common_regions.py
      |       comtrade_pull.py
      |
      \---__pycache__
              BRICS.cpython-311.pyc
              BRICS_GT.cpython-311.pyc
              BRICS_GT.cpython-314.pyc
              global_risk_data.cpython-314.pyc
              knowledge_graph.cpython-311.pyc
              knowledge_graph.cpython-314.pyc
              news_ai.cpython-311.pyc
              news_ai.cpython-314.pyc
              risk_data_collector.cpython-314.pyc
              risk_data_loader.cpython-314.pyc
              risk_model.cpython-311.pyc
              risk_model.cpython-314.pyc

---

## Pipeline Overview: News → Signals → Graph

## News: BRICS.py

`BRICS.py` is a complete data‑collection and visualization toolkit for analyzing economic, social, resource, governance, and defense indicators for the five BRICS countries: **Brazil, Russia, India, China, and South Africa**.

The script performs three major tasks:

1. **Data Collection**
   - Retrieves a broad range of indicators from the **World Bank API** (GDP, inflation, energy use, employment, life expectancy, etc.).
   - Generates simulated trade data (placeholder values for exports and imports).
   - Organizes all collected data into a timestamped, structured dataset.

2. **Data Storage & Export**
   - Saves the full dataset as a JSON file (`brics_data.json`).
   - Exports country‑sector CSV tables for further analysis.

3. **Data Visualization**
   - Generates interactive Plotly dashboards for individual countries.
   - Produces cross‑country comparisons within any selected sector.
   - Creates a comprehensive heatmap summarizing multi‑year trends across all indicators.

---

**Visualization**

**1. Single‑Country Dashboard**
**Function:** `create_country_dashboard(country)`

This dashboard displays time‑series charts for key indicators of a selected BRICS country.

**What it shows:**
- Year‑by‑year **GDP Growth** (and optionally other indicators)
- Multiple subplots in a clean, interactive layout
- Visual overview of a country’s economic and social trajectory

Use this when you want a **deep dive into one country** rather than comparisons across countries.

**2. Sector Comparison**
**Function:** `create_sector_comparison(sector)`

Compares all BRICS countries within a chosen sector (economic, resources, governance, social development, etc.).

**What it shows:**
- Up to four indicators from the selected sector
- Each indicator displayed as a time‑series line plot
- BRICS countries color‑coded consistently
- Organized in a 2×2 subplot grid

Use this to quickly compare **how different countries evolve** on the same variables.

**3. Comprehensive Trend Heatmap**
**Function:** `create_comprehensive_heatmap()`

This heatmap summarizes the **trend direction and magnitude** of every indicator across all BRICS countries.

**How it works:**
- Uses the **last five years** of each indicator
- Fits a linear trendline
- Computes a normalized trend value:
  - **Positive = indicator increasing**
  - **Negative = indicator decreasing**
- Colors are assigned via **RdYlBu_r**:
  - **Red = strong upward trend**
  - **Blue = strong downward trend**
  - **White/Yellow = stable or minimal change**

**What the heatmap answers:**
> *Which indicators are improving or declining in each BRICS country — and by how much?*

It serves as a high‑level diagnostic tool to identify:
- Rapid improvements (e.g., rising internet access or GDP per capita)
- Declining indicators (e.g., falling energy use or reduced forest area)
- Mixed trends across sectors and countries

---

### news_ai.py

This module transforms real‑world news into numerical signals.

**fetch_news()**
Pulls BRICS‑related articles from Google News RSS:

- title  
- link  
- published date  
- source  

Saved to:

      data/news_cache.json

**extract_signals()**
Counts keyword frequencies to generate:

- **tariff_signal**  
- **coord_signal**  

These signals drive the geopolitical graph.

---

### knowledge_graph.py

Maintains and updates:

      graph_state.json

- Loads or initializes the graph  
- Updates intensities based on news signals  
- Ensures file integrity even if corrupted  

Signals modify:

- USA tariff aggression  
- China/Russia coordination  
- India’s alignment drift  

This graph becomes the **parameter backbone** for all game‑theory models.

---

## Signals: update_data.py

This script ties the entire intelligence system together.

### Pipeline:

1. **Collect macro‑economic BRICS data**  
   via `BRICSDataCollector`  
   → saved to `brics_data.json`

2. **Fetch and parse BRICS news**  
   → saved to `news_cache.json`

3. **Extract numerical signals**  
   → tariff_signal, coord_signal

4. **Update geopolitical graph**  
   → saved to `graph_state.json`

Run the full update cycle with:

      python update_data.py


This ensures the dashboard and models always run on **fresh intelligence**.

---

## Graph: BRICS_GT.py

The `BRICS_GT` class loads:

- macro‑data  
- news cache  
- geopolitical graph  

and computes:

- tariff aggression intensity  
- coordination intensity  

These become the parameters for all three models.

It also includes:

- Plotly visualization  
- HTML export utilities  
- A mathematical summary engine that interprets model output  

---

### Game Theory Models

The engine implements three complementary models, each capturing a different facet of strategic behavior.


### 1. Adaptive Tariff Game

A repeated game with logistic‑based adaptive defection:

$$
p_{\text{USA}} = \sigma(0.4T + 0.7 \cdot \text{BRICS}_{t-1})
$$

$$
p_{\text{BRICS}} = \sigma(0.35T + 0.6 \cdot \text{USA}_{t-1})
$$

where  

$$
\sigma(x) = \frac{1}{1 + e^{-x}}.
$$

Each round generates two key outcomes:

- **A binary action** (0 = cooperate, 1 = defect) for both USA and BRICS  
- **A resulting payoff** drawn from the 2×2 matrix  

$$
\begin{array}{c|cc}
      & \text{USA: C} & \text{USA: D} \\
    \hline
    \text{BRICS: C} & (3,3) & (-2,4) \\
    \text{BRICS: D} & (4,-2) & (-1,-1)
\end{array}
$$

Over time, the interaction forms two evolving curves:

1. **Cumulative BRICS payoff**, showing whether escalation or cooperation becomes dominant  
2. **BRICS defection probability**, which adjusts based on previous actions and the tariff intensity parameter \(T\)

Because both sides update their strategy probabilities using sigmoid functions, the system behaves like a *soft* reinforcement model: early actions shape future tendencies, but no agent becomes deterministic. This creates an iterative dynamic that often drifts toward quasi‑stable regimes before occasionally jumping into new strategic patterns — similar to how non‑linear systems settle, oscillate, or wander depending on parameter strength.

The output visualization highlights this interplay, making the long‑term strategic trajectory easy to interpret.


### 2. Energy & Currency Coordination Game

A coalition‑formation payoff model:

$$
\text{Net}(n) = 4 n^{1.2} + 0.6 C \cdot n - \text{Penalty}(n)
$$

where $$\( C \)$$ is the China–Russia coordination intensity.

This model quantifies:

- marginal benefit of additional cooperating states  
- diminishing returns  
- structural penalties  
- coalition stability  

It is a **non‑linear cooperative game** embedded in economic constraints.


### 3. Richardson‑Style Tariff Arms Race

A continuous‑time escalation model:

$$
\frac{dU}{dt} = k_1 B - c_1 U + s_1
$$
$$
\frac{dB}{dt} = k_2 U - c_2 B + s_2
$$

with parameters derived from the geopolitical graph.

This model captures:

- reactive escalation  
- internal damping  
- exogenous pressure  
- long‑run equilibrium or divergence  

It is the classical arms‑race system, reinterpreted for tariff policy.

---
## Scenario Risk Map

The dashboard now includes a Scenario‑Driven Global Risk Map, a new analytical layer that transforms geopolitical shocks into a spatial risk geometry. It quantifies how disruptions propagate through global trade networks, maritime chokepoints, BRICS‑aligned corridors, energy dependencies, and currency blocs.

The result is a live, interactive world map that updates whenever the pipeline refreshes.

### How the Scenario Engine Works
The system integrates three major components:

1. Chokepoint Exposure Models

Files:

      etl/build_hormuz_exposure.py
      etl/build_suez_exposure.py
      data/hormuz_exposure.csv
      data/suez_exposure.csv

These scripts compute country‑level exposure to:

- Strait of Hormuz (energy flow risk)
- Suez Canal (container + oil transit risk)

Each exposure dataset encodes:
- trade share routed through the chokepoint
- energy dependency
- rerouting elasticity
- shock propagation coefficients

These values become risk multipliers in scenario simulations.

2. Scenario Engine
File: `global_risk_data.py`

This module defines structured geopolitical scenarios, including:
- Hormuz Closure
- Suez Disruption
- BRICS Currency Bloc Formation
- Tariff Shock
- Energy Coalition Expansion

Each scenario injects shocks into the system:
- supply chain delays
- price volatility
- alliance realignment
- tariff retaliation
- currency fragmentation

The engine computes a risk score for every country, combining:
- chokepoint exposure
- BRICS alignment
- macro‑economic fragility
- news‑derived signals
- geopolitical graph pressure

3. Global Risk Map Renderer
The dashboard visualizes scenario output using a custom color scale:
- Deep Red — severe systemic risk
- Orange — elevated exposure
- Yellow — moderate sensitivity
- Blue — low exposure
- Grey — neutral or insufficient data

Features:
- hover for country‑level breakdown
- switch scenarios in real time
- compare baseline vs. shock states

This turns the dashboard into a geopolitical stress‑testing environment.

### ETL Pipeline
The repository includes a dedicated Extract–Transform–Load (ETL) pipeline that prepares all structural data used by the models and dashboard.

Directory:

      etl/
          build_hormuz_exposure.py
          build_suez_exposure.py
          common_regions.py
          comtrade_pull.py

ETL Stages
1. Extraction
- Pulls raw trade data (via Comtrade or placeholders)
- Loads region mappings and ISO3 codes
- Reads maritime exposure datasets
- Integrates World Bank indicators (via BRICS.py)

2. Transformation
- Normalizes country names and codes
- Computes chokepoint exposure coefficients
- Aggregates trade flows by region
- Cleans and validates datasets
- Harmonizes time‑series formats

3. Loading
- Writes standardized CSVs to /data
- Updates brics_data.json
- Refreshes graph_state.json
- Prepares scenario‑ready risk tables
- The ETL pipeline ensures clean, consistent, reproducible data across all models.

### Global Risk Model
File: `risk_model.py`

This module fuses:
- macro‑economic fragility
- chokepoint exposure
- BRICS alignment
- news‑derived signals
- game‑theory outputs
- into a unified systemic risk index.

It computes:
- baseline systemic risk
- scenario‑adjusted risk
- regional spillover effects
- BRICS vs. non‑BRICS divergence

The output feeds directly into:
- the Scenario Risk Map
- the dashboard’s risk summary panels

## Full System Flow
The expanded intelligence pipeline now follows:

      News → Signals → Graph → Game Theory → Risk Model → Scenario Engine → Global Map

Each layer enriches the next:
- News shifts the geopolitical graph
- The graph shifts game‑theory parameters
- Game‑theory outputs shift systemic risk
- Risk shifts scenario propagation
- Scenarios reshape the global map

This creates a computational geopolitics stack where every component is mathematically linked.

---

## Dash App

The final script builds the **interactive dashboard**.

It integrates:

- live news feed  
- BRICS world influence map  
- tariff game simulation  
- energy coordination model  
- arms‑race dynamics  
- model‑generated summaries  

The dashboard uses:

- `BRICS_GT` for simulations  
- `news_ai` for live news  
- `knowledge_graph` for geopolitical state  
- Plotly for all visualizations  
- Dash Tabs for navigation  

The world map is fully responsive and uses a custom color scale to represent:

- BRICS members  
- high‑influence states  
- medium‑influence states  
- low‑influence states  
- neutral states  

The dashboard is the **final layer** of the pipeline — the visualization of everything computed upstream.

Run it with:

      python app.py

---

## Dependencies

Core libraries:

- numpy  
- plotly  
- dash  
- feedparser  
- json  
- textwrap  
- os  
- webbrowser  

Install with:

      pip install numpy plotly dash feedparser

---

# Why This Project Exists

This repository is an attempt to treat geopolitics as a **computable system**:

- incentives become payoff matrices  
- alignment becomes graph structure  
- escalation becomes differential equations  
- cooperation becomes coalition payoffs  
- uncertainty becomes stochastic strategy selection  
- news becomes numerical signals  
- macro‑data becomes structural parameters  
- everything flows into a unified dashboard  

It is a way of seeing BRICS not as headlines, but as **strategic agents embedded in a dynamic landscape**.

The mathematics does not replace political analysis —  
it reveals the structure beneath it.

### Data Sources

This project uses publicly available datasets from:

- **World Bank Open Data API**
  https://data.worldbank.org  
  Used for: GDP, inflation, trade, population, energy, governance indicators.
- **World Economic Forum — Global Risk Factors**
  https://raw.githubusercontent.com/WEF/global-risks/master/factors.json
  Used for: Middle East Tension, Energy Supply Risk, Sanctions Pressure, Alliance Volatility, Global Trade Exposure, Logitics Chokepoint Risk
- **Google News RSS**  
  Used to fetch recent BRICS‑related articles for signal extraction.
- **Local Exposure Layers (User‑Provided CSVs)**  
  The system optionally loads two chokepoint‑specific exposure datasets:
  a) Suez Exposure: `data/suez_exposure.csv`
  Represents trade dependence on the Suez corridor.
  b) Hormuz Exposure: `data/hormuz_exposure.csv`
  Represents logistics and energy‑flow dependence on the Strait of Hormuz.
  
---

# License

MIT License

