"""
文档处理工具模块
提供行业板块报告生成和多行业板块总结报告生成功能
"""

from .sector_report_generator import SectorReportGenerator
from .sectors_summary_generator import SectorsSummaryGenerator

__all__ = [
    'SectorReportGenerator',
    'SectorsSummaryGenerator'
]
