import numpy as np
from risk_data_collector import RiskDataCollector

# =============================================================
# BRICS (ISO3 codes)
# =============================================================
BRICS_COUNTRIES = ["BRA", "RUS", "IND", "CHN", "ZAF"]

# =============================================================
# FACTORS & SHOCK TYPES
# =============================================================
GEOPOLITICAL_FACTORS = [
    "Middle East Tension",
    "Energy Supply Risk",
    "Sanctions Pressure",
    "Alliance Volatility",
    "Global Trade Exposure",
    "Logistics Chokepoint Risk",
]

SHOCK_TYPES = [
    "Regional Conflict",
    "Oil Supply Disruption",
    "Sanctions Escalation",
    "Diplomatic Breakdown",
    "Suez Blockage",
    "Maritime Shipping Delay",
]

# =============================================================
# LOAD DATA
# =============================================================
collector = RiskDataCollector()
DATA = collector.load_all(BRICS_COUNTRIES)

HORMUZ_EXPOSURE = DATA.get("logistics", {})
SUEZ_EXPOSURE   = DATA.get("trade", {})

HORMUZ_EXPOSURE = {k: float(max(0, min(1, v))) for k, v in HORMUZ_EXPOSURE.items()}
SUEZ_EXPOSURE   = {k: float(max(0, min(1, v))) for k, v in SUEZ_EXPOSURE.items()}

WGI = DATA["wgi"]
WEF = DATA["wef"]

# Normalize WGI to 0–1
WGI_NORM = {c: (v + 2.5) / 5.0 if v is not None else 0.5 for c, v in WGI.items()}

# Universe of countries for world heatmap
ALL_COUNTRIES = list(WGI_NORM.keys())

# =============================================================
# UTILS
# =============================================================


def expand_to_full_map(exposure_dict, default=0.0):
    """
    Expand sparse ISO3→value dict to full world map.
    """
    full = {iso: float(default) for iso in ALL_COUNTRIES}
    for iso, v in exposure_dict.items():
        if iso in full:
            full[iso] = float(max(0, min(1, v)))
    return full

# =============================================================
# MATRIX BUILDERS
# =============================================================


def build_B_dynamic():
    B = []
    for iso3 in BRICS_COUNTRIES:
        gov = WGI_NORM.get(iso3, 0.5)
        row = [gov * WEF.get(f, 1.0) for f in GEOPOLITICAL_FACTORS]
        B.append(row)
    return np.array(B)


def build_S_dynamic():
    S = []
    for f in GEOPOLITICAL_FACTORS:
        row = [WEF.get(f, 1.0) for _ in SHOCK_TYPES]
        S.append(row)
    return np.array(S)

# =============================================================
# CORE COMPUTATIONS
# =============================================================


def compute_factor_shocks(shock_vector):
    return build_S_dynamic() @ shock_vector


def compute_country_risk_scores(factor_shocks):
    return build_B_dynamic() @ factor_shocks

# =============================================================
# SCENARIOS
# =============================================================


def iran_escalation_scenario():
    shock_vector = np.array([1.0, 0.9, 1.0, 0.7, 0.0, 0.1])
    factor_shocks = compute_factor_shocks(shock_vector)
    country_scores = compute_country_risk_scores(factor_shocks)

    brics_scores = dict(zip(BRICS_COUNTRIES, country_scores))
    full_map = expand_to_full_map(brics_scores, default=0.0)

    return {
        "shock_vector": dict(zip(SHOCK_TYPES, shock_vector)),
        "factors": dict(zip(GEOPOLITICAL_FACTORS, factor_shocks)),
        "countries": full_map,
        "description": "Iran–Israel escalation scenario."
    }


def hormuz_closure_scenario():
    if not HORMUZ_EXPOSURE:
        shock_vector = np.array([0.9, 1.0, 0.6, 0.5, 0.0, 0.2])
        factor_shocks = compute_factor_shocks(shock_vector)
        country_scores = compute_country_risk_scores(factor_shocks)
        brics_scores = dict(zip(BRICS_COUNTRIES, country_scores))
        full_map = expand_to_full_map(brics_scores, default=0.0)
        return {
            "shock_vector": dict(zip(SHOCK_TYPES, shock_vector)),
            "factors": dict(zip(GEOPOLITICAL_FACTORS, factor_shocks)),
            "countries": full_map,
            "description": "Fallback Hormuz closure model."
        }

    full_map = expand_to_full_map(HORMUZ_EXPOSURE, default=0.0)
    return {
        "shock_vector": None,
        "factors": None,
        "countries": full_map,
        "description": "Data-driven Hormuz exposure."
    }


def suez_disruption_scenario():
    if not SUEZ_EXPOSURE:
        shock_vector = np.array([0.4, 0.2, 0.1, 0.2, 1.0, 0.9])
        factor_shocks = compute_factor_shocks(shock_vector)
        country_scores = compute_country_risk_scores(factor_shocks)
        brics_scores = dict(zip(BRICS_COUNTRIES, country_scores))
        full_map = expand_to_full_map(brics_scores, default=0.0)
        return {
            "shock_vector": dict(zip(SHOCK_TYPES, shock_vector)),
            "factors": dict(zip(GEOPOLITICAL_FACTORS, factor_shocks)),
            "countries": full_map,
            "description": "Fallback Suez disruption model."
        }

    full_map = expand_to_full_map(SUEZ_EXPOSURE, default=0.0)
    return {
        "shock_vector": None,
        "factors": None,
        "countries": full_map,
        "description": "Data-driven Suez exposure."
    }
