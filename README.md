# 📈 Stock Price Agent — LangChain + Groq

A conversational AI agent that fetches **real-time and historical share prices** for any company worldwide, powered by [LangChain](https://www.langchain.com/) and [Groq](https://groq.com/).

---

## ✨ Features

| Capability | Description |
|---|---|
| **Current Price** | Fetch live share price, 52-week high/low, and market cap |
| **Historical Data** | Get OHLCV history for periods from 1 day to all-time |
| **Ticker Lookup** | Find ticker symbols by company name (supports US, NSE, BSE) |
| **Groq LLM** | Ultra-fast inference with `llama3-70b-8192` |
| **ReAct Agent** | Thinks step-by-step, calls tools as needed |

---

## 🏗️ Project Structure

```
stock-price-agent/
├── agent.py              # LangChain ReAct agent (Groq LLM + tools)
├── main.py               # Interactive CLI entry-point
├── test_agent.py         # Unit tests (no API calls needed)
├── tools/
│   ├── __init__.py       # Exports ALL_TOOLS list
│   └── stock_tools.py    # 3 custom @tool functions (yfinance)
├── requirements.txt
├── .env.example          # Template — copy to .env and add your key
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd stock-price-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Groq API key

```bash
cp .env.example .env
# Open .env and replace 'your_groq_api_key_here' with your actual key
```

Get your free Groq API key at 👉 [https://console.groq.com/keys](https://console.groq.com/keys)

### 5. Run the agent

```bash
python main.py
```

---

## 💬 Example Conversations

```
You: What is the current share price of Apple?

> Entering new AgentExecutor chain...
Thought: The user wants the current price of Apple. Let me find the ticker first.
Action: search_ticker_by_company_name
Action Input: Apple
Observation: Possible ticker(s) for 'Apple': Apple → AAPL
Thought: Now I'll fetch the current price for AAPL.
Action: get_current_stock_price
Action Input: AAPL
Observation: 📈 Stock Information for Apple Inc. (AAPL)
  Exchange       : NMS
  Current Price  : USD 213.49
  52-Week High   : USD 237.23
  52-Week Low    : USD 164.08
  Market Cap     : 3.19T

🤖 Agent: Apple Inc. (AAPL) is currently trading at USD 213.49.
         Its 52-week range is USD 164.08 – USD 237.23 with a market cap of $3.19 Trillion.
```

```
You: Show me 3 months history of Reliance Industries

🤖 Agent: 📊 RELIANCE.NS — 3mo History
  Start Price : 2,850.00
  End Price   : 2,935.40
  Period High : 3,020.10
  Period Low  : 2,790.00
  Change      : +2.99% 📈 UP
```

---

## 🛠️ Available Tools

| Tool | Description |
|---|---|
| `get_current_stock_price` | Live price + fundamentals for any ticker |
| `get_stock_history` | Historical OHLCV data (1d to max) |
| `search_ticker_by_company_name` | Map company name → ticker symbol |

---

## 🧪 Running Tests

```bash
python test_agent.py
```

Tests use mocked `yfinance` calls — no internet or API key required.

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `model` (in `agent.py`) | `llama3-70b-8192` | Groq model ID |
| `temperature` | `0.0` | LLM temperature (0 = deterministic) |

Other supported Groq models: `mixtral-8x7b-32768`, `gemma2-9b-it`, `llama3-8b-8192`

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `langchain` | Agent orchestration framework |
| `langchain-groq` | Groq LLM integration |
| `langchain-community` | Community tool utilities |
| `yfinance` | Real-time & historical stock data |
| `python-dotenv` | `.env` file loading |

---

## 📄 License

MIT License — feel free to use, modify and distribute.
