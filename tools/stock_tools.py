"""
tools/stock_tools.py
--------------------
Custom LangChain tools for fetching real-time and historical
share price data using the yfinance library.
"""

import yfinance as yf
from langchain.tools import tool


@tool
def get_current_stock_price(ticker: str) -> str:
    """
    Fetch the CURRENT (latest) share price of a company.

    Args:
        ticker: The stock ticker symbol (e.g. 'AAPL' for Apple,
                'RELIANCE.NS' for Reliance Industries on NSE,
                'TCS.NS' for TCS on NSE).

    Returns:
        A formatted string with the current price, currency,
        52-week high/low and market cap.
    """
    try:
        ticker = ticker.strip().upper()
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        if current_price is None:
            return (
                f"Could not retrieve price for '{ticker}'. "
                "Please verify the ticker symbol is correct "
                "(e.g., 'AAPL', 'RELIANCE.NS', 'TCS.BO')."
            )

        currency     = info.get("currency", "USD")
        company_name = info.get("longName") or info.get("shortName", ticker)
        week52_high  = info.get("fiftyTwoWeekHigh", "N/A")
        week52_low   = info.get("fiftyTwoWeekLow",  "N/A")
        market_cap   = info.get("marketCap", "N/A")
        exchange     = info.get("exchange", "N/A")

        if market_cap != "N/A":
            if market_cap >= 1_000_000_000_000:
                market_cap = f"{market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                market_cap = f"{market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                market_cap = f"{market_cap / 1_000_000:.2f}M"

        return (
            f"📈 Stock Information for {company_name} ({ticker})\n"
            f"  Exchange       : {exchange}\n"
            f"  Current Price  : {currency} {current_price:,.2f}\n"
            f"  52-Week High   : {currency} {week52_high}\n"
            f"  52-Week Low    : {currency} {week52_low}\n"
            f"  Market Cap     : {market_cap}"
        )

    except Exception as exc:
        return f"Error fetching data for '{ticker}': {exc}"


@tool
def get_stock_history(query: str) -> str:
    """
    Fetch the HISTORICAL share price data for a company.

    Args:
        query: A string in the format 'TICKER PERIOD', where PERIOD is one of:
               1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
               Example: 'AAPL 1mo'  or  'TCS.NS 6mo'

    Returns:
        A summary of the historical OHLCV data.
    """
    try:
        parts = query.strip().split()
        if len(parts) < 2:
            return (
                "Please provide both a ticker and a period. "
                "Example: 'AAPL 1mo' or 'TCS.NS 6mo'."
            )

        ticker = parts[0].upper()
        period = parts[1].lower()

        valid_periods = {"1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"}
        if period not in valid_periods:
            return (
                f"Invalid period '{period}'. "
                f"Choose from: {', '.join(sorted(valid_periods))}."
            )

        stock = yf.Ticker(ticker)
        hist  = stock.history(period=period)

        if hist.empty:
            return f"No historical data found for '{ticker}' over period '{period}'."

        start_price = hist["Close"].iloc[0]
        end_price   = hist["Close"].iloc[-1]
        high_price  = hist["High"].max()
        low_price   = hist["Low"].min()
        avg_volume  = hist["Volume"].mean()
        pct_change  = ((end_price - start_price) / start_price) * 100
        trend       = "📈 UP" if pct_change >= 0 else "📉 DOWN"

        return (
            f"📊 Historical Data for {ticker} — Period: {period}\n"
            f"  Start Price  : {start_price:,.2f}\n"
            f"  End Price    : {end_price:,.2f}\n"
            f"  Period High  : {high_price:,.2f}\n"
            f"  Period Low   : {low_price:,.2f}\n"
            f"  Avg Volume   : {avg_volume:,.0f}\n"
            f"  Change       : {pct_change:+.2f}% ({trend})\n"
            f"  Data Points  : {len(hist)} trading sessions"
        )

    except Exception as exc:
        return f"Error fetching historical data for '{query}': {exc}"


@tool
def search_ticker_by_company_name(company_name: str) -> str:
    """
    Attempt to find the stock ticker symbol for a given company name.

    Args:
        company_name: The full or partial name of the company
                      (e.g. 'Apple', 'Tata Consultancy', 'Tesla').

    Returns:
        Suggested ticker symbols to try.
    """
    # A curated mapping of common company names to tickers.
    name_map = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "tesla": "TSLA",
        "meta": "META",
        "facebook": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "reliance": "RELIANCE.NS",
        "tata consultancy": "TCS.NS",
        "tcs": "TCS.NS",
        "infosys": "INFY.NS",
        "wipro": "WIPRO.NS",
        "hdfc bank": "HDFCBANK.NS",
        "icici bank": "ICICIBANK.NS",
        "state bank": "SBIN.NS",
        "sbi": "SBIN.NS",
        "bajaj finance": "BAJFINANCE.NS",
        "bharti airtel": "BHARTIARTL.NS",
        "airtel": "BHARTIARTL.NS",
        "asian paints": "ASIANPAINT.NS",
        "maruti": "MARUTI.NS",
        "maruti suzuki": "MARUTI.NS",
        "sun pharma": "SUNPHARMA.NS",
        "samsung": "005930.KS",
        "toyota": "TM",
        "sony": "SONY",
        "alibaba": "BABA",
    }

    query = company_name.strip().lower()
    matches = [
        f"{name.title()} → {ticker}"
        for name, ticker in name_map.items()
        if query in name
    ]

    if matches:
        return (
            f"Possible ticker(s) for '{company_name}':\n"
            + "\n".join(f"  • {m}" for m in matches)
            + "\n\nTip: For Indian stocks add '.NS' (NSE) or '.BO' (BSE) suffix."
        )

    return (
        f"No direct match found for '{company_name}'.\n"
        "Tips:\n"
        "  • US stocks  : use plain ticker (e.g., 'AAPL')\n"
        "  • NSE stocks : add '.NS' suffix (e.g., 'TCS.NS')\n"
        "  • BSE stocks : add '.BO' suffix (e.g., 'TCS.BO')\n"
        "  • Try Yahoo Finance (https://finance.yahoo.com) to look up the exact ticker."
    )
