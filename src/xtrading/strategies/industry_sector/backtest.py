"""
回测验证模块
基于指定日期的真实数据进行回测验证不同策略的表现
"""

import pandas as pd
import numpy as np
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from .macd_strategy import IndustryMACDStrategy
from .rsi_strategy import IndustryRSIStrategy
from .bollinger_bands_strategy import IndustryBollingerBandsStrategy
from .moving_average_strategy import IndustryMovingAverageStrategy
from ...repositories.stock.industry_info_query import IndustryInfoQuery
from ...static import INDUSTRY_CATEGORIES, ReportDirectoryConfig
from ...static.industry_sectors import get_industry_category
from ...utils.graphics import ChartGenerator
from ...utils.calculator import ReturnCalculator, RiskCalculator, StatisticsCalculator, TradingCalculator, AnomalyCalculator, MarketCalculator
from ...utils.docs import SectorReportGenerator, SectorsSummaryGenerator

class StrategyBacktest:
    """策略回测验证类"""
    
    def __init__(self):
        """初始化回测类"""
        self.industry_query = IndustryInfoQuery()
        self.macd_strategy = IndustryMACDStrategy()
        self.rsi_strategy = IndustryRSIStrategy()
        self.bb_strategy = IndustryBollingerBandsStrategy()
        self.ma_strategy = IndustryMovingAverageStrategy()
        self.chart_generator = ChartGenerator()
        
        # 初始化文档处理工具类
        self.sector_generator = SectorReportGenerator()
        self.summary_generator = SectorsSummaryGenerator()
        self.anomaly_calculator = AnomalyCalculator()
    
    def _detect_anomalies_wrapper(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        异动检测包装方法，用于兼容旧的接口
        
        Args:
            results: 回测结果列表
            
        Returns:
            List[str]: 异动提醒信息列表
        """
        if not results:
            return []
        
        first_result = results[0]
        hist_data = first_result.get('historical_data')
        industry_name = first_result.get('industry_name', '')
        
        if hist_data is None or hist_data.empty:
            return []
        
        # 使用计算器计算异动指标
        sector_metrics = self.anomaly_calculator.calculate_sector_anomaly_metrics(hist_data, industry_name)
        strategy_metrics = self.anomaly_calculator.calculate_strategy_anomaly_metrics(results, hist_data)
        
        # 使用检测器生成异动提醒
        return self.sector_generator.generate_anomaly_alerts(sector_metrics, strategy_metrics)
    
    def _calculate_sector_performance(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        计算板块表现数据
        
        Args:
            results: 回测结果列表
            
        Returns:
            Dict[str, Any]: 板块表现数据
        """
        if not results:
            return None
        
        first_result = results[0]
        hist_data = first_result.get('historical_data')
        
        if hist_data is None or hist_data.empty:
            return None
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return None
        
        # 计算板块买入并持有的表现
        sector_total_return = ReturnCalculator.calculate_sector_return(hist_data[close_col])
        
        # 计算板块年化收益率
        data_points = len(hist_data)
        sector_annualized_return = ReturnCalculator.calculate_annualized_return(sector_total_return, data_points)
        
        # 计算板块波动率
        sector_returns = ReturnCalculator.calculate_daily_returns(hist_data[close_col])
        sector_volatility = RiskCalculator.calculate_volatility(sector_returns)
        
        # 计算板块夏普比率
        sector_sharpe_ratio = RiskCalculator.calculate_sharpe_ratio(sector_returns)
        
        # 计算板块最大回撤
        sector_max_drawdown = RiskCalculator.calculate_max_drawdown(hist_data[close_col])
        
        # 计算初始和最终价值（假设初始资金100000）
        initial_capital = 100000
        final_value = initial_capital * (1 + sector_total_return)
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': sector_total_return,
            'annualized_return': sector_annualized_return,
            'volatility': sector_volatility,
            'sharpe_ratio': sector_sharpe_ratio,
            'max_drawdown': sector_max_drawdown,
            'data_points': data_points
        }
    
    def _calculate_sector_returns(self, results: List[Dict[str, Any]]) -> Tuple[List[float], List[float]]:
        """
        计算板块收益率数据
        
        Args:
            results: 回测结果列表
            
        Returns:
            Tuple[List[float], List[float]]: (日收益率序列, 累计收益率序列)
        """
        if not results:
            return [], []
        
        first_result = results[0]
        hist_data = first_result.get('historical_data')
        
        if hist_data is None or hist_data.empty:
            return [], []
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return [], []
        
        # 计算板块日收益率和累计收益率
        daily_returns = ReturnCalculator.calculate_daily_returns(hist_data[close_col])
        cumulative_returns = ReturnCalculator.calculate_cumulative_returns(hist_data[close_col])
        
        return daily_returns.tolist(), cumulative_returns.tolist()
    
    def _calculate_strategy_returns(self, results: List[Dict[str, Any]]) -> None:
        """
        计算策略收益率数据并添加到结果中
        
        Args:
            results: 回测结果列表
        """
        for result in results:
            portfolio_values = result.get('portfolio_values', [])
            initial_capital = result.get('initial_capital', 100000)
            
            if not portfolio_values:
                result['daily_returns'] = []
                result['cumulative_returns'] = []
                result['trade_statistics'] = TradingCalculator.calculate_trade_statistics([])
                continue
            
            # 计算日收益率
            portfolio_values_list = [pv['portfolio_value'] for pv in portfolio_values]
            daily_returns = TradingCalculator.calculate_portfolio_daily_returns(portfolio_values_list)
            
            # 计算累计收益率
            cumulative_returns = []
            for i, pv in enumerate(portfolio_values):
                cumulative_return = ReturnCalculator.calculate_strategy_cumulative_return(
                    portfolio_values, i, initial_capital
                )
                cumulative_returns.append(cumulative_return)
            
            # 计算交易统计
            trades = result.get('trades', [])
            trade_stats = TradingCalculator.calculate_trade_statistics(trades)
            trade_stats['trading_frequency'] = TradingCalculator.calculate_trading_frequency(
                trade_stats['total_trades'], result.get('data_points', 0)
            )
            
            # 添加到结果中
            result['daily_returns'] = daily_returns
            result['cumulative_returns'] = cumulative_returns
            result['trade_statistics'] = trade_stats
    
    def get_historical_data(self, industry_name: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取行业板块历史数据
        
        Args:
            industry_name: 行业板块名称
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 历史数据
        """
        try:
            
            hist_data = self.industry_query.get_board_industry_hist(industry_name, start_date, end_date)
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {industry_name} 的历史数据")
                return None
            
            print(f"✅ 成功获取 {industry_name} 历史数据 ({len(hist_data)} 条记录)")
            return hist_data
            
        except Exception as e:
            print(f"❌ 获取 {industry_name} 历史数据失败: {e}")
            return None
    
    def calculate_strategy_signals(self, data: pd.DataFrame, strategy_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        计算策略交易信号
        
        Args:
            data: 历史数据
            strategy_name: 策略名称
            **kwargs: 策略参数
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        try:
            if strategy_name == "MACD":
                # 提取MACD相关参数
                macd_params = {k: v for k, v in kwargs.items() if k in ['fast_period', 'slow_period', 'signal_period']}
                # 计算MACD指标
                macd_data = self.macd_strategy.calculate_macd(data, **macd_params)
                if macd_data is None:
                    return None
                # 生成交易信号
                return self.macd_strategy.generate_macd_signals(macd_data)
                
            elif strategy_name == "RSI":
                # 提取RSI相关参数
                rsi_params = {k: v for k, v in kwargs.items() if k in ['period']}
                signal_params = {k: v for k, v in kwargs.items() if k in ['oversold', 'overbought']}
                # 计算RSI指标
                rsi_data = self.rsi_strategy.calculate_rsi(data, **rsi_params)
                if rsi_data is None:
                    return None
                # 生成交易信号
                return self.rsi_strategy.generate_rsi_signals(rsi_data, **signal_params)
                
            elif strategy_name == "BollingerBands":
                # 提取布林带相关参数
                bb_params = {k: v for k, v in kwargs.items() if k in ['period', 'std_dev']}
                # 计算布林带指标
                bb_data = self.bb_strategy.calculate_bollinger_bands(data, **bb_params)
                if bb_data is None:
                    return None
                # 生成交易信号
                return self.bb_strategy.generate_bollinger_signals(bb_data)
                
            elif strategy_name == "MovingAverage":
                # 提取移动平均相关参数
                ma_params = {k: v for k, v in kwargs.items() if k in ['short_period', 'medium_period', 'long_period']}
                # 计算移动平均指标
                ma_data = self.ma_strategy.calculate_moving_averages(data, **ma_params)
                if ma_data is None:
                    return None
                # 生成交易信号
                return self.ma_strategy.generate_ma_signals(ma_data)
                
            else:
                print(f"❌ 不支持的策略: {strategy_name}")
                return None
                
        except Exception as e:
            print(f"❌ 计算 {strategy_name} 策略信号失败: {e}")
            return None
    
    def simulate_trading(self, signal_data: pd.DataFrame, initial_capital: float = 100000) -> Dict[str, Any]:
        """
        模拟交易过程
        
        Args:
            signal_data: 包含交易信号的DataFrame
            initial_capital: 初始资金
            
        Returns:
            Dict: 交易结果统计
        """
        if signal_data is None or signal_data.empty:
            return None
        
        # 确保有收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in signal_data.columns:
                close_col = col
                break
        
        if close_col is None:
            print("❌ 未找到收盘价列")
            return None
        
        # 初始化交易状态
        capital = initial_capital
        position = 0  # 持仓数量
        trades = []  # 交易记录
        portfolio_values = []  # 组合价值记录
        
        # 遍历每个交易日
        for i, row in signal_data.iterrows():
            current_price = row[close_col]
            signal = row.get('Signal', 0)
            signal_type = row.get('Signal_Type', 'HOLD')
            date = row.get('日期', f'Day_{i}')
            
            # 计算当前组合价值
            current_value = capital + (position * current_price)
            portfolio_values.append({
                'date': date,
                'price': current_price,
                'capital': capital,
                'position': position,
                'portfolio_value': current_value,
                'signal': signal,
                'signal_type': signal_type
            })
            
            # 执行交易
            if signal == 1:  # 买入信号
                if capital > 0:
                    # 全仓买入
                    shares_to_buy = capital // current_price
                    if shares_to_buy > 0:
                        cost = shares_to_buy * current_price
                        capital -= cost
                        position += shares_to_buy
                        trades.append({
                            'date': date,
                            'action': 'BUY',
                            'price': current_price,
                            'shares': shares_to_buy,
                            'amount': cost,
                            'capital_after': capital,
                            'position_after': position
                        })
            
            elif signal == -1:  # 卖出信号
                if position > 0:
                    # 全仓卖出
                    proceeds = position * current_price
                    capital += proceeds
                    trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': current_price,
                        'shares': position,
                        'amount': proceeds,
                        'capital_after': capital,
                        'position_after': 0
                    })
                    position = 0
            
            elif signal == 2:  # 强势买入
                if capital > 0:
                    shares_to_buy = capital // current_price
                    if shares_to_buy > 0:
                        cost = shares_to_buy * current_price
                        capital -= cost
                        position += shares_to_buy
                        trades.append({
                            'date': date,
                            'action': 'STRONG_BUY',
                            'price': current_price,
                            'shares': shares_to_buy,
                            'amount': cost,
                            'capital_after': capital,
                            'position_after': position
                        })
            
            elif signal == -2:  # 强势卖出
                if position > 0:
                    proceeds = position * current_price
                    capital += proceeds
                    trades.append({
                        'date': date,
                        'action': 'STRONG_SELL',
                        'price': current_price,
                        'shares': position,
                        'amount': proceeds,
                        'capital_after': capital,
                        'position_after': 0
                    })
                    position = 0
        
        # 计算最终结果
        final_price = signal_data.iloc[-1][close_col]
        final_value = TradingCalculator.calculate_portfolio_value(capital, position, final_price)
        
        # 计算统计指标
        portfolio_df = pd.DataFrame(portfolio_values)
        portfolio_values_list = portfolio_df['portfolio_value'].tolist()
        
        # 计算组合日收益率
        portfolio_returns = ReturnCalculator.calculate_daily_returns(portfolio_df['portfolio_value'])
        
        total_return = ReturnCalculator.calculate_total_return(initial_capital, final_value)
        annualized_return = ReturnCalculator.calculate_annualized_return(total_return, len(signal_data))
        volatility = RiskCalculator.calculate_volatility(portfolio_returns)
        sharpe_ratio = RiskCalculator.calculate_sharpe_ratio(portfolio_returns)
        max_drawdown = RiskCalculator.calculate_max_drawdown(portfolio_df['portfolio_value'])
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'buy_trades': len([t for t in trades if t['action'] in ['BUY', 'STRONG_BUY']]),
            'sell_trades': len([t for t in trades if t['action'] in ['SELL', 'STRONG_SELL']]),
            'trades': trades,
            'portfolio_values': portfolio_values
        }
    
    def backtest_strategy(self, industry_name: str, strategy_name: str, 
                         start_date: str, end_date: str, initial_capital: float = 100000,
                         **strategy_params) -> Optional[Dict[str, Any]]:
        """
        回测单个策略
        
        Args:
            industry_name: 行业板块名称
            strategy_name: 策略名称
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            **strategy_params: 策略参数
            
        Returns:
            Dict: 回测结果
        """
        print(f"🔍 开始回测 {industry_name} 的 {strategy_name} 策略...")
        
        # 获取历史数据
        hist_data = self.get_historical_data(industry_name, start_date, end_date)
        if hist_data is None:
            return None
        
        # 计算策略信号
        signal_data = self.calculate_strategy_signals(hist_data, strategy_name, **strategy_params)
        if signal_data is None:
            return None
        
        # 模拟交易
        trading_result = self.simulate_trading(signal_data, initial_capital)
        if trading_result is None:
            return None
        
        # 添加策略信息和历史数据
        trading_result.update({
            'industry_name': industry_name,
            'strategy_name': strategy_name,
            'start_date': start_date,
            'end_date': end_date,
            'strategy_params': strategy_params,
            'data_points': len(hist_data),
            'historical_data': hist_data  # 保存历史数据，避免重复调用
        })
        
        print(f"✅ {industry_name} {strategy_name} 策略回测完成")
        return trading_result
    
    def compare_strategies(self, industry_name: str, strategies: List[str], 
                         start_date: str, end_date: str, initial_capital: float = 100000,
                         **strategy_params) -> List[Dict[str, Any]]:
        """
        比较多个策略的表现
        
        Args:
            industry_name: 行业板块名称
            strategies: 策略名称列表
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            **strategy_params: 策略参数
            
        Returns:
            List[Dict]: 各策略回测结果列表
        """
        results = []
        
        print(f"🔍 开始比较 {industry_name} 的 {len(strategies)} 个策略...")
        
        for strategy in strategies:
            result = self.backtest_strategy(industry_name, strategy, start_date, end_date, 
                                          initial_capital, **strategy_params)
            if result:
                results.append(result)
        
        # 按总收益率排序
        results.sort(key=lambda x: x['total_return'], reverse=True)
        
        print(f"✅ {industry_name} 策略比较完成")
        return results
    
    def print_backtest_results(self, results: List[Dict[str, Any]]):
        """
        打印回测结果（使用DataFrame格式）
        
        Args:
            results: 回测结果列表
        """
        if not results:
            print("❌ 无回测结果可显示")
            return
        
        # 创建按回测日期和行业分类的回测结果目录
        backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
        industry_name = results[0].get('industry_name', 'Unknown')
        category = get_industry_category(industry_name)
        
        # 创建目录
        reports_dir, images_dir, summary_dir = ReportDirectoryConfig.create_report_directories(backtest_date)
        
        # 生成统一的时间戳，确保报告和图片使用相同的时间戳
        timestamp = datetime.now().strftime('%H%M%S')
        
        # 计算板块表现数据
        sector_performance = self._calculate_sector_performance(results)
        
        # 计算板块收益率数据
        sector_daily_returns, sector_cumulative_returns = self._calculate_sector_returns(results)
        
        # 计算策略收益率数据
        self._calculate_strategy_returns(results)
        
        # 使用工具类生成数据（现在只负责拼接，不涉及计算）
        comprehensive_data = self.sector_generator.get_comprehensive_data(results, sector_performance)
        daily_data = self.sector_generator.get_daily_returns_data(results, sector_daily_returns, results[0].get('historical_data'))
        cumulative_data = self.sector_generator.get_cumulative_returns_data(results, sector_cumulative_returns, results[0].get('historical_data'))
        daily_summary_data = self.sector_generator.get_daily_returns_summary_data(daily_data, results)
        cumulative_summary_data = self.sector_generator.get_cumulative_returns_summary_data(cumulative_data, results)
        # 检测异动
        first_result = results[0] if results else None
        if first_result:
            hist_data = first_result.get('historical_data')
            industry_name = first_result.get('industry_name', '')
            
            # 使用计算器计算异动指标
            sector_metrics = self.anomaly_calculator.calculate_sector_anomaly_metrics(hist_data, industry_name)
            strategy_metrics = self.anomaly_calculator.calculate_strategy_anomaly_metrics(results, hist_data)
            
            # 使用检测器生成异动提醒
            anomaly_alerts = self.sector_generator.generate_anomaly_alerts(sector_metrics, strategy_metrics)
        else:
            anomaly_alerts = []
        # 生成分析结论文档内容
        analysis_conclusion = self.sector_generator.generate_analysis_conclusion(results, anomaly_alerts)
        
        # 3. 保存Markdown报告
        self.sector_generator.generate_sector_report(
            results=results,
            reports_dir=reports_dir,
            category=category,
            industry_name=industry_name,
            timestamp=timestamp,
            comprehensive_data=comprehensive_data,
            daily_data=daily_data,
            cumulative_data=cumulative_data,
            daily_summary_data=daily_summary_data,
            cumulative_summary_data=cumulative_summary_data,
            analysis_conclusion=analysis_conclusion
        )
        
        # 4. 生成折线图
        self._generate_line_chart(results, images_dir, category, industry_name, timestamp)
        
        # 5. 生成累计收益折线图
        self._generate_cumulative_returns_chart(results, images_dir, category, industry_name, timestamp)
        
        print("=" * 80)

    def print_backtest_summary(self, all_results: List[List[Dict[str, Any]]]):
        """
        打印多行业板块回测总结报告

        Args:
            all_results: 多个行业板块的回测结果列表，每个元素是一个行业板块的回测结果列表
        """
        if not all_results:
            print("❌ 无回测数据可总结")
            return

        print("🔍 生成多行业板块回测总结报告...")

        # 创建整体回测报告目录
        backtest_date = datetime.now().strftime('%Y%m%d')
        reports_dir, images_dir, summary_dir = ReportDirectoryConfig.create_report_directories(backtest_date)

        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%H%M%S')

        # 使用MarketCalculator预计算各种统计数据
        market_stats = MarketCalculator.calculate_market_overview_stats(all_results)
        category_stats = MarketCalculator.calculate_sector_category_stats(all_results, get_industry_category)
        industry_stats = MarketCalculator.calculate_industry_stats(all_results, get_industry_category)
        strategy_ranking_data = MarketCalculator.calculate_strategy_ranking_stats(all_results)
        risk_return_stats = MarketCalculator.calculate_risk_return_stats(all_results)
        recommendation_data = MarketCalculator.calculate_investment_recommendations(all_results)
        
        # 计算各行业胜率
        industry_win_rates = {}
        for industry_stat in industry_stats:
            industry_name = industry_stat['industry']
            industry_win_rates[industry_name] = MarketCalculator.calculate_industry_win_rate(all_results, industry_name)
        
        # 收集所有异动信息
        all_anomalies = []
        for results in all_results:
            if results:
                anomalies = self._detect_anomalies_wrapper(results)
                all_anomalies.extend(anomalies)

        # 使用SectorsSummaryGenerator生成各种分析文档
        market_analysis = self.summary_generator.generate_market_overall_analysis(market_stats)
        sector_analysis = self.summary_generator.generate_sector_category_analysis(category_stats)
        industry_analysis = self.summary_generator.generate_industry_detail_analysis(industry_stats, industry_win_rates)
        strategy_ranking = self.summary_generator.generate_strategy_ranking(strategy_ranking_data)
        risk_return_analysis = self.summary_generator.generate_risk_return_analysis(risk_return_stats)
        anomaly_summary = self.summary_generator.generate_anomaly_summary(all_anomalies)
        investment_recommendations = self.summary_generator.generate_investment_recommendations(recommendation_data)

        # 生成总结报告
        self.summary_generator.generate_summary_report(
            all_results=all_results,
            summary_dir=summary_dir,
            timestamp=timestamp,
            market_analysis=market_analysis,
            sector_analysis=sector_analysis,
            industry_analysis=industry_analysis,
            strategy_ranking=strategy_ranking,
            risk_return_analysis=risk_return_analysis,
            anomaly_summary=anomaly_summary,
            investment_recommendations=investment_recommendations
        )

    def _generate_line_chart(self, results: List[Dict[str, Any]], images_dir: str = None, category: str = None, industry_name: str = None, timestamp: str = None):
        """生成日收益明细表的折线图"""
        if not results:
            print("❌ 无数据可生成折线图")
            return
        
        # 获取行业名称
        if industry_name is None:
            industry_name = results[0].get('industry_name', 'Unknown')
        if category is None:
            category = get_industry_category(industry_name)
        if timestamp is None:
            timestamp = datetime.now().strftime('%H%M%S')
        
        # 如果没有提供目录，创建新的回测结果目录
        if images_dir is None:
            backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
            images_dir = f"reports/images/{backtest_date}"
            os.makedirs(images_dir, exist_ok=True)
        
        # 计算板块收益率数据
        sector_daily_returns, _ = self._calculate_sector_returns(results)
        
        # 计算策略收益率数据
        self._calculate_strategy_returns(results)
        
        # 获取日收益数据
        daily_data = self.sector_generator.get_daily_returns_data(results, sector_daily_returns, results[0].get('historical_data'))
        if not daily_data:
            print("❌ 无日收益数据可生成折线图")
            return
        
        # 使用图形工具类生成图表
        self.chart_generator.generate_daily_returns_chart(
            daily_data=daily_data,
            results=results,
            industry_name=industry_name,
            category=category,
            output_dir=images_dir,
            timestamp=timestamp
        )
    
    def _generate_cumulative_returns_chart(self, results: List[Dict[str, Any]], images_dir: str = None, category: str = None, industry_name: str = None, timestamp: str = None):
        """生成累计收益明细表的折线图"""
        if not results:
            print("❌ 无数据可生成累计收益折线图")
            return
        
        # 获取行业名称
        if industry_name is None:
            industry_name = results[0].get('industry_name', 'Unknown')
        if category is None:
            category = get_industry_category(industry_name)
        if timestamp is None:
            timestamp = datetime.now().strftime('%H%M%S')
        
        # 如果没有提供目录，创建新的回测结果目录
        if images_dir is None:
            backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
            images_dir = f"reports/images/{backtest_date}"
            os.makedirs(images_dir, exist_ok=True)
        
        # 计算板块收益率数据
        _, sector_cumulative_returns = self._calculate_sector_returns(results)
        
        # 计算策略收益率数据
        self._calculate_strategy_returns(results)
        
        # 获取累计收益数据
        cumulative_data = self.sector_generator.get_cumulative_returns_data(results, sector_cumulative_returns, results[0].get('historical_data'))
        if not cumulative_data:
            print("❌ 无累计收益数据可生成折线图")
            return
        
        # 使用图形工具类生成图表
        self.chart_generator.generate_cumulative_returns_chart(
            cumulative_data=cumulative_data,
            results=results,
            industry_name=industry_name,
            category=category,
            output_dir=images_dir,
            timestamp=timestamp
        )