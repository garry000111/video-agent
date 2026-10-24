"""
AI Video Assistant — Streamlit UI
Run:  streamlit run app.py
Expects your pipeline file (main.py) with run_pipeline() and core.rag_engine.ask_question().
"""
import os
import tempfile

import streamlit as st

from main import run_pipeline            # your existing pipeline file
from core.rag_engine import ask_question

# ───────────────────────── Page setup ─────────────────────────
st.set_page_config(
    page_title="Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root{
  --ink:#10243E; --muted:#5B6B80; --line:#D9E1EC; --paper:#F3F6FA; --card:#FFFFFF;
  --teal:#0E7C86; --teal-soft:#DDF1F2; --amber:#F2A33A; --amber-soft:#FDF0D9;
}
html, body, [class*="css"], .stApp { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:var(--paper); }
#MainMenu, footer, .stDeployButton{ visibility:hidden; }
/* Keep the header (it holds the sidebar expand button) but make it blend in */
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="collapsedControl"], [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"]{
  visibility:visible !important; color:var(--ink) !important;
}
[data-testid="collapsedControl"] *, [data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] *{
  color:var(--ink) !important; fill:var(--ink) !important;
}
.block-container{ padding-top:3.5rem; padding-bottom:4rem; max-width:1180px; }

h1,h2,h3,.display{ font-family:'Bricolage Grotesque',sans-serif !important; letter-spacing:-0.01em; color:var(--ink); }

/* Sidebar */
section[data-testid="stSidebar"]{ background:var(--ink); }
section[data-testid="stSidebar"] *{ color:#E8EEF6 !important; }
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea{ color:var(--ink) !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] *{ color:var(--ink) !important; }
section[data-testid="stSidebar"] .stButton>button{
  background:var(--amber); color:#2A1B00 !important; border:0; font-weight:600; width:100%;
  border-radius:10px; padding:.65rem 1rem;
}
section[data-testid="stSidebar"] .stButton>button:hover{ filter:brightness(1.06); }
.brand{ font-family:'Bricolage Grotesque'; font-weight:800; font-size:1.45rem; margin-bottom:.1rem; }
.brand-sub{ color:#9FB2C8 !important; font-size:.88rem; margin-bottom:1.2rem; }

/* Hero (idle state) */
.hero{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:2.4rem 2rem; }
.hero h1{ font-size:clamp(1.8rem,4.5vw,3rem); line-height:1.08; margin:0 0 .6rem; font-weight:800; }
.hero p{ color:var(--muted); font-size:1.05rem; max-width:56ch; margin:0 0 1.2rem; }
.steps{ display:flex; gap:.6rem; flex-wrap:wrap; }
.step{ background:var(--teal-soft); color:var(--teal); border-radius:999px; padding:.35rem .9rem; font-weight:600; font-size:.88rem; }

/* Result header */
.result-head{ background:var(--ink); color:#fff; border-radius:20px; padding:1.6rem 1.8rem; margin-bottom:1rem; }
.result-head h1{ color:#fff !important; font-size:clamp(1.4rem,3.4vw,2.1rem); margin:0; font-weight:800; line-height:1.15; }
.result-head small{ color:#9FB2C8; }

/* Stat tiles */
.stat{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.9rem 1.1rem; }
.stat b{ font-family:'Bricolage Grotesque'; font-size:1.7rem; display:block; line-height:1.1; }
.stat span{ color:var(--muted); font-size:.85rem; }
.stat.accent{ border-left:5px solid var(--amber); }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap:.25rem; overflow-x:auto; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{ padding:.55rem .9rem; font-weight:600; color:var(--muted); white-space:nowrap; }
.stTabs [aria-selected="true"]{ color:var(--teal) !important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--teal) !important; }

/* Content panel */
.panel{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.3rem 1.5rem; line-height:1.65; }
.panel.transcript{ max-height:520px; overflow-y:auto; white-space:pre-wrap; font-size:.95rem; }
.empty{ color:var(--muted); font-style:italic; }

/* Chat */
[data-testid="stChatMessage"]{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.8rem 1rem; }
.stButton>button{ border-radius:10px; border:1px solid var(--line); font-weight:500; }
.stButton>button:hover{ border-color:var(--teal); color:var(--teal); }
.stDownloadButton>button{ border-radius:10px; }

/* Mobile */
@media (max-width: 768px){
  .block-container{ padding:1rem .8rem 3rem; }
  .hero{ padding:1.4rem 1.1rem; }
  .result-head{ padding:1.1rem 1.2rem; }
  .panel{ padding:1rem; }
}
@media (prefers-reduced-motion: reduce){ *{ transition:none !important; animation:none !important; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────── Helpers ─────────────────────────
def to_md(value) -> str:
    """Pipeline outputs may be str or list — render both nicely."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(f"- {v}" for v in value)
    return str(value)


def count_items(value) -> int:
    if not value:
        return 0
    if isinstance(value, (list, tuple)):
        return len(value)
    lines = [l for l in str(value).splitlines() if l.strip().startswith(("-", "*", "•")) or l.strip()[:2].rstrip(".").isdigit()]
    return len(lines) or 1


def panel(value, empty_msg: str):
    text = to_md(value).strip()
    if not text or text.lower() in {"none", "none found", "n/a"}:
        st.markdown(f'<div class="panel empty">{empty_msg}</div>', unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(text)


def build_report(r: dict) -> str:
    return (
        f"# {r['title']}\n\n## Summary\n{to_md(r['summary'])}\n\n"
        f"## Action items\n{to_md(r['action_items'])}\n\n"
        f"## Key decisions\n{to_md(r['key_decisions'])}\n\n"
        f"## Open questions\n{to_md(r['open_questions'])}\n"
    )


# ───────────────────────── State ─────────────────────────
st.session_state.setdefault("result", None)
st.session_state.setdefault("messages", [])

# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">🎬 Video Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Summaries and answers from any video or recording.</div>', unsafe_allow_html=True)

    mode = st.radio("Source", ["YouTube link", "Upload file"], horizontal=True, label_visibility="collapsed")
    url, upload = "", None
    if mode == "YouTube link":
        url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    else:
        upload = st.file_uploader(
            "Video or audio file",
            type=["mp4", "mkv", "mov", "avi", "webm", "mp3", "wav", "m4a"],
        )

    language = st.selectbox("Spoken language", ["english", "hinglish"])
    go = st.button("Analyze video", type="primary")

    if st.session_state.result:
        st.divider()
        if st.button("Start over"):
            st.session_state.result = None
            st.session_state.messages = []
            st.rerun()

# ───────────────────────── Run pipeline ─────────────────────────
if go:
    source = None
    if mode == "YouTube link":
        if not url.strip():
            st.sidebar.error("Paste a YouTube link first.")
        else:
            source = url.strip()
    else:
        if upload is None:
            st.sidebar.error("Choose a file to upload.")
        else:
            suffix = os.path.splitext(upload.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(upload.getbuffer())
                source = tmp.name

    if source:
        with st.status("Analyzing your video…", expanded=True) as status:
            st.write("Downloading and splitting audio, transcribing speech, then writing the summary. Long videos can take a few minutes.")
            try:
                st.session_state.result = run_pipeline(source, language)
                st.session_state.messages = []
                status.update(label="Analysis complete", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Something went wrong", state="error")
                st.error(f"Could not process this video: {e}")

# ───────────────────────── Idle state ─────────────────────────
result = st.session_state.result
if not result:
    st.markdown(
        """
        <div class="hero">
          <h1>Watch less. Know more.</h1>
          <p>Add a YouTube link or upload a recording. You get a summary, action items, decisions and open
             questions, and you can ask the video anything afterwards.</p>
          <div class="steps">
            <span class="step">Add a video</span>
            <span class="step">Read the summary</span>
            <span class="step">Ask questions</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ───────────────────────── Results ─────────────────────────
st.markdown(
    f'<div class="result-head"><small>Video analysis</small><h1>{result["title"]}</h1></div>',
    unsafe_allow_html=True,
)

words = len(result["transcript"].split())
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stat accent"><b>{words:,}</b><span>words transcribed</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stat"><b>{count_items(result["action_items"])}</b><span>action items</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stat"><b>{count_items(result["key_decisions"])}</b><span>key decisions</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stat"><b>{count_items(result["open_questions"])}</b><span>open questions</span></div>', unsafe_allow_html=True)

st.write("")
tab_sum, tab_act, tab_dec, tab_q, tab_tr, tab_chat = st.tabs(
    ["Summary", "Action items", "Decisions", "Open questions", "Transcript", "Ask the video"]
)

with tab_sum:
    panel(result["summary"], "No summary was generated.")
    st.download_button("Download report (.md)", build_report(result), file_name="video_report.md", mime="text/markdown")

with tab_act:
    panel(result["action_items"], "No action items were found in this video.")

with tab_dec:
    panel(result["key_decisions"], "No key decisions were found in this video.")

with tab_q:
    panel(result["open_questions"], "No open questions were found in this video.")

with tab_tr:
    st.markdown(f'<div class="panel transcript">{result["transcript"]}</div>', unsafe_allow_html=True)
    st.download_button("Download transcript (.txt)", result["transcript"], file_name="transcript.txt")

with tab_chat:
    def answer(q: str):
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            a = ask_question(result["rag_chain"], q)
        except Exception as e:
            a = f"I couldn't answer that: {e}"
        st.session_state.messages.append({"role": "assistant", "content": str(a)})

    if not st.session_state.messages:
        st.markdown("Try one of these, or type your own question below.")
        s1, s2, s3 = st.columns(3)
        for col, q in zip(
            (s1, s2, s3),
            ("What is this video about?", "What are the main takeaways?", "Who is speaking and what do they decide?"),
        ):
            if col.button(q, use_container_width=True):
                with st.spinner("Thinking…"):
                    answer(q)
                st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask anything about this video…"):
        with st.spinner("Searching the transcript…"):
            answer(prompt)
        st.rerun()