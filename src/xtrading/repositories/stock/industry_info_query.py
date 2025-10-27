"""
行业信息查询模块
基于AKShare实现行业相关数据查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional
from ...utils.limiter.akshare_rate_limiter import rate_limit_manual


class IndustryInfoQuery:
    """行业信息查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 行业信息查询服务初始化成功")
    
    def get_board_industry_name(self) -> Optional[pd.DataFrame]:
        """
        查询行业板块列表
        
        Returns:
            DataFrame: 包含行业板块列表信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取行业板块列表
            industry_names = ak.stock_board_industry_summary_ths()
            print("✅ 成功获取行业板块列表")
            return industry_names
        except Exception as e:
            print(f"❌ 获取行业板块列表失败: {e}")
            return None
    
    def get_board_industry_cons(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        查询板块成分股
        
        Args:
            symbol: 板块代码
            
        Returns:
            DataFrame: 包含板块成分股信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取板块成分股
            cons_data = ak.stock_board_industry_cons_em(symbol=symbol)
            return cons_data
        except Exception as e:
            print(f"❌ 获取板块 {symbol} 成分股失败: {e}")
            return None
    
    def get_board_industry_hist(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        查询板块日频行情
        
        Args:
            symbol: 板块代码
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            
        Returns:
            DataFrame: 包含板块日频行情信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取板块日频行情
            hist_data = ak.stock_board_industry_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)
            return hist_data
        except Exception as e:
            print(f"❌ 获取板块 {symbol} 日频行情失败: {e}")
            return None

    def get_sector_fund_flow(self, symbol: str, indicator: str = "今日") -> Optional[pd.DataFrame]:
        """
        查询板块资金流向数据
        
        Args:
            symbol: 板块代码
            indicator: 指标类型，可选值：今日、3日、5日、10日、20日、60日
            
        Returns:
            DataFrame: 包含板块资金流向信息的DataFrame
            
        查询结果包含以下列：
            代码	str	板块代码
            名称	str	板块名称
            主力净流入	float	主力净流入金额(万元)
            主力净流入占比	float	主力净流入占比(%)
            超大单净流入	float	超大单净流入金额(万元)
            超大单净流入占比	float	超大单净流入占比(%)
            大单净流入	float	大单净流入金额(万元)
            大单净流入占比	float	大单净流入占比(%)
            中单净流入	float	中单净流入金额(万元)
            中单净流入占比	float	中单净流入占比(%)
            小单净流入	float	小单净流入金额(万元)
            小单净流入占比	float	小单净流入占比(%)
            涨跌幅	float	涨跌幅(%)
            最新价	float	最新价格
            成交额	float	成交额(万元)
            流通市值	float	流通市值(万元)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print(f"🔍 正在获取板块 {symbol} 的{indicator}资金流向数据...")
            
            # 获取板块资金流向数据
            fund_flow_data = ak.stock_sector_fund_flow_hist(symbol=symbol, indicator=indicator)
            
            if fund_flow_data is None or fund_flow_data.empty:
                print(f"❌ 获取板块 {symbol} 的{indicator}资金流向数据为空")
                return None
            
            print(f"✅ 成功获取板块 {symbol} 的{indicator}资金流向数据，共 {len(fund_flow_data)} 条记录")
            return fund_flow_data
            
        except Exception as e:
            print(f"❌ 获取板块 {symbol} 的{indicator}资金流向数据失败: {e}")
            return None

    def get_industry_stock_fund_flow(self, symbol: str, indicator: str = "今日") -> Optional[pd.DataFrame]:
        """
        查询行业个股资金流向数据
        
        Args:
            symbol: 板块代码
            indicator: 指标类型，可选值：今日、3日、5日、10日、20日、60日
            
        Returns:
            DataFrame: 包含行业个股资金流向信息的DataFrame
            
        查询结果包含以下列：
            代码	str	股票代码
            名称	str	股票名称
            最新价	float	最新价格
            涨跌幅	float	涨跌幅(%)
            涨跌额	float	涨跌额
            成交量	float	成交量(万股)
            成交额	float	成交额(万元)
            振幅	float	振幅(%)
            最高	float	最高价
            最低	float	最低价
            今开	float	今开价
            昨收	float	昨收价
            量比	float	量比
            换手率	float	换手率(%)
            市盈率-动态	float	市盈率-动态
            市净率	float	市净率
            总市值	float	总市值(万元)
            流通市值	float	流通市值(万元)
            主力净流入	float	主力净流入金额(万元)
            主力净流入占比	float	主力净流入占比(%)
            超大单净流入	float	超大单净流入金额(万元)
            超大单净流入占比	float	超大单净流入占比(%)
            大单净流入	float	大单净流入金额(万元)
            大单净流入占比	float	大单净流入占比(%)
            中单净流入	float	中单净流入金额(万元)
            中单净流入占比	float	中单净流入占比(%)
            小单净流入	float	小单净流入金额(万元)
            小单净流入占比	float	小单净流入占比(%)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print(f"🔍 正在获取板块 {symbol} 的{indicator}个股资金流向数据...")
            
            # 获取行业个股资金流向数据
            stock_fund_flow_data = ak.stock_sector_fund_flow_summary(symbol=symbol, indicator=indicator)
            
            if stock_fund_flow_data is None or stock_fund_flow_data.empty:
                print(f"❌ 获取板块 {symbol} 的{indicator}个股资金流向数据为空")
                return None
            
            print(f"✅ 成功获取板块 {symbol} 的{indicator}个股资金流向数据，共 {len(stock_fund_flow_data)} 条记录")
            return stock_fund_flow_data
            
        except Exception as e:
            print(f"❌ 获取板块 {symbol} 的{indicator}个股资金流向数据失败: {e}")
            return None

    def get_sector_fund_flow_rank(self, indicator: str = "今日") -> Optional[pd.DataFrame]:
        """
        查询板块资金流排名数据
        
        Args:
            indicator: 指标类型，可选值：今日、3日、5日、10日、20日、60日
            
        Returns:
            DataFrame: 包含板块资金流排名信息的DataFrame
            
        查询结果包含以下列：
            代码	str	板块代码
            名称	str	板块名称
            最新价	float	最新价格
            涨跌幅	float	涨跌幅(%)
            涨跌额	float	涨跌额
            成交量	float	成交量(万股)
            成交额	float	成交额(万元)
            振幅	float	振幅(%)
            最高	float	最高价
            最低	float	最低价
            今开	float	今开价
            昨收	float	昨收价
            量比	float	量比
            换手率	float	换手率(%)
            市盈率-动态	float	市盈率-动态
            市净率	float	市净率
            总市值	float	总市值(万元)
            流通市值	float	流通市值(万元)
            主力净流入	float	主力净流入金额(万元)
            主力净流入占比	float	主力净流入占比(%)
            超大单净流入	float	超大单净流入金额(万元)
            超大单净流入占比	float	超大单净流入占比(%)
            大单净流入	float	大单净流入金额(万元)
            大单净流入占比	float	大单净流入占比(%)
            中单净流入	float	中单净流入金额(万元)
            中单净流入占比	float	中单净流入占比(%)
            小单净流入	float	小单净流入金额(万元)
            小单净流入占比	float	小单净流入占比(%)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print(f"🔍 正在获取{indicator}板块资金流排名数据...")
            
            # 获取板块资金流排名数据
            sector_fund_flow_rank_data = ak.stock_sector_fund_flow_rank(indicator=indicator)
            
            if sector_fund_flow_rank_data is None or sector_fund_flow_rank_data.empty:
                print(f"❌ 获取{indicator}板块资金流排名数据为空")
                return None
            
            print(f"✅ 成功获取{indicator}板块资金流排名数据，共 {len(sector_fund_flow_rank_data)} 条记录")
            return sector_fund_flow_rank_data
            
        except Exception as e:
            print(f"❌ 获取{indicator}板块资金流排名数据失败: {e}")
            return None