"""
静态参数模块
包含各种静态数据和配置参数
"""

from .industry_sectors import (
    INDUSTRY_SECTORS,
    INDUSTRY_SECTORS_COUNT,
    INDUSTRY_CATEGORIES,
    get_industry_sectors,
    get_industry_categories,
    get_sectors_by_category
)

from .backtest_report_config import ReportDirectoryConfig
from .sector_strategy_params import StrategyParams, strategy_config
from .stock_strategy_params import StockStrategyParams, stock_strategy_config

__all__ = [
    'INDUSTRY_SECTORS',
    'INDUSTRY_SECTORS_COUNT', 
    'INDUSTRY_CATEGORIES',
    'get_industry_sectors',
    'get_industry_categories',
    'get_sectors_by_category',
    'ReportDirectoryConfig',
    'StrategyParams',
    'strategy_config',
    'StockStrategyParams',
    'stock_strategy_config'
]
