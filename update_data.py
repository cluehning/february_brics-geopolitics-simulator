# update_data.py
from BRICS import BRICSDataCollector
from news_ai import fetch_news, extract_signals
from knowledge_graph import update_graph
import json


def update():
    # Update BRICS macro data
    collector = BRICSDataCollector()
    data = collector.collect_all_data()

    with open("data/brics_data.json", "w") as f:
        json.dump(data, f, indent=2)

    # Update news signals
    articles = fetch_news()
    signals = extract_signals(articles)

    # Update relationship graph
    update_graph(signals)

    print("✔ Data & Intelligence System Updated")


if __name__ == "__main__":
    update()
