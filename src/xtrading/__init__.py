"""
XTrading核心模块
"""

from .static import (
    INDUSTRY_SECTORS,
    INDUSTRY_SECTORS_COUNT,
    INDUSTRY_CATEGORIES,
    get_industry_sectors,
    get_industry_categories,
    get_sectors_by_category,
    ReportDirectoryConfig,
    StrategyParams,
    strategy_config,
    StockStrategyParams,
    stock_strategy_config
)
from .services import SectorSignalService, StockSignalService, SignalReportGenerator

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
    'stock_strategy_config',
    'SectorSignalService',
    'StockSignalService',
    'SignalReportGenerator'
]
