import math, pandas as pd
from etl.comtrade_pull import cached_pull, extract_value
from etl.common_regions import EU, E_ASIA, S_ASIA, SE_ASIA, OCEANIA, N_AFRICA, E_AFRICA, W_AFRICA, S_AFRICA

YEARS = [2022, 2023]
# “Suez counterparties” per region. You can refine per reporter region.
SUEZ_PARTIES = (E_ASIA | S_ASIA | SE_ASIA | OCEANIA | N_AFRICA | E_AFRICA | W_AFRICA | S_AFRICA)


def build(reporter_list):
    rows = []
    for r in reporter_list:
        total_trade = 0.0
        suez_trade = 0.0
        for y in YEARS:
            # TOTAL merchandise trade (imports + exports) — proxy with imports + exports across all partners
            # Imports
            all_imp = cached_pull(f"cache/{r}_{y}_imp_all.json", y, r, "all", "TOTAL", "import")
            total_trade += extract_value(all_imp)
            # Exports
            all_exp = cached_pull(f"cache/{r}_{y}_exp_all.json", y, r, "all", "TOTAL", "export")
            total_trade += extract_value(all_exp)

            # Trade with counterparties likely routed via Suez (imports + exports)
            for p in SUEZ_PARTIES:
                imp = cached_pull(f"cache/{r}_{y}_imp_{p}.json", y, r, p, "TOTAL", "import")
                suez_trade += extract_value(imp)
                exp = cached_pull(f"cache/{r}_{y}_exp_{p}.json", y, r, p, "TOTAL", "export")
                suez_trade += extract_value(exp)

        share = suez_trade / total_trade if total_trade > 0 else 0.0
        rows.append({"iso3": r, "value": max(0.0, min(1.0, share))})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    reporters = ["DEU","FRA","ITA","ESP","NLD","GBR","POL","SWE","GRC","EGY","SAU","ARE","QAT","OMN","IND","PAK","BGD","LKA","CHN","JPN","KOR","SGP","USA","BRA","ZAF"]
    df = build(reporters)
    df.to_csv("data/suez_exposure.csv", index=False)
    print("Wrote data/suez_exposure.csv")
