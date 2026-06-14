# ⚖️ LegalX AI Knowledge Centre

An AI-powered legal knowledge platform that automatically fetches, processes, and presents Indian legal information in plain English — built for LegalX Round 2 Assessment.

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/YASTREAMER/legalx-ai-knowledge-centre.git
cd legalx-ai-knowledge-centre

# Create and activate conda environment
conda create -n legalx python=3.14.4
conda activate legalx

# Install dependencies
conda env create -f environment.yml

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run everything (pipeline + app) with one command
python run.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📌 Project Overview

LegalX AI Knowledge Centre makes Indian law accessible to ordinary citizens. The system automatically:

- Fetches legal content from public sources (Wikipedia)
- Processes and indexes it using AI embeddings
- Generates plain-English summaries and key information using LLMs
- Provides an AI legal assistant powered by RAG (Retrieval-Augmented Generation)
- Converts summaries to audio for accessibility
- Accepts voice questions via speech-to-text

### Legal Topics Covered

| Topic | Description |
|-------|-------------|
| 🛡️ POCSO Act | Protection of Children from Sexual Offences Act, 2012 |
| 🛒 Consumer Protection Act | Consumer Protection Act, 2019 |
| 💻 Cyber Crime Laws | Information Technology Act, 2000 |
| 📋 RTI Act | Right to Information Act, 2005 |
| 🧾 GST Registration | Goods and Services Tax Registration |

---

## 🏗️ Architecture Design

```
┌─────────────────────────────────────────────────────┐
│                   AUTOMATION PIPELINE                │
│                                                      │
│  Wikipedia API                                       │
│      │                                               │
│      ▼                                               │
│  scraper.py  ──► data/raw/*.txt                      │
│      │                                               │
│      ▼                                               │
│  processor.py ──► FAISS Vector Index                 │
│  (LangChain + sentence-transformers)                 │
│      │                                               │
│      ▼                                               │
│  generator.py ──► data/cards.json                    │
│  (Groq Llama 3.3 70b)                                  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  STREAMLIT APP                       │
│                                                      │
│  Home Page ──► Topic Cards (from cards.json)        │
│      │                                               │
│      ▼                                               │
│  Topic Page                                          │
│  ├── Tab 1: Summary + Audio (gTTS) + Citation       │
│  ├── Tab 2: Key Rights, Provisions, Penalties       │
│  └── Tab 3: AI Q&A Chat (RAG + Groq Whisper STT)   │
└─────────────────────────────────────────────────────┘
```

---

## 🤖 AI Models Used

| Model | Provider | Used For |
|-------|----------|----------|
| `llama-3.3-70b-versatile` | Groq | Summary generation, key info extraction, Q&A |
| `whisper-large-v3` | Groq | Speech-to-text transcription |
| `all-MiniLM-L6-v2` | HuggingFace (local) | Text embeddings for RAG |

---

## 🛠️ Technologies Used

| Category | Technology |
|----------|------------|
| **Frontend** | Streamlit |
| **LLM Framework** | LangChain |
| **Vector Database** | FAISS |
| **Embeddings** | sentence-transformers |
| **LLM API** | Groq |
| **Audio (TTS)** | gTTS (Google Text-to-Speech) |
| **Audio (STT)** | Groq Whisper |
| **Web Scraping** | requests, BeautifulSoup4 |
| **Language** | Python 3.11 |

---

## ⚙️ Automation Pipeline Explained

The entire pipeline runs automatically with a single command (`python run.py`). Here's what happens under the hood:

### Step 1 — Scraper (`pipeline/scraper.py`)
Fetches raw legal content for all 5 topics from the Wikipedia API using structured queries. Saves plain text to `data/raw/<topic>.txt` along with the source URL for citations. No manual content — fully automated.

### Step 2 — Processor (`pipeline/processor.py`)
Loads each raw text file and splits it into overlapping 800-character chunks using LangChain's `RecursiveCharacterTextSplitter`. Each chunk is embedded using `sentence-transformers/all-MiniLM-L6-v2` (runs locally, no API cost) and stored in a per-topic FAISS vector index saved to `data/faiss_index/`.

### Step 3 — Generator (`pipeline/generator.py`)
Sends the first 4000 characters of each topic's text to Groq's LLaMA 3 70B model with a structured JSON prompt. The model returns a card description, 250-word plain-English summary, key rights, important provisions, penalties, and who can benefit. Results are saved to `data/cards.json`.

### Smart Caching
`run.py` checks if each step's output already exists before running it. Re-running `python run.py` is instant if data is already present. Use `python run.py --reset` to force a full re-run.

---

## ✨ Features

### Core Features
- **Automated Knowledge Cards** — 5 legal topic cards auto-generated from source content
- **AI Summaries** — Plain English summaries (max 250 words) generated by LLaMA 3
- **Key Information Extraction** — Rights, provisions, penalties, and beneficiaries extracted intelligently
- **AI Legal Assistant** — RAG-powered Q&A chat with topic-specific context
- **Audio Summary** — Play and download TTS audio for each summary

### Bonus Features
- ✅ **RAG Implementation** — FAISS similarity search retrieves relevant chunks before answering
- ✅ **Vector Database** — FAISS indexes for all 5 topics
- ✅ **Source Citations** — Wikipedia source URL displayed below each summary
- ✅ **Chat History** — Conversation history maintained throughout the session
- ✅ **Speech-to-Text** — Upload audio questions, transcribed by Groq Whisper
- ✅ **Suggested Questions** — Pre-built topic-specific starter questions

---

## 📁 Project Structure

```
legalx-ai-knowledge-centre/
├── app.py                  # Streamlit app (UI + routing)
├── run.py                  # Single entry point — pipeline + app launcher
├── pipeline/
│   ├── __init__.py
│   ├── scraper.py          # Fetch legal text from Wikipedia API
│   ├── processor.py        # Chunk, embed, build FAISS index
│   └── generator.py        # Generate summaries and card data via Groq
├── data/
│   ├── raw/                # Raw scraped text files (auto-generated)
│   ├── faiss_index/        # FAISS vector indexes per topic (auto-generated)
│   └── cards.json          # Generated card data (auto-generated)
├── requirements.txt
└── .env                    # API keys (not committed)
```

---

## 📦 Requirements

```
streamlit
langchain
langchain-community
langchain-text-splitters
langchain-groq
groq
faiss-cpu
sentence-transformers
beautifulsoup4
requests
gtts
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.11+
- Conda (recommended)
- Groq API key — get one free at [console.groq.com](https://console.groq.com)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YASTREAMER/legalx-ai-knowledge-centre.git
cd legalx-ai-knowledge-centre

# 2. Create conda environment
conda create -n legalx python=3.11
conda activate legalx

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the app (pipeline runs automatically on first launch)
python run.py

# To force re-run the full pipeline
python run.py --reset
```

---

## 🧗 Challenges Faced

1. **indiankanoon.org blocking scrapers** — The primary legal source blocked automated requests with 403 errors. Solved by switching to the Wikipedia API which is open, free, and returns clean structured text.

2. **LangChain module restructuring** — `langchain.text_splitter` was moved to `langchain_text_splitters` in newer versions, causing import errors. Fixed by installing and importing from the correct package.

3. **streamlit-audiorec Python 3.14 incompatibility** — The audio recording component didn't support Python 3.14. Replaced with `st.file_uploader` + Groq Whisper which is more reliable and works across all Python versions.

4. **FAISS index loading** — `allow_dangerous_deserialization=True` flag required for loading saved FAISS indexes in newer LangChain versions.

5. **Groq returning non-JSON responses** — Occasionally the LLM would wrap JSON in markdown code fences. Added a stripping step before `json.loads()` to handle this gracefully.

---

## 🔮 Future Improvements

1. **MongoDB integration** — Store Q&A cache and chat history in MongoDB for persistence across sessions and reduced API calls
2. **Authentication** — User login with personal chat history and bookmarks
3. **Multi-language support** — Hindi and regional language summaries for wider accessibility
4. **Dockerization** — Containerize the full stack for one-command deployment anywhere
5. **More legal topics** — Expand beyond 5 topics to cover IPC, labour laws, property laws
6. **Real-time legal updates** — Periodic pipeline re-runs to keep content current with legislative changes
7. **AI Search** — Cross-topic semantic search across all legal content

---

## 👤 Author

**Yash (Priyanshu Arya)**  
BS-MS Physics, IIT Roorkee  
[GitHub](https://github.com/YASTREAMER)

---

*Built for LegalX AI/ML Internship — Round 2 Assessment, June 2026*
