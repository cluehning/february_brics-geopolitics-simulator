import os
import csv
import time
import requests
import numpy as np
from typing import Dict, List, Optional
import plotly.express as px


class RiskDataCollector:
    """
    Unified loader for governance (WGI), WEF factor weights,
    and scenario-specific exposure layers (trade exposure, chokepoint risk).

    - WGI: World Bank API (latest non-null average across selected indicators)
    - WEF: factor weights JSON (fallback defaults if fetch fails)
    - Trade exposure: optional CSV {iso3, value}
    - Chokepoint risk: optional CSV {iso3, value}

    All outputs normalize to country ISO3 keys when possible.
    """

    def __init__(self, timeout: int = 10, retries: int = 2, backoff: float = 0.5):
        # APIs
        self.wgi_url_tpl = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json"
        self.wef_url = "https://raw.githubusercontent.com/WEF/global-risks/master/factors.json"

        # WGI indicator codes (World Bank)
        self.wgi_indicators = {
            "RuleOfLaw": "RL.EST",
            "Stability": "PV.EST",
            "Effectiveness": "GE.EST",
            "Corruption": "CC.EST",
        }

        # HTTP settings
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "BRICS-Risk-Dashboard/1.0 (+github.com/your-org)",
                "Accept": "application/json",
            }
        )

        # Country index for ISO3/name normalization (Plotly dataset; static)
        self._country_idx = px.data.gapminder().query("year == 2007")[
            ["country", "iso_alpha"]
        ].rename(columns={"iso_alpha": "iso3"})
        # Fast lookup maps
        self._name_to_iso = {r["country"]: r["iso3"] for _, r in self._country_idx.iterrows()}
        self._iso_set = set(self._country_idx["iso3"])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _request_json(self, url: str) -> Optional[dict]:
        for attempt in range(self.retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
            time.sleep(self.backoff * (attempt + 1))
        return None

    def _to_iso3(self, key: str) -> Optional[str]:
        """
        Accepts ISO3 or English country name; returns ISO3 if known, else None.
        """
        if not key:
            return None
        key = key.strip()
        if len(key) == 3 and key.upper() in self._iso_set:
            return key.upper()
        return self._name_to_iso.get(key)

    def _normalize_country_list(self, countries: List[str]) -> List[str]:
        """
        Normalize input list (ISO3 or names) → ISO3 unique list.
        """
        out: List[str] = []
        seen = set()
        for c in countries:
            iso = self._to_iso3(c)
            if iso and iso not in seen:
                out.append(iso)
                seen.add(iso)
        return out

    # ------------------------------------------------------------------
    # 1) World Governance Indicators (WGI)
    # ------------------------------------------------------------------
    def _load_wgi_one(self, iso3: str) -> Optional[float]:
        """
        Fetch latest non-null average over selected WGI indicators for a single country (ISO3).
        Returns None if no data.
        """
        series_values: List[float] = []
        for _, ind in self.wgi_indicators.items():
            url = self.wgi_url_tpl.format(country=iso3.lower(), indicator=ind)
            data = self._request_json(url)
            if not data or not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list):
                continue

            # Find the latest non-null value in the time series
            values = data[1]
            val = None
            for row in values:
                # API typically returns most-recent first, but be defensive
                if row and isinstance(row, dict) and row.get("value") is not None:
                    try:
                        val = float(row["value"])
                        break
                    except Exception:
                        continue
            if val is not None:
                series_values.append(val)

        if series_values:
            return float(np.mean(series_values))
        return None

    def load_wgi(self, countries: List[str]) -> Dict[str, Optional[float]]:
        """
        Load WGI averages for a list of countries (ISO3 or names).
        Output dict is keyed by ISO3.
        """
        iso_list = self._normalize_country_list(countries)
        out: Dict[str, Optional[float]] = {}
        for iso3 in iso_list:
            out[iso3] = self._load_wgi_one(iso3)
        return out

    # ------------------------------------------------------------------
    # 2) WEF Global Risk Factors
    # ------------------------------------------------------------------
    def load_wef_factors(self, factor_names: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Load WEF factor weights (expects a JSON dict of factor -> weight).
        If fetch fails, return sensible defaults and ensure requested factor_names exist.
        """
        fallback = {
            # Existing factors you used
            "Middle East Tension": 1.0,
            "Energy Supply Risk": 1.0,
            "Sanctions Pressure": 1.0,
            "Alliance Volatility": 1.0,
            # Added factors for Suez/Hormuz modelling
            "Global Trade Exposure": 1.0,
            "Logistics Chokepoint Risk": 1.0,
        }

        data = self._request_json(self.wef_url)
        if isinstance(data, dict):
            # Keep only numeric weights; merge with fallback to ensure coverage
            cleaned = {k: float(v) for k, v in data.items() if self._is_number(v)}
            merged = {**fallback, **cleaned}
        else:
            merged = fallback

        if factor_names:
            # Ensure all requested factors are present; default weight = 1.0
            out: Dict[str, float] = {}
            for f in factor_names:
                out[f] = float(merged.get(f, 1.0))
            return out
        return merged

    @staticmethod
    def _is_number(x) -> bool:
        try:
            float(x)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 3) OPTIONAL: Trade exposure & chokepoint risk (from local CSVs)
    # ------------------------------------------------------------------
    # CSV schema: iso3,value
    def _load_csv_series(self, path: str) -> Dict[str, float]:
        out: Dict[str, float] = {}
        if not os.path.exists(path):
            return out
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    iso = self._to_iso3(row.get("iso3", ""))
                    if not iso:
                        continue
                    try:
                        val = float(row.get("value", ""))
                    except Exception:
                        continue
                    # clip to [0,1]
                    out[iso] = max(0.0, min(1.0, val))
        except Exception:
            # fail safe
            return {}
        return out

    def load_trade_exposure(self, countries: List[str], path: str = "data/trade_exposure.csv") -> Dict[str, float]:
        """
        Load normalized trade exposure (e.g., share of trade affected by Suez / maritime reliance).
        """
        data = self._load_csv_series(path)
        # filter to requested countries if provided
        if countries:
            iso_list = set(self._normalize_country_list(countries))
            return {k: v for k, v in data.items() if k in iso_list}
        return data

    def load_chokepoint_risk(self, countries: List[str], path: str = "data/chokepoint_risk.csv") -> Dict[str, float]:
        """
        Load normalized chokepoint risk (e.g., dependence on Suez/Hormuz lanes, port reliance).
        """
        data = self._load_csv_series(path)
        if countries:
            iso_list = set(self._normalize_country_list(countries))
            return {k: v for k, v in data.items() if k in iso_list}
        return data

    # ------------------------------------------------------------------
    # 4) Unified loader
    # ------------------------------------------------------------------
    def load_all(self, countries: List[str]) -> Dict[str, dict]:
        """
        Returns:
            {
              "wgi": {ISO3: float|None},
              "wef": {factor: weight},
              "trade": {ISO3: 0..1},           # optional if CSV present
              "logistics": {ISO3: 0..1},       # optional if CSV present
            }
        """
        # Normalize once
        iso_list = self._normalize_country_list(countries)

        # Governance (WGI)
        wgi = self.load_wgi(iso_list)

        # WEF factors (ensure the ones your model expects exist)
        wef = self.load_wef_factors(
            factor_names=[
                "Middle East Tension",
                "Energy Supply Risk",
                "Sanctions Pressure",
                "Alliance Volatility",
                "Global Trade Exposure",
                "Logistics Chokepoint Risk",
            ]
        )

        # Optional CSV-based layers (present if you create the files)
        # in RiskDataCollector.load_all(...)
        trade = self.load_trade_exposure(iso_list, path="data/suez_exposure.csv")
        logistics = self.load_chokepoint_risk(iso_list, path="data/hormuz_exposure.csv")

        return {
            "wgi": wgi,            # ISO3 -> float|None
            "wef": wef,            # factor -> weight (float)
            "trade": trade,        # ISO3 -> float (0..1), optional
            "logistics": logistics # ISO3 -> float (0..1), optional
        }
