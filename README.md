# ESG-News-Radar

# 🌿 ESG News Radar

Ferramenta de monitoramento de notícias ESG para análise de empresas parceiras.

## 🚀 Como rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/esg-news-radar.git
cd esg-news-radar

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode o app
streamlit run app.py
```

## 🔑 NewsAPI (opcional, recomendado)

Para resultados mais abrangentes, obtenha uma chave gratuita em [newsapi.org](https://newsapi.org) e insira na sidebar do app.

- Plano gratuito: 100 requisições/dia, últimos 30 dias
- Plano pago: sem limites, histórico completo

**Sem a chave**, o app ainda funciona via **Google News RSS** — sem limite de uso.

## 📁 Estrutura

```
esg-news-radar/
├── app.py            # App principal Streamlit
├── sources.py        # Base de fontes e categorias ESG
├── requirements.txt  # Dependências Python
└── README.md
```

## ✨ Funcionalidades

| Recurso | Descrição |
|---|---|
| 🔍 Busca por empresa | Pesquise qualquer empresa parceira |
| 🌱 Filtros ESG | Meio Ambiente, Social, Governança, Risco, Positivo |
| 📅 Filtro de data | Últimos 1 a 90 dias |
| 🌐 Multi-idioma | Português, Inglês, Espanhol |
| ⚠️ Alertas de risco | Destaque automático de notícias negativas |
| 📥 Exportação CSV | Baixe os resultados para análise |
| 📡 200+ fontes | Google News RSS + NewsAPI |

## 🏷️ Detecção automática de tags ESG

O app analisa cada notícia e classifica automaticamente em:
- 🌱 Meio Ambiente
- 👥 Social
- 🏛️ Governança
- ⚠️ Risco ESG
- 📈 Positivo ESG

## 🗂️ Fontes incluídas (200+)

- **Brasil**: Folha, Estadão, Globo, Valor Econômico, Exame, Envolverde, ConJur, IBAMA...
- **ESG Global**: ESG Today, GreenBiz, Carbon Brief, Bloomberg Green, FT Moral Money...
- **América Latina**: América Economía, Bloomberg Línea, El País...
- **Supply Chain**: Compliance Week, TRACE International, FCPAméricas...
- **Dados & Análise**: CDP, GRI, MSCI ESG, Sustainalytics...

## 🛣️ Roadmap sugerido

- [ ] Cache de resultados (Redis / SQLite)
- [ ] Alertas por e-mail (novidades sobre empresa monitorada)
- [ ] Dashboard de risco ESG com score por empresa
- [ ] Integração com Serasa/Bureau de crédito ESG
- [ ] Análise de sentimento com IA (Anthropic Claude API)
- [ ] Comparativo entre empresas
