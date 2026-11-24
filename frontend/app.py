import os
import streamlit as st
import requests


# Step 1: Configure page
st.set_page_config(
    page_title="Spotify AI Assistant",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Step 2: Spotify dark theme
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 85% 15%, #153c2d, transparent 45%),
        linear-gradient(135deg, #081310, #101e23);
    color: #F5FFF8;
}

.block-container {
    max-width: 900px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

h1, h2, h3, h4, p, label {
    color: #F5FFF8 !important;
}

h1 {
    font-size: 2rem !important;
}

[data-testid="stCaptionContainer"] {
    color: #A9C5B5 !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    width: 100% !important;
    min-height: 46px !important;
    background: #18382B !important;
    color: white !important;
    border: 1px solid #286849 !important;
    border-radius: 10px !important;
    white-space: normal !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #1DB954 !important;
    color: #07150C !important;
}


/* RAG mode selector */
div[data-testid="stSelectbox"] label {
    color: #F5FFF8 !important;
}

/* Dropdown background and selected text */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #172A2A !important;
    border: 1px solid #286849 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* Selected option */
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Dropdown arrow */
div[data-testid="stSelectbox"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
}

/* Dropdown menu options */
div[data-baseweb="popover"] [role="option"] {
    color: #FFFFFF !important;
    background-color: #172A2A !important;
}

/* Highlight selected option */
div[data-baseweb="popover"] [aria-selected="true"] {
    background-color: #286849 !important;
    color: #FFFFFF !important;
}

/* Scrollable chat container */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
}

/* Chat message cards */
[data-testid="stChatMessage"] {
    background: #172A2A !important;
    border: 1px solid #25463A !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin-bottom: 8px !important;
}

/* Readable chat answers */
[data-testid="stChatMessage"],
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
    color: #F5FFF8 !important;
}

/* Question input */
[data-testid="stTextInput"] input {
    background: #172A2A !important;
    color: white !important;
    border: 1px solid #28764E !important;
    border-radius: 10px !important;
    min-height: 46px !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #A9C5B5 !important;
}

/* Floating music notes */
.music-note {
    position: fixed;
    color: #1DB954;
    opacity: 0.10;
    font-size: 30px;
    pointer-events: none;
    z-index: 0;
    animation: floatMusic 14s linear infinite;
}

.note1 {
    left: 7%;
    bottom: -10%;
    animation-delay: 0s;
}

.note2 {
    left: 23%;
    bottom: -10%;
    animation-delay: 4s;
}

.note3 {
    left: 75%;
    bottom: -10%;
    animation-delay: 7s;
}

.note4 {
    left: 92%;
    bottom: -10%;
    animation-delay: 10s;
}

@keyframes floatMusic {
    0% {
        transform: translateY(0) rotate(0deg);
        opacity: 0;
    }
    20%, 80% {
        opacity: 0.10;
    }
    100% {
        transform: translateY(-110vh) rotate(25deg);
        opacity: 0;
    }
}

@media (prefers-reduced-motion: reduce) {
    .music-note {
        animation: none;
    }
}

hr {
    border-color: #25463A !important;
}
</style>

<div class="music-note note1">♫</div>
<div class="music-note note2">♪</div>
<div class="music-note note3">♬</div>
<div class="music-note note4">♫</div>
""", unsafe_allow_html=True)


# Step 3: Header
st.title("🎵 Spotify AI Assistant")
st.caption("Your Music Technology Companion | Powered by RAG")


# Step 4: Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Step 5: Select RAG mode
rag_mode = st.selectbox(
    "Choose Retrieval Mode",
    ["Hybrid RAG", "Vector RAG", "Graph RAG"],
    help="Choose how Spotify architecture information is retrieved."
)

st.caption({
    "Hybrid RAG": "Searches both PDF content and Neo4j relationships.",
    "Vector RAG": "Searches PDF content using FAISS.",
    "Graph RAG": "Searches relationships stored in Neo4j."
}[rag_mode])


# Step 6: FAQ questions
st.subheader("Frequently Asked Questions")

faqs = [
    "What database stores user information?",
    "How does Spotify manage playlists?",
    "What technologies power the frontend?",
    "What does the Media Processor Service do?"
]

selected_question = None
cols = st.columns(2, gap="small")

for i, faq in enumerate(faqs):
    with cols[i % 2]:
        if st.button(faq, key=f"faq_{i}", use_container_width=True):
            selected_question = faq

st.divider()


# Step 7: Scrollable chat section
st.subheader("Chat with Spotify AI")

chat_area = st.container(height=380, border=True)

with chat_area:
    if not st.session_state.messages and not selected_question:
        st.markdown(
            "🎵 **Welcome!** Ask a Spotify architecture question "
            "or select an FAQ above to get started."
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Step 8: Question input and Ask button
with st.form("question_form", clear_on_submit=True):
    input_col, button_col = st.columns([5, 1], gap="small")

    with input_col:
        typed_question = st.text_input(
            "Your question",
            placeholder="Ask about Spotify architecture...",
            label_visibility="collapsed"
        )

    with button_col:
        submitted = st.form_submit_button(
            "Ask",
            use_container_width=True
        )

question = selected_question or (
    typed_question if submitted else None
)


# Step 9: Call FastAPI with selected mode
if question and question.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with chat_area:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Spotify architecture..."):
                try:
                    response = requests.post(
                        os.getenv("BACKEND_URL", "http://127.0.0.1:8000") + "/ask",
                        json={
                            "question": question,
                            "mode": rag_mode
                        },
                        timeout=120
                    )

                    response.raise_for_status()
                    answer = response.json()["answer"]

                except requests.RequestException:
                    answer = (
                        "Unable to connect to the backend. "
                        "Please check whether FastAPI is running."
                    )

                except (ValueError, KeyError):
                    answer = "The backend returned an unexpected response."

            st.markdown(answer)

    # Save answer and retrieval mode in chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()


# Step 10: Clear chat history
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
