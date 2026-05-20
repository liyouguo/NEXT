"""
数据模块包
包含 ETF 和 NASDAQ 数据获取模块
"""

from .etf_fetcher import get_etf_uptrend_data, get_themes
from .nasdaq_fetcher import get_nasdaq_chart_data

__all__ = ['get_etf_uptrend_data', 'get_themes', 'get_nasdaq_chart_data']
