"""
个股信息查询模块
基于AKShare实现个股相关数据查询功能
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from xtrading.utils.rules.stock_code_utils import StockCodeUtils
from xtrading.utils.limiter.akshare_rate_limiter import rate_limit_manual

class StockQuery:
    """个股信息查询类"""
    
    def __init__(self):
        """初始化查询类"""
        self.stock_utils = StockCodeUtils()
        print("✅ 个股信息查询服务初始化成功")
    
    def get_stock_basic_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询个股基础信息
        
        Args:
            symbol: 股票代码 (如: 000001)
            
        Returns:
            DataFrame: 包含基础信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            print(f"✅ 成功获取 {symbol} 基础信息")
            return stock_info
        except Exception as e:
            print(f"❌ 获取 {symbol} 基础信息失败: {e}")
            return None
    
    def get_company_scale(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询公司规模信息
        
        Args:
            symbol: 股票代码 (如: 000001)
            
        Returns:
            DataFrame: 包含公司规模信息的DataFrame
        """
        try:
            # 为股票代码添加市场前缀
            symbol_with_prefix = self.stock_utils.add_market_prefix(symbol, False)
            if not symbol_with_prefix:
                print(f"❌ 无法为股票代码 {symbol} 添加市场前缀")
                return None
            
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取公司规模信息
            scale_info = ak.stock_zh_scale_comparison_em(symbol=symbol_with_prefix)
            print(f"✅ 成功获取 {symbol} ({symbol_with_prefix}) 公司规模信息")
            return scale_info
        except Exception as e:
            print(f"❌ 获取 {symbol} 公司规模信息失败: {e}")
            return None
    
    def get_main_business_composition(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询主营构成信息
        
        Args:
            symbol: 股票代码 (如: 000001)
            
        Returns:
            DataFrame: 包含主营构成信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取主营构成信息
            business_info = ak.stock_zyjs_ths(symbol=symbol)
            print(f"✅ 成功获取 {symbol} 主营构成信息")
            return business_info
        except Exception as e:
            print(f"❌ 获取 {symbol} 主营构成信息失败: {e}")
            return None
    
    def get_realtime_quotes(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询实时行情
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame: 包含实时行情信息的DataFrame
        """
        # try:
        #     # 获取实时行情
        #     realtime_data = ak.stock_zh_a_spot_em()
        #     # 筛选指定股票
        #     stock_data = realtime_data[realtime_data['代码'] == symbol]
        #     if not stock_data.empty:
        #         print(f"✅ 成功获取 {symbol} 实时行情")
        #         return stock_data
        #     else:
        #         print(f"❌ 未找到 {symbol} 的实时行情数据")
        #         return None
        # except Exception as e:
        #     print(f"❌ 获取 {symbol} 实时行情失败: {e}")
        #     return None
    
    def get_historical_quotes(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        查询历史行情
        
        Args:
            symbol: 股票代码 (如: 000001)
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            
        Returns:
            DataFrame: 包含历史行情信息的DataFrame
        """
        try:
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取历史行情
            historical_data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq" # 默认前复权
            )
            print(f"✅ 成功获取 {symbol} 历史行情 ({start_date} 到 {end_date})")
            return historical_data
        except Exception as e:
            print(f"❌ 获取 {symbol} 历史行情失败: {e}")
            return None
    
    def get_intraday_tick_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询日内分笔数据（最近一个交易日）
        
        Args:
            symbol: 股票代码 (如: sh000001)

        Returns:
            DataFrame: 包含日内分笔数据的DataFrame
        """
        try:
            # 为股票代码添加市场前缀
            symbol_with_prefix = self.stock_utils.add_market_prefix(symbol, True)
            if not symbol_with_prefix:
                print(f"❌ 无法为股票代码 {symbol} 添加市场前缀")
                return None
            
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取日内分笔数据
            tick_data = ak.stock_zh_a_tick_tx_js(symbol=symbol_with_prefix)
            print(f"✅ 成功获取 {symbol} ({symbol_with_prefix}) 日内分笔数据")
            return tick_data
        except Exception as e:
            print(f"❌ 获取 {symbol} 日内分笔数据失败: {e}")
            return None
    
    def get_intraday_time_data(self, symbol: str, date: str = None) -> Optional[pd.DataFrame]:
        """
        查询日内分时数据
        
        Args:
            symbol: 股票代码 (如: 000001)
            date: 查询日期 (格式: YYYYMMDD)，默认为今天
            
        Returns:
            DataFrame: 包含日内分时数据的DataFrame
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取日内分时数据
            time_data = ak.stock_zh_a_hist_min_em(symbol=symbol, start_date=date, end_date=date, period="1")
            print(f"✅ 成功获取 {symbol} 日内分时数据 ({date})")
            return time_data
        except Exception as e:
            print(f"❌ 获取 {symbol} 日内分时数据失败: {e}")
            return None
    
    def get_chip_distribution(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询近90 个交易日筹码分布
        
        Args:
            symbol: 股票代码 (如: 000001)
            
        Returns:
            DataFrame: 包含筹码分布信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取筹码分布数据
            chip_data = ak.stock_cyq_em(symbol=symbol)
            print(f"✅ 成功获取 {symbol} 筹码分布信息")
            return chip_data
        except Exception as e:
            print(f"❌ 获取 {symbol} 筹码分布信息失败: {e}")
            return None
    
