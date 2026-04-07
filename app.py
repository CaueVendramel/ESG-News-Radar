import streamlit as st
import feedparser
import requests
import pandas as pd
import anthropic
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import re
import json
from sources import NEWS_SOURCES, ESG_CATEGORIES

st.set_page_config(page_title="ESG News Radar · RB Asset", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');
:root{--bg-base:#0a1209;--bg-surface:#0f1a0e;--bg-card:#152614;--bg-card-hov:#1a3020;--border:#1e3320;--border-mid:#2a4a22;--lime:#5ab527;--lime-bright:#7ed646;--lime-dim:#3d6032;--text-primary:#d4e8bc;--text-sec:#6a9e55;--text-dim:#3d6032;--text-faint:#2a4020;--risk:#ef4444;--risk-bg:#3d1414;--risk-border:#5c1e1e;--risk-text:#f87171;--amber:#f59e0b;--amber-bg:#3d2a00;--blue:#60a5fa;--blue-bg:#0c1e3d}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background-color:var(--bg-base)!important;color:var(--text-primary)!important}
.stApp{background-color:var(--bg-base)!important}.block-container{padding-top:1.5rem!important;max-width:1150px}
[data-testid="stSidebar"]{background:var(--bg-base)!important;border-right:1px solid var(--border)!important}
[data-testid="stSidebar"] *{color:var(--text-primary)!important}
[data-testid="stSidebar"] label{color:var(--text-sec)!important;font-size:.75rem!important;letter-spacing:.06em;text-transform:uppercase}
[data-testid="stSidebar"] .stTextInput>div>div>input,[data-testid="stSidebar"] .stSelectbox>div>div,[data-testid="stSidebar"] .stMultiSelect>div>div{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;color:var(--text-primary)!important;border-radius:8px!important;font-size:.85rem!important}
[data-testid="stSidebar"] hr{border-color:var(--border)!important}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] small,[data-testid="stSidebar"] .stCaption{color:var(--text-dim)!important;font-size:.75rem!important}
.rb-brand{display:flex;align-items:center;gap:12px;padding:.25rem 0 1.25rem}
.rb-logo{width:38px;height:38px;background:var(--lime);border-radius:7px;display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-weight:700;font-size:14px;color:#fff;flex-shrink:0}
.rb-brand-text-top{font-size:.72rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--lime)!important}
.rb-brand-text-bot{font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;color:var(--text-dim)!important;margin-top:3px}
.esg-header{background:var(--bg-surface);border:1px solid var(--border);border-top:2px solid var(--lime);border-radius:10px;padding:1.75rem 2rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between}
.esg-header h1{font-family:'Playfair Display',serif!important;font-weight:700!important;font-size:2rem!important;color:var(--text-primary)!important;margin:0!important;line-height:1.1!important}
.esg-header h1 em{font-style:normal;color:var(--lime)!important}
.esg-header p{color:var(--text-sec)!important;margin:.35rem 0 0!important;font-size:.85rem!important;font-weight:300}
.esg-badge{display:inline-block;background:rgba(90,181,39,.12);color:var(--lime-bright)!important;border:1px solid rgba(90,181,39,.25);font-size:.65rem;font-weight:600;padding:.2rem .6rem;border-radius:20px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.55rem}
.hdr-tags{display:flex;gap:6px;flex-wrap:wrap}
.hdr-tag{font-size:.68rem;font-weight:500;padding:4px 10px;border-radius:20px;letter-spacing:.05em;text-transform:uppercase}
.hdr-tag-e{background:rgba(90,181,39,.1);color:var(--lime-bright)!important;border:1px solid rgba(90,181,39,.2)}
.hdr-tag-s{background:rgba(96,165,250,.1);color:#93c5fd!important;border:1px solid rgba(96,165,250,.2)}
.hdr-tag-g{background:rgba(251,191,36,.1);color:#fcd34d!important;border:1px solid rgba(251,191,36,.2)}
.stTextInput>div>div>input{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-radius:8px!important;color:var(--text-primary)!important;font-size:.95rem!important;padding:.7rem 1rem!important;font-family:'Inter',sans-serif!important}
.stTextInput>div>div>input::placeholder{color:var(--text-dim)!important}
.stTextInput>div>div>input:focus{border-color:var(--lime)!important;box-shadow:0 0 0 3px rgba(90,181,39,.12)!important}
.stButton>button[kind="primary"]{background:var(--lime)!important;color:#0a1a08!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:.85rem!important;border:none!important;border-radius:8px!important}
.stButton>button[kind="primary"]:hover{background:var(--lime-bright)!important}
.stButton>button:not([kind="primary"]){background:var(--bg-card)!important;color:var(--text-sec)!important;border:1px solid var(--border-mid)!important;border-radius:8px!important}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;gap:0!important}
.stTabs [data-baseweb="tab"]{font-family:'Inter',sans-serif!important;font-weight:500!important;font-size:.82rem!important;color:var(--text-dim)!important;padding:.55rem 1.2rem!important;background:transparent!important;border:none!important;border-bottom:2px solid transparent!important}
.stTabs [aria-selected="true"]{color:var(--lime-bright)!important;border-bottom:2px solid var(--lime)!important}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.1rem!important}
.score-panel{background:var(--bg-surface);border:1px solid var(--border);border-radius:10px;padding:1.5rem 1.75rem;margin-bottom:1.25rem;display:flex;gap:2rem;align-items:flex-start;flex-wrap:wrap}
.score-circle{width:90px;height:90px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:3px solid var(--lime);margin-bottom:.5rem}
.score-circle.medium{border-color:var(--amber)}.score-circle.high{border-color:var(--risk)}
.score-num{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:700;color:var(--lime);line-height:1}
.score-num.medium{color:var(--amber)}.score-num.high{color:var(--risk-text)}
.score-label{font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-dim);margin-top:2px}
.score-title{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-dim);margin-bottom:.75rem;font-weight:500}
.score-bar-row{display:flex;align-items:center;gap:10px;margin-bottom:.55rem}
.score-bar-label{font-size:.75rem;color:var(--text-sec);width:90px;flex-shrink:0}
.score-bar-track{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.score-bar-fill{height:5px;border-radius:3px}
.score-bar-val{font-size:.75rem;color:var(--text-sec);width:28px;text-align:right;flex-shrink:0}
.ai-box{background:var(--bg-card);border:1px solid var(--border-mid);border-left:3px solid var(--blue);border-radius:8px;padding:1rem 1.1rem}
.ai-box-label{font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:var(--blue)!important;margin-bottom:.5rem;font-weight:600}
.ai-box-text{font-size:.85rem;color:var(--text-sec);line-height:1.65;font-weight:300}
.stats-bar{display:flex;gap:1px;background:var(--border);border-radius:10px;overflow:hidden;margin-bottom:1.25rem}
.stat-chip{flex:1;background:var(--bg-surface);padding:.85rem 1rem}
.stat-num{font-family:'Playfair Display',serif;font-weight:700;font-size:1.5rem;color:var(--lime-bright);line-height:1}
.stat-num.risk{color:var(--risk-text)}.stat-lbl{font-size:.7rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.08em;margin-top:3px}
.news-card{background:var(--bg-card);border:1px solid var(--border);border-left:3px solid var(--lime);border-radius:8px;padding:1rem 1.25rem;margin-bottom:.65rem;transition:background .12s}
.news-card:hover{background:var(--bg-card-hov)}.news-card.risk{border-left-color:var(--risk)}.news-card.neutral{border-left-color:var(--border-mid)}
.news-card-source{font-size:.7rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--lime);margin-bottom:5px}
.news-card.risk .news-card-source{color:var(--risk-text)}
.news-card-title{font-size:.92rem;font-weight:500;color:var(--text-primary);line-height:1.55;margin-bottom:.55rem}
.news-card-title a{color:var(--text-primary);text-decoration:none}.news-card-title a:hover{color:var(--lime-bright)}
.news-card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:.75rem;color:var(--text-dim)}
.news-card-summary{color:var(--text-sec);font-size:.85rem;line-height:1.65;font-weight:300;margin-top:.5rem}
.ai-sentiment-badge{font-size:.65rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:4px;margin-left:4px}
.ai-sentiment-badge.positivo{background:rgba(90,181,39,.15);color:var(--lime-bright);border:1px solid rgba(90,181,39,.3)}
.ai-sentiment-badge.negativo{background:var(--risk-bg);color:var(--risk-text);border:1px solid var(--risk-border)}
.ai-sentiment-badge.neutro{background:var(--text-faint);color:var(--text-dim);border:1px solid var(--border)}
.ai-sentiment-badge.misto{background:var(--amber-bg);color:var(--amber);border:1px solid rgba(245,158,11,.3)}
.tag-pill{font-size:.65rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:4px;background:rgba(90,181,39,.1);color:var(--lime-bright);border:1px solid rgba(90,181,39,.2)}
.tag-pill.risk{background:var(--risk-bg);color:var(--risk-text);border-color:var(--risk-border)}
.tag-pill.neutral{background:var(--text-faint);color:var(--text-dim);border-color:var(--border)}
.section-title{font-family:'Inter',sans-serif;font-weight:500;font-size:.78rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.1em;margin:1rem 0 .8rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}
.empty-state{text-align:center;padding:4rem 1rem}
.empty-state .icon{font-size:2rem;margin-bottom:.75rem;opacity:.3}
.empty-state p{color:var(--text-dim)!important;font-size:.9rem!important}
.empty-state .title{font-family:'Playfair Display',serif;font-size:1.2rem!important;color:var(--text-sec)!important;font-weight:600}
.stDownloadButton>button{background:var(--lime)!important;color:#0a1a08!important;font-weight:600!important;border:none!important;border-radius:8px!important}
.stDataFrame{background:var(--bg-surface)!important;border:1px solid var(--border)!important;border-radius:8px!important}
.stAlert{border-radius:8px!important}
</style>
""", unsafe_allow_html=True)


# ── Helpers: fetch ─────────────────────────────────────────────────────────────
def fetch_google_news(query: str, lang: str = "pt", max_items: int = 50) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl={lang}&gl=BR&ceid=BR:{lang.upper()}"
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries[:max_items]:
        try:    pub_dt = datetime(*e.published_parsed[:6])
        except: pub_dt = None
        out.append({"title": e.get("title",""), "url": e.get("link","#"),
                    "source": e.get("source",{}).get("title","Google News"),
                    "published": pub_dt,
                    "summary": re.sub(r"<[^>]+>","",e.get("summary","")),
                    "origin": "Google News RSS"})
    return out


def fetch_newsapi(query: str, api_key: str, days_back: int = 90,
                  language: str = "pt", max_items: int = 50) -> list[dict]:
    from_date = (datetime.utcnow() - timedelta(days=min(days_back, 30))).strftime("%Y-%m-%d")
    url = (f"https://newsapi.org/v2/everything?q={quote_plus(query)}"
           f"&from={from_date}&language={language}&sortBy=relevancy"
           f"&pageSize={max_items}&apiKey={api_key}")
    try:
        data = requests.get(url, timeout=10).json()
        out = []
        for a in data.get("articles", []):
            try:    pub_dt = datetime.fromisoformat(a.get("publishedAt","").replace("Z","+00:00"))
            except: pub_dt = None
            out.append({"title": a.get("title",""), "url": a.get("url","#"),
                        "source": a.get("source",{}).get("name","NewsAPI"),
                        "published": pub_dt,
                        "summary": a.get("description") or a.get("content") or "",
                        "origin": "NewsAPI"})
        return out
    except Exception as ex:
        st.warning(f"NewsAPI indisponível: {ex}")
        return []


def deduplicate(articles):
    seen, out = set(), []
    for a in articles:
        k = a["title"][:80].lower().strip()
        if k and k not in seen:
            seen.add(k); out.append(a)
    return out


# ── ESG tagging ────────────────────────────────────────────────────────────────
ESG_KW = {
    "🌱 Ambiental":    ["carbono","emissão","clima","sustentabilidade","reciclagem","poluição",
                        "floresta","desmatamento","biodiversidade","energia renovável","aquecimento",
                        "net zero","queimada","derramamento","resíduo","água","seca","enchente",
                        "metano","eólica","solar","hidrogênio verde","compensação ambiental"],
    "👥 Social":       ["trabalhador","diversidade","inclusão","direitos humanos","trabalho infantil",
                        "trabalho escravo","saúde ocupacional","acidente de trabalho","comunidade",
                        "gênero","racial","equidade","assédio","demissão em massa","greve",
                        "salário mínimo","discriminação","bem-estar","benefícios"],
    "🏛️ Governança":  ["corrupção","compliance","transparência","auditoria","conselho","ética",
                        "fraude","lavagem","caixa dois","leniência","suborno","conflito de interesse",
                        "insider","operação policial","delação","irregularidade","anticorrupção",
                        "governança corporativa","conselheiro","código de conduta"],
    "⚠️ Risco ESG":   ["multa","embargo","escândalo","investigação","processo","denúncia","infração",
                        "acidente","vazamento","crise","suspensão","autuação","ibama","procon",
                        "anvisa","interdição","descumprimento","penalidade","dano","recall",
                        "falência","fraude fiscal","inadimplência","CVM","SEC","enforcement"],
    "📈 Positivo":     ["premiação","certificação","relatório de sustentabilidade","carbono neutro",
                        "green bond","título verde","b corp","gri","índice de sustentabilidade",
                        "impacto positivo","responsabilidade social","doação","voluntariado",
                        "net zero","renovável","economia circular","inclusão financeira"],
}


def detect_esg_tags(text: str) -> list[str]:
    tl = text.lower()
    tags = [t for t, kws in ESG_KW.items() if any(k in tl for k in kws)]
    return tags or ["📰 Geral"]


def classify_sentiment(tags):
    if "⚠️ Risco ESG" in tags: return "risk"
    if "📈 Positivo" in tags:   return "positive"
    return "neutral"


# ── ESG Risk Score ─────────────────────────────────────────────────────────────
def compute_esg_score(articles: list[dict]) -> dict:
    total = max(len(articles), 1)
    pillar = {"Ambiental": 0, "Social": 0, "Governança": 0, "Risco": 0}
    for a in articles:
        for tag in a.get("tags", []):
            if "Ambiental"  in tag: pillar["Ambiental"]  += 1
            if "Social"     in tag: pillar["Social"]     += 1
            if "Governança" in tag: pillar["Governança"] += 1
            if "Risco"      in tag: pillar["Risco"]      += 3

    def norm(v, m): return round(min(10, max(0, (v / m) * 10)), 1)
    env  = norm(pillar["Ambiental"],  total * 1.5)
    soc  = norm(pillar["Social"],     total * 1.5)
    gov  = norm(pillar["Governança"], total * 1.5)
    risk = norm(pillar["Risco"],      total * 2)

    n_risk = sum(1 for a in articles if a.get("sentiment") == "risk")
    n_pos  = sum(1 for a in articles if a.get("sentiment") == "positive")
    rp = n_risk / total; pp = n_pos / total

    glob = round(min(10, max(0, rp*6 + env*.15 + soc*.15 + gov*.2 - pp*1.5)), 1)
    level = "low" if glob < 3.5 else ("medium" if glob < 6.5 else "high")
    return {"global": glob, "level": level, "env": env, "soc": soc, "gov": gov, "risk": risk,
            "n_risk": n_risk, "n_pos": n_pos}


# ── Claude AI ──────────────────────────────────────────────────────────────────
def analyze_with_claude(company: str, articles: list[dict], api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    snippets = [f"[{i+1}] TÍTULO: {a['title']}\nRESUMO: {a['summary'][:200]}"
                for i, a in enumerate(articles[:20])]
    prompt = f"""Você é analista sênior de ESG da RB Asset Management.
Analise as notícias sobre "{company}" e retorne SOMENTE este JSON (sem markdown):
{{
  "resumo_executivo": "2-3 frases sobre o perfil ESG.",
  "principais_riscos": ["risco 1","risco 2","risco 3"],
  "pontos_positivos": ["ponto 1","ponto 2"],
  "recomendacao": "MONITORAR|ATENÇÃO|CRÍTICO|FAVORÁVEL",
  "justificativa": "Uma frase.",
  "sentimentos": {{"1":"positivo","2":"negativo"}}
}}
O campo sentimentos mapeia índice (1 a {min(20,len(articles))}) para: positivo, negativo, neutro ou misto.

NOTÍCIAS:
{"".join(chr(10)*2 + s for s in snippets)}"""
    try:
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=1200,
                                     messages=[{"role":"user","content":prompt}])
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```json|^```|```$","",raw,flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as ex:
        return {"error": str(ex)}


def render_score_panel(score, company, ai_result):
    lc = score["level"]
    ll = {"low":"BAIXO","medium":"MODERADO","high":"ALTO"}[lc]
    lcolor = {"low":"#5ab527","medium":"#f59e0b","high":"#ef4444"}[lc]

    def bar(v):
        c = "#5ab527" if v<4 else ("#f59e0b" if v<7 else "#ef4444")
        return f'<div class="score-bar-track"><div class="score-bar-fill" style="width:{v*10}%;background:{c}"></div></div>'

    ai_html = ""
    if ai_result and "error" not in ai_result:
        rec = ai_result.get("recomendacao","")
        rc  = {"FAVORÁVEL":"#5ab527","MONITORAR":"#60a5fa","ATENÇÃO":"#f59e0b","CRÍTICO":"#ef4444"}.get(rec,"#6a9e55")
        risks = "".join(f"<li>{r}</li>" for r in ai_result.get("principais_riscos",[]))
        ai_html = f"""
        <div style="flex:2;min-width:260px">
          <div class="ai-box">
            <div class="ai-box-label">✦ Análise Claude AI · {company}</div>
            <div class="ai-box-text">{ai_result.get("resumo_executivo","")}</div>
            <div style="margin-top:.75rem;font-size:.72rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.07em">Principais riscos</div>
            <ul style="margin:.3rem 0 .6rem;padding-left:1.1rem;font-size:.82rem;color:var(--text-sec);line-height:1.7">{risks}</ul>
            <div style="font-size:.75rem;font-weight:600;color:{rc};letter-spacing:.08em;text-transform:uppercase">
              Recomendação: {rec} — <span style="font-weight:300;color:var(--text-sec)">{ai_result.get("justificativa","")}</span>
            </div>
          </div>
        </div>"""

    st.markdown(f"""
    <div class="score-panel">
      <div>
        <div class="score-circle {lc}"><div class="score-num {lc}">{score['global']}</div><div class="score-label">/ 10</div></div>
        <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.09em;color:var(--text-dim);text-align:center">Risco <span style="color:{lcolor}">{ll}</span></div>
      </div>
      <div style="min-width:220px">
        <div class="score-title">Score por Pilar ESG</div>
        <div class="score-bar-row"><span class="score-bar-label">Ambiental</span>{bar(score['env'])}<span class="score-bar-val">{score['env']}</span></div>
        <div class="score-bar-row"><span class="score-bar-label">Social</span>{bar(score['soc'])}<span class="score-bar-val">{score['soc']}</span></div>
        <div class="score-bar-row"><span class="score-bar-label">Governança</span>{bar(score['gov'])}<span class="score-bar-val">{score['gov']}</span></div>
        <div class="score-bar-row"><span class="score-bar-label">Alertas</span>{bar(score['risk'])}<span class="score-bar-val">{score['risk']}</span></div>
      </div>
      {ai_html}
    </div>""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
total_sources = sum(len(v) for v in NEWS_SOURCES.values())

with st.sidebar:
    st.markdown("""<div class="rb-brand"><div class="rb-logo">RB</div><div>
    <div class="rb-brand-text-top">RB Asset</div>
    <div class="rb-brand-text-bot">ESG News Radar</div></div></div>
    <hr style="border-color:#1e3320;margin:0 0 1rem">""", unsafe_allow_html=True)

    st.markdown("#### 🔑 APIs")
    _napi = st.secrets.get("NEWSAPI_KEY","") if hasattr(st,"secrets") else ""
    newsapi_key = st.text_input("NewsAPI Key", value=_napi, type="password",
                                help="newsapi.org — histórico de 30 dias grátis")
    if _napi and not newsapi_key: newsapi_key = _napi

    _capi = st.secrets.get("ANTHROPIC_API_KEY","") if hasattr(st,"secrets") else ""
    claude_key = st.text_input("Anthropic API Key", value=_capi, type="password",
                               help="console.anthropic.com — análise IA por empresa")
    if _capi and not claude_key: claude_key = _capi

    st.markdown("---")
    st.markdown("#### 🔍 Filtros")
    language = st.selectbox("Idioma", ["pt","en","es"],
                            format_func=lambda x:{"pt":"🇧🇷 Português","en":"🇺🇸 Inglês","es":"🇪🇸 Espanhol"}[x])

    days_back = st.slider("Período (dias)", 1, 1825, 90, step=1,
                          help="Máximo 5 anos. NewsAPI gratuita: apenas 30 dias.")
    if days_back >= 365:
        st.caption(f"≈ {days_back/365:.1f} ano(s) atrás")
    else:
        st.caption(f"{days_back} dias atrás")

    esg_filter = st.multiselect("Tema ESG", list(ESG_CATEGORIES.keys()),
                                help="Vazio = todos os temas")
    extra_keywords = st.text_input("Palavras-chave extras", placeholder="ex: multa, ESG, clima...")
    max_results = st.slider("Máx. resultados por fonte", 10, 100, 50)
    use_ai = st.toggle("Análise IA (Claude)", value=bool(claude_key),
                       help="Requer Anthropic API Key")

    st.markdown("---")
    st.markdown("#### 📡 Fontes")
    st.markdown(f"**{len(NEWS_SOURCES)}** categorias · **{total_sources}** fontes")
    if st.toggle("Ver todas as fontes", False):
        for cat, srcs in NEWS_SOURCES.items():
            st.markdown(f"**{cat}**")
            for s in srcs: st.markdown(f"- {s}")

    st.markdown("---")
    st.caption("RB Asset Management · v2.0 · ESG Intelligence")


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="esg-header">
  <div>
    <div class="esg-badge">RB Asset · ESG Intelligence v2.0</div>
    <h1>News <em>Radar</em></h1>
    <p>Monitoramento, score de risco e análise IA de notícias ESG para empresas parceiras</p>
  </div>
  <div class="hdr-tags">
    <span class="hdr-tag hdr-tag-e">Ambiental</span>
    <span class="hdr-tag hdr-tag-s">Social</span>
    <span class="hdr-tag hdr-tag-g">Governança</span>
  </div>
</div>""", unsafe_allow_html=True)

c1, c2 = st.columns([5, 1])
with c1:
    company = st.text_input("Empresa", placeholder="Ex: Petrobras, Vale, BRF, Ambev, Embraer...",
                            label_visibility="collapsed")
with c2:
    search_clicked = st.button("🔍 Buscar", use_container_width=True, type="primary")

# ── Search ─────────────────────────────────────────────────────────────────────
if search_clicked and company.strip():
    qparts = [company.strip()]
    if extra_keywords: qparts.append(extra_keywords.strip())
    if esg_filter:
        kws = [k for cat in esg_filter for k in ESG_CATEGORIES[cat]]
        qparts.append(" OR ".join(kws[:8]))
    full_query = " ".join(qparts)

    with st.spinner("🔎 Buscando em centenas de fontes..."):
        arts = fetch_google_news(full_query, lang=language, max_items=max_results)
        if newsapi_key:
            arts += fetch_newsapi(full_query, newsapi_key, days_back, language, max_results)
        arts = deduplicate(arts)
        def sort_key(a):
            pub = a["published"]
            if pub is None:
                return datetime.min
            return pub.replace(tzinfo=None) if pub.tzinfo else pub
        arts.sort(key=sort_key, reverse=True)
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        arts = [a for a in arts if a["published"] is None or a["published"].replace(tzinfo=None) >= cutoff]
        for a in arts:
            a["tags"]      = detect_esg_tags(a["title"] + " " + a["summary"])
            a["sentiment"] = classify_sentiment(a["tags"])
        if esg_filter:
            tm = {"Meio Ambiente":"🌱 Ambiental","Social":"👥 Social","Governança":"🏛️ Governança",
                  "Risco":"⚠️ Risco ESG","Positivo":"📈 Positivo"}
            keep = [tm.get(f,f) for f in esg_filter]
            arts = [a for a in arts if any(t in a["tags"] for t in keep)]

    score = compute_esg_score(arts)

    ai_result, ai_sent = None, {}
    if use_ai and claude_key and arts:
        with st.spinner("✦ Claude analisando notícias com IA..."):
            ai_result = analyze_with_claude(company, arts, claude_key)
            if "error" not in ai_result:
                ai_sent = ai_result.get("sentimentos", {})

    for i, a in enumerate(arts[:20]):
        a["ai_sentiment"] = ai_sent.get(str(i+1), None)

    render_score_panel(score, company, ai_result)

    n_risk = sum(1 for a in arts if a["sentiment"]=="risk")
    n_pos  = sum(1 for a in arts if a["sentiment"]=="positive")
    n_neu  = len(arts) - n_risk - n_pos

    st.markdown(f"""<div class="stats-bar">
      <div class="stat-chip"><div class="stat-num">{len(arts)}</div><div class="stat-lbl">Notícias</div></div>
      <div class="stat-chip"><div class="stat-num risk">{n_risk}</div><div class="stat-lbl">Alertas</div></div>
      <div class="stat-chip"><div class="stat-num">{n_pos}</div><div class="stat-lbl">Positivas</div></div>
      <div class="stat-chip"><div class="stat-num">{n_neu}</div><div class="stat-lbl">Neutras</div></div>
      <div class="stat-chip"><div class="stat-num">{score['global']}</div><div class="stat-lbl">Score Risco</div></div>
    </div>""", unsafe_allow_html=True)

    tab_all, tab_risk, tab_ai, tab_export = st.tabs(
        ["📰 Todas","⚠️ Riscos","✦ Análise IA","📥 Exportar"])

    def render_articles(lst):
        if not lst:
            st.markdown('<div class="empty-state"><div class="icon">◎</div><p>Nenhuma notícia encontrada.</p></div>',
                        unsafe_allow_html=True); return
        for a in lst:
            cc  = {"risk":"news-card risk","positive":"news-card","neutral":"news-card neutral"}.get(a["sentiment"],"news-card")
            pub = a["published"].strftime("%d/%m/%Y") if a["published"] else "—"
            tgs = "".join(f'<span class="tag-pill {"risk" if "Risco" in t else ("neutral" if "Geral" in t else "")}">{t}</span>' for t in a["tags"])
            aib = f'<span class="ai-sentiment-badge {a["ai_sentiment"]}">IA: {a["ai_sentiment"]}</span>' if a.get("ai_sentiment") else ""
            sm  = a["summary"][:300]+("..." if len(a["summary"])>300 else "")
            st.markdown(f"""<div class="{cc}">
              <div class="news-card-source">{a['source']}</div>
              <div class="news-card-title"><a href="{a['url']}" target="_blank">{a['title']}</a></div>
              <div class="news-card-meta"><span>{pub}</span><span>·</span><span>{a['origin']}</span><span style="margin-left:4px">{tgs}</span>{aib}</div>
              <div class="news-card-summary">{sm}</div></div>""", unsafe_allow_html=True)

    with tab_all:
        st.markdown(f'<div class="section-title">Resultados para: {company} — {len(arts)} notícias</div>',
                    unsafe_allow_html=True)
        render_articles(arts)

    with tab_risk:
        ra = [a for a in arts if a["sentiment"]=="risk"]
        st.markdown(f'<div class="section-title">Alertas de Risco ESG — {len(ra)} notícias</div>',
                    unsafe_allow_html=True)
        render_articles(ra)

    with tab_ai:
        if not claude_key:
            st.info("Configure a **Anthropic API Key** na sidebar para ativar a análise com IA.")
        elif ai_result is None:
            st.info("Ative o toggle **Análise IA** na sidebar e busque novamente.")
        elif "error" in ai_result:
            st.error(f"Erro na API Claude: {ai_result['error']}")
        else:
            rec = ai_result.get("recomendacao","")
            rc  = {"FAVORÁVEL":"#5ab527","MONITORAR":"#60a5fa","ATENÇÃO":"#f59e0b","CRÍTICO":"#ef4444"}.get(rec,"#6a9e55")
            st.markdown('<div class="section-title">✦ Análise de Sentimento e Risco · Claude AI</div>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Resumo Executivo**")
                st.markdown(ai_result.get("resumo_executivo",""))
                st.markdown("**Principais Riscos**")
                for r in ai_result.get("principais_riscos",[]): st.markdown(f"- {r}")
            with c2:
                st.markdown("**Pontos Positivos**")
                for p in ai_result.get("pontos_positivos",[]): st.markdown(f"- {p}")
                st.markdown(f"**Recomendação:** <span style='color:{rc};font-weight:600'>{rec}</span>",
                            unsafe_allow_html=True)
                st.markdown(ai_result.get("justificativa",""))
            st.markdown("---")
            st.markdown("**Sentimento por Artigo (primeiros 20)**")
            for i, a in enumerate(arts[:20]):
                s = ai_sent.get(str(i+1),"neutro")
                icon = {"positivo":"✅","negativo":"🔴","neutro":"⬜","misto":"🟡"}.get(s,"⬜")
                st.markdown(f"{icon} **{s.upper()}** — [{a['title'][:90]}...]({a['url']})")

    with tab_export:
        st.markdown('<div class="section-title">Exportar Resultados</div>', unsafe_allow_html=True)
        if arts:
            df = pd.DataFrame([{
                "Empresa": company, "Título": a["title"], "Fonte": a["source"],
                "Data": a["published"].strftime("%Y-%m-%d") if a["published"] else "",
                "URL": a["url"], "Tags ESG": ", ".join(a["tags"]),
                "Sentimento": a["sentiment"], "Sentimento IA": a.get("ai_sentiment",""),
                "Resumo": a["summary"][:300],
                "Score Global": score["global"], "Score Ambiental": score["env"],
                "Score Social": score["soc"], "Score Governança": score["gov"],
            } for a in arts])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV completo", data=csv,
                               file_name=f"esg_{company.replace(' ','_')}_{datetime.today().strftime('%Y%m%d')}.csv",
                               mime="text/csv", use_container_width=True)
            st.dataframe(df, use_container_width=True, height=400)

elif search_clicked:
    st.warning("Digite o nome de uma empresa para iniciar a busca.")
else:
    st.markdown("""<div class="empty-state">
      <div class="icon">◎</div>
      <p class="title">ESG News Radar</p>
      <p>Digite o nome de uma empresa parceira e clique em Buscar<br>
         para análise completa com score de risco e inteligência artificial.</p>
    </div>""", unsafe_allow_html=True)
