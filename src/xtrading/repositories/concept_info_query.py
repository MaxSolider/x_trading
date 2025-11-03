"""
概念板块信息查询模块
基于AKShare实现概念板块相关数据查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional
from ..utils.limiter.akshare_rate_limiter import rate_limit_manual


class ConceptInfoQuery:
    """概念板块信息查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 概念板块信息查询服务初始化成功")
    
    def get_board_concept_name(self) -> Optional[pd.DataFrame]:
        """
        查询概念板块列表
        
        Returns:
            DataFrame: 包含概念板块列表信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取概念板块列表
            concept_names = ak.stock_board_concept_name_ths()
            print("✅ 成功获取概念板块列表")
            return concept_names
        except Exception as e:
            print(f"❌ 获取概念板块列表失败: {e}")
            return None
    
    def get_board_concept_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询概念板块概况
        
        Args:
            symbol: 概念板块名称
            
        Returns:
            DataFrame: 包含概念板块概况信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取概念板块概况
            concept_info = ak.stock_board_concept_info_ths(symbol=symbol)
            print(f"✅ 成功获取概念板块 {symbol} 概况")
            return concept_info
        except Exception as e:
            print(f"❌ 获取概念板块 {symbol} 概况失败: {e}")
            return None
    
    def get_board_concept_index(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        查询概念板块日频行情
        
        Args:
            symbol: 概念板块名称
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            
        Returns:
            DataFrame: 包含概念板块日频行情信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取概念板块日频行情
            concept_index = ak.stock_board_concept_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)
            print(f"✅ 成功获取概念板块 {symbol} 日频行情")
            return concept_index
        except Exception as e:
            print(f"❌ 获取概念板块 {symbol} 日频行情失败: {e}")
            return None