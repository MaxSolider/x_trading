"""
个股信息查询模块
基于AKShare实现个股相关数据查询功能
"""

import time
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union, List
from ..utils.rules.stock_code_utils import StockCodeUtils
from ..utils.limiter.akshare_rate_limiter import rate_limit_manual
from ..data.stock_history_dao import StockHistoryDAO

class StockQuery:
    """个股信息查询类"""
    
    def __init__(self):
        """初始化查询类"""
        self.stock_utils = StockCodeUtils()
        self.stock_dao = StockHistoryDAO()
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
        try:

            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取实时行情
            realtime_data = ak.stock_zh_a_spot_em()
            # 筛选指定股票
            stock_data = realtime_data[realtime_data['代码'] == symbol]
            if not stock_data.empty:
                print(f"✅ 成功获取 {symbol} 实时行情")
                return stock_data
            else:
                print(f"❌ 未找到 {symbol} 的实时行情数据")
                return None
        except Exception as e:
            print(f"❌ 获取 {symbol} 实时行情失败: {e}")
            return None

    def get_realtime_quotes_list(self) -> Optional[pd.DataFrame]:
        """
        查询实时行情
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame: 包含实时行情信息的DataFrame
        """
        try:

            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取实时行情
            realtime_data = ak.stock_zh_a_spot_em()
            return realtime_data
        except Exception as e:
            print(f"❌ 获取实时行情失败: {e}")
            return None

    def get_all_stock(self) -> Optional[pd.DataFrame]:
        """
        查询所有股票列表

        Returns:
            DataFrame: A股股票列表，包含code和name
        """
        try:

            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取所有A股股票列表
            stock_info_a_code_name_df = ak.stock_info_a_code_name()
            return stock_info_a_code_name_df
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None

    
    def get_historical_quotes(self, symbol: Union[str, List[str]], start_date: str = None, end_date: str = None, use_db: bool = True) -> Optional[pd.DataFrame]:
        """
        查询历史行情（支持批量查询）
        
        Args:
            symbol: 股票代码 (如: 000001) 或股票代码列表 (如: ['000001', '000002'])
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            use_db: 是否从数据库查询，默认为 True。如果为 False，则从 akshare 接口查询
            
        Returns:
            DataFrame: 历史行情数据
            如果单个股票代码，返回列：date, open, high, low, close, volume, amount, outstanding_share, turnover
            如果批量查询，返回列：code, date, open, high, low, close, volume, amount, outstanding_share, turnover
        """
        # 统一处理为列表
        is_batch = isinstance(symbol, list)
        symbols = symbol if is_batch else [symbol]
        
        if not symbols:
            return pd.DataFrame()
        
        # 如果从数据库查询
        if use_db:
            try:
                if is_batch:
                    # 批量查询
                    df = self.stock_dao.query_by_codes(symbols, start_date, end_date)
                else:
                    # 单个查询
                    df = self.stock_dao.query_by_code(symbols[0], start_date, end_date)
                
                if df is not None and not df.empty:
                    # 移除数据库返回的 id 列
                    df = df.drop(columns=['id'], errors='ignore')
                    
                    # 如果是单个查询，移除 code 列以保持与接口返回格式一致
                    # 如果是批量查询，保留 code 列以便区分不同股票
                    if not is_batch and 'code' in df.columns:
                        df = df.drop(columns=['code'])
                    
                    if is_batch:
                        print(f"✅ 成功从数据库批量获取 {len(symbols)} 只股票的历史行情 ({len(df)} 条记录)")
                    else:
                        print(f"✅ 成功从数据库获取 {symbols[0]} 历史行情 ({len(df)} 条记录)")
                    return df
                else:
                    if is_batch:
                        print(f"⚠️ 数据库中未找到批量股票的历史行情数据，尝试从接口获取")
                    else:
                        print(f"⚠️ 数据库中未找到 {symbols[0]} 的历史行情数据，尝试从接口获取")
                    # 如果数据库中没有数据，继续从接口查询
            except Exception as e:
                if is_batch:
                    print(f"⚠️ 从数据库批量查询历史行情失败: {e}，尝试从接口获取")
                else:
                    print(f"⚠️ 从数据库查询 {symbols[0]} 历史行情失败: {e}，尝试从接口获取")
                # 查询失败，继续从接口查询
        
        # 从接口查询（循环遍历）
        # 设置默认日期范围
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        results = []
        failed_symbols = []
        
        for idx, sym in enumerate(symbols, 1):
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries:
                try:
                    # 频控：等待到可以调用API
                    rate_limit_manual()
                    
                    # 获取历史行情
                    historical_data = ak.stock_zh_a_daily(
                        symbol=self.stock_utils.add_market_prefix(stock_code=sym, lower_case=True),
                        start_date=start_date,
                        end_date=end_date,
                        adjust="qfq"  # 默认前复权
                    )
                    
                    # 检查返回数据是否为空
                    if historical_data is None or (isinstance(historical_data, pd.DataFrame) and historical_data.empty):
                        raise ValueError(f"返回数据为空")
                    
                    # 如果是批量查询，添加 code 列
                    if is_batch:
                        historical_data = historical_data.copy()
                        historical_data['code'] = sym
                    
                    results.append(historical_data)
                    success = True
                    if is_batch:
                        print(f"✅ [{idx}/{len(symbols)}] 成功从接口获取 {sym} 历史行情")
                    else:
                        print(f"✅ 成功从接口获取 {sym} 历史行情 ({start_date} 到 {end_date})")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        failed_symbols.append(sym)
                        if is_batch:
                            print(f"❌ [{idx}/{len(symbols)}] 获取 {sym} 历史行情失败（已重试{max_retries}次）: {e}")
                        else:
                            print(f"❌ 获取 {sym} 历史行情失败（已重试{max_retries}次）: {e}")
            
            if not success and not is_batch:
                return None
        
        # 合并结果
        if results:
            combined_df = pd.concat(results, ignore_index=True)
            if is_batch:
                # 按 code 和 date 排序
                if 'code' in combined_df.columns and 'date' in combined_df.columns:
                    combined_df = combined_df.sort_values(['code', 'date'])
                print(f"✅ 批量查询完成：成功 {len(results)}/{len(symbols)}，失败 {len(failed_symbols)}")
            return combined_df
        else:
            return pd.DataFrame() if is_batch else None
    
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
            chip_data = ak.stock_cyq_em(symbol=symbol, adjust="qfq")
            print(f"✅ 成功获取 {symbol} 筹码分布信息")
            return chip_data
        except Exception as e:
            print(f"❌ 获取 {symbol} 筹码分布信息失败: {e}")
            return None
    
    def get_upward_breakout_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询向上突破股票列表
        
        Returns:
            DataFrame: 包含向上突破股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取向上突破股票列表
            upward_breakout_data = ak.stock_rank_xstp_ths('20日均线')
            print("✅ 成功获取向上突破股票列表")
            return upward_breakout_data
        except Exception as e:
            print(f"❌ 获取向上突破股票列表失败: {e}")
            return None
    
    def get_downward_breakout_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询向下突破股票列表
        
        Returns:
            DataFrame: 包含向下突破股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取向下突破股票列表
            downward_breakout_data = ak.stock_rank_xxtp_ths('20日均线')
            print("✅ 成功获取向下突破股票列表")
            return downward_breakout_data
        except Exception as e:
            print(f"❌ 获取向下突破股票列表失败: {e}")
            return None
    
    def get_volume_price_up_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询量价齐升股票列表
        
        Returns:
            DataFrame: 包含量价齐升股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取量价齐升股票列表
            volume_price_up_data = ak.stock_rank_ljqs_ths()
            print("✅ 成功获取量价齐升股票列表")
            return volume_price_up_data
        except Exception as e:
            print(f"❌ 获取量价齐升股票列表失败: {e}")
            return None
    
    def get_volume_price_down_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询量价齐跌股票列表
        
        Returns:
            DataFrame: 包含量价齐跌股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取量价齐跌股票列表
            volume_price_down_data = ak.stock_rank_ljqd_ths()
            print("✅ 成功获取量价齐跌股票列表")
            return volume_price_down_data
        except Exception as e:
            print(f"❌ 获取量价齐跌股票列表失败: {e}")
            return None
    
    def get_new_high_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询创新高股票列表
        
        Returns:
            DataFrame: 包含创新高股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取创新高股票列表
            new_high_data = ak.stock_rank_cxg_ths('半年新高')
            print("✅ 成功获取创新高股票列表")
            return new_high_data
        except Exception as e:
            print(f"❌ 获取创新高股票列表失败: {e}")
            return None
    
    def get_new_low_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询创新低股票列表
        
        Returns:
            DataFrame: 包含创新低股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取创新低股票列表
            new_low_data = ak.stock_rank_cxd_ths('半年新低')
            print("✅ 成功获取创新低股票列表")
            return new_low_data
        except Exception as e:
            print(f"❌ 获取创新低股票列表失败: {e}")
            return None
    
    def get_consecutive_up_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询连续上涨股票列表
        
        Returns:
            DataFrame: 包含连续上涨股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取连续上涨股票列表
            consecutive_up_data = ak.stock_rank_lxsz_ths()
            print("✅ 成功获取连续上涨股票列表")
            return consecutive_up_data
        except Exception as e:
            print(f"❌ 获取连续上涨股票列表失败: {e}")
            return None
    
    def get_consecutive_down_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询连续下跌股票列表
        
        Returns:
            DataFrame: 包含连续下跌股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取连续下跌股票列表
            consecutive_down_data = ak.stock_rank_lxxd_ths()
            print("✅ 成功获取连续下跌股票列表")
            return consecutive_down_data
        except Exception as e:
            print(f"❌ 获取连续下跌股票列表失败: {e}")
            return None
    
    def get_volume_expand_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询持续放量股票列表
        
        Returns:
            DataFrame: 包含持续放量股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取持续放量股票列表
            volume_expand_data = ak.stock_rank_cxfl_ths()
            print("✅ 成功获取持续放量股票列表")
            return volume_expand_data
        except Exception as e:
            print(f"❌ 获取持续放量股票列表失败: {e}")
            return None
    
    def get_volume_shrink_stocks(self) -> Optional[pd.DataFrame]:
        """
        查询持续缩量股票列表
        
        Returns:
            DataFrame: 包含持续缩量股票信息的DataFrame
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取持续缩量股票列表
            volume_shrink_data = ak.stock_rank_cxsl_ths()
            print("✅ 成功获取持续缩量股票列表")
            return volume_shrink_data
        except Exception as e:
            print(f"❌ 获取持续缩量股票列表失败: {e}")
            return None
    
    def get_institutional_participation(self) -> Optional[pd.DataFrame]:
        """
        查询机构参与度数据
        
        Returns:
            DataFrame: 包含机构参与度信息的DataFrame
            
        查询结果包含以下列：
            日期	str	交易日期
            机构参与度	float	机构参与度指标
            机构参与度变化	float	机构参与度变化幅度
            机构参与度趋势	str	机构参与度趋势描述
            机构持股比例	float	机构持股比例(%)
            机构持股变化	float	机构持股变化幅度
            机构交易活跃度	float	机构交易活跃度指标
            机构资金流向	float	机构资金流向指标
            机构持仓集中度	float	机构持仓集中度指标
            机构调研热度	float	机构调研热度指标
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取机构参与度数据...")
            
            # 获取机构参与度数据
            institutional_data = ak.stock_comment_detail_zlkp_jgcyd_em()
            
            if institutional_data is None or institutional_data.empty:
                print("❌ 获取的机构参与度数据为空")
                return None
            
            # 截断数据，只返回前120行
            if len(institutional_data) > 120:
                institutional_data = institutional_data.head(120)
                print(f"✅ 成功获取机构参与度数据，截断为前120条记录")
            else:
                print(f"✅ 成功获取机构参与度数据，共 {len(institutional_data)} 条记录")
            
            return institutional_data
            
        except Exception as e:
            print(f"❌ 获取机构参与度数据失败: {e}")
            return None
    
    def get_individual_fund_flow_rank(self, indicator: str = "今日") -> Optional[pd.DataFrame]:
        """
        查询个股资金流排名数据
        
        Args:
            indicator: 指标类型，可选值：今日、3日、5日、10日、20日、60日
            
        Returns:
            DataFrame: 包含个股资金流排名信息的DataFrame
            
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
            
            print(f"🔍 正在获取{indicator}个股资金流排名数据...")
            
            # 获取个股资金流排名数据
            fund_flow_rank_data = ak.stock_individual_fund_flow_rank(indicator=indicator)
            
            if fund_flow_rank_data is None or fund_flow_rank_data.empty:
                print(f"❌ 获取{indicator}个股资金流排名数据为空")
                return None
            
            print(f"✅ 成功获取{indicator}个股资金流排名数据，共 {len(fund_flow_rank_data)} 条记录")
            return fund_flow_rank_data
            
        except Exception as e:
            print(f"❌ 获取{indicator}个股资金流排名数据失败: {e}")
            return None
    
    def get_main_fund_flow_rank(self, indicator: str = "今日") -> Optional[pd.DataFrame]:
        """
        查询主力净流入排名数据
        
        Args:
            indicator: 指标类型，可选值：今日、3日、5日、10日、20日、60日
            
        Returns:
            DataFrame: 包含主力净流入排名信息的DataFrame
            
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
            
            print(f"🔍 正在获取{indicator}主力净流入排名数据...")
            
            # 获取主力净流入排名数据
            main_fund_flow_data = ak.stock_main_fund_flow(indicator=indicator)
            
            if main_fund_flow_data is None or main_fund_flow_data.empty:
                print(f"❌ 获取{indicator}主力净流入排名数据为空")
                return None
            
            print(f"✅ 成功获取{indicator}主力净流入排名数据，共 {len(main_fund_flow_data)} 条记录")
            return main_fund_flow_data
            
        except Exception as e:
            print(f"❌ 获取{indicator}主力净流入排名数据失败: {e}")
            return None
    
    def search_stock_by_name(self, stock_name: str) -> Optional[str]:
        """
        通过股票名称搜索股票代码
        
        Args:
            stock_name: 股票名称（如：平安银行）
            
        Returns:
            Optional[str]: 股票代码（如：000001）或 None
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            # 获取所有股票代码和名称的映射
            stock_info = ak.stock_info_a_code_name()
            
            if stock_info is None or stock_info.empty:
                print(f"❌ 无法获取股票信息列表")
                return None
            
            # 搜索匹配的股票
            # 列名可能是 'code', '代码' 或 'name', '名称'
            code_col = None
            name_col = None
            
            for col in stock_info.columns:
                if 'code' in col.lower() or col == '代码':
                    code_col = col
                elif 'name' in col.lower() or col == '名称':
                    name_col = col
            
            if code_col is None or name_col is None:
                # 如果找不到标准列名，尝试使用所有列
                print(f"⚠️ 无法识别列名，使用默认列")
                if len(stock_info.columns) >= 2:
                    code_col = stock_info.columns[0]
                    name_col = stock_info.columns[1]
                else:
                    print(f"❌ 股票信息表列数不足")
                    return None
            
            # 精确匹配
            match = stock_info[stock_info[name_col].str.contains(stock_name, na=False)]
            if not match.empty:
                code = match.iloc[0][code_col]
                print(f"✅ 找到股票: {stock_name} -> {code}")
                return code
            
            # 如果精确匹配失败，尝试模糊匹配
            print(f"⚠️ 无法精确匹配股票名称: {stock_name}")
            return None
            
        except Exception as e:
            print(f"❌ 搜索股票 {stock_name} 失败: {e}")
            return None
    


