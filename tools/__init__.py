"""tools/__init__.py — expose all tools as a flat list."""

from tools.stock_tools import (
    get_current_stock_price,
    get_stock_history,
    search_ticker_by_company_name,
)

ALL_TOOLS = [
    get_current_stock_price,
    get_stock_history,
    search_ticker_by_company_name,
]

__all__ = ["ALL_TOOLS"]
