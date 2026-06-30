"""
test_agent.py
-------------
Lightweight smoke tests for the stock tools (no LLM call needed).
Run with:  python test_agent.py
"""

import unittest
from unittest.mock import patch, MagicMock

# ── Tool-level unit tests ────────────────────────────────────────────────────

class TestSearchTickerByCompanyName(unittest.TestCase):
    """Tests for the ticker-lookup tool."""

    def _invoke(self, name: str) -> str:
        from tools.stock_tools import search_ticker_by_company_name
        return search_ticker_by_company_name.invoke(name)

    def test_known_company_apple(self):
        result = self._invoke("apple")
        self.assertIn("AAPL", result)

    def test_known_indian_company_tcs(self):
        result = self._invoke("tcs")
        self.assertIn("TCS.NS", result)

    def test_unknown_company(self):
        result = self._invoke("xyz unknown corp 12345")
        self.assertIn("No direct match found", result)


class TestGetCurrentStockPrice(unittest.TestCase):
    """Tests for get_current_stock_price with a mocked yfinance call."""

    def _invoke(self, ticker: str) -> str:
        from tools.stock_tools import get_current_stock_price
        return get_current_stock_price.invoke(ticker)

    @patch("tools.stock_tools.yf.Ticker")
    def test_valid_ticker_returns_price(self, mock_ticker_cls):
        mock_info = {
            "currentPrice": 175.50,
            "currency": "USD",
            "longName": "Apple Inc.",
            "fiftyTwoWeekHigh": 199.62,
            "fiftyTwoWeekLow": 124.17,
            "marketCap": 2_750_000_000_000,
            "exchange": "NMS",
        }
        mock_ticker_cls.return_value.info = mock_info

        result = self._invoke("AAPL")
        self.assertIn("175.50", result)
        self.assertIn("Apple Inc.", result)
        self.assertIn("2.75T", result)

    @patch("tools.stock_tools.yf.Ticker")
    def test_invalid_ticker_returns_error_message(self, mock_ticker_cls):
        mock_ticker_cls.return_value.info = {}
        result = self._invoke("FAKEXYZ")
        self.assertIn("Could not retrieve price", result)


class TestGetStockHistory(unittest.TestCase):
    """Tests for get_stock_history with a mocked yfinance call."""

    def _invoke(self, query: str) -> str:
        from tools.stock_tools import get_stock_history
        return get_stock_history.invoke(query)

    def test_missing_period_returns_help(self):
        result = self._invoke("AAPL")
        self.assertIn("Please provide both a ticker and a period", result)

    def test_invalid_period_returns_error(self):
        result = self._invoke("AAPL 999y")
        self.assertIn("Invalid period", result)

    @patch("tools.stock_tools.yf.Ticker")
    def test_valid_query(self, mock_ticker_cls):
        import pandas as pd
        import numpy as np

        dates = pd.date_range("2024-01-01", periods=5, freq="B")
        mock_hist = pd.DataFrame({
            "Open":   [150, 152, 153, 154, 155],
            "High":   [155, 156, 157, 158, 160],
            "Low":    [149, 151, 152, 153, 154],
            "Close":  [152, 153, 154, 155, 158],
            "Volume": [1_000_000] * 5,
        }, index=dates)

        mock_ticker_cls.return_value.history.return_value = mock_hist

        result = self._invoke("AAPL 1mo")
        self.assertIn("152.00", result)   # start price
        self.assertIn("158.00", result)   # end price
        self.assertIn("UP", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
