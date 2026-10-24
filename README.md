<p align="center">
  <img src="docs/banner.svg" alt="AI Video Agent" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/LLM-Mistral-F2A33A" alt="Mistral">
  <img src="https://img.shields.io/badge/STT-Whisper-412991" alt="Whisper">
  <img src="https://img.shields.io/badge/RAG-LangChain%20%2B%20ChromaDB-0E7C86" alt="LangChain + ChromaDB">
</p>

# 🎬 AI Video Agent

> **Watch less. Know more.**
> Paste a YouTube link or upload a recording. Get a transcript, a summary, action items, key decisions and open questions, then **chat with the video** to ask anything about it.

AI Video Agent turns long videos, meetings and recordings into structured, searchable knowledge. Speech is transcribed locally with Whisper, analysed by a Mistral LLM through LangChain, and indexed in a ChromaDB vector store so you can ask follow-up questions in plain language.

---

## ✨ Features

- **Two input modes**: YouTube URL or file upload (`mp4`, `mkv`, `mov`, `avi`, `webm`, `mp3`, `wav`, `m4a`).
- **Local speech-to-text** using OpenAI Whisper, so your audio is not sent to a transcription API.
- **English and Hinglish support**: Hinglish audio is handled and translated to English text.
- **Auto-generated insights**:
  - 📌 Video title
  - 📝 Summary
  - ✅ Action items
  - 🔑 Key decisions
  - ❓ Open questions
- **Ask the video**: a RAG chatbot answers questions using only the transcript, with one-click starter questions.
- **Stat tiles** showing words transcribed and counts of action items, decisions and questions.
- **Downloads**: export the full report (`.md`) and the transcript (`.txt`).
- **Two interfaces**: a polished Streamlit web app and a command-line mode.

---

## 🖼️ Screenshots

<!--
  Add your own screenshots to docs/screenshots/ and uncomment the lines below.
  Suggested shots: the landing page, the results page with stat tiles, and the "Ask the video" tab.

<p align="center">
  <img src="docs/screenshots/home.png" alt="Landing page" width="48%">
  <img src="docs/screenshots/results.png" alt="Results with summary and stat tiles" width="48%">
</p>
<p align="center">
  <img src="docs/screenshots/chat.png" alt="Ask the video chat" width="48%">
</p>
-->

*Screenshots coming soon.*

---

## 🧠 How it works

<p align="center">
  <img src="docs/architecture.svg" alt="Pipeline architecture" width="100%">
</p>

1. **Acquire audio**: `utils/audio_processor.py` downloads audio from YouTube (yt-dlp) or reads the uploaded file, then splits it into chunks using FFmpeg/pydub.
2. **Transcribe**: `core/transcriber.py` runs Whisper locally over every chunk and joins the results into one transcript. For Hinglish it translates to English.
3. **Analyse**: `core/summarize.py` and `core/extractor.py` prompt a Mistral model (via LangChain) to produce the title, summary, action items, key decisions and open questions.
4. **Index**: `core/rag_engine.py` splits the transcript, embeds it with a HuggingFace sentence-transformer, stores it in ChromaDB and builds a retrieval chain.
5. **Present**: `app.py` shows everything in a tabbed Streamlit interface, and `ask_question()` powers the chat tab.

The whole flow is a single function, `run_pipeline(source, language)` in `main.py`, which returns a dictionary with `title`, `transcript`, `summary`, `action_items`, `key_decisions`, `open_questions` and `rag_chain`.

---

## 🧰 Tech stack

| Layer | Tools |
|---|---|
| UI | Streamlit |
| Audio and video | yt-dlp, FFmpeg, pydub, ffmpeg-python |
| Speech-to-text | OpenAI Whisper (local), PyTorch, torchaudio |
| Translation | deep-translator |
| LLM | Mistral (`langchain-mistralai`, `mistralai`) |
| Orchestration | LangChain (LCEL) |
| RAG | ChromaDB, sentence-transformers, `langchain-huggingface` |
| Config | python-dotenv |

---

## 📁 Project structure

```
video-agent/
├── app.py                  # Streamlit web interface
├── main.py                 # Pipeline (run_pipeline) + CLI entry point
├── core/
│   ├── transcriber.py      # Whisper transcription
│   ├── summarize.py        # Title + summary generation
│   ├── extractor.py        # Action items, decisions, open questions
│   └── rag_engine.py       # Vector store + question answering
├── utils/
│   └── audio_processor.py  # Download, convert and chunk audio
├── .streamlit/             # Streamlit configuration
├── downloads/              # Temporary downloaded media
├── test.py                 # Test script
├── requirements.txt
└── .env                    # API keys (never commit this file)
```

---

## 🚀 Getting started

### Prerequisites

- **Python 3.10 or newer**
- **FFmpeg** installed and available on your `PATH`
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- A **Mistral API key** from [console.mistral.ai](https://console.mistral.ai/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/garry000111/video-agent.git
cd video-agent

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

> ⚠️ Never commit real API keys. Make sure `.env` is listed in `.gitignore`.

---

## ▶️ Usage

### Web app (recommended)

```bash
streamlit run app.py
```

Then open the URL shown in your terminal (usually http://localhost:8501).

1. In the sidebar, choose **YouTube link** or **Upload file**.
2. Select the spoken language (`english` or `hinglish`).
3. Click **Analyze video** and wait. Long videos can take a few minutes.
4. Browse the tabs: **Summary, Action items, Decisions, Open questions, Transcript, Ask the video**.
5. Download the report or transcript, or click **Start over** for a new video.

### Command line

```bash
python main.py
```

You will be asked for a YouTube URL or local file path and a language. The summary and extracted items are printed, and you can then chat with the video in the terminal (type `exit` to quit).

### Use it from your own code

```python
from main import run_pipeline
from core.rag_engine import ask_question

result = run_pipeline("https://youtube.com/watch?v=...", language="english")

print(result["title"])
print(result["summary"])

print(ask_question(result["rag_chain"], "What are the main takeaways?"))
```

---

## 💡 Example use cases

- Summarise a lecture or conference talk without watching it end to end
- Turn a recorded team meeting into action items and decisions
- Pull open questions out of a client call
- Search a long podcast for what was said about a specific topic

---

## ⚠️ Known limitations

- Whisper runs locally, so transcription speed depends on your hardware (a GPU helps a lot).
- Very long videos take longer and use more API calls.
- Answers are limited to what is in the transcript, so audio quality affects accuracy.

---

## 🗺️ Roadmap

- [ ] Timestamps in the transcript and in chat answers
- [ ] PDF export of the report
- [ ] More languages
- [ ] Speaker identification
- [ ] Docker image for one-command setup

---

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## 📄 License

No license has been added yet. Consider adding one, for example [MIT](https://choosealicense.com/licenses/mit/).

---

<p align="center">Built with Streamlit, Whisper, LangChain, Mistral and ChromaDB</p>
