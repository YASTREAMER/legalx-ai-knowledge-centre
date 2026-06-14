import streamlit as st
import tempfile
import json
import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

load_dotenv()

# Page config — must be the very first Streamlit call
st.set_page_config(
    page_title="LegalX AI Knowledge Centre",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Add project root to path so pipeline imports work
sys.path.insert(0, str(Path(__file__).parent))

CARDS_PATH = "data/cards.json"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOPIC_ICONS = {
    "pocso_act": "🛡️",
    "consumer_protection_act": "🛒",
    "cyber_crime_laws": "💻",
    "rti_act": "📋",
    "gst_registration": "🧾",
}

SUGGESTED_QUESTIONS = {
    "pocso_act": [
        "What is the punishment under POCSO?",
        "Who can file a POCSO complaint?",
        "What is mandatory reporting under POCSO?",
    ],
    "consumer_protection_act": [
        "What are my rights as a consumer?",
        "How do I file a consumer complaint?",
        "What is the time limit to file a complaint?",
    ],
    "cyber_crime_laws": [
        "What is cyber fraud?",
        "How do I report cybercrime in India?",
        "What are the penalties for hacking?",
    ],
    "rti_act": [
        "Who can file an RTI?",
        "How do I apply for RTI?",
        "What is the time limit for RTI response?",
    ],
    "gst_registration": [
        "Who needs to register for GST?",
        "What is the GST threshold limit?",
        "How do I apply for GST registration?",
    ],
}


# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────


def inject_css():
    st.markdown(
        """
    <style>
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { background-color: #07111F; }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ── Hero ── */
    .hero {
        background: linear-gradient(135deg, #0F1C2E 0%, #162744 100%);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        margin-bottom: 2.5rem;
        border-left: 5px solid #F59E0B;
    }
    .hero h1 {
        color: #E8EDF5;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    .hero p { color: #94A3B8; font-size: 1.05rem; margin: 0; }
    .hero span { color: #F59E0B; }

    /* ── Section label ── */
    .section-label {
        color: #F59E0B;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* ── Topic card ── */
    .topic-card {
        background: #0F1C2E;
        border: 1px solid #1E3A5F;
        border-radius: 14px;
        padding: 1.6rem;
        margin-bottom: 0.5rem;
        min-height: 190px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .card-title { color: #E8EDF5; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.5rem; }
    .card-desc { color: #94A3B8; font-size: 0.87rem; line-height: 1.55; }

    /* ── Topic title bar ── */
    .topic-title-bar {
        background: #0F1C2E;
        border-radius: 12px;
        padding: 1.4rem 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #F59E0B;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .topic-title-bar .t-icon { font-size: 2rem; }
    .topic-title-bar h2 { color: #E8EDF5; margin: 0; font-size: 1.6rem; font-weight: 700; }

    /* ── Summary box ── */
    .summary-box {
        background: #0F1C2E;
        border-radius: 12px;
        padding: 1.8rem;
        border-left: 4px solid #F59E0B;
        color: #C8D6E8;
        line-height: 1.85;
        font-size: 0.97rem;
        margin-bottom: 1.5rem;
    }

    /* ── Info item (bullet) ── */
    .info-item {
        background: #0F1C2E;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.6rem;
        border: 1px solid #1E3A5F;
        color: #C8D6E8;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .info-item::before { content: "→ "; color: #F59E0B; font-weight: bold; }

    /* ── Chat bubbles ── */
    .chat-q {
        background: #162744;
        border-radius: 10px 10px 2px 10px;
        padding: 0.85rem 1.2rem;
        color: #E8EDF5;
        margin: 0.5rem 0 0.5rem 3rem;
        font-size: 0.93rem;
    }
    .chat-a {
        background: #0F1C2E;
        border: 1px solid #1E3A5F;
        border-radius: 10px 10px 10px 2px;
        padding: 0.85rem 1.2rem;
        color: #C8D6E8;
        margin-bottom: 1rem;
        font-size: 0.93rem;
        line-height: 1.75;
    }
    .chat-empty {
        color: #94A3B8;
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }

    /* ── Buttons ── */
    .stButton > button {
        background-color: #F59E0B !important;
        color: #07111F !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.2rem !important;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #D97706 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0F1C2E;
        border-radius: 10px;
        padding: 0.3rem;
        gap: 0.3rem;
        margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #F59E0B !important;
        color: #07111F !important;
    }

    /* ── Expander ── */
    details { border-radius: 10px !important; overflow: hidden; margin-bottom: 0.5rem; }
    summary {
        background: #0F1C2E !important;
        color: #E8EDF5 !important;
        font-weight: 600 !important;
        padding: 0.8rem 1rem !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 10px !important;
    }

    /* ── Audio ── */
    audio { width: 100%; border-radius: 8px; margin-top: 0.5rem; }

    /* ── Error / info box ── */
    .setup-box {
        background: #0F1C2E;
        border: 1px solid #F59E0B;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        color: #94A3B8;
        font-size: 0.93rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────


@st.cache_data
def load_cards() -> dict:
    if not os.path.exists(CARDS_PATH):
        return {}
    with open(CARDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource
def load_vectorstore(topic_key: str):
    """Load FAISS index once and cache it for the session."""
    try:
        from pipeline.processor import load_index

        return load_index(topic_key)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Audio
# ─────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def generate_audio(text: str) -> bytes:
    tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.getvalue()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Send recorded audio to Groq Whisper and return transcribed text."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=("audio.mp3", f, "audio/mpeg"),
                model="whisper-large-v3",
            )
        return transcription.text.strip()
    finally:
        os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────────
# RAG + Groq Q&A
# ─────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def answer_question(topic_key: str, display_name: str, question: str) -> str:
    context = ""
    vectorstore = load_vectorstore(topic_key)

    if vectorstore:
        docs = vectorstore.similarity_search(question, k=4)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

    if context:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a legal assistant helping ordinary Indian citizens understand the {display_name}. "
                    "Answer ONLY using the context provided. Use simple, plain English. "
                    "If the answer is not in the context, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a legal assistant helping ordinary Indian citizens understand the {display_name}. "
                    "Use simple, plain English. Be accurate and concise."
                ),
            },
            {"role": "user", "content": question},
        ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────
# Home page
# ─────────────────────────────────────────────────────────────


def render_home(cards: dict):
    st.markdown(
        """
    <div class="hero">
        <h1>⚖️ LegalX <span>AI Knowledge Centre</span></h1>
        <p>Understand Indian law in plain English — powered by AI</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not cards:
        st.markdown(
            """
        <div class="setup-box">
            <b style="color:#F59E0B">⚠️ No data found.</b><br><br>
            Run the pipeline to get started:<br>
            <code>python pipeline/scraper.py</code><br>
            <code>python pipeline/processor.py</code><br>
            <code>python pipeline/generator.py</code>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<p class="section-label">Browse Legal Topics</p>', unsafe_allow_html=True
    )

    topics = list(cards.items())

    # Row 1: 3 cards
    cols = st.columns(3, gap="medium")
    for i, (topic_key, card) in enumerate(topics[:3]):
        with cols[i]:
            icon = TOPIC_ICONS.get(topic_key, "📄")
            st.markdown(
                f"""
            <div class="topic-card">
                <div>
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{card['display_name']}</div>
                    <div class="card-desc">{card.get('card_description', '')}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button("Read More →", key=f"card_{topic_key}"):
                st.session_state.current_topic = topic_key
                st.session_state[f"chat_{topic_key}"] = []
                st.rerun()

    # Row 2: remaining cards centered
    remaining = topics[3:]
    if remaining:
        pad = (3 - len(remaining)) // 2
        cols2 = st.columns(3, gap="medium")
        for i, (topic_key, card) in enumerate(remaining):
            with cols2[pad + i]:
                icon = TOPIC_ICONS.get(topic_key, "📄")
                st.markdown(
                    f"""
                <div class="topic-card">
                    <div>
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{card['display_name']}</div>
                        <div class="card-desc">{card.get('card_description', '')}</div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                if st.button("Read More →", key=f"card_{topic_key}"):
                    st.session_state.current_topic = topic_key
                    st.session_state[f"chat_{topic_key}"] = []
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# Topic detail page
# ─────────────────────────────────────────────────────────────


def render_topic(topic_key: str, card: dict):
    icon = TOPIC_ICONS.get(topic_key, "📄")
    display_name = card["display_name"]

    if st.button("← Back to Topics"):
        st.session_state.current_topic = None
        st.rerun()

    st.markdown(
        f"""
    <div class="topic-title-bar">
        <span class="t-icon">{icon}</span>
        <h2>{display_name}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        ["📄  Summary & Audio", "🔑  Key Information", "💬  Ask a Question"]
    )

    # ── Tab 1: Summary & Audio ─────────────────────────────────
    with tab1:
        summary = card.get("summary", "Summary not available.")

        st.markdown(
            '<p class="section-label">AI-Generated Summary</p>', unsafe_allow_html=True
        )
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

        # Source citation
        source_url = card.get("source_url", "")
        if source_url:
            st.markdown(
                f"""<p style="color:#94A3B8;font-size:0.8rem;margin-top:0.6rem;">
                📎 Source: <a href="{source_url}" target="_blank" style="color:#F59E0B;">{source_url}</a>
                </p>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p class="section-label">Audio Summary</p>', unsafe_allow_html=True
        )

        audio_key = f"audio_{topic_key}"

        if audio_key not in st.session_state:
            if st.button("🔊 Generate Audio", key="gen_audio"):
                with st.spinner("Generating audio..."):
                    st.session_state[audio_key] = generate_audio(summary)
                st.rerun()
        else:
            st.audio(st.session_state[audio_key], format="audio/mp3")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="⬇️ Download Audio",
                    data=st.session_state[audio_key],
                    file_name=f"{topic_key}_summary.mp3",
                    mime="audio/mp3",
                    key="dl_audio",
                )
            with col2:
                if st.button("🔄 Regenerate", key="regen_audio"):
                    del st.session_state[audio_key]
                    st.rerun()

    # ── Tab 2: Key Information ─────────────────────────────────
    with tab2:
        sections = [
            ("⚡  Key Rights", card.get("key_rights", [])),
            ("📌  Important Provisions", card.get("important_provisions", [])),
            ("⚠️  Penalties", card.get("penalties", [])),
            ("👥  Who Can Benefit", card.get("who_can_benefit", [])),
        ]

        for title, items in sections:
            with st.expander(title, expanded=True):
                if items:
                    for item in items:
                        st.markdown(
                            f'<div class="info-item">{item}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        '<p style="color:#94A3B8;font-size:0.9rem">No data available.</p>',
                        unsafe_allow_html=True,
                    )

    # ── Tab 3: Q&A Chat ────────────────────────────────────────
    with tab3:
        chat_key = f"chat_{topic_key}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        # Display chat history
        for msg in st.session_state[chat_key]:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-q">🧑&nbsp;&nbsp;{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-a">⚖️&nbsp;&nbsp;{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

        # Suggested questions (only shown when chat is empty)
        if not st.session_state[chat_key]:
            st.markdown(
                '<p class="chat-empty">Not sure where to start? Try one of these:</p>',
                unsafe_allow_html=True,
            )
            suggestions = SUGGESTED_QUESTIONS.get(topic_key, [])
            sq_cols = st.columns(len(suggestions))
            for i, q in enumerate(suggestions):
                with sq_cols[i]:
                    if st.button(q, key=f"sq_{topic_key}_{i}"):
                        st.session_state[chat_key].append(
                            {"role": "user", "content": q}
                        )
                        with st.spinner("Thinking..."):
                            ans = answer_question(topic_key, display_name, q)
                        st.session_state[chat_key].append(
                            {"role": "assistant", "content": ans}
                        )
                        st.rerun()

        # ── Speech-to-Text ──────────────────────────────────
        st.markdown(
            '<p class="section-label" style="margin-top:1.2rem">🎙️ Ask by Voice</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="color:#94A3B8;font-size:0.82rem;margin-bottom:0.5rem">Record your question — it will be transcribed and answered automatically.</p>',
            unsafe_allow_html=True,
        )
        audio_file = st.file_uploader(
            "Upload an audio file with your question (wav, mp3, m4a)",
            type=["wav", "mp3", "m4a"],
            key=f"audio_upload_{topic_key}",
        )
        if audio_file:
            with st.spinner("Transcribing your question..."):
                transcribed = transcribe_audio(audio_file.read())
            if transcribed:
                st.markdown(
                    f'<p style="color:#F59E0B;font-size:0.88rem;">🎤 Heard: <em>"{transcribed}"</em></p>',
                    unsafe_allow_html=True,
                )
                st.session_state[chat_key].append(
                    {"role": "user", "content": transcribed}
                )
                with st.spinner("Thinking..."):
                    ans = answer_question(topic_key, display_name, transcribed)
                st.session_state[chat_key].append({"role": "assistant", "content": ans})
                st.rerun()
        # ── Free-text input ──────────────────────────────────
        user_input = st.chat_input(f"Ask anything about the {display_name}…")
        if user_input:
            st.session_state[chat_key].append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                ans = answer_question(topic_key, display_name, user_input)
            st.session_state[chat_key].append({"role": "assistant", "content": ans})
            st.rerun()


# ─────────────────────────────────────────────────────────────
# Auto Setup Screen
# ─────────────────────────────────────────────────────────────


def render_setup():
    """Shown on first launch when no data exists. Runs the full pipeline automatically."""
    st.markdown(
        """
    <div class="hero">
        <h1>⚖️ LegalX <span>AI Knowledge Centre</span></h1>
        <p>First-time setup — fetching and processing legal data automatically</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="summary-box">
        No legal data found. Click <b>Run Setup</b> to automatically:<br><br>
        &nbsp;&nbsp;📥 &nbsp;Fetch legal content from Wikipedia<br>
        &nbsp;&nbsp;🔧 &nbsp;Build AI search indexes (FAISS + embeddings)<br>
        &nbsp;&nbsp;🤖 &nbsp;Generate summaries and key information using Groq<br><br>
        This runs once and takes about 2–3 minutes.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Run Automated Setup", key="run_setup"):
        with st.status("⚙️ Running automated pipeline...", expanded=True) as status:

            st.write("📥 Step 1/3 — Fetching legal data from Wikipedia...")
            try:
                from pipeline.scraper import scrape_all_topics

                scrape_all_topics()
                st.write("✅ Legal data fetched successfully.")
            except Exception as e:
                st.error(f"Scraper failed: {e}")
                status.update(label="Setup failed at Step 1", state="error")
                return

            st.write("🔧 Step 2/3 — Building FAISS search indexes...")
            try:
                from pipeline.processor import build_all_indexes

                build_all_indexes()
                st.write("✅ Search indexes built successfully.")
            except Exception as e:
                st.error(f"Processor failed: {e}")
                status.update(label="Setup failed at Step 2", state="error")
                return

            st.write("🤖 Step 3/3 — Generating AI summaries with Groq...")
            try:
                from pipeline.generator import generate_all_cards

                generate_all_cards()
                st.write("✅ AI content generated successfully.")
            except Exception as e:
                st.error(f"Generator failed: {e}")
                status.update(label="Setup failed at Step 3", state="error")
                return

            status.update(
                label="✅ Setup complete! Loading Knowledge Centre...", state="complete"
            )

        # Clear cache so load_cards() picks up the new file
        load_cards.clear()
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Main router
# ─────────────────────────────────────────────────────────────


def main():
    inject_css()

    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None

    cards = load_cards()

    if not cards:
        st.markdown(
            """
        <div class="hero">
            <h1>⚖️ LegalX <span>AI Knowledge Centre</span></h1>
        </div>
        <div class="summary-box">
            ⚠️ No data found. Start the app using:<br><br>
            <code>python run.py</code>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    if st.session_state.current_topic is None:
        render_home(cards)
    else:
        topic_key = st.session_state.current_topic
        if topic_key in cards:
            render_topic(topic_key, cards[topic_key])
        else:
            st.error("Topic not found.")
            st.session_state.current_topic = None
            st.rerun()


if __name__ == "__main__":
    main()
