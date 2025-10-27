"""
市场全貌查询模块
基于AKShare实现市场概况数据查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict
from ...utils.limiter.akshare_rate_limiter import rate_limit_manual


class MarketOverviewQuery:
    """市场全貌查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 市场全貌查询服务初始化成功")

    def get_market_summary(self, date: str) -> Optional[pd.DataFrame]:
        """
        获取所有市场概况数据并合并到一个表格中
        
        Returns:
            DataFrame: 包含所有市场概况数据的合并表格
            
        合并后的表格包含以下列：
            证券类别	object	包含：上证主板A、科创板、深证主板A、创业版、基金、ETF、债券
            数量	int64	证券数量
            成交金额	float64	成交金额
            总市值	float64	总市值
            流通市值	float64	流通市值
            流通换手率	float64	成交金额/流通市值
        """
        try:
            print("🔍 正在获取所有市场概况数据...")
            
            # 获取各种市场概况数据
            sse_data = self._get_sse_deal_daily(date)
            szse_data = self._get_szse_summary(date)
            
            # 检查数据是否获取成功
            if sse_data is None and szse_data is None:
                print("❌ 未能获取任何市场概况数据")
                return None
            
            # 合并数据
            merged_data = []
            
            # 添加上证数据
            if sse_data is not None and not sse_data.empty:
                merged_data.append(sse_data)

            # 添加深证数据
            if szse_data is not None and not szse_data.empty:
                merged_data.append(szse_data)

            # 合并所有数据
            if merged_data:
                result_df = pd.concat(merged_data, ignore_index=True)
                print(f"✅ 成功获取市场概况数据，总计 {len(result_df)} 条记录")
                return result_df
            else:
                print("❌ 没有有效数据可以合并")
                return None
                
        except Exception as e:
            print(f"❌ 获取市场概况数据失败: {e}")
            return None
    
    def get_limit_up_stocks(self, date: str) -> Optional[pd.DataFrame]:
        """
        获取涨停股列表
        
        Args:
            date (str): 查询日期，格式为'YYYYMMDD'
            
        Returns:
            DataFrame: 包含涨停股信息的DataFrame
            
        查询结果包含以下列：
            序号	int	序号
            代码	str	股票代码
            名称	str	股票名称
            涨跌幅	float	涨跌幅(%)
            最新价	float	最新价格
            成交额	float	成交额(元)
            流通市值	float	流通市值(元)
            总市值	float	总市值(元)
            换手率	float	换手率(%)
            封板资金	float	封板资金(元)
            首次封板时间	str	首次封板时间
            最后封板时间	str	最后封板时间
            炸板次数	int	炸板次数
            涨停统计	str	涨停统计
            连板数	int	连板数
            所属行业	str	所属行业
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print(f"🔍 正在获取 {date} 的涨停股列表...")
            
            # 获取涨停股数据
            limit_up_data = ak.stock_zt_pool_em(date)
            
            if limit_up_data is None or limit_up_data.empty:
                print(f"❌ 获取 {date} 的涨停股数据为空")
                return None
            
            print(f"✅ 成功获取涨停股数据，共 {len(limit_up_data)} 只股票")
            return limit_up_data
            
        except Exception as e:
            print(f"❌ 获取涨停股数据失败: {e}")
            return None

    def get_market_activity(self) -> Optional[pd.DataFrame]:
        """
        获取市场赚钱效应数据
        
        Returns:
            DataFrame: 包含市场赚钱效应信息的DataFrame
            
        查询结果包含以下列：
            统计日期	str	交易日期
            上涨	int	上涨股票数量
            涨停	int	涨停股票数量（包含炸板票）
            真实涨停	int	涨停股票数量
            st st*涨停	int	st涨停股票数量
            下跌	int	下跌股票数量
            跌停	int	跌停股票数量（包含炸板票）
            真实跌停	int	跌停股票数量
            st st*跌停	int	st涨停股票数量
            平盘	int	平盘股票数量
            停牌 int 停牌股票数量
            活跃度 float 市场活跃度
            上涨比例	float	上涨股票占比(%)
            下跌比例	float	下跌股票占比(%)
            平盘比例	float	平盘股票占比(%)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取市场赚钱效应数据...")
            
            # 获取市场赚钱效应数据
            market_activity_data = ak.stock_market_activity_legu()
            
            if market_activity_data is None or market_activity_data.empty:
                print("❌ 获取的市场赚钱效应数据为空")
                return None

            # 检查数据格式并转换（stock_market_activity_legu返回的是item-value格式）
            if 'item' in market_activity_data.columns and 'value' in market_activity_data.columns:
                # 创建字典来存储转换后的数据
                converted_data = {}
                
                # 遍历每一行，将item-value对转换为字典
                for _, row in market_activity_data.iterrows():
                    item = row['item']
                    value = row['value']
                    converted_data[item] = value
                
                # 创建新的DataFrame
                market_activity_data = pd.DataFrame([converted_data])

            # 检查必要的列是否存在
            required_columns = ['上涨', '下跌', '平盘', '停牌']
            missing_columns = [col for col in required_columns if col not in market_activity_data.columns]
            
            if missing_columns:
                print(f"❌ 缺少必要的列: {missing_columns}")
                print(f"可用列: {list(market_activity_data.columns)}")
                return market_activity_data
            
            # 确保数值列为数值类型
            for col in required_columns:
                market_activity_data[col] = pd.to_numeric(market_activity_data[col], errors='coerce').fillna(0)
            
            # 计算上涨比例、下跌比例、平盘比例
            market_activity_data = market_activity_data.copy()
            
            # 计算总股票数量（上涨+下跌+平盘+停牌）
            market_activity_data['总股票数'] = (
                market_activity_data['上涨'] + 
                market_activity_data['下跌'] + 
                market_activity_data['平盘'] + 
                market_activity_data['停牌']
            )
            
            # 计算比例（避免除零错误）
            market_activity_data['上涨比例'] = (
                market_activity_data['上涨'] / market_activity_data['总股票数'] * 100
            ).round(2)
            
            market_activity_data['下跌比例'] = (
                market_activity_data['下跌'] / market_activity_data['总股票数'] * 100
            ).round(2)
            
            market_activity_data['平盘比例'] = (
                market_activity_data['平盘'] / market_activity_data['总股票数'] * 100
            ).round(2)
            
            # 删除临时列
            market_activity_data = market_activity_data.drop('总股票数', axis=1)
            
            print(f"✅ 成功获取市场赚钱效应数据，共 {len(market_activity_data)} 条记录")
            return market_activity_data
            
        except Exception as e:
            print(f"❌ 获取市场赚钱效应数据失败: {e}")
            return None

    def get_margin_account_info(self) -> Optional[pd.DataFrame]:
        """
        查询两融账户信息
        
        Returns:
            DataFrame: 包含两融账户信息的DataFrame
            
        查询结果包含以下列：
            日期	str	交易日期
            融资余额	float	融资余额(亿元)
            融券余额	float	融券余额(亿元)
            融资融券余额	float	融资融券总余额(亿元)
            融资买入额	float	融资买入额(亿元)
            融券卖出量	float	融券卖出量(万股)
            融资偿还额	float	融资偿还额(亿元)
            融券偿还量	float	融券偿还量(万股)
            融资净买入	float	融资净买入额(亿元)
            融券净卖出	float	融券净卖出量(万股)
            融资融券净买入	float	融资融券净买入额(亿元)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取两融账户信息...")
            
            # 获取两融账户信息
            margin_account_data = ak.stock_margin_account_info()
            
            if margin_account_data is None or margin_account_data.empty:
                print("❌ 获取的两融账户信息为空")
                return None
            
            # 截断数据，只返回最后120行
            if len(margin_account_data) > 120:
                margin_account_data = margin_account_data.tail(120)
                print(f"✅ 成功获取两融账户信息，截断为最后120条记录")
            else:
                print(f"✅ 成功获取两融账户信息，共 {len(margin_account_data)} 条记录")
            
            return margin_account_data
            
        except Exception as e:
            print(f"❌ 获取两融账户信息失败: {e}")
            return None

    def get_northbound_funds_data(self) -> Optional[pd.DataFrame]:
        """
        查询北向资金数据
        
        Returns:
            DataFrame: 包含北向资金信息的DataFrame
            
        查询结果包含以下列：
            日期	str	交易日期
            沪股通净买入	float	沪股通净买入额(亿元)
            深股通净买入	float	深股通净买入额(亿元)
            北向资金净买入	float	北向资金净买入额(亿元)
            沪股通买入额	float	沪股通买入额(亿元)
            深股通买入额	float	深股通买入额(亿元)
            沪股通卖出额	float	沪股通卖出额(亿元)
            深股通卖出额	float	深股通卖出额(亿元)
            沪股通成交额	float	沪股通成交额(亿元)
            深股通成交额	float	深股通成交额(亿元)
            北向资金成交额	float	北向资金成交额(亿元)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取北向资金数据...")
            
            # 获取北向资金数据
            northbound_funds_data = ak.stock_hsgt_hist_em('北向资金')
            
            if northbound_funds_data is None or northbound_funds_data.empty:
                print("❌ 获取的北向资金数据为空")
                return None
            
            # 截断数据，只返回前120行
            if len(northbound_funds_data) > 120:
                northbound_funds_data = northbound_funds_data.tail(120)
                print(f"✅ 成功获取北向资金数据，截断为前120条记录")
            else:
                print(f"✅ 成功获取北向资金数据，共 {len(northbound_funds_data)} 条记录")
            
            return northbound_funds_data
            
        except Exception as e:
            print(f"❌ 获取北向资金数据失败: {e}")
            return None

    def get_market_participation_desire(self) -> Optional[pd.DataFrame]:
        """
        查询市场参与意愿数据
        
        Returns:
            DataFrame: 包含市场参与意愿信息的DataFrame
            
        查询结果包含以下列：
            日期	str	交易日期
            参与意愿	float	市场参与意愿指标
            参与意愿变化	float	参与意愿变化幅度
            参与意愿趋势	str	参与意愿趋势描述
            市场情绪	str	市场情绪状态
            投资者信心	float	投资者信心指数
            交易活跃度	float	交易活跃度指标
            资金流入意愿	float	资金流入意愿指标
            风险偏好	float	风险偏好指标
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取市场参与意愿数据...")
            
            # 获取市场参与意愿数据
            participation_desire_data = ak.stock_comment_detail_scrd_desire_daily_em()
            
            if participation_desire_data is None or participation_desire_data.empty:
                print("❌ 获取的市场参与意愿数据为空")
                return None
            
            # 截断数据，只返回前120行
            if len(participation_desire_data) > 120:
                participation_desire_data = participation_desire_data.head(120)
                print(f"✅ 成功获取市场参与意愿数据，截断为前120条记录")
            else:
                print(f"✅ 成功获取市场参与意愿数据，共 {len(participation_desire_data)} 条记录")
            
            return participation_desire_data
            
        except Exception as e:
            print(f"❌ 获取市场参与意愿数据失败: {e}")
            return None

    def get_market_fund_flow(self) -> Optional[pd.DataFrame]:
        """
        查询大盘资金流数据
        
        Returns:
            DataFrame: 包含大盘资金流信息的DataFrame
            
        查询结果包含以下列：
            日期	str	交易日期
            主力净流入	float	主力净流入金额(亿元)
            主力净流入占比	float	主力净流入占比(%)
            超大单净流入	float	超大单净流入金额(亿元)
            超大单净流入占比	float	超大单净流入占比(%)
            大单净流入	float	大单净流入金额(亿元)
            大单净流入占比	float	大单净流入占比(%)
            中单净流入	float	中单净流入金额(亿元)
            中单净流入占比	float	中单净流入占比(%)
            小单净流入	float	小单净流入金额(亿元)
            小单净流入占比	float	小单净流入占比(%)
            上证指数	float	上证指数收盘价
            深证成指	float	深证成指收盘价
            创业板指	float	创业板指收盘价
            科创50	float	科创50收盘价
            沪深300	float	沪深300收盘价
            中证500	float	中证500收盘价
            成交额	float	市场总成交额(亿元)
            成交量	float	市场总成交量(亿股)
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()
            
            print("🔍 正在获取大盘资金流数据...")
            
            # 获取大盘资金流数据
            market_fund_flow_data = ak.stock_market_fund_flow()
            
            if market_fund_flow_data is None or market_fund_flow_data.empty:
                print("❌ 获取的大盘资金流数据为空")
                return None
            
            # 截断数据，只返回前120行
            if len(market_fund_flow_data) > 120:
                market_fund_flow_data = market_fund_flow_data.tail(120)
                print(f"✅ 成功获取大盘资金流数据，截断为前120条记录")
            else:
                print(f"✅ 成功获取大盘资金流数据，共 {len(market_fund_flow_data)} 条记录")
            
            return market_fund_flow_data
            
        except Exception as e:
            print(f"❌ 获取大盘资金流数据失败: {e}")
            return None

    def _get_sse_deal_daily(self, date: str) -> Optional[pd.DataFrame]:
        """
        查询上证市场成交概况

        Returns:
            DataFrame: 包含上证市场成交概况信息的DataFrame

        查询结果包含以下列：
            证券类别	object	包含：上证主板A、科创板
            数量	int64	挂牌数
            成交金额	float64	成交金额
            总市值	float64	市价总值
            流通市值	float64	流通市值
            流通换手率	float64	流通换手率
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取上证市场成交概况
            sse_data = ak.stock_sse_deal_daily(date)

            if sse_data is None or sse_data.empty:
                print("❌ 获取的上证市场数据为空")
                return None

            # 将非标准表格格式转换为标准表格格式
            # 原始数据：行是指标，列是证券类别
            # 需要转换为：行是证券类别，列是指标

            # 转置数据，使证券类别成为行，指标成为列
            transposed_data = sse_data.T

            # 重置列名为指标名称
            transposed_data.columns = sse_data['单日情况'].tolist()

            # 重置索引，使证券类别成为一列
            transposed_data = transposed_data.reset_index()
            transposed_data.rename(columns={'index': '证券类别'}, inplace=True)

            # 筛选需要的证券类别（排除股票回购等不需要的数据）
            target_categories = ['主板A', '科创板']
            filtered_data = transposed_data[transposed_data['证券类别'].isin(target_categories)].copy()

            # 重命名证券类别以符合标准格式
            category_mapping = {
                '主板A': '上证主板A',
                '科创板': '科创板'
            }
            filtered_data['证券类别'] = filtered_data['证券类别'].map(category_mapping)

            # 重新组织列名以符合标准格式
            result_data = []
            for _, row in filtered_data.iterrows():
                # 计算流通换手率
                turnover_amount = row.get('成交金额', 0)
                circulation_market_value = row.get('流通市值', 0)

                # 避免除零错误
                turnover_rate = 0
                if circulation_market_value > 0:
                    turnover_rate = turnover_amount / circulation_market_value

                result_data.append({
                    '证券类别': row['证券类别'],
                    '数量': row.get('挂牌数', 0),
                    '成交金额': turnover_amount,
                    '总市值': row.get('市价总值', 0),
                    '流通市值': circulation_market_value,
                    '流通换手率': turnover_rate
                })

            # 创建新的DataFrame
            result_df = pd.DataFrame(result_data)

            return result_df

        except Exception as e:
            print(f"❌ 获取上证市场成交概况失败: {e}")
            return None

    def _get_szse_summary(self, date: str) -> Optional[pd.DataFrame]:
        """
        查询深证市场成交概况

        Returns:
            DataFrame: 包含深证市场成交概况信息的DataFrame

        查询结果包含以下列：
            证券类别	object	包含：深证主板A、创业版
            数量	int64	注意单位: 只
            成交金额	float64	注意单位: 亿元
            总市值	float64	注意单位: 亿元
            流通市值	float64	注意单位: 亿元
            流通换手率	float64	成交金额/流通市值
        """
        try:
            # 频控：等待到可以调用API
            rate_limit_manual()

            # 获取深证市场成交概况
            szse_data = ak.stock_szse_summary(date)

            if szse_data is None or szse_data.empty:
                print("❌ 获取的深证市场数据为空")
                return None

            # 创建新的数据结构
            result_data = []

            # 定义证券类别映射
            category_mapping = {
                '主板A股': '深证主板A',
                '创业板A股': '创业版'
            }

            # 处理每一行数据
            for _, row in szse_data.iterrows():
                category = row.get('证券类别', '')

                # 检查是否是我们需要的证券类别
                if category in category_mapping:
                    # 计算流通换手率
                    turnover_amount = row.get('成交金额', 0)
                    circulation_market_value = row.get('流通市值', 0)

                    # 避免除零错误
                    turnover_rate = 0
                    if circulation_market_value > 0:
                        turnover_rate = turnover_amount / circulation_market_value

                    result_data.append({
                        '证券类别': category_mapping[category],
                        '数量': row.get('数量', 0),
                        '成交金额': round(turnover_amount / 100000000, 2),
                        '总市值': round(row.get('总市值', 0) / 100000000, 2),
                        '流通市值': round(circulation_market_value / 100000000, 2),
                        '流通换手率': turnover_rate
                    })

            # 创建新的DataFrame
            result_df = pd.DataFrame(result_data)

            return result_df

        except Exception as e:
            print(f"❌ 获取深证市场成交概况失败: {e}")
            return None


