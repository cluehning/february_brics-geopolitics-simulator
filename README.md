# BRICS Game Theory — Modeling Strategy, Incentives, and the Geometry of Power

## How This Project Began

This repository started with a simple intuition:

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

---

# The Core Idea: Game Theory

The engine implements three complementary models, each capturing a different facet of strategic behavior.

---

## 1. Adaptive Tariff Game

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

---

## 2. Energy & Currency Coordination Game

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

---

## 3. Richardson‑Style Tariff Arms Race

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

# Overview — News → Signals → Graph

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

## 📊 Visualizations

### 1. Single‑Country Dashboard
**Function:** `create_country_dashboard(country)`

This dashboard displays time‑series charts for key indicators of a selected BRICS country.

**What it shows:**
- Year‑by‑year **GDP Growth** (and optionally other indicators)
- Multiple subplots in a clean, interactive layout
- Visual overview of a country’s economic and social trajectory

Use this when you want a **deep dive into one country** rather than comparisons across countries.

---

### 2. Sector Comparison
**Function:** `create_sector_comparison(sector)`

Compares all BRICS countries within a chosen sector (economic, resources, governance, social development, etc.).

**What it shows:**
- Up to four indicators from the selected sector
- Each indicator displayed as a time‑series line plot
- BRICS countries color‑coded consistently
- Organized in a 2×2 subplot grid

Use this to quickly compare **how different countries evolve** on the same variables.

---

### 3. Comprehensive Trend Heatmap
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

## ✔️ Summary

`BRICS.py` gives you a full workflow:
**Collect → Organize → Analyze → Visualize**,  
allowing researchers and analysts to explore long‑term development patterns across BRICS nations.

### news_ai.py

This module transforms real‑world news into numerical signals.

#### fetch_news()
Pulls BRICS‑related articles from Google News RSS:

- title  
- link  
- published date  
- source  

Saved to:

      data/news_cache.json

#### extract_signals()
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

# Signals: update_data.py

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

## Game‑Theory Engine — brics_gt.py

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

# Graph: Dash App

Your final script builds the **interactive dashboard**.

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

# Project Structure

      │   app.py
      │   BRICS.py
      │   BRICS_GT.py
      │   knowledge_graph.py
      │   news_ai.py
      │   update_data.py
      │
      ├───assets
      │   │   font_v3.css
      │   │
      │   └───fonts
      │           TTNormsPro-Medium.ttf
      │           TTNormsPro-Regular.ttf
      │
      ├───data
      │       graph_state.json
      │       news_cache.json


---

# Dependencies

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

---

# License

MIT License

