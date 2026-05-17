import ast
from groq import Groq
from duckduckgo_search import DDGS


class ResearchAgent:
    """
    Professional autonomous research agent powered by Groq's ultra-fast LPU inference.
    4-step pipeline: plan → search → extract insights → synthesize professional report.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        max_results: int = 5,
        temperature: float = 0.6,
    ):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_results = max_results
        self.temperature = temperature

    # ── Web Search ────────────────────────────────────────────────────────────
    def search_web(self, query: str) -> list[dict]:
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=self.max_results):
                    results.append({
                        "title":   r.get("title", ""),
                        "url":     r.get("href", ""),
                        "snippet": r.get("body", ""),
                    })
        except Exception as e:
            results = [{"title": "Search Error", "url": "", "snippet": str(e)}]
        return results

    # ── Format results for LLM ────────────────────────────────────────────────
    def _format_results(self, results: list[dict]) -> str:
        out = ""
        for i, r in enumerate(results, 1):
            out += f"\n[Source {i}]\nTitle: {r['title']}\nURL: {r['url']}\nExcerpt: {r['snippet']}\n---"
        return out.strip()

    # ── Step 1: Plan smart sub-queries ────────────────────────────────────────
    def _plan_searches(self, query: str) -> list[str]:
        prompt = f"""You are a senior research strategist. Break the following query into 3 highly specific, complementary search queries that together give a complete picture. Cover: definitions/overview, latest trends/tools, and real-world examples/comparisons.

Research Query: {query}

Respond ONLY with a Python list of 3 strings. No explanation.
["query 1", "query 2", "query 3"]"""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=250,
        )
        raw = resp.choices[0].message.content.strip()
        try:
            queries = ast.literal_eval(raw)
            return queries if isinstance(queries, list) else [query]
        except Exception:
            return [query]

    # ── Step 2: Extract key insights ─────────────────────────────────────────
    def _extract_insights(self, query: str, results: list[dict]) -> str:
        context = self._format_results(results)
        prompt = f"""You are a research analyst. From the search results below, extract ONLY the most relevant, specific, and factual insights related to: "{query}"

Rules:
- Extract concrete facts, numbers, names, tools, libraries, companies
- Ignore vague or generic statements
- Group similar insights together
- Cite [Source N] for each insight

Search Results:
{context}

Return a clean bullet-point list of key insights with citations."""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        return resp.choices[0].message.content.strip()

    # ── Step 3: Synthesize professional report ────────────────────────────────
    def _synthesize_report(self, query: str, insights: str, results: list[dict]) -> str:
        context = self._format_results(results)

        system = """You are a world-class research analyst and technical writer producing professional, McKinsey-level research reports. Your reports are:
- Deeply analytical, not just descriptive
- Backed by specific facts, tools, names, and real numbers
- Written in authoritative, precise language
- Actionable — readers know exactly what to DO after reading

Always use this EXACT structure:

---

## 📌 Executive Summary
[3-4 sentences: what the topic is, why it matters, and the single most important takeaway]

---

## 🔍 Key Findings
[6-8 specific, fact-backed bullet points — each with a cited [Source N] and concrete detail like tool names, percentages, or company names]

---

## 📊 Deep Dive Analysis

### [Relevant Subtopic 1 — name it based on the query]
[2-3 paragraphs of detailed, specific analysis with citations]

### [Relevant Subtopic 2]
[2-3 paragraphs of detailed, specific analysis with citations]

### [Relevant Subtopic 3]
[2-3 paragraphs of detailed, specific analysis with citations]

---

## 🚀 Current Trends & Innovations (2025–2026)
[What is happening RIGHT NOW — specific tools, frameworks, companies, new releases, adoption numbers]

---

## ⚖️ Pros, Cons & Trade-offs
| Aspect | Pros | Cons |
|--------|------|------|
[Fill a markdown table with balanced, specific pros and cons]

---

## 💡 Actionable Recommendations
1. [Specific action — with tool/resource name]
2. [Specific action]
3. [Specific action]
4. [Specific action]
5. [Specific action]

---

## 🏁 Conclusion
[2-3 sentences: key message + forward-looking perspective]

---

Use markdown throughout. Mention real tools, libraries, companies, and numbers. Cite [Source N] liberally."""

        user = f"""Research Query: {query}

Pre-extracted Key Insights:
{insights}

Full Search Results:
{context}

Write the complete professional research report following the structure exactly. Be specific and thorough."""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.temperature,
            max_tokens=3500,
        )
        return resp.choices[0].message.content.strip()

    # ── Step 4: TL;DR ────────────────────────────────────────────────────────
    def _generate_tldr(self, report: str, query: str) -> str:
        prompt = f"""Given this research report about "{query}", write a crisp 3-bullet TL;DR a busy professional can read in 10 seconds. Each bullet = one specific, concrete takeaway. No vague statements.

Report:
{report[:2000]}

Format exactly:
• [Bullet 1 — specific fact or tool]
• [Bullet 2 — specific fact or recommendation]
• [Bullet 3 — specific future outlook or action]"""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()

    # ── Main pipeline ─────────────────────────────────────────────────────────
    def run(self, query: str) -> dict:
        """
        4-step professional research pipeline:
        1. Plan    → generate 3 smart sub-queries
        2. Search  → fetch live web results for each
        3. Extract → pull out key insights from raw data
        4. Synthesize → professional report + TL;DR
        """
        # 1. Plan
        search_queries = self._plan_searches(query)

        # 2. Search
        all_results, sources, seen_urls = [], [], set()
        for sq in search_queries:
            for r in self.search_web(sq):
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
                    if r.get("title"):
                        sources.append({"title": r["title"][:70], "url": url})

        all_results = all_results[: self.max_results * 3]
        sources     = sources[: self.max_results * 3]

        # 3. Extract insights
        insights = self._extract_insights(query, all_results)

        # 4. Synthesize report + TL;DR
        report = self._synthesize_report(query, insights, all_results)
        tldr   = self._generate_tldr(report, query)

        return {
            "report":         report,
            "tldr":           tldr,
            "insights":       insights,
            "sources":        sources,
            "search_queries": search_queries,
            "raw_results":    all_results,
        }
