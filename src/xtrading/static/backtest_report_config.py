"""
报告目录配置模块
负责管理回测报告的目录结构和路径配置
"""

import os
from typing import Tuple


class ReportDirectoryConfig:
    """报告目录配置类"""
    
    # 基础目录配置
    BASE_BACKTEST_DIR = "backtest"
    REPORTS_SUBDIR = "reports"
    IMAGES_SUBDIR = "images"
    SECTOR_SUBDIR = "sector"
    SUMMARY_SUBDIR = "summary"
    
    @staticmethod
    def create_report_directories(backtest_date: str) -> Tuple[str, str, str]:
        """
        创建报告和图片目录
        
        Args:
            backtest_date: 回测日期
            
        Returns:
            Tuple[str, str, str]: (reports_dir, images_dir, summary_dir) 报告目录、图片目录和总结目录路径
        """
        # 构建目录路径
        reports_dir = os.path.join(
            ReportDirectoryConfig.BASE_BACKTEST_DIR,
            ReportDirectoryConfig.REPORTS_SUBDIR,
            backtest_date,
            ReportDirectoryConfig.SECTOR_SUBDIR
        )
        
        images_dir = os.path.join(
            ReportDirectoryConfig.BASE_BACKTEST_DIR,
            ReportDirectoryConfig.IMAGES_SUBDIR,
            backtest_date
        )
        
        summary_dir = os.path.join(
            ReportDirectoryConfig.BASE_BACKTEST_DIR,
            ReportDirectoryConfig.REPORTS_SUBDIR,
            backtest_date,
            ReportDirectoryConfig.SUMMARY_SUBDIR
        )
        
        # 创建目录
        os.makedirs(reports_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(summary_dir, exist_ok=True)
        
        return reports_dir, images_dir, summary_dir
    
    @staticmethod
    def get_base_backtest_dir() -> str:
        """获取基础回测目录"""
        return ReportDirectoryConfig.BASE_BACKTEST_DIR
    
    @staticmethod
    def get_reports_dir(backtest_date: str) -> str:
        """获取报告目录"""
        return os.path.join(
            ReportDirectoryConfig.BASE_BACKTEST_DIR,
            ReportDirectoryConfig.REPORTS_SUBDIR,
            backtest_date
        )
    
    @staticmethod
    def get_images_dir(backtest_date: str) -> str:
        """获取图片目录"""
        return os.path.join(
            ReportDirectoryConfig.BASE_BACKTEST_DIR,
            ReportDirectoryConfig.IMAGES_SUBDIR,
            backtest_date
        )
