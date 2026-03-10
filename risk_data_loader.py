import pandas as pd
import numpy as np
import plotly.express as px


# -------------------------------------------------------------------
# Helper: build country name → ISO3 lookup using Plotly’s dataset
# -------------------------------------------------------------------
COUNTRY_IDX = px.data.gapminder().query("year == 2007")[
    ["country", "iso_alpha"]
].rename(columns={"iso_alpha": "iso3"})

NAME_TO_ISO = {r["country"]: r["iso3"] for _, r in COUNTRY_IDX.iterrows()}
ISO3_SET = set(COUNTRY_IDX["iso3"])


def to_iso3(name):
    """
    Convert a country name or ISO3 code to ISO3.
    Returns None if no match.
    """
    if not isinstance(name, str):
        return None
    name = name.strip()
    if len(name) == 3 and name.upper() in ISO3_SET:
        return name.upper()
    return NAME_TO_ISO.get(name)


# -------------------------------------------------------------------
# 1. Fragile States Index
# -------------------------------------------------------------------
def load_fsi(path="data/fragile_states_index.csv"):
    """
    Expected columns: Country, Score
    Converts Country → ISO3 and returns { ISO3: score }
    """
    df = pd.read_csv(path)
    out = {}
    for _, row in df.iterrows():
        iso = to_iso3(row["Country"])
        if iso:
            out[iso] = float(row["Score"])
    return out


# -------------------------------------------------------------------
# 2. World Governance Indicators (averaged)
# -------------------------------------------------------------------
def load_wgi(path="data/world_governance_indicators.csv"):
    """
    Expected columns: Country, RuleOfLaw, Stability, Effectiveness, Corruption
    Returns { ISO3: average_score }
    """
    df = pd.read_csv(path)

    indicators = ["RuleOfLaw", "Stability", "Effectiveness", "Corruption"]

    out = {}
    for _, row in df.iterrows():
        iso = to_iso3(row["Country"])
        if not iso:
            continue
        vals = []
        for col in indicators:
            try:
                vals.append(float(row[col]))
            except:
                continue
        if vals:
            out[iso] = float(np.mean(vals))
        else:
            out[iso] = None
    return out


# -------------------------------------------------------------------
# 3. WEF Factor Weights
# -------------------------------------------------------------------
def load_wef_factor_weights(path="data/wef_risk_factors.csv"):
    """
    Expected columns: Factor, Weight
    Returns { factor_name: weight }
    """
    df = pd.read_csv(path)

    out = {}
    for _, row in df.iterrows():
        factor = str(row["Factor"]).strip()
        weight = float(row["Weight"])
        out[factor] = weight
    return out
