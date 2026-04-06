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

# ── Custom CSS — RB Asset Visual Identity (refined) ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --bg-base:      #0a1209;
    --bg-surface:   #0f1a0e;
    --bg-card:      #152614;
    --bg-card-hov:  #1a3020;
    --border:       #1e3320;
    --border-mid:   #2a4a22;
    --lime:         #5ab527;
    --lime-bright:  #7ed646;
    --lime-dim:     #3d6032;
    --lime-muted:   #2d4d25;
    --text-primary: #d4e8bc;
    --text-sec:     #6a9e55;
    --text-dim:     #3d6032;
    --text-faint:   #2a4020;
    --risk:         #ef4444;
    --risk-bg:      #3d1414;
    --risk-border:  #5c1e1e;
    --risk-text:    #f87171;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}
.stApp { background-color: var(--bg-base) !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-base) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] label { color: var(--text-sec) !important; font-size: 0.78rem !important; letter-spacing: 0.06em; text-transform: uppercase; }
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-mid) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] small { color: var(--text-dim) !important; font-size: 0.78rem !important; }

/* ── Sidebar brand ── */
.rb-brand {
    display: flex; align-items: center; gap: 12px; padding: 0.25rem 0 1.25rem;
}
.rb-logo {
    width: 38px; height: 38px; background: var(--lime);
    border-radius: 7px; display: flex; align-items: center; justify-content: center;
    font-family: 'Playfair Display', serif; font-weight: 700; font-size: 14px;
    color: #fff; flex-shrink: 0; letter-spacing: -0.5px;
}
.rb-brand-text-top {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--lime) !important; line-height: 1;
}
.rb-brand-text-bot {
    font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-dim) !important; margin-top: 3px;
}

/* ── Header ── */
.esg-header {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-top: 2px solid var(--lime);
    border-radius: 10px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
}
.esg-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important; font-size: 2rem !important;
    color: var(--text-primary) !important; margin: 0 !important; line-height: 1.1 !important;
}
.esg-header h1 em { font-style: normal; color: var(--lime) !important; }
.esg-header p { color: var(--text-sec) !important; margin: 0.35rem 0 0 !important; font-size: 0.85rem !important; font-weight: 300; letter-spacing: 0.02em; }
.esg-badge {
    display: inline-block; background: rgba(90,181,39,0.12);
    color: var(--lime-bright) !important; border: 1px solid rgba(90,181,39,0.25);
    font-size: 0.65rem; font-weight: 600; padding: 0.2rem 0.6rem;
    border-radius: 20px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.55rem;
}
.hdr-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.hdr-tag {
    font-size: 0.68rem; font-weight: 500; padding: 4px 10px;
    border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase;
}
.hdr-tag-e { background: rgba(90,181,39,0.1); color: var(--lime-bright) !important; border: 1px solid rgba(90,181,39,0.2); }
.hdr-tag-s { background: rgba(96,165,250,0.1); color: #93c5fd !important; border: 1px solid rgba(96,165,250,0.2); }
.hdr-tag-g { background: rgba(251,191,36,0.1); color: #fcd34d !important; border: 1px solid rgba(251,191,36,0.2); }

/* ── Search ── */
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-dim) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--lime) !important;
    box-shadow: 0 0 0 3px rgba(90,181,39,0.12) !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: var(--lime) !important; color: #0a1a08 !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 0.85rem !important; letter-spacing: 0.04em !important;
    border: none !important; border-radius: 8px !important;
    transition: background 0.15s !important;
}
.stButton > button[kind="primary"]:hover { background: var(--lime-bright) !important; }
.stButton > button:not([kind="primary"]) {
    background: var(--bg-card) !important; color: var(--text-sec) !important;
    border: 1px solid var(--border-mid) !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important; font-weight: 500 !important;
    font-size: 0.82rem !important; letter-spacing: 0.04em !important;
    color: var(--text-dim) !important; padding: 0.55rem 1.2rem !important;
    background: transparent !important; border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--lime-bright) !important;
    border-bottom: 2px solid var(--lime) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.1rem !important; }

/* ── Stats bar ── */
.stats-bar { display: flex; gap: 1px; background: var(--border); border-radius: 10px; overflow: hidden; margin-bottom: 1.25rem; }
.stat-chip { flex: 1; background: var(--bg-surface); padding: 0.85rem 1rem; }
.stat-num {
    font-family: 'Playfair Display', serif; font-weight: 700;
    font-size: 1.5rem; color: var(--lime-bright); line-height: 1;
}
.stat-num.risk { color: var(--risk-text); }
.stat-lbl { font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 3px; }

/* ── Cards ── */
.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--lime);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.65rem;
    transition: background 0.12s, border-color 0.12s;
}
.news-card:hover { background: var(--bg-card-hov); }
.news-card.risk { border-left-color: var(--risk); }
.news-card.neutral { border-left-color: var(--border-mid); }

.news-card-source {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--lime); margin-bottom: 5px;
}
.news-card.risk .news-card-source { color: var(--risk-text); }

.news-card-title {
    font-size: 0.92rem; font-weight: 500; color: var(--text-primary);
    line-height: 1.55; margin-bottom: 0.55rem;
}
.news-card-title a { color: var(--text-primary); text-decoration: none; }
.news-card-title a:hover { color: var(--lime-bright); }

.news-card-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.75rem; color: var(--text-dim); }

.tag-pill {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    padding: 2px 7px; border-radius: 4px;
    background: rgba(90,181,39,0.1); color: var(--lime-bright);
    border: 1px solid rgba(90,181,39,0.2);
}
.tag-pill.risk { background: var(--risk-bg); color: var(--risk-text); border-color: var(--risk-border); }
.tag-pill.neutral { background: var(--text-faint); color: var(--text-dim); border-color: var(--border); }

/* ── Section title ── */
.section-title {
    font-family: 'Inter', sans-serif; font-weight: 500; font-size: 0.78rem;
    color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1rem 0 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);
}

/* ── Empty state ── */
.empty-state { text-align: center; padding: 4rem 1rem; }
.empty-state .icon { font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.3; }
.empty-state p { color: var(--text-dim) !important; font-size: 0.9rem !important; }
.empty-state .title { font-family: 'Playfair Display', serif; font-size: 1.2rem !important; color: var(--text-sec) !important; font-weight: 600; }

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--lime) !important; color: #0a1a08 !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    border: none !important; border-radius: 8px !important;
}
.stDataFrame { background: var(--bg-surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stAlert { border-radius: 8px !important; }
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
    <div class="rb-brand">
      <div class="rb-logo">RB</div>
      <div>
        <div class="rb-brand-text-top">RB Asset</div>
        <div class="rb-brand-text-bot">ESG News Radar</div>
      </div>
    </div>
    <hr style="border-color:#1e3320; margin: 0 0 1rem;">
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
  <div>
    <div class="esg-badge">RB Asset · ESG Intelligence</div>
    <h1>News <em>Radar</em></h1>
    <p>Monitoramento de notícias ESG para análise de empresas parceiras</p>
  </div>
  <div class="hdr-tags">
    <span class="hdr-tag hdr-tag-e">Ambiental</span>
    <span class="hdr-tag hdr-tag-s">Social</span>
    <span class="hdr-tag hdr-tag-g">Governança</span>
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
      <div class="stat-chip"><div class="stat-num">{len(articles)}</div><div class="stat-lbl">Encontradas</div></div>
      <div class="stat-chip"><div class="stat-num risk">{n_risk}</div><div class="stat-lbl">Alertas de risco</div></div>
      <div class="stat-chip"><div class="stat-num">{n_positive}</div><div class="stat-lbl">Positivas</div></div>
      <div class="stat-chip"><div class="stat-num">{n_neutral}</div><div class="stat-lbl">Neutras</div></div>
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
              <div class="news-card-source">{a['source']}</div>
              <div class="news-card-title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
              <div class="news-card-meta">
                <span>{pub_str}</span>
                <span>·</span>
                <span>{a['origin']}</span>
                <span style="margin-left:4px">{tags_html}</span>
              </div>
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
      <p class="title">ESG News Radar</p>
      <p>Digite o nome de uma empresa parceira e clique em <strong>Buscar</strong><br>para iniciar o monitoramento de notícias ESG.</p>
    </div>
    """, unsafe_allow_html=True)
