import time, os, json, pandas as pd, requests

BASE = "https://comtradeapi.un.org/data/v1/get/agg/COMMODITY/HS"
# We’ll pull simple yearly totals for HS 2709 and 2710 by reporter/partner.

def comtrade_pull(year:int, reporter:str, partner:str, hs:str, flow:str="import"):
    params = {
        "time": year,
        "freq": "A",
        "px": "HS",
        "r": reporter,  # ISO3 reporter
        "p": partner,   # ISO3 partner (or all)
        "rg": 1 if flow=="import" else 2,
        "cc": hs,       # commodity code
        "fmt": "JSON"
    }
    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def cached_pull(path, *args, **kwargs):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    data = comtrade_pull(*args, **kwargs)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data, f)
    time.sleep(1.0)  # basic rate-limit spacing
    return data

def extract_value(json_obj)->float:
    try:
        # API result structure contains 'dataset' with 'PrimaryValue'
        vals = [float(d["PrimaryValue"]) for d in json_obj.get("dataset", []) if d.get("PrimaryValue") is not None]
        return sum(vals)
    except Exception:
        return 0.0