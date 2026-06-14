import requests
import os
import json
import time

OUTPUT_DIR = "data/raw"

WIKI_API = "https://en.wikipedia.org/w/api.php"

# Wikipedia requires a descriptive User-Agent
HEADERS = {
    "User-Agent": "LegalXKnowledgeBot/1.0 (legal knowledge centre project; contact@example.com)"
}

TOPICS = {
    "pocso_act": {
        "display_name": "POCSO Act",
        "wiki_title": "Protection of Children from Sexual Offences Act, 2012",
    },
    "consumer_protection_act": {
        "display_name": "Consumer Protection Act",
        "wiki_title": "Consumer Protection Act, 2019",
    },
    "cyber_crime_laws": {
        "display_name": "Cyber Crime Laws",
        "wiki_title": "Information Technology Act, 2000",
    },
    "rti_act": {
        "display_name": "Right to Information Act",
        "wiki_title": "Right to Information Act, 2005",
    },
    "gst_registration": {
        "display_name": "GST Registration",
        "wiki_title": "Goods and Services Tax (India)",
    },
}


def fetch_wikipedia_text(title: str) -> str:
    """Fetch plain text content of a Wikipedia article using the official API."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,  # Returns plain text, no HTML markup
        "exsectionformat": "plain",
        "format": "json",
    }

    try:
        response = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "missing" in page:
            print(f"  [WARN] Article not found on Wikipedia: '{title}'")
            return ""

        return page.get("extract", "")

    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch '{title}': {e}")
        return ""


def scrape_all_topics():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = {}

    for topic_key, meta in TOPICS.items():
        print(f"\n{'='*50}")
        print(f"Fetching: {meta['display_name']}")
        print(f"Wikipedia title: {meta['wiki_title']}")

        text = fetch_wikipedia_text(meta["wiki_title"])

        if text:
            output_path = os.path.join(OUTPUT_DIR, f"{topic_key}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"TOPIC: {meta['display_name']}\n")
                f.write(
                    f"SOURCE: https://en.wikipedia.org/wiki/{meta['wiki_title'].replace(' ', '_')}\n"
                )
                f.write("=" * 60 + "\n\n")
                f.write(text)

            word_count = len(text.split())
            print(f"  [OK] Saved {word_count} words -> {output_path}")
            summary[topic_key] = {
                "status": "success",
                "display_name": meta["display_name"],
                "words": word_count,
                "file": output_path,
            }
        else:
            print(f"  [FAIL] No text retrieved for {topic_key}")
            summary[topic_key] = {
                "status": "failed",
                "display_name": meta["display_name"],
            }

        time.sleep(1)  # be polite to Wikipedia servers

    # Save a summary so you know what was fetched
    summary_path = os.path.join(OUTPUT_DIR, "scrape_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*50}")
    print("SCRAPING COMPLETE")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    scrape_all_topics()
