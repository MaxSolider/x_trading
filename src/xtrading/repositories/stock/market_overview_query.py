"""
市场全貌查询模块
基于AKShare实现市场概况数据查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict
from xtrading.utils.limiter.akshare_rate_limiter import rate_limit_manual


class MarketOverviewQuery:
    """市场全貌查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 市场全貌查询服务初始化成功")
    
    def get_sse_deal_daily(self, date: str) -> Optional[pd.DataFrame]:
        """
        查询上证市场成交概况
        
        Returns:
            DataFrame: 包含上证市场成交概况信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取上证市场成交概况
            sse_data = ak.stock_sse_deal_daily(date)
            print("✅ 成功获取上证市场成交概况")
            return sse_data
        except Exception as e:
            print(f"❌ 获取上证市场成交概况失败: {e}")
            return None
    
    def get_szse_summary(self, date: str) -> Optional[pd.DataFrame]:
        """
        查询深证市场成交概况
        
        Returns:
            DataFrame: 包含深证市场成交概况信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取深证市场成交概况
            szse_data = ak.stock_szse_summary(date)
            print("✅ 成功获取深证市场成交概况")
            return szse_data
        except Exception as e:
            print(f"❌ 获取深证市场成交概况失败: {e}")
            return None
    
    def get_market_summary_all(self, date: str) -> Dict[str, Optional[pd.DataFrame]]:
        """
        获取所有市场概况数据
        
        Returns:
            Dict: 包含所有市场概况数据的字典
        """
        results = {}
        
        print("🔍 正在获取所有市场概况数据...")
        
        # 获取各种市场概况数据
        results['sse_deal_daily'] = self.get_sse_deal_daily(date)
        results['szse_summary'] = self.get_szse_summary(date)
        
        print("✅ 市场概况数据获取完成")
        return results