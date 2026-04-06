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

# ── Custom CSS — RB Asset Visual Identity ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300&family=Barlow+Condensed:wght@600;700;800&display=swap');

:root {
    --forest:      #152a13;
    --forest-mid:  #1e3d1b;
    --lime:        #6abf2e;
    --lime-bright: #7ed636;
    --lime-dim:    #3d7019;
    --ink:         #0b0f0a;
    --surface:     #111a10;
    --card:        #182616;
    --card-hover:  #1f3320;
    --border:      #243d21;
    --text-main:   #e8f0e6;
    --text-muted:  #7a9977;
    --text-dim:    #4a6647;
    --white:       #ffffff;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: var(--ink) !important;
    color: var(--text-main) !important;
}

/* ── App background ── */
.stApp {
    background-color: var(--ink) !important;
}
.block-container {
    padding-top: 1.5rem !important;
    max-width: 1100px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--forest) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--lime) !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
}

/* ── Sidebar brand mark ── */
.rb-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.25rem 0 1rem;
}
.rb-logo-mark {
    width: 36px;
    height: 36px;
    background: var(--lime);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    color: var(--forest) !important;
    letter-spacing: -1px;
    flex-shrink: 0;
}
.rb-brand-text {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    line-height: 1.3;
}

/* ── Main header ── */
.esg-header {
    background: var(--forest);
    border: 1px solid var(--border);
    border-top: 3px solid var(--lime);
    border-radius: 6px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.esg-header::before {
    content: 'ESG';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 6rem;
    color: rgba(106,191,46,0.06);
    letter-spacing: -4px;
    pointer-events: none;
    user-select: none;
}
.esg-header-left {}
.esg-badge {
    display: inline-block;
    background: var(--lime);
    color: var(--forest) !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.68rem;
    padding: 0.2rem 0.65rem;
    border-radius: 2px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.esg-header h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    color: var(--white) !important;
    margin: 0 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.5px;
    text-transform: uppercase;
}
.esg-header h1 span {
    color: var(--lime) !important;
}
.esg-header p {
    color: var(--text-muted) !important;
    margin: 0.4rem 0 0 !important;
    font-size: 0.9rem !important;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* ── Search bar ── */
.stTextInput > div > div > input {
    font-family: 'Barlow', sans-serif !important;
    font-size: 1rem !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text-main) !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--lime) !important;
    box-shadow: 0 0 0 2px rgba(106,191,46,0.18) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-dim) !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: var(--lime) !important;
    color: var(--forest) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.2rem !important;
    transition: background 0.15s, transform 0.1s !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--lime-bright) !important;
    transform: translateY(-1px) !important;
}
.stButton > button {
    background: var(--surface) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: 'Barlow', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    padding: 0.6rem 1.4rem !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--lime) !important;
    border-bottom: 2px solid var(--lime) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.25rem !important;
}

/* ── News card ── */
.news-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--lime);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: background 0.15s, border-color 0.15s;
}
.news-card:hover {
    background: var(--card-hover);
    border-color: var(--lime-dim);
}
.news-card.risk  { border-left-color: #e05c3a; }
.news-card.neutral { border-left-color: var(--text-dim); }

.news-card-title {
    font-family: 'Barlow', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: var(--text-main);
    margin-bottom: 0.45rem;
    line-height: 1.45;
}
.news-card-title a {
    color: var(--text-main);
    text-decoration: none;
}
.news-card-title a:hover { color: var(--lime); }

.news-card-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 0.55rem;
    align-items: center;
}
.news-card-source {
    background: rgba(106,191,46,0.12);
    color: var(--lime) !important;
    font-weight: 600;
    padding: 0.1rem 0.5rem;
    border-radius: 2px;
    font-size: 0.75rem;
    letter-spacing: 0.03em;
}
.news-card-summary {
    color: var(--text-muted);
    font-size: 0.875rem;
    line-height: 1.65;
    font-weight: 300;
}

/* ── Tag pills ── */
.tag-pill {
    display: inline-block;
    background: rgba(106,191,46,0.1);
    color: var(--lime);
    border: 1px solid rgba(106,191,46,0.25);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 0.12rem 0.5rem;
    border-radius: 2px;
    margin: 0.1rem;
    text-transform: uppercase;
}
.tag-pill.risk {
    background: rgba(224,92,58,0.1);
    color: #e05c3a;
    border-color: rgba(224,92,58,0.25);
}
.tag-pill.neutral {
    background: rgba(122,153,119,0.1);
    color: var(--text-muted);
    border-color: rgba(122,153,119,0.2);
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-chip {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.6rem 1.1rem;
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 400;
}
.stat-chip span {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    color: var(--lime);
    font-size: 1.15rem;
    margin-right: 0.3rem;
}

/* ── Section title ── */
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.25rem 0 0.9rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 1rem;
    color: var(--text-dim);
}
.empty-state .icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.5; }
.empty-state p { color: var(--text-muted) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--lime) !important;
    color: var(--forest) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 4px !important;
}

/* ── Dataframe ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 4px; }

/* ── Warning / info ── */
.stAlert { border-radius: 4px !important; }
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
    st.markdown("""
    <div class="rb-sidebar-brand">
      <div class="rb-logo-mark">RB</div>
      <div class="rb-brand-text">RB Asset<br>ESG Intelligence</div>
    </div>
    <hr style="border-color:#243d21; margin: 0 0 1rem;">
    """, unsafe_allow_html=True)

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
    st.markdown(f"**{len(NEWS_SOURCES)}** categorias · **200+** fontes")
    show_sources = st.toggle("Ver lista de fontes", False)
    if show_sources:
        for cat, srcs in NEWS_SOURCES.items():
            st.markdown(f"**{cat}**")
            for s in srcs:
                st.markdown(f"- {s}")

    st.markdown("---")
    st.caption("RB Asset Management · v1.0 · ESG Intelligence")


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="esg-header">
  <div class="esg-header-left">
    <div class="esg-badge">RB Asset · ESG Intelligence</div>
    <h1>News <span>Radar</span></h1>
    <p>Monitoramento de notícias ESG para análise de empresas parceiras</p>
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
            st.markdown('<div class="empty-state"><div class="icon">◎</div><p>Nenhuma notícia encontrada para este filtro.</p></div>', unsafe_allow_html=True)
            return
        for a in art_list:
            card_class = {
                "risk":     "news-card risk",
                "positive": "news-card",
                "neutral":  "news-card neutral",
            }.get(a["sentiment"], "news-card")

            pub_str = a["published"].strftime("%d/%m/%Y %H:%M") if a["published"] else "Data desconhecida"
            tags_html = "".join(
                f'<span class="tag-pill {"risk" if "Risco" in t else ("neutral" if "Geral" in t else "")}">{t}</span>'
                for t in a["tags"]
            )
            summary = a["summary"][:280] + ("..." if len(a["summary"]) > 280 else "")

            st.markdown(f"""
            <div class="{card_class}">
              <div class="news-card-title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
              <div class="news-card-meta">
                <span class="news-card-source">{a['source']}</span>
                <span>{pub_str}</span>
                <span>{a['origin']}</span>
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
      <div class="icon">◎</div>
      <p style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#6abf2e;">ESG News Radar</p>
      <p>Digite o nome de uma empresa parceira e clique em <strong>Buscar</strong><br>para iniciar o monitoramento de notícias ESG.</p>
    </div>
    """, unsafe_allow_html=True)
