import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = "data/raw"
OUTPUT_PATH = "data/cards.json"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOPICS = {
    "pocso_act": "POCSO Act",
    "consumer_protection_act": "Consumer Protection Act",
    "cyber_crime_laws": "Cyber Crime Laws",
    "rti_act": "Right to Information Act",
    "gst_registration": "GST Registration",
}


def load_raw_text(topic_key: str) -> str:
    path = os.path.join(RAW_DIR, f"{topic_key}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw file not found: {path}. Run scraper.py first.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_source_url(topic_key: str) -> str:
    """Read the SOURCE line that scraper.py wrote at the top of each txt file."""
    try:
        text = load_raw_text(topic_key)
        for line in text.splitlines():
            if line.startswith("SOURCE:"):
                return line.replace("SOURCE:", "").strip()
    except Exception:
        pass
    return ""


def call_groq(prompt: str) -> str:
    """Send a prompt to Groq and return the response text."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_card_data(topic_key: str, display_name: str) -> dict:
    """Generate all card data for one topic using Groq."""
    print(f"\n{'='*50}")
    print(f"Generating: {display_name}")

    raw_text = load_raw_text(topic_key)
    context = raw_text[:4000]

    prompt = f"""You are a legal information expert helping ordinary Indian citizens understand the law.

Based on the following legal text about the {display_name}, generate structured information.

Return ONLY valid JSON — no explanation, no markdown, no code fences. Just raw JSON.

The JSON must follow this exact structure:
{{
  "card_description": "A 1-2 sentence plain English description of what this law is about. Max 40 words.",
  "summary": "A plain English summary of this law for non-lawyers. Max 250 words. Use simple language anyone can understand.",
  "key_rights": [
    "Right 1 in simple language",
    "Right 2 in simple language",
    "Right 3 in simple language",
    "Right 4 in simple language"
  ],
  "important_provisions": [
    "Provision 1 explained simply",
    "Provision 2 explained simply",
    "Provision 3 explained simply"
  ],
  "penalties": [
    "Penalty 1 with consequences",
    "Penalty 2 with consequences",
    "Penalty 3 with consequences"
  ],
  "who_can_benefit": [
    "Group 1",
    "Group 2",
    "Group 3"
  ]
}}

Legal text:
{context}
"""

    print("  Calling Groq API...")
    raw_response = call_groq(prompt)

    try:
        clean = raw_response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        card_data = json.loads(clean)
        print(f"  [OK] Generated card data for {display_name}")
        return card_data

    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse JSON for {display_name}: {e}")
        print(f"  Raw response: {raw_response[:300]}")
        return {}


def generate_all_cards():
    os.makedirs("data", exist_ok=True)
    all_cards = {}

    for topic_key, display_name in TOPICS.items():
        try:
            card_data = generate_card_data(topic_key, display_name)
            if card_data:
                all_cards[topic_key] = {
                    "topic_key": topic_key,
                    "display_name": display_name,
                    "source_url": extract_source_url(topic_key),   # ← citation
                    **card_data,
                }
        except FileNotFoundError as e:
            print(f"  [SKIP] {e}")
        except Exception as e:
            print(f"  [ERROR] Unexpected error for {topic_key}: {e}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"GENERATION COMPLETE — {len(all_cards)}/5 topics generated")
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_all_cards()
