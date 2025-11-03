"""
热度查询模块
基于AKShare实现股票热度数据查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional
from ..utils.limiter.akshare_rate_limiter import rate_limit_manual


class HeatQuery:
    """热度查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 热度查询服务初始化成功")
    
    def get_hot_stocks(self, symbol: str = "A股", date: str = None, time: str = "今日") -> Optional[pd.DataFrame]:
        """
        获取热搜股票数据
        
        Args:
            symbol: 市场类型，可选值：{"全部", "A股", "港股", "美股"}，默认为"A股"
            date: 日期，格式为'YYYYMMDD'，默认为今天
            time: 时间范围，可选值：{"今日", "1小时"}，默认为"今日"
            
        Returns:
            DataFrame: 包含热搜股票信息的DataFrame
            
        返回的DataFrame包含以下列：
            名称/代码	object	股票名称和代码
            涨跌幅	object	涨跌幅
            综合热度	int64	综合热度值
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print(f"🔍 正在获取热搜股票数据... (市场: {symbol}, 日期: {date}, 时间范围: {time})")
            
            # 如果没有指定日期，使用当前日期
            if date is None:
                from datetime import datetime
                date = datetime.now().strftime('%Y%m%d')
            
            # 调用AKShare接口
            hot_stocks_data = ak.stock_hot_search_baidu(symbol=symbol, date=date, time=time)
            
            if hot_stocks_data is None or (isinstance(hot_stocks_data, pd.DataFrame) and hot_stocks_data.empty):
                print(f"❌ 获取热搜股票数据为空")
                return None
            
            print(f"✅ 成功获取热搜股票数据，共 {len(hot_stocks_data)} 条记录")
            return hot_stocks_data
            
        except Exception as e:
            print(f"❌ 获取热搜股票数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None

