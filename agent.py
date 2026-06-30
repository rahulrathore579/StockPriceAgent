"""
agent.py
--------
LangChain ReAct agent powered by Groq LLM.
Capable of finding real-time and historical stock prices for any company.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

# ── Version-safe imports (LangChain 0.2 / 0.3 compatibility) ─────────────────
try:
    from langchain.agents import AgentExecutor, create_react_agent
except ImportError:
    from langchain.agents.agent import AgentExecutor          # type: ignore
    from langchain.agents.react.agent import create_react_agent  # type: ignore

from tools import ALL_TOOLS

# ── Load environment variables ────────────────────────────────────────────────
# override=True ensures .env always wins over any stale shell/session env vars
load_dotenv(override=True)


# ── System prompt / ReAct template ───────────────────────────────────────────
REACT_TEMPLATE = """You are a knowledgeable financial assistant specialized in
retrieving real-time and historical stock market data for companies worldwide.

You have access to the following tools:

{tools}

## Guidelines
- If the user mentions a company name (not a ticker), use the
  `search_ticker_by_company_name` tool FIRST to find the correct ticker symbol.
- Once you have the ticker, use `get_current_stock_price` to fetch the current price.
- For historical trends use `get_stock_history` with the appropriate period.
- Always present prices with the correct currency symbol.
- If a ticker is ambiguous (e.g., same company listed on multiple exchanges),
  mention both options (e.g., NSE and BSE suffixes for Indian stocks).
- Never make up financial data — always rely on tool output.

## Output Format
Use the following format strictly:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

PROMPT = PromptTemplate.from_template(REACT_TEMPLATE)


def build_agent(model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
    """
    Construct and return a LangChain AgentExecutor backed by Groq LLM.

    Args:
        model:       Groq model ID. Defaults to 'llama-3.3-70b-versatile'.
                     Other options: 'llama-3.1-70b-versatile', 'llama-3.1-8b-instant'
        temperature: Sampling temperature (0 = deterministic).

    Returns:
        A configured AgentExecutor ready to receive queries.

    Raises:
        ValueError: If GROQ_API_KEY is missing from the environment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Get your free key at https://console.groq.com/keys "
            "then add it to your .env file."
        )

    # Set env var explicitly so the Groq SDK always picks it up
    os.environ["GROQ_API_KEY"] = api_key

    llm = ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=api_key,
    )

    agent = create_react_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=PROMPT,
    )

    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,            # show Thought / Action / Observation steps
        handle_parsing_errors=True,
        max_iterations=10,
    )
