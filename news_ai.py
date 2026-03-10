import os
import json
import feedparser


FEED_URL = (
    "https://news.google.com/rss/search?"
    "q=BRICS+trade+tariffs+sanctions+economy+geopolitics"
    "&hl=en&gl=US&ceid=US:en"
)


def fetch_news():
    """
    Fetch structured BRICS news:
    - title
    - link
    - published date
    - source name

    Saves results to data/news_cache.json
    """
    os.makedirs("data", exist_ok=True)

    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries[:12]:
        published = getattr(entry, "published", "Unknown date")
        source = getattr(entry, "source", None)

        if isinstance(source, dict):
            source_title = source.get("title", "Unknown source")
        else:
            source_title = "Unknown source"

        article = {
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "source": source_title
        }
        articles.append(article)

    with open("data/news_cache.json", "w", encoding="utf-8") as file:
        json.dump(articles, file, indent=2)

    return articles


def extract_signals(articles):
    """
    Convert news into numerical signals for the BRICS intelligence engine.
    """
    keywords = [
        "tariff",
        "sanction",
        "retaliation",
        "currency",
        "yuan",
        "china",
        "export",
        "import ban",
        "trade war",
    ]

    score = 0
    for article in articles:
        title = article["title"].lower()
        for word in keywords:
            if word in title:
                score += 1

    return {
        "tariff_signal": min(score, 10),
        "coord_signal": max(0, 10 - score),
    }
