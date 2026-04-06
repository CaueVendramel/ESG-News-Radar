import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import time
import re
from sources import NEWS_SOURCES, ESG_CATEGORIES

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG News Radar",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --green-dark:   #0d3b2e;
    --green-mid:    #1a6b4a;
    --green-accent: #2dce89;
    --green-light:  #b7f5d8;
    --sand:         #f5f0e8;
    --charcoal:     #1c1c1e;
    --muted:        #6b7280;
    --card-bg:      #ffffff;
    --border:       #e5e7eb;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--green-dark) !important;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #e8f5ee !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] h1, h2, h3 {
    color: var(--green-light) !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(45,206,137,0.3) !important;
    color: white !important;
}

/* ── Header ── */
.esg-header {
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-mid) 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    overflow: hidden;
}
.esg-header::after {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(45,206,137,0.15);
}
.esg-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    color: #ffffff !important;
    margin: 0;
    line-height: 1.1;
}
.esg-header p {
    color: var(--green-light) !important;
    margin: 0.3rem 0 0;
    font-size: 1rem;
}
.esg-badge {
    background: var(--green-accent);
    color: var(--green-dark) !important;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
}

/* ── Search bar ── */
.stTextInput > div > div > input {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--green-accent) !important;
    box-shadow: 0 0 0 3px rgba(45,206,137,0.15) !important;
}

/* ── News card ── */
.news-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--green-accent);
    transition: box-shadow 0.2s, transform 0.2s;
}
.news-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}
.news-card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--charcoal);
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.news-card-title a {
    color: var(--charcoal);
    text-decoration: none;
}
.news-card-title a:hover { color: var(--green-mid); }
.news-card-meta {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 0.6rem;
}
.news-card-source {
    background: #f0fdf8;
    color: var(--green-mid);
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-size: 0.78rem;
}
.news-card-summary {
    color: #374151;
    font-size: 0.9rem;
    line-height: 1.6;
}
.tag-pill {
    display: inline-block;
    background: #f0fdf8;
    color: var(--green-mid);
    border: 1px solid #bbf7d0;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    margin: 0.15rem;
}
.tag-pill.risk {
    background: #fff7ed;
    color: #c2410c;
    border-color: #fed7aa;
}
.tag-pill.neutral {
    background: #f8fafc;
    color: #475569;
    border-color: #cbd5e1;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-chip {
    background: var(--sand);
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    color: var(--charcoal);
    font-weight: 500;
}
.stat-chip span {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    color: var(--green-mid);
    font-size: 1.1rem;
    margin-right: 0.3rem;
}

/* ── Misc ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--green-dark);
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid var(--green-light);
}
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--muted);
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def build_google_news_rss_url(query: str, lang: str = "pt") -> str:
    encoded = quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl={lang}&gl=BR&ceid=BR:{lang.upper()}"


def fetch_google_news(query: str, lang: str = "pt", max_items: int = 30) -> list[dict]:
    url = build_google_news_rss_url(query, lang)
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:max_items]:
        pub = entry.get("published", "")
        try:
            pub_dt = datetime(*entry.published_parsed[:6])
        except Exception:
            pub_dt = None
        results.append({
            "title":     entry.get("title", "Sem título"),
            "url":       entry.get("link", "#"),
            "source":    entry.get("source", {}).get("title", "Google News"),
            "published": pub_dt,
            "summary":   re.sub(r'<[^>]+>', '', entry.get("summary", "")),
            "origin":    "Google News RSS",
        })
    return results


def fetch_newsapi(query: str, api_key: str, days_back: int = 30,
                  language: str = "pt", max_items: int = 30) -> list[dict]:
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={quote_plus(query)}"
        f"&from={from_date}"
        f"&language={language}"
        f"&sortBy=relevancy"
        f"&pageSize={max_items}"
        f"&apiKey={api_key}"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        results = []
        for a in data.get("articles", []):
            pub_raw = a.get("publishedAt", "")
            try:
                pub_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except Exception:
                pub_dt = None
            results.append({
                "title":     a.get("title", "Sem título"),
                "url":       a.get("url", "#"),
                "source":    a.get("source", {}).get("name", "NewsAPI"),
                "published": pub_dt,
                "summary":   a.get("description") or a.get("content") or "",
                "origin":    "NewsAPI",
            })
        return results
    except Exception as e:
        st.warning(f"NewsAPI indisponível: {e}")
        return []


def detect_esg_tags(text: str) -> list[str]:
    """Heurística simples para detectar tags ESG no texto."""
    text_lower = text.lower()
    tags = []
    keywords = {
        "🌱 Meio Ambiente":    ["carbono", "emissão", "clima", "sustentabilidade", "reciclagem",
                                "poluição", "floresta", "desmatamento", "biodiversidade",
                                "energia renovável", "aquecimento global", "esg ambiental"],
        "👥 Social":           ["trabalhador", "diversidade", "inclusão", "direitos humanos",
                                "comunidade", "saúde", "segurança", "trabalho infantil",
                                "bem-estar", "gênero", "racial", "equidade"],
        "🏛️ Governança":      ["corrupção", "compliance", "transparência", "auditoria",
                                "conselho", "ética", "governança", "bribery", "fraude",
                                "conflito de interesse", "lavagem"],
        "⚠️ Risco ESG":       ["multa", "embargo", "escândalo", "investigação", "processo",
                                "denúncia", "infração", "acidente", "vazamento", "crise"],
        "📈 Positivo ESG":     ["premiação", "certificação", "sustentável", "esg", "green",
                                "relatório de sustentabilidade", "net zero", "carbono neutro"],
    }
    for tag, kws in keywords.items():
        if any(k in text_lower for k in kws):
            tags.append(tag)
    return tags if tags else ["📰 Geral"]


def classify_sentiment(tags: list[str]) -> str:
    if "⚠️ Risco ESG" in tags:
        return "risk"
    if "📈 Positivo ESG" in tags:
        return "positive"
    return "neutral"


def deduplicate(articles: list[dict]) -> list[dict]:
    seen, out = set(), []
    for a in articles:
        key = a["title"][:80].lower().strip()
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 ESG News Radar")
    st.markdown("---")

    st.markdown("#### 🔑 Configuração de API")
    # Lê do Streamlit Secrets automaticamente; permite override manual
    _secret_key = st.secrets.get("NEWSAPI_KEY", "") if hasattr(st, "secrets") else ""
    newsapi_key = st.text_input(
        "NewsAPI Key (opcional)",
        value=_secret_key,
        type="password",
        help="Configure via Streamlit Secrets (NEWSAPI_KEY) ou insira manualmente"
    )
    if _secret_key and not newsapi_key:
        newsapi_key = _secret_key

    st.markdown("---")
    st.markdown("#### 🔍 Filtros de Busca")

    language = st.selectbox(
        "Idioma principal",
        options=["pt", "en", "es"],
        format_func=lambda x: {"pt": "🇧🇷 Português", "en": "🇺🇸 Inglês", "es": "🇪🇸 Espanhol"}[x]
    )

    days_back = st.slider("Período (dias atrás)", 1, 90, 30)

    esg_filter = st.multiselect(
        "Filtrar por tema ESG",
        options=list(ESG_CATEGORIES.keys()),
        default=[],
        help="Deixe em branco para todos os temas"
    )

    extra_keywords = st.text_input(
        "Palavras-chave adicionais",
        placeholder="ex: multa, sustentabilidade, ESG...",
        help="Serão adicionadas à busca"
    )

    max_results = st.slider("Máx. de resultados", 10, 100, 40)

    st.markdown("---")
    st.markdown("#### 📡 Fontes Ativas")
    st.markdown(f"**{len(NEWS_SOURCES)}** fontes cadastradas")
    show_sources = st.toggle("Ver lista de fontes", False)
    if show_sources:
        for cat, srcs in NEWS_SOURCES.items():
            st.markdown(f"**{cat}**")
            for s in srcs:
                st.markdown(f"- {s}")

    st.markdown("---")
    st.caption("v1.0 · Projeto ESG Interno")


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="esg-header">
  <div>
    <div class="esg-badge">ESG INTELLIGENCE</div>
    <h1>🌿 ESG News Radar</h1>
    <p>Monitoramento de notícias ESG para empresas parceiras</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Search bar
col_search, col_btn = st.columns([5, 1])
with col_search:
    company = st.text_input(
        "Nome da empresa",
        placeholder="Ex: Petrobras, Vale, Magazine Luiza...",
        label_visibility="collapsed"
    )
with col_btn:
    search_clicked = st.button("🔍 Buscar", use_container_width=True, type="primary")

# ── Run search ─────────────────────────────────────────────────────────────────
if search_clicked and company.strip():
    # Build query
    query_parts = [company.strip()]
    if extra_keywords:
        query_parts.append(extra_keywords.strip())
    if esg_filter:
        esg_kws = [kw for cat in esg_filter for kw in ESG_CATEGORIES[cat]]
        query_parts.append(" OR ".join(esg_kws[:6]))

    full_query = " ".join(query_parts)

    with st.spinner("Buscando notícias..."):
        all_articles = []

        # Google News RSS (always)
        gnews = fetch_google_news(full_query, lang=language, max_items=max_results)
        all_articles.extend(gnews)

        # NewsAPI (if key provided)
        if newsapi_key:
            napi = fetch_newsapi(
                full_query, api_key=newsapi_key,
                days_back=days_back, language=language, max_items=max_results
            )
            all_articles.extend(napi)

        # Deduplicate & sort
        articles = deduplicate(all_articles)
        articles.sort(
            key=lambda a: a["published"] or datetime.min,
            reverse=True
        )

        # Filter by date
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        articles = [
            a for a in articles
            if a["published"] is None or a["published"].replace(tzinfo=None) >= cutoff
        ]

        # Tag each article
        for a in articles:
            a["tags"] = detect_esg_tags(a["title"] + " " + a["summary"])
            a["sentiment"] = classify_sentiment(a["tags"])

        # Filter by ESG theme if selected
        if esg_filter:
            tag_labels = [f"🌱 Meio Ambiente", "👥 Social", "🏛️ Governança", "⚠️ Risco ESG", "📈 Positivo ESG"]
            theme_map = {
                "Meio Ambiente": "🌱 Meio Ambiente",
                "Social":        "👥 Social",
                "Governança":    "🏛️ Governança",
                "Risco":         "⚠️ Risco ESG",
                "Positivo":      "📈 Positivo ESG",
            }
            keep_tags = [theme_map.get(f, f) for f in esg_filter]
            articles = [a for a in articles if any(t in a["tags"] for t in keep_tags)]

    # Stats
    n_risk     = sum(1 for a in articles if a["sentiment"] == "risk")
    n_positive = sum(1 for a in articles if a["sentiment"] == "positive")
    n_neutral  = len(articles) - n_risk - n_positive

    st.markdown(f"""
    <div class="stats-bar">
      <div class="stat-chip"><span>{len(articles)}</span> notícias encontradas</div>
      <div class="stat-chip"><span>{n_risk}</span> alertas de risco</div>
      <div class="stat-chip"><span>{n_positive}</span> positivas</div>
      <div class="stat-chip"><span>{n_neutral}</span> neutras</div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab_all, tab_risk, tab_export = st.tabs(["📰 Todas", "⚠️ Riscos ESG", "📥 Exportar"])

    def render_articles(art_list):
        if not art_list:
            st.markdown('<div class="empty-state"><div class="icon">🔎</div><p>Nenhuma notícia encontrada para este filtro.</p></div>', unsafe_allow_html=True)
            return
        for a in art_list:
            border_color = {
                "risk":     "#ef4444",
                "positive": "#2dce89",
                "neutral":  "#94a3b8",
            }.get(a["sentiment"], "#2dce89")

            pub_str = a["published"].strftime("%d/%m/%Y %H:%M") if a["published"] else "Data desconhecida"
            tags_html = "".join(
                f'<span class="tag-pill {"risk" if "Risco" in t else ("neutral" if "Geral" in t else "")}">{t}</span>'
                for t in a["tags"]
            )
            summary = a["summary"][:280] + ("..." if len(a["summary"]) > 280 else "")

            st.markdown(f"""
            <div class="news-card" style="border-left-color: {border_color}">
              <div class="news-card-title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
              <div class="news-card-meta">
                <span class="news-card-source">{a['source']}</span>
                <span>🕐 {pub_str}</span>
                <span>🔗 {a['origin']}</span>
              </div>
              <div style="margin-bottom:0.5rem">{tags_html}</div>
              <div class="news-card-summary">{summary}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_all:
        st.markdown(f'<div class="section-title">Resultados para: <em>{company}</em></div>', unsafe_allow_html=True)
        render_articles(articles)

    with tab_risk:
        risk_arts = [a for a in articles if a["sentiment"] == "risk"]
        st.markdown(f'<div class="section-title">⚠️ Alertas de risco ESG — {len(risk_arts)} notícias</div>', unsafe_allow_html=True)
        render_articles(risk_arts)

    with tab_export:
        st.markdown('<div class="section-title">📥 Exportar Resultados</div>', unsafe_allow_html=True)
        if articles:
            df = pd.DataFrame([{
                "Título":      a["title"],
                "Fonte":       a["source"],
                "Data":        a["published"].strftime("%Y-%m-%d %H:%M") if a["published"] else "",
                "URL":         a["url"],
                "Tags ESG":    ", ".join(a["tags"]),
                "Sentimento":  a["sentiment"],
                "Resumo":      a["summary"][:300],
            } for a in articles])

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=csv,
                file_name=f"esg_{company.replace(' ','_')}_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.dataframe(df, use_container_width=True, height=400)

elif search_clicked and not company.strip():
    st.warning("⚠️ Digite o nome de uma empresa para iniciar a busca.")
else:
    st.markdown("""
    <div class="empty-state">
      <div class="icon">🌿</div>
      <p style="font-size:1.1rem; font-weight:600; color:#1a6b4a;">Bem-vindo ao ESG News Radar</p>
      <p>Digite o nome de uma empresa parceira e clique em <strong>Buscar</strong><br>
         para iniciar o monitoramento de notícias ESG.</p>
    </div>
    """, unsafe_allow_html=True)
