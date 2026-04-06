# sources.py — Base colossal de fontes de notícias ESG

# ── ESG Keyword Categories ─────────────────────────────────────────────────────
ESG_CATEGORIES = {
    "Meio Ambiente": [
        "carbono", "emissão", "clima", "aquecimento global", "desmatamento",
        "biodiversidade", "poluição", "energia renovável", "reciclagem",
        "sustentabilidade ambiental", "queimada", "lixo", "resíduo", "net zero",
    ],
    "Social": [
        "trabalhador", "acidente de trabalho", "diversidade", "inclusão",
        "direitos humanos", "trabalho infantil", "trabalho escravo", "saúde",
        "comunidade", "gênero", "racial", "equidade", "bem-estar",
    ],
    "Governança": [
        "corrupção", "compliance", "transparência", "auditoria", "ética",
        "conselho", "fraude", "bribery", "lavagem de dinheiro", "conflito de interesse",
        "leniência", "caixa dois", "desvio",
    ],
    "Risco": [
        "multa", "embargo", "investigação", "processo judicial", "denúncia",
        "infração", "vazamento", "acidente", "desastre", "crise", "escândalo",
        "suspensão", "autuação", "ibama", "procon", "anvisa",
    ],
    "Positivo": [
        "premiação esg", "certificação", "relatório de sustentabilidade",
        "carbono neutro", "net zero", "índice de sustentabilidade",
        "green bond", "título verde", "isb", "b corp", "gri",
    ],
}

# ── News Sources Database ──────────────────────────────────────────────────────
NEWS_SOURCES = {

    # ── Brasil — Geral ─────────────────────────────────────────────────────────
    "🇧🇷 Brasil — Grandes Veículos": [
        "Folha de S.Paulo (folha.uol.com.br)",
        "O Globo (oglobo.globo.com)",
        "Estadão (estadao.com.br)",
        "UOL Notícias (noticias.uol.com.br)",
        "G1 / Globo News (g1.globo.com)",
        "CNN Brasil (cnnbrasil.com.br)",
        "R7 (r7.com)",
        "Terra (terra.com.br)",
        "Metrópoles (metropoles.com)",
        "Correio Braziliense (correiobraziliense.com.br)",
        "O Tempo (otempo.com.br)",
        "A Tarde (atarde.com.br)",
        "Diário de Pernambuco (diariodepernambuco.com.br)",
        "Gazeta do Povo (gazetadopovo.com.br)",
        "Zero Hora (gauchazh.clicrbs.com.br)",
        "O Dia (odia.com.br)",
        "Band News (bandnewsfm.com.br)",
    ],

    # ── Brasil — Negócios & Finanças ───────────────────────────────────────────
    "🇧🇷 Brasil — Negócios & Finanças": [
        "Valor Econômico (valor.com.br)",
        "InfoMoney (infomoney.com.br)",
        "Exame (exame.com)",
        "Bloomberg Línea Brasil (bloomberglinea.com.br)",
        "The Brazilian Report (brazilian.report)",
        "Poder360 (poder360.com.br)",
        "NeoFeed (neofeed.com.br)",
        "Pipeline / Valor Econômico (pipelinevalor.com.br)",
        "Startups (startups.com.br)",
        "IstoÉ Dinheiro (istoedinheiro.com.br)",
        "Veja Negócios (veja.abril.com.br/coluna/negócios)",
        "Mercado & Consumo (mercadoeconsumo.com.br)",
        "Monitor do Mercado (monitormercado.com.br)",
        "Agência Estado (estadao.com.br/economia)",
    ],

    # ── Brasil — ESG & Sustentabilidade ───────────────────────────────────────
    "🇧🇷 Brasil — ESG & Sustentabilidade": [
        "Época Negócios — Sustentabilidade (epocanegocios.globo.com)",
        "Envolverde (envolverde.com.br)",
        "Planeta Sustentável (planetasustentavel.com.br)",
        "ESG Insights (esginsights.com.br)",
        "Sustainable Business (sustainablebusiness.com.br)",
        "Exame ESG (exame.com/esg)",
        "Valor Econômico — ESG (valor.com.br/esg)",
        "IstoÉ — Sustentabilidade (istoe.com.br/sustentabilidade)",
        "Portal do Agronegócio (portaldoagronegocio.com.br)",
        "Carbono Brasil (carbonobrasil.com)",
        "Amazônia Real (amazoniareal.com.br)",
        "InfoAmazônia (infoamazonia.org)",
        "((o))eco (oeco.org.br)",
        "Mongabay Brasil (brasil.mongabay.com)",
        "Nexo Jornal — Meio Ambiente (nexojornal.com.br)",
        "Agência Pública (apublica.org)",
    ],

    # ── Brasil — Setoriais ────────────────────────────────────────────────────
    "🇧🇷 Brasil — Setoriais": [
        "Canal Energia (canalenergia.com.br)",
        "Petroquímica (petroquimica.com.br)",
        "Minérios & Minerales (minerioseminerales.com.br)",
        "Portal PCH (portalpchnoticias.com.br)",
        "Agrolink (agrolink.com.br)",
        "Notícias Agrícolas (noticiasagricolas.com.br)",
        "Canal Rural (canalrural.com.br)",
        "CanalSaúde (canalsaude.fiocruz.br)",
        "Saneamento Ambiental (saneamentoambiental.com.br)",
        "Construção Mercado (construcaomercado.com.br)",
        "Logística Descomplicada (logisticadescomplicada.com)",
        "TI Inside (tiinside.com.br)",
        "Automotive Business (automotivebusiness.com.br)",
        "Super Varejo (supervarejo.com.br)",
    ],

    # ── Brasil — Jurídico & Regulatório ───────────────────────────────────────
    "🇧🇷 Brasil — Jurídico & Regulatório": [
        "Consultor Jurídico — ConJur (conjur.com.br)",
        "Migalhas (migalhas.com.br)",
        "Jota (jota.info)",
        "Direito Net (direitonet.com.br)",
        "Compliance Total (compliancetotal.com.br)",
        "Agência Senado (agencia.senado.leg.br)",
        "TCU — Tribunal de Contas da União (tcu.gov.br)",
        "Receita Federal (gov.br/receitafederal)",
        "IBAMA (ibama.gov.br)",
        "MMA — Ministério do Meio Ambiente (gov.br/mma)",
    ],

    # ── Internacional — Global ────────────────────────────────────────────────
    "🌍 Internacional — Global": [
        "Reuters (reuters.com)",
        "Bloomberg (bloomberg.com)",
        "Financial Times (ft.com)",
        "The Wall Street Journal (wsj.com)",
        "Associated Press (apnews.com)",
        "BBC News (bbc.com/news)",
        "The Guardian (theguardian.com)",
        "The New York Times (nytimes.com)",
        "CNN International (edition.cnn.com)",
        "Al Jazeera (aljazeera.com)",
        "Deutsche Welle (dw.com)",
        "France 24 (france24.com)",
        "CNBC (cnbc.com)",
        "Forbes (forbes.com)",
        "Fortune (fortune.com)",
        "The Economist (economist.com)",
        "Time (time.com)",
        "Axios (axios.com)",
        "Politico (politico.com)",
    ],

    # ── Internacional — ESG & Sustentabilidade ────────────────────────────────
    "🌍 Internacional — ESG & Sustentabilidade": [
        "ESG Today (esgtoday.com)",
        "GreenBiz (greenbiz.com)",
        "Responsible Investor (responsible-investor.com)",
        "Environmental Finance (environmental-finance.com)",
        "Carbon Brief (carbonbrief.org)",
        "Climate Home News (climatechangenews.com)",
        "BusinessGreen (businessgreen.com)",
        "Triple Pundit (triplepundit.com)",
        "Sustainable Brands (sustainablebrands.com)",
        "Corporate Knights (corporateknights.com)",
        "The Business of Sustainability (sustainabilitymag.com)",
        "ESG Clarity (esgclarity.com)",
        "Impakter (impakter.com)",
        "Ethical Corporation (ethicalcorp.com)",
        "Sustainability Magazine (sustainabilitymag.com)",
        "Bloomberg Green (bloomberg.com/green)",
        "Reuters — Sustainability (reuters.com/sustainability)",
        "FT — Moral Money (ft.com/moral-money)",
        "MSCI ESG Research (msci.com/esg)",
        "S&P Global ESG (spglobal.com/esg)",
    ],

    # ── Internacional — Supply Chain & Compliance ─────────────────────────────
    "🌍 Internacional — Supply Chain & Compliance": [
        "Supply Chain Dive (supplychaindive.com)",
        "Logistics Management (logisticsmgmt.com)",
        "Supply Management (cips.org/supply-management)",
        "Global Trade Magazine (globaltrademag.com)",
        "Trade Finance Global (tradefinanceglobal.com)",
        "Compliance Week (complianceweek.com)",
        "Global Compliance News (globalcompliancenews.com)",
        "Anti-Corruption Digest (anti-corruptiondigest.com)",
        "TRACE International (traceinternational.org)",
        "FCPAméricas (fcpamericas.com)",
    ],

    # ── América Latina ────────────────────────────────────────────────────────
    "🌎 América Latina": [
        "América Economía (americaeconomia.com)",
        "El País América (elpais.com/america)",
        "Infobae (infobae.com)",
        "La Nación Argentina (lanacion.com.ar)",
        "El Comercio Perú (elcomercio.pe)",
        "El Espectador Colombia (elespectador.com)",
        "La República Colombia (larepublica.co)",
        "El Financiero México (elfinanciero.com.mx)",
        "Expansión México (expansion.mx)",
        "Bloomberg Línea (bloomberglinea.com)",
        "Diálogo Chino (dialogochino.net)",
    ],

    # ── Agências de Análise & Dados ───────────────────────────────────────────
    "📊 Dados & Análise": [
        "Refinitiv ESG (refinitiv.com/esg)",
        "Moody's ESG (moodys.com/esg)",
        "Sustainalytics (sustainalytics.com)",
        "ISS ESG (issgovernance.com/esg)",
        "Vigeo Eiris (vigeo-eiris.com)",
        "MSCI ESG (msci.com/esg-investing)",
        "CDP — Carbon Disclosure (cdp.net)",
        "GRI (globalreporting.org)",
        "SASB (sasb.org)",
        "UN Global Compact (unglobalcompact.org)",
        "World Resources Institute (wri.org)",
        "IPCC (ipcc.ch)",
    ],
}
