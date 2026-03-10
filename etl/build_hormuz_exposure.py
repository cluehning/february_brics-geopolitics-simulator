import pandas as pd
from etl.comtrade_pull import cached_pull, extract_value
from etl.common_regions import GULF

YEARS = [2022, 2023]  # adjust to latest available
HS_CODES = ["2709", "2710"]  # crude oil + refined products


def build(reporter_list):
    rows = []
    for r in reporter_list:
        total = 0.0
        gulf = 0.0
        for y in YEARS:
            for hs in HS_CODES:
                # total imports of HS from ALL partners (p=all)
                all_json = cached_pull(f"cache/{r}_{y}_{hs}_all.json", y, r, "all", hs, "import")
                total += extract_value(all_json)

                # imports from each Gulf partner
                for p in GULF:
                    g_json = cached_pull(f"cache/{r}_{y}_{hs}_{p}.json", y, r, p, hs, "import")
                    gulf += extract_value(g_json)

        share = gulf / total if total > 0 else 0.0
        rows.append({"iso3": r, "value": max(0.0, min(1.0, share))})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Provide a reporter list (ISO3). Start with world list you care about.
    reporters = ["IND","CHN","JPN","KOR","PAK","BGD","SGP","MYS","THA","VNM","PHL","IDN","DEU","FRA","ITA","ESP","NLD","GBR","USA","BRA","ZAF","EGY"]
    df = build(reporters)
    df.to_csv("data/hormuz_exposure.csv", index=False)
    print("Wrote data/hormuz_exposure.csv")
