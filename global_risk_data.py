import pandas as pd


def load_global_risk_data():
    """
    Loads open-source geopolitical risk data.
    Currently uses Fragile States Index (FSI) from Fund for Peace.
    You must place the CSV in the /data folder.
    """

    try:
        df = pd.read_csv("data/fragile_states_index.csv")
        # Expect columns: Country, Score
        risk = dict(zip(df["Country"], df["Score"]))
        return risk

    except Exception as e:
        print("Error loading FSI data:", e)
        return {}
