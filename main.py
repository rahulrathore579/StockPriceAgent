"""
main.py
-------
Interactive CLI entry-point for the Stock Price Agent.
Run with:  python main.py

If GOOGLE_API_KEY is missing from .env, the user is prompted to
enter it once -- it is then saved to .env automatically.
"""

import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv, set_key

# ── Force UTF-8 output on Windows (fixes UnicodeEncodeError) ─────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Load .env first ─────────────────────────────────────────────────
ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

BANNER = """
+------------------------------------------------------+
|   [STOCK AGENT]  Stock Price Agent (LangChain+Gemini)|
|   Ask me about any company's share price!            |
+------------------------------------------------------+
Type 'exit' or 'quit' to stop.
"""

EXAMPLE_QUERIES = [
    "What is the current share price of Apple?",
    "Show me TCS stock price",
    "Give me the 1-month history of Tesla",
    "What is RELIANCE.NS trading at right now?",
]


def print_examples() -> None:
    print("\n💡 Example queries you can try:")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print()


def ensure_api_key() -> str:
    """
    Return the Groq API key.
    If it is not in the environment, prompt the user to paste it,
    validate it is non-empty, then persist it to .env automatically.
    """
    key = os.getenv("GROQ_API_KEY", "").strip()

    if key and key != "your_groq_api_key_here":
        return key

    print("\n" + "─" * 56)
    print("🔑  Groq API Key not found in your .env file.")
    print("    Get a FREE key at: https://console.groq.com/keys")
    print("─" * 56)

    while True:
        try:
            key = input("\nPaste your Groq API Key here: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)

        if not key:
            print("⚠️  Key cannot be empty. Please try again.")
            continue

        # Save to .env so the user never has to do this again
        ENV_FILE.touch(exist_ok=True)
        set_key(str(ENV_FILE), "GROQ_API_KEY", key)
        os.environ["GROQ_API_KEY"] = key
        print(f"\n✅ Key saved to .env — you won't be asked again!\n")
        return key


def main() -> None:
    print(BANNER)

    # ── Ensure API key is available before importing agent ───────────────────
    ensure_api_key()

    # ── Import and build agent (after key is guaranteed in env) ─────────────
    from agent import build_agent

    print_examples()

    try:
        agent_executor = build_agent()
    except ValueError as exc:
        print(f"\n❌ Configuration error: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌ Failed to build agent: {exc}")
        sys.exit(1)

    print("Agent is ready! Ask your first question:\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "q", "bye"}:
            print("Goodbye! 👋")
            break

        print()
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Agent: {result['output']}\n")
            print("─" * 56)
        except Exception as exc:
            print(f"\n⚠️  An error occurred: {exc}\n")


if __name__ == "__main__":
    main()
