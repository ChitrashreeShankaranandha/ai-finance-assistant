# 💰 AI Finance Assistant

> Democratizing Financial Literacy Through Intelligent Conversational AI

---

## 🎯 Project Overview

The AI Finance Assistant is a production-ready multi-agent AI system designed to democratize financial literacy for beginner investors. It combines real-time market data, a curated financial knowledge base, and intelligent conversational AI to provide personalized guidance on investing, portfolio management, tax education, and financial goal planning — all while maintaining strict educational guardrails to ensure responsible use.

---

## 🏗️ Architecture

User Query
↓
[LLM Security Layer]  ← prompt injection detection, rate limiting
↓
[LangGraph Router]    ← intelligently routes to the right agent
↓
| Agent | Data Source |
|-------|------------|
| 📊 Portfolio Agent | Portfolio CSV + yFinance |
| 💹 Trading Agent | yFinance + CSV |
| 🎯 Portfolio Advisor | GPT + RAG |
| 📈 Market Analysis Agent | yFinance + GPT |
| 🎯 Goal Planning Agent | Math + GPT |
| 📰 News Synthesizer Agent | yFinance + RAG + GPT |
| 💰 Tax Education Agent | Pinecone RAG + GPT |

---

## 🤖 The 7 Specialized Agents

| Agent | Purpose | Tech |
|-------|---------|------|
| **Portfolio Agent** | Loads and analyzes user portfolio with live prices | yFinance + GPT |
| **Trading Agent** | Simulates buying and selling stocks | yFinance + CSV |
| **Portfolio Advisor** | Educational portfolio recommendations | GPT + RAG |
| **Market Analysis Agent** | Real-time stock data and beginner-friendly insights | yFinance + GPT |
| **Goal Planning Agent** | Financial goal calculator with risk profiles | Math + GPT |
| **News Synthesizer Agent** | Live news headlines with AI synthesis | yFinance + RAG + GPT |
| **Tax Education Agent** | RAG-powered tax education with guardrails | Pinecone + GPT |

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language Model | OpenAI GPT-4o-mini |
| Agent Orchestration | LangGraph + LangChain |
| Vector Database | Pinecone |
| Market Data | yFinance |
| Web Interface | Streamlit |
| LLM Security | Custom security layer |
| MCP Server | Model Context Protocol |
| Testing | pytest |

---

## 📁 Project Structure

ai-finance-assistant/
├── src/
│   ├── agents/
│   │   ├── portfolio_agent.py
│   │   ├── trading_agent.py
│   │   ├── portfolio_advisor_agent.py
│   │   ├── market_analysis_agent.py
│   │   ├── goal_planning_agent.py
│   │   ├── news_synthesizer_agent.py
│   │   └── tax_education_agent.py
│   ├── core/
│   │   ├── openai_client.py
│   │   └── security.py
│   ├── data/
│   │   ├── demo_portfolio.csv
│   │   ├── demo_portfolio_backup.csv
│   │   └── finance_knowledge.py
│   ├── mcp_server/
│   │   └── finance_mcp_server.py
│   ├── rag/
│   │   ├── embedding.py
│   │   ├── index_data.py
│   │   ├── pinecone_client.py
│   │   └── retriever.py
│   ├── utils/
│   │   └── market_data.py
│   ├── web_app/
│   │   └── app.py
│   └── workflow/
│       └── finance_workflow.py
├── tests/
│   ├── test_agents.py
│   ├── test_security.py
│   └── test_workflow.py
├── .env.example
├── config.yaml
├── requirements.txt
└── README.md

---

## 🔐 LLM Security Layer

The system includes a comprehensive security layer that protects against:

- **Prompt Injection** — detects and blocks attempts to override system instructions
- **Harmful Content** — blocks requests for illegal financial advice (market manipulation, insider trading)
- **Off-topic Queries** — redirects non-finance questions with helpful guidance
- **Output Validation** — ensures responses don't contain direct investment advice or guaranteed returns
- **Rate Limiting** — prevents abuse with configurable request limits per user

---

## 🧠 RAG Knowledge Base

- **55 financial education documents** across 6 categories:
  - 📚 Basics — investing fundamentals, ETFs, dividends, compound interest
  - 💼 Portfolio — diversification, asset allocation, rebalancing, risk
  - 🎯 Planning — retirement, goal setting, debt payoff, savings
  - 💰 Tax — IRA, 401k, capital gains, tax-loss harvesting
  - 📈 Market — P/E ratio, volatility, Fed, sectors, technical analysis
  - 📰 News — earnings season, economic indicators, geopolitical risk
- Indexed in Pinecone vector database
- Semantic search retrieves most relevant docs for each query

---

## 🖥️ Streamlit UI — 5 Tabs

| Tab | Features |
|-----|---------|
| 💬 Finance Chat | Conversational AI with automatic agent routing |
| 📊 Portfolio | Manual editor, live analysis, pie chart, gain/loss chart, trading panel |
| 📈 Market Analysis | Company name resolution, live prices, 52W gauge chart |
| 🎯 Goal Planner | Interactive calculator, projection chart, risk profiles |
| 📰 News | Live headlines, expandable cards, AI synthesis |

---

## 🔌 MCP Server — Claude Desktop Integration

Exposes 5 finance tools to Claude Desktop via Model Context Protocol:

| Tool | Description |
|------|-------------|
| `get_stock_info` | Real-time stock price and analysis |
| `analyze_portfolio` | Portfolio summary with live prices |
| `calculate_goal` | Financial goal projection calculator |
| `get_stock_news` | Latest news headlines with AI synthesis |
| `answer_finance_question` | General finance Q&A via RAG |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- OpenAI API key
- Pinecone API key

### Installation

```bash
# Clone the repository
git clone https://github.com/ChitrashreeShankaranandha/ai-finance-assistant.git
cd ai-finance-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Then edit .env and add your API keys
```

### Running the App

```bash
streamlit run src/web_app/app.py
```

### Running Tests

```bash
pytest tests/ -v
```

### MCP Server Setup (Claude Desktop)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-finance-assistant": {
      "command": "/path/to/venv/Scripts/python.exe",
      "args": ["/path/to/src/mcp_server/finance_mcp_server.py"],
      "cwd": "/path/to/ai-finance-assistant"
    }
  }
}
```

---

## 🧪 Testing

40 tests across 3 test files:
├── test_agents.py    → 12 tests (market, goal, tax, news agents)
├── test_security.py  → 24 tests (injection, harmful content, rate limiting)
└── test_workflow.py  →  4 tests (LangGraph routing)

---

## ⚠️ Disclaimer

This system is for **educational purposes only** and does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## 🔮 Future Directions

- **User Authentication** — private portfolios per user with Streamlit Authenticator
- **Cloud Database** — PostgreSQL/Supabase for persistent multi-user portfolios
- **Voice Interface** — natural speech interaction
- **Mobile App** — native iOS/Android apps
- **Advanced Analytics** — Monte Carlo simulations, risk modeling
- **International Markets** — support for global exchanges
- **Cryptocurrency** — digital asset education and analysis

---

## 👩‍💻 Author

**Chitrashree Shankaranandha**  
Built with passion for making financial literacy accessible to everyone.  
[GitHub](https://github.com/ChitrashreeShankaranandha) · [LinkedIn](https://www.linkedin.com/in/chitrashreeshankaranandha/)
