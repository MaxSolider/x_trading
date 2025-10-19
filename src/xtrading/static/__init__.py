"""
静态参数模块
包含各种静态数据和配置参数
"""

from .industry_sectors import (
    INDUSTRY_SECTORS,
    INDUSTRY_SECTORS_COUNT,
    INDUSTRY_CATEGORIES,
    get_industry_sectors,
    get_industry_sectors_count,
    get_industry_categories,
    get_sectors_by_category,
    search_sectors,
    get_sector_index
)

__all__ = [
    'INDUSTRY_SECTORS',
    'INDUSTRY_SECTORS_COUNT', 
    'INDUSTRY_CATEGORIES',
    'get_industry_sectors',
    'get_industry_sectors_count',
    'get_industry_categories',
    'get_sectors_by_category',
    'search_sectors',
    'get_sector_index'
]
