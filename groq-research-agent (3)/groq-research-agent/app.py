import streamlit as st
import time
from agent import ResearchAgent
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groq Research Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --border: #1e1e2e;
    --accent: #00ff88;
    --accent2: #7c3aed;
    --text: #e2e8f0;
    --muted: #64748b;
}
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: var(--bg); color: var(--text); }
.stApp { background-color: var(--bg); }
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

.hero { text-align: center; padding: 2rem 0 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.hero h1 { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #00ff88, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: -1px; }
.hero p { color: var(--muted); font-family: 'Space Mono', monospace; font-size: 0.85rem; margin-top: 0.5rem; }

.stats-row { display: flex; gap: 1rem; justify-content: center; margin: 1rem 0; flex-wrap: wrap; }
.stat-badge { background: var(--border); border: 1px solid #2a2a3e; border-radius: 20px; padding: 0.3rem 1rem; font-family: 'Space Mono', monospace; font-size: 0.75rem; color: var(--accent); }

.stTextArea textarea { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; color: var(--text) !important; font-family: 'Syne', sans-serif !important; font-size: 1rem !important; }
.stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(0,255,136,0.1) !important; }

.stButton > button { background: linear-gradient(135deg, #00ff88, #00cc6e) !important; color: #0a0a0f !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; border: none !important; border-radius: 10px !important; padding: 0.6rem 2rem !important; font-size: 1rem !important; transition: all 0.2s !important; width: 100%; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(0,255,136,0.3) !important; }

.tldr-card { background: linear-gradient(135deg, #0d1f17, #0f0f1a); border: 1px solid var(--accent); border-radius: 14px; padding: 1.5rem 2rem; margin: 1.5rem 0; }
.tldr-card h3 { color: var(--accent); font-family: 'Space Mono', monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 0.8rem; }

.result-card { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
.result-card h3 { color: var(--accent); font-size: 0.75rem; font-family: 'Space Mono', monospace; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 0.8rem; }

.thought-step { background: #0d0d18; border: 1px solid #1a1a2e; border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0; font-family: 'Space Mono', monospace; font-size: 0.78rem; color: var(--muted); display: flex; align-items: flex-start; gap: 0.6rem; }
.thought-step .icon { color: var(--accent2); flex-shrink: 0; }

.metric-box { background: var(--border); border-radius: 10px; padding: 1rem; text-align: center; }
.metric-box .value { font-size: 1.8rem; font-weight: 800; color: var(--accent); font-family: 'Space Mono', monospace; }
.metric-box .label { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

.source-chip { display: inline-block; background: #1a1a2e; border: 1px solid var(--accent2); border-radius: 20px; padding: 0.2rem 0.8rem; font-size: 0.72rem; font-family: 'Space Mono', monospace; color: #a78bfa; margin: 0.2rem; }
.source-link { color: #a78bfa; text-decoration: none; }
.source-link:hover { color: var(--accent); }

.query-chip { display: inline-block; background: #0d1117; border: 1px dashed #2a2a3e; border-radius: 6px; padding: 0.2rem 0.7rem; font-size: 0.72rem; font-family: 'Space Mono', monospace; color: var(--muted); margin: 0.2rem; }

.history-item { background: var(--border); border-radius: 8px; padding: 0.6rem 0.8rem; margin: 0.3rem 0; font-size: 0.85rem; color: var(--muted); border-left: 2px solid transparent; }
.stSelectbox > div > div { background: var(--surface) !important; border-color: var(--border) !important; color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("history", []), ("total_queries", 0), ("total_time", 0.0)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Configuration")
    st.markdown("---")

    # Auto-load from Streamlit secrets (deployed) or let user enter manually
    _secret_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    if _secret_key:
        api_key = _secret_key
        st.success("✅ API Key loaded automatically", icon="🔑")
    else:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", help="Get free key at console.groq.com")

    model   = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"])
    max_search_results = st.slider("Search Results per Query", 3, 10, 5)
    temperature        = st.slider("Temperature", 0.0, 1.0, 0.6, 0.1)

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    c1, c2 = st.columns(2)
    avg = (st.session_state.total_time / st.session_state.total_queries) if st.session_state.total_queries > 0 else 0
    c1.markdown(f'<div class="metric-box"><div class="value">{st.session_state.total_queries}</div><div class="label">Queries</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="value">{avg:.1f}s</div><div class="label">Avg Time</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🕘 History")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-8:]):
            q = item["query"][:38] + "..." if len(item["query"]) > 38 else item["query"]
            st.markdown(f'<div class="history-item">🔍 {q}</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown('<div style="color:#64748b;font-size:0.8rem;">No history yet</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚡ Groq Research Agent</h1>
    <p>autonomous · multi-step · professional-grade reports · powered by groq lpu</p>
    <div class="stats-row">
        <span class="stat-badge">🦙 Llama 3.3 70B</span>
        <span class="stat-badge">🔍 Live Web Search</span>
        <span class="stat-badge">🧠 4-Step Pipeline</span>
        <span class="stat-badge">📋 McKinsey-Level Reports</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Preset queries ─────────────────────────────────────────────────────────────
st.markdown("**💡 Try a sample query:**")
presets = [
    "Top 5 Python projects for AI portfolio 2026",
    "How does Groq LPU differ from GPU?",
    "Best RAG pipeline frameworks compared",
    "LangChain vs CrewAI vs AutoGen agents",
]
cols = st.columns(len(presets))
selected_preset = None
for i, (col, preset) in enumerate(zip(cols, presets)):
    with col:
        if st.button(preset, key=f"p{i}"):
            selected_preset = preset

# ── Input ─────────────────────────────────────────────────────────────────────
query = st.text_area(
    "query",
    value=selected_preset or "",
    placeholder="e.g. Top 5 Python projects for AI/ML portfolio in 2026",
    height=100,
    label_visibility="collapsed",
)

cb1, cb2 = st.columns([4, 1])
with cb1:
    run_btn = st.button("⚡ Run Professional Research Agent", use_container_width=True)
with cb2:
    st.button("🔄 Clear", use_container_width=True, on_click=lambda: None)

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ Enter your Groq API key in the sidebar — free at console.groq.com")
        st.stop()
    if not query.strip():
        st.warning("Please enter a research query.")
        st.stop()

    try:
        agent = ResearchAgent(api_key=api_key, model=model, max_results=max_search_results, temperature=temperature)
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.stop()

    start = time.time()
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline Running...")

    thoughts_ph = st.empty()

    STEPS = [
        ("🧠", "Analyzing query and planning 3 targeted sub-searches..."),
        ("🌐", "Executing live web searches across multiple sources..."),
        ("📖", "Reading and extracting key insights from results..."),
        ("✍️",  "Synthesizing professional report with deep analysis..."),
        ("💬", "Generating executive TL;DR summary..."),
        ("✅", ""),  # filled after timing
    ]

    # Show first 5 steps immediately
    def render_thoughts(steps_done: int, elapsed: float = 0):
        html = ""
        for idx, (icon, text) in enumerate(STEPS):
            if idx < steps_done:
                label = text if idx < 5 else f"Complete — report ready in {elapsed:.2f}s ✓"
                html += f'<div class="thought-step"><span class="icon">{icon}</span>{label}</div>'
        thoughts_ph.markdown(html, unsafe_allow_html=True)

    render_thoughts(1)

    with st.spinner("Researching — this takes ~10–20s for a professional report..."):
        try:
            render_thoughts(2)
            result = agent.run(query)
            elapsed = time.time() - start

            render_thoughts(6, elapsed)

            # Update stats
            st.session_state.total_queries += 1
            st.session_state.total_time += elapsed
            st.session_state.history.append({"query": query, "time": elapsed})

            st.markdown("---")

            # ── Metrics ──────────────────────────────────────────────────────
            m1, m2, m3, m4, m5 = st.columns(5)
            metrics = [
                (f"{elapsed:.1f}s", "Total Time"),
                (str(len(result.get("raw_results", []))), "Sources Read"),
                (str(len(result.get("search_queries", []))), "Sub-Queries"),
                (str(len(result.get("report", "").split())), "Words"),
                ("4", "Pipeline Steps"),
            ]
            for col, (val, lbl) in zip([m1, m2, m3, m4, m5], metrics):
                col.markdown(f'<div class="metric-box"><div class="value">{val}</div><div class="label">{lbl}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Sub-queries used ─────────────────────────────────────────────
            if result.get("search_queries"):
                qhtml = "**🔎 Sub-queries executed:** &nbsp;"
                for q in result["search_queries"]:
                    qhtml += f'<span class="query-chip">{q}</span> '
                st.markdown(qhtml, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # ── TL;DR ────────────────────────────────────────────────────────
            if result.get("tldr"):
                st.markdown(f"""
                <div class="tldr-card">
                    <h3>⚡ TL;DR — Executive Summary</h3>
                    <div style="color:#e2e8f0;line-height:1.8;">{result['tldr'].replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Full Report ──────────────────────────────────────────────────
            st.markdown('<div class="result-card"><h3>📋 Full Professional Report</h3></div>', unsafe_allow_html=True)
            st.markdown(result.get("report", "No report generated."))

            # ── Sources ──────────────────────────────────────────────────────
            sources = result.get("sources", [])
            if sources:
                st.markdown("---")
                st.markdown("**🔗 Sources & References**")
                src_html = ""
                for s in sources:
                    if isinstance(s, dict):
                        title = s.get("title", "Source")
                        url   = s.get("url", "#")
                        src_html += f'<span class="source-chip"><a class="source-link" href="{url}" target="_blank">🌐 {title}</a></span>'
                    else:
                        src_html += f'<span class="source-chip">🌐 {str(s)[:50]}</span>'
                st.markdown(src_html, unsafe_allow_html=True)

            # ── Download ─────────────────────────────────────────────────────
            st.markdown("---")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            report_md = f"""# Research Report
**Query:** {query}
**Model:** {model}  |  **Time:** {elapsed:.2f}s  |  **Date:** {now_str}
**Sources:** {len(sources)}  |  **Pipeline Steps:** 4

---

## ⚡ TL;DR
{result.get('tldr', '')}

---

{result.get('report', '')}

---

## 🔗 Sources
"""
            for s in sources:
                if isinstance(s, dict):
                    report_md += f"- [{s.get('title', 'Source')}]({s.get('url', '')})\n"
                else:
                    report_md += f"- {s}\n"

            st.download_button(
                "📥 Download Professional Report (.md)",
                data=report_md,
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
            )

        except Exception as e:
            st.error(f"❌ Agent error: {str(e)}")
            st.info("💡 Check your Groq API key at console.groq.com")
