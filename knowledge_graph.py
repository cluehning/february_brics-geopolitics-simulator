import json
import os

GRAPH_PATH = "data/graph_state.json"


def load_graph():
    """Loads graph. Creates a default one if missing or corrupted."""
    os.makedirs("data", exist_ok=True)

    default_graph = {
        "USA": {"tariff_aggression": 5},
        "China": {"coordination": 5},
        "Russia": {"coordination": 6},
        "India": {"alignment": 3},
        "Brazil": {"alignment": 2},
        "South Africa": {"alignment": 2},
    }

    # If file does not exist → create it
    if not os.path.exists(GRAPH_PATH):
        with open(GRAPH_PATH, "w") as f:
            json.dump(default_graph, f, indent=2)
        return default_graph

    # If file exists → try to load it
    try:
        with open(GRAPH_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # File exists but is empty or corrupted → overwrite with default
        with open(GRAPH_PATH, "w") as f:
            json.dump(default_graph, f, indent=2)
        return default_graph


def update_graph(signals):
    """Updates relationship graph based on news-derived signals."""
    graph = load_graph()

    # Increase tariff aggression if news mentions sanctions/tariffs
    graph["USA"]["tariff_aggression"] = min(10, 5 + signals["tariff_signal"])

    # Coordination grows with anti-dollar or tariff pressure news
    graph["China"]["coordination"] = min(10, 5 + signals["coord_signal"])
    graph["Russia"]["coordination"] = min(10, 6 + signals["coord_signal"])

    # Mixed alignment country:
    graph["India"]["alignment"] = 3 + (signals["coord_signal"] // 3)

    # Ensure saving folder exists
    os.makedirs("data", exist_ok=True)

    with open(GRAPH_PATH, "w") as f:
        json.dump(graph, f, indent=2)

    return graph
