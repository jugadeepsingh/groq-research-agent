# ⚡ Groq Research Agent

An autonomous AI research agent powered by **Groq's ultra-fast LPU inference** and **Llama 3.3 70B**. It searches the web, reads results, and synthesizes a structured research report in seconds.

---

## 🚀 Quick Setup (5 minutes)

### 1. Get a FREE Groq API Key
→ Go to [console.groq.com](https://console.groq.com)  
→ Sign up (free) → Create API Key → Copy it

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Open in browser
→ Streamlit will open at **http://localhost:8501**  
→ Paste your Groq API key in the sidebar  
→ Type any research query and hit **Run Research Agent** ⚡

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `groq` | Ultra-fast LLM inference (LPU chip) |
| `streamlit` | Beautiful web UI |
| `duckduckgo-search` | Free web search (no API key needed) |
| `Llama 3.3 70B` | Most capable open-source LLM |

---

## 🤖 How It Works

```
User Query
    │
    ▼
[Step 1] Plan - LLM generates 2-3 smart sub-queries
    │
    ▼
[Step 2] Search - DuckDuckGo fetches live web results
    │
    ▼
[Step 3] Synthesize - LLM reads all results → structured report
    │
    ▼
Research Report + Sources + Download
```

---

## 📂 Project Structure

```
groq-research-agent/
├── app.py              ← Streamlit UI
├── agent.py            ← Agent logic (search + synthesize)
├── requirements.txt    ← Dependencies
├── .env.example        ← Environment variables template
├── .streamlit/
│   └── config.toml     ← Streamlit theme config
└── README.md           ← This file
```

---

## 💡 Example Queries

- *"Latest breakthroughs in AI agents 2025"*
- *"Best practices for deploying ML models in production"*
- *"How does Groq LPU differ from GPU for AI inference?"*
- *"Top Python libraries for data science in 2026"*

---

## 🏆 LinkedIn Post Template

> I built an autonomous AI Research Agent using **Groq + Llama 3.3 70B** that:
> 🔍 Searches the web in real-time
> 🧠 Reasons through multiple sources
> ⚡ Generates full research reports in under 3 seconds
>
> Built with: Python · Streamlit · Groq API · DuckDuckGo Search
> 
> #AI #MachineLearning #Groq #LLM #Python #OpenSource

---

Made with ⚡ by [Your Name]
