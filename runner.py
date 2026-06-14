"""
Usage:
    python run.py            # full pipeline + launch app
    python run.py --reset    # force re-run pipeline even if data exists
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

CARDS_PATH = "data/cards.json"
RAW_DIR = "data/raw"
INDEX_DIR = "data/faiss_index"


def already_done(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 0


def run_step(label: str, script: str):
    print(f"\n{'─'*50}")
    print(f"  ▶  {label}")
    print(f"{'─'*50}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\n  ✖  {label} failed. Fix the error above and re-run.")
        sys.exit(1)
    print(f"  ✔  {label} done.")


def main():
    parser = argparse.ArgumentParser(description="LegalX AI Knowledge Centre launcher")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Force re-run all pipeline steps even if data already exists",
    )
    args = parser.parse_args()

    print("\n" + "═" * 50)
    print("  ⚖️   LegalX AI Knowledge Centre")
    print("═" * 50)

    # ── Step 1: Scrape ─────────────────────────────────────
    raw_files_exist = (
        any(Path(RAW_DIR).glob("*.txt")) if os.path.exists(RAW_DIR) else False
    )

    if args.reset or not raw_files_exist:
        run_step("Step 1/3 — Fetching legal data", "pipeline/scraper.py")
    else:
        print(f"\n  ✔  Step 1/3 — Raw data already exists, skipping scraper.")

    # ── Step 2: Process (FAISS index) ──────────────────────
    index_exists = os.path.exists(INDEX_DIR) and any(Path(INDEX_DIR).iterdir())

    if args.reset or not index_exists:
        run_step("Step 2/3 — Building search indexes", "pipeline/processor.py")
    else:
        print(f"  ✔  Step 2/3 — FAISS indexes already exist, skipping processor.")

    # ── Step 3: Generate cards ─────────────────────────────
    if args.reset or not already_done(CARDS_PATH):
        run_step("Step 3/3 — Generating AI summaries", "pipeline/generator.py")
    else:
        print(f"  ✔  Step 3/3 — cards.json already exists, skipping generator.")

    # ── Launch Streamlit ───────────────────────────────────
    print("\n" + "═" * 50)
    print("  🚀  Launching Streamlit app...")
    print("  📎  Open http://localhost:8501 in your browser")
    print("═" * 50 + "\n")

    subprocess.run(["streamlit", "run", "app.py"])


if __name__ == "__main__":
    main()
