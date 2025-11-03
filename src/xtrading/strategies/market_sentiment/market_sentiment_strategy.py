"""
市场情绪分析策略
基于多维度数据计算市场情绪指数，并生成六边雷达图
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import os

from openpyxl.styles.builtins import total

from ...repositories.market_overview_query import MarketOverviewQuery
from ...repositories.stock_query import StockQuery
from ...utils.date import DateUtils
from ...utils.graphics.radar_chart_generator import RadarChartGenerator


class MarketSentimentStrategy:
    """市场情绪分析策略类"""
    
    def __init__(self):
        """初始化市场情绪分析策略"""
        self.market_query = MarketOverviewQuery()
        self.stock_query = StockQuery()
        self.radar_generator = RadarChartGenerator()
        print("✅ 市场情绪分析策略初始化成功")
    
    def analyze_market_sentiment(self, date: str = None) -> Dict[str, Any]:
        """
        分析市场情绪
        
        Args:
            date: 分析日期，格式为'YYYYMMDD'，默认为今天
            
        Returns:
            Dict[str, Any]: 市场情绪分析结果
        """
        try:
            if not date:
                date = DateUtils.get_recent_trading_day(datetime.now().strftime('%Y%m%d'))
            
            print(f"🔍 开始分析 {date} 的市场情绪...")
            
            # 获取各项数据
            market_activity_data = self.market_query.get_market_activity()
            market_summary_data = self.market_query.get_market_summary(date)
            breakout_data = self.stock_query.get_upward_breakout_stocks()
            margin_data = self.market_query.get_margin_account_info()
            fund_flow_data = self.market_query.get_market_fund_flow()

            # 计算各维度分数
            sentiment_scores = self._calculate_sentiment_scores(
                market_activity_data,
                market_summary_data,
                breakout_data,
                margin_data,
                fund_flow_data
            )
            
            # 计算综合情绪指数
            overall_sentiment = self._calculate_overall_sentiment(sentiment_scores)
            
            # 生成分析结果
            result = {
                'analysis_date': date,
                'sentiment_scores': sentiment_scores,
                'overall_sentiment': overall_sentiment,
                'sentiment_level': self._get_sentiment_level(overall_sentiment),
                'raw_data': {
                    'market_activity': market_activity_data,
                    'market_summary': market_summary_data,
                    'breakout_data': breakout_data,
                    'margin_data': margin_data,
                    'fund_flow_data': fund_flow_data,
                }
            }
            
            print(f"✅ 市场情绪分析完成，综合情绪指数: {overall_sentiment:.1f}")
            
            # 保存历史数据
            self._save_sentiment_history(result)

            # 生成综合图表（雷达图+5个趋势图）
            print("\n📈 正在生成市场情绪综合分析图...")
            comprehensive_chart_path = self._generate_comprehensive_sentiment_chart(result)
            if comprehensive_chart_path:
                print(f"✅ 综合分析图已生成: {comprehensive_chart_path}")
                # 将图表路径添加到结果中
                result['radar_chart_path'] = comprehensive_chart_path
            else:
                print("❌ 综合分析图生成失败")

            # 打印分析结果
            self.print_sentiment_analysis(result)

            return result
            
        except Exception as e:
            print(f"❌ 市场情绪分析失败: {e}")
            return {}
    
    def _generate_sentiment_radar_chart(self, sentiment_result: Dict[str, Any]) -> Optional[str]:
        """
        生成市场情绪雷达图
        
        Args:
            sentiment_result: 市场情绪分析结果
            output_dir: 输出目录
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            if not sentiment_result or 'sentiment_scores' not in sentiment_result:
                print("❌ 无效的市场情绪分析结果")
                return None
            
            # 确保输出目录存在
            output_dir: str = "reports/radar/images"
            os.makedirs(output_dir, exist_ok=True)
            
            # 准备雷达图数据
            sentiment_scores = sentiment_result['sentiment_scores']
            radar_data = {
                '市场活跃度': sentiment_scores.get('market_activity', 0),
                '个股赚钱效应': sentiment_scores.get('profit_effect', 0),
                '风险偏好': sentiment_scores.get('risk_preference', 0),
                '市场参与意愿': sentiment_scores.get('participation_willingness', 0),
                '综合情绪指数': sentiment_result.get('overall_sentiment', 0)
            }
            
            # 生成文件名（只使用日期，有冲突则覆盖）
            analysis_date = sentiment_result.get('analysis_date', datetime.now().strftime('%Y%m%d'))
            filename = f"市场情绪雷达图_{analysis_date}.png"
            output_path = os.path.join(output_dir, filename)
            
            # 生成雷达图
            chart_path = self.radar_generator.generate_market_sentiment_radar(
                radar_data, output_path, f"市场情绪雷达图 - {sentiment_result.get('analysis_date', '')}"
            )
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 生成市场情绪雷达图失败: {e}")
            return None
    
    def _save_sentiment_history(self, sentiment_result: Dict[str, Any]) -> Optional[str]:
        """
        保存市场情绪分析历史数据
        
        Args:
            sentiment_result: 市场情绪分析结果
            
        Returns:
            str: 保存的文件路径
        """
        try:
            if not sentiment_result or 'sentiment_scores' not in sentiment_result:
                print("❌ 无效的市场情绪分析结果")
                return None
            
            # 确保输出目录存在
            output_dir = "reports/history"
            os.makedirs(output_dir, exist_ok=True)
            
            # 准备历史数据
            analysis_date = sentiment_result.get('analysis_date', datetime.now().strftime('%Y%m%d'))
            sentiment_scores = sentiment_result['sentiment_scores']
            overall_sentiment = sentiment_result.get('overall_sentiment', 0)
            
            history_data = {
                'date': analysis_date,
                'market_activity': sentiment_scores.get('market_activity', 0),
                'profit_effect': sentiment_scores.get('profit_effect', 0),
                'risk_preference': sentiment_scores.get('risk_preference', 0),
                'participation_willingness': sentiment_scores.get('participation_willingness', 0),
                'overall_sentiment': overall_sentiment,
                'sentiment_level': sentiment_result.get('sentiment_level', '未知')
            }
            
            # 保存到CSV文件
            csv_file = os.path.join(output_dir, "market_sentiment_history.csv")
            
            # 检查文件是否存在
            if os.path.exists(csv_file):
                # 读取现有数据
                df = pd.read_csv(csv_file)
                
                # 确保日期字段为字符串类型
                df['date'] = df['date'].astype(str)
                
                # 检查是否存在相同日期的数据
                existing_date_mask = df['date'] == analysis_date
                if existing_date_mask.any():
                    # 覆盖相同日期的数据
                    df.loc[existing_date_mask, list(history_data.keys())] = list(history_data.values())
                    print(f"🔄 覆盖了日期 {analysis_date} 的现有数据")
                else:
                    # 添加新数据
                    new_row = pd.DataFrame([history_data])
                    df = pd.concat([df, new_row], ignore_index=True)
                    print(f"➕ 添加了新日期 {analysis_date} 的数据")
            else:
                # 创建新文件
                df = pd.DataFrame([history_data])
                print(f"📝 创建了新的历史数据文件，日期: {analysis_date}")
            
            # 确保日期字段为字符串类型，然后按日期排序（最新的在前）
            df['date'] = df['date'].astype(str)
            df = df.sort_values('date', ascending=False)
            
            # 保存数据
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            print(f"✅ 市场情绪历史数据已保存: {csv_file}")
            return csv_file
            
        except Exception as e:
            print(f"❌ 保存市场情绪历史数据失败: {e}")
            return None
    
    def _generate_comprehensive_sentiment_chart(self, sentiment_result: Dict[str, Any]) -> Optional[str]:
        """
        生成市场情绪综合分析图（雷达图+趋势图）
        
        Args:
            sentiment_result: 市场情绪分析结果
            
        Returns:
            str: 生成的图片文件路径
        """
        try:
            if not sentiment_result or 'sentiment_scores' not in sentiment_result:
                print("❌ 无效的市场情绪分析结果")
                return None
            
            # 确保输出目录存在
            output_dir = "reports/images/sentiment"
            os.makedirs(output_dir, exist_ok=True)
            
            # 准备雷达图数据
            sentiment_scores = sentiment_result['sentiment_scores']
            radar_data = {
                '市场活跃度': sentiment_scores.get('market_activity', 0),
                '个股赚钱效应': sentiment_scores.get('profit_effect', 0),
                '风险偏好': sentiment_scores.get('risk_preference', 0),
                '市场参与意愿': sentiment_scores.get('participation_willingness', 0),
                '综合情绪指数': sentiment_result.get('overall_sentiment', 0)
            }
            
            # 准备趋势数据
            trend_data = self._prepare_trend_data()
            
            # 生成文件名（只使用日期，有冲突则覆盖）
            analysis_date = sentiment_result.get('analysis_date', datetime.now().strftime('%Y%m%d'))
            filename = f"市场情绪综合分析图_{analysis_date}.png"
            output_path = os.path.join(output_dir, filename)
            
            # 生成综合分析图
            chart_path = self.radar_generator.generate_comprehensive_sentiment_chart(
                radar_data, trend_data, output_path, 
                f"市场情绪综合分析图 - {sentiment_result.get('analysis_date', '')}"
            )
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 生成市场情绪综合分析图失败: {e}")
            return None
    
    def _prepare_trend_data(self) -> Dict[str, Dict[str, list]]:
        """
        准备趋势数据
            
        Returns:
            Dict[str, Dict[str, list]]: 趋势数据字典
        """
        try:
            # 读取历史数据
            csv_file = "reports/history/market_sentiment_history.csv"
            if not os.path.exists(csv_file):
                print("❌ 历史数据文件不存在")
                return {}
            
            df = pd.read_csv(csv_file)
            if df.empty:
                print("❌ 历史数据为空")
                return {}
            
            # 确保日期字段为字符串类型
            df['date'] = df['date'].astype(str)
            
            # 获取最近10天的数据
            df = df.tail(10)
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            
            # 准备趋势数据
            trend_data = {}
            dimensions = {
                'overall_sentiment': '综合情绪指数',
                'market_activity': '市场活跃度',
                'profit_effect': '个股赚钱效应',
                'risk_preference': '风险偏好',
                'participation_willingness': '市场参与意愿'
            }
            
            for key, name in dimensions.items():
                if key in df.columns:
                    trend_data[key] = {
                        'dates': df['date'].tolist(),
                        'values': df[key].tolist()
                    }
            
            return trend_data
            
        except Exception as e:
            print(f"❌ 准备趋势数据失败: {e}")
            return {}
    
    def _calculate_sentiment_scores(self,
                                  market_activity_data: Optional[pd.DataFrame],
                                  market_summary_data: Optional[pd.DataFrame],
                                  breakout_data: Optional[pd.DataFrame],
                                  margin_data: Optional[pd.DataFrame],
                                  fund_flow_data: Optional[pd.DataFrame]) -> Dict[str, float]:
        """
        计算各维度情绪分数
            
        Returns:
            Dict[str, float]: 各维度分数 (0-10分)
        """
        scores = {}
        
        # 1. 市场活跃度分数
        scores['market_activity'] = self._calculate_market_activity_score(
            market_activity_data, market_summary_data
        )
        
        # 2. 个股赚钱效应分数
        scores['profit_effect'] = self._calculate_profit_effect_score(
            market_activity_data, breakout_data
        )
        
        # 3. 风险偏好分数
        scores['risk_preference'] = self._calculate_risk_preference_score(margin_data, market_summary_data)
        
        # 4. 市场参与意愿分数
        scores['participation_willingness'] = self._calculate_participation_willingness_score(
            fund_flow_data
        )
        
        return scores
    
    def _calculate_market_activity_score(self, 
                                       market_activity_data: Optional[pd.DataFrame],
                                       market_summary_data: Optional[pd.DataFrame]) -> float:
        """计算市场活跃度分数"""
        try:
            # 初始化各指标分数
            limit_up_score = 0.0
            total_amount_score = 0.0
            turnover_score = 0.0
            
            # 1. 涨停股数量归一化
            if market_activity_data is not None and not market_activity_data.empty:
                latest_data = market_activity_data.iloc[0]
                limit_up_count = latest_data.get('真实涨停', 0)
                # 归一化: 涨停股数量 / 历史单日最多涨停股票数量
                limit_up_score = limit_up_count / 2000
            
            # 2. 市场总成交金额归一化
            if market_summary_data is not None and not market_summary_data.empty:
                total_amount = market_summary_data['成交金额'].sum()
                # 归一化: 成交金额 / 30000 (单位: 亿元)
                total_amount_score = total_amount / 30000
            
            # 3. 流通换手率归一化
            if market_summary_data is not None and not market_summary_data.empty:
                avg_turnover = market_summary_data['流通换手率'].mean()
                # 归一化: 换手率 / 1 (换手率本身就是比例)
                turnover_score = avg_turnover / 0.1
            
            # 等权重简单平均
            normalized_scores = [limit_up_score, total_amount_score, turnover_score]
            # 过滤掉无效分数（为0的分数）
            valid_scores = [score for score in normalized_scores if score > 0]
            
            if valid_scores:
                # 计算等权重平均分
                avg_score = sum(valid_scores) / len(valid_scores) * 10
                # 限制在0-10分范围内
                final_score = max(0.0, min(avg_score, 10.0))
            else:
                # 如果没有有效数据，返回默认分数
                final_score = 5.0
            
            return round(final_score, 1)
            
        except Exception as e:
            print(f"❌ 计算市场活跃度分数失败: {e}")
            return 5.0
    
    def _calculate_profit_effect_score(self, 
                                     market_activity_data: Optional[pd.DataFrame],
                                     breakout_data: Optional[pd.DataFrame]) -> float:
        """计算个股赚钱效应分数"""
        try:
            # 初始化各指标分数
            up_ratio_score = 0.0
            breakout_score = 0.0

            latest_data = market_activity_data.iloc[0]
            total = latest_data.get('下跌', 0) + latest_data.get('上涨', 0) + latest_data.get('平盘', 0)
            
            # 1. 上涨家数分数：即上涨比例
            up_ratio = latest_data.get('上涨比例', 0)
            up_ratio_score = up_ratio / 100.0  # 上涨比例直接作为分数
            
            # 2. 突破20日均线个股数量占比评分：突破20日均线个股数量/1000
            if breakout_data is not None and not breakout_data.empty:
                breakout_count = len(breakout_data)
                breakout_score = breakout_count / total
            
            # 加权计算最终分数
            # 上涨家数权重：40%，突破20日均线个股数量占比权重：60%
            up_weight = 0.4
            breakout_weight = 0.6
            
            # 计算加权平均分数
            if up_ratio_score > 0 or breakout_score > 0:
                final_score = (up_ratio_score * up_weight + breakout_score * breakout_weight) * 10
                # 限制在0-10分范围内
                final_score = max(0.0, min(final_score, 10.0))
            else:
                # 如果没有有效数据，返回默认分数
                final_score = 5.0
            
            return round(final_score, 1)
            
        except Exception as e:
            print(f"❌ 计算赚钱效应分数失败: {e}")
            return 5.0
    
    def _calculate_risk_preference_score(self, margin_data: Optional[pd.DataFrame], market_summary_data: Optional[pd.DataFrame]) -> float:
        """计算风险偏好分数"""
        try:
            score = 5.0  # 基础分数
            
            if margin_data is not None and not margin_data.empty:
                latest_data = margin_data.iloc[-1]
                margin_balance = latest_data.get('融资余额', 0)
                score = margin_balance / market_summary_data['流通市值'].sum() / 0.05 * 10

            
            return round(max(0.0, min(score, 10.0)), 1)  # 限制在0-10分
            
        except Exception as e:
            print(f"❌ 计算风险偏好分数失败: {e}")
            return 5.0
    
    def _calculate_participation_willingness_score(self, fund_flow_data: Optional[pd.DataFrame]) -> float:
        """计算市场参与意愿分数"""
        try:
            score = 5.0  # 基础分数
            
            if fund_flow_data is not None and not fund_flow_data.empty:
                latest_data = fund_flow_data.iloc[-1]  # 使用最后一行数据
                main_inflow_ratio = latest_data.get('主力净流入-净占比', 0)
                super_inflow_ratio = latest_data.get('超大单净流入-净占比', 0)
                big_inflow_ratio = latest_data.get('大单净流入-净占比', 0)
                score = 5 + big_inflow_ratio
            
            return round(max(0.0, min(score, 10.0)), 1)  # 限制在0-10分
            
        except Exception as e:
            print(f"❌ 计算市场参与意愿分数失败: {e}")
            return 5.0

    def _calculate_overall_sentiment(self, sentiment_scores: Dict[str, float]) -> float:
        """
        计算综合情绪指数
        
        Args:
            sentiment_scores: 各维度分数
            
        Returns:
            float: 综合情绪指数 (0-10分，保留一位小数)
        """
        try:
            # 等权重法：将所有标准化后的指标简单平均
            scores = list(sentiment_scores.values())
            if not scores:
                return 5.0
            
            overall_score = sum(scores) / len(scores)
            return round(overall_score, 1)
            
        except Exception as e:
            print(f"❌ 计算综合情绪指数失败: {e}")
            return 5.0
    
    def _get_sentiment_level(self, score: float) -> str:
        """
        根据分数获取情绪等级
        
        Args:
            score: 情绪分数 (0-10)
            
        Returns:
            str: 情绪等级描述
        """
        if score >= 7.5:
            return "极度乐观"
        elif score >= 5.5:
            return "乐观"
        elif score >= 4.5:
            return "中性"
        elif score >= 2.5:
            return "悲观"
        else:
            return "极度悲观"
    
    def print_sentiment_analysis(self, sentiment_result: Dict[str, Any]):
        """
        打印市场情绪分析结果
        
        Args:
            sentiment_result: 市场情绪分析结果
        """
        try:
            if not sentiment_result:
                print("❌ 没有可显示的分析结果")
                return
            
            print("\n" + "="*60)
            print("📊 市场情绪分析报告")
            print("="*60)
            
            # 基本信息
            analysis_date = sentiment_result.get('analysis_date', '未知')
            overall_sentiment = sentiment_result.get('overall_sentiment', 0)
            sentiment_level = sentiment_result.get('sentiment_level', '未知')
            
            print(f"📅 分析日期: {analysis_date}")
            print(f"📈 综合情绪指数: {overall_sentiment:.1f}/10.0")
            print(f"🎯 情绪等级: {sentiment_level}")
            
            # 各维度分数
            sentiment_scores = sentiment_result.get('sentiment_scores', {})
            if sentiment_scores:
                print("\n📋 各维度情绪分数:")
                print("-" * 40)
                
                dimension_names = {
                    'market_activity': '市场活跃度',
                    'profit_effect': '个股赚钱效应',
                    'risk_preference': '风险偏好',
                    'participation_willingness': '市场参与意愿'
                }
                
                for key, name in dimension_names.items():
                    score = sentiment_scores.get(key, 0)
                    print(f"{name:12}: {score:5.1f}/10.0")
            
            print("="*60)

        except Exception as e:
            print(f"❌ 打印市场情绪分析结果失败: {e}")