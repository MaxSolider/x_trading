"""
个股策略回测框架
基于个股历史数据进行多种策略的回测验证
"""

import pandas as pd
import numpy as np
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from .trend_tracking_strategy import IndividualTrendTrackingStrategy
from .breakout_strategy import IndividualBreakoutStrategy
from .oversold_rebound_strategy import IndividualOversoldReboundStrategy
from ...repositories.stock.stock_query import StockQuery
from ...static.stock_strategy_params import StockStrategyParams
from ...utils.calculator import ReturnCalculator, RiskCalculator, StatisticsCalculator, TradingCalculator
from ...utils.graphics import ChartGenerator
from ...utils.docs import SectorReportGenerator

class IndividualStockBacktest:
    """个股策略回测验证类"""
    
    def __init__(self):
        """初始化回测类"""
        self.stock_query = StockQuery()
        self.trend_strategy = IndividualTrendTrackingStrategy()
        self.breakout_strategy = IndividualBreakoutStrategy()
        self.oversold_strategy = IndividualOversoldReboundStrategy()
        self.chart_generator = ChartGenerator()
        self.sector_generator = SectorReportGenerator()
        
        print("✅ 个股策略回测框架初始化成功")
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取个股历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 历史数据
        """
        try:
            hist_data = self.stock_query.get_historical_quotes(symbol, start_date, end_date)
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {symbol} 的历史数据")
                return None
            
            print(f"✅ 成功获取 {symbol} 历史数据 ({len(hist_data)} 条记录)")
            return hist_data
            
        except Exception as e:
            print(f"❌ 获取 {symbol} 历史数据失败: {e}")
            return None
    
    def calculate_strategy_signals(self, data: pd.DataFrame, strategy_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        计算策略交易信号
        
        Args:
            data: 历史数据
            strategy_name: 策略名称
            **kwargs: 策略参数（可选，如果不提供则使用默认参数）
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        try:
            # 获取策略参数
            strategy_params = StockStrategyParams.get_strategy_params(strategy_name)
            
            if strategy_name == "TrendTracking":
                # 提取移动平均线参数
                ma_params = {
                    'short_period': kwargs.get('short_period', strategy_params.get('short_period', 5)),
                    'medium_period': kwargs.get('medium_period', strategy_params.get('medium_period', 20)),
                    'long_period': kwargs.get('long_period', strategy_params.get('long_period', 60))
                }
                
                # 提取MACD参数
                macd_params = {
                    'fast_period': kwargs.get('fast_period', strategy_params.get('fast_period', 12)),
                    'slow_period': kwargs.get('slow_period', strategy_params.get('slow_period', 26)),
                    'signal_period': kwargs.get('signal_period', strategy_params.get('signal_period', 9))
                }
                
                # 计算移动平均线
                ma_data = self.trend_strategy.calculate_moving_averages(data, **ma_params)
                if ma_data is None:
                    return None
                
                # 计算MACD指标
                macd_data = self.trend_strategy.calculate_macd(ma_data, **macd_params)
                if macd_data is None:
                    return None
                
                # 生成交易信号
                return self.trend_strategy.generate_trend_signals(macd_data)
                
            elif strategy_name == "Breakout":
                # 提取布林带参数
                bb_params = {
                    'period': kwargs.get('period', strategy_params.get('period', 20)),
                    'std_dev': kwargs.get('std_dev', strategy_params.get('std_dev', 2.0))
                }
                
                # 提取量比参数
                volume_params = {
                    'period': kwargs.get('volume_period', strategy_params.get('volume_period', 5))
                }
                
                # 提取阻力位参数
                resistance_params = {
                    'lookback_period': kwargs.get('resistance_lookback_period', strategy_params.get('resistance_lookback_period', 60))
                }
                
                # 提取突破信号参数
                signal_params = {
                    'volume_threshold': kwargs.get('volume_threshold', strategy_params.get('volume_threshold', 1.2))
                }
                
                # 计算布林带指标
                bb_data = self.breakout_strategy.calculate_bollinger_bands(data, **bb_params)
                if bb_data is None:
                    return None
                
                # 计算量比指标
                volume_data = self.breakout_strategy.calculate_volume_ratio(bb_data, **volume_params)
                if volume_data is None:
                    return None
                
                # 计算阻力位
                resistance_data = self.breakout_strategy.calculate_resistance_levels(volume_data, **resistance_params)
                if resistance_data is None:
                    return None
                
                # 生成交易信号
                return self.breakout_strategy.generate_breakout_signals(resistance_data, **signal_params)
                
            elif strategy_name == "OversoldRebound":
                # 提取KDJ参数
                kdj_params = {
                    'k_period': kwargs.get('k_period', strategy_params.get('k_period', 9)),
                    'd_period': kwargs.get('d_period', strategy_params.get('d_period', 3)),
                    'j_period': kwargs.get('j_period', strategy_params.get('j_period', 3))
                }
                
                # 提取RSI参数
                rsi_params = {
                    'period': kwargs.get('rsi_period', strategy_params.get('rsi_period', 14))
                }
                
                # 提取价格跌幅参数
                decline_params = {
                    'period': kwargs.get('decline_period', strategy_params.get('decline_period', 20))
                }
                
                # 提取超卖信号参数
                signal_params = {
                    'kdj_oversold': kwargs.get('kdj_oversold', strategy_params.get('kdj_oversold', 20)),
                    'rsi_oversold': kwargs.get('rsi_oversold', strategy_params.get('rsi_oversold', 30)),
                    'decline_threshold': kwargs.get('decline_threshold', strategy_params.get('decline_threshold', 15))
                }
                
                # 计算KDJ指标
                kdj_data = self.oversold_strategy.calculate_kdj(data, **kdj_params)
                if kdj_data is None:
                    return None
                
                # 计算RSI指标
                rsi_data = self.oversold_strategy.calculate_rsi(kdj_data, **rsi_params)
                if rsi_data is None:
                    return None
                
                # 计算价格跌幅
                decline_data = self.oversold_strategy.calculate_price_decline(rsi_data, **decline_params)
                if decline_data is None:
                    return None
                
                # 生成交易信号
                return self.oversold_strategy.generate_oversold_signals(decline_data, **signal_params)
                
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
        for col in ['收盘', '收盘价', 'close', 'Close']:
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
    
    def backtest_strategy(self, symbol: str, strategy_name: str, 
                         start_date: str, end_date: str, initial_capital: float = 100000,
                         **strategy_params) -> Optional[Dict[str, Any]]:
        """
        回测单个策略
        
        Args:
            symbol: 股票代码
            strategy_name: 策略名称
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            **strategy_params: 策略参数
            
        Returns:
            Dict: 回测结果
        """
        print(f"🔍 开始回测 {symbol} 的 {strategy_name} 策略...")
        
        # 获取历史数据
        hist_data = self.get_historical_data(symbol, start_date, end_date)
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
            'symbol': symbol,
            'strategy_name': strategy_name,
            'start_date': start_date,
            'end_date': end_date,
            'strategy_params': strategy_params,
            'data_points': len(hist_data),
            'historical_data': hist_data  # 保存历史数据，避免重复调用
        })
        
        print(f"✅ {symbol} {strategy_name} 策略回测完成")
        return trading_result
    
    def compare_strategies(self, symbol: str, strategies: List[str], 
                         start_date: str, end_date: str, initial_capital: float = 100000,
                         **strategy_params) -> List[Dict[str, Any]]:
        """
        比较多个策略的表现
        
        Args:
            symbol: 股票代码
            strategies: 策略名称列表
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            **strategy_params: 策略参数
            
        Returns:
            List[Dict]: 各策略回测结果列表
        """
        results = []
        
        print(f"🔍 开始比较 {symbol} 的 {len(strategies)} 个策略...")
        
        for strategy in strategies:
            result = self.backtest_strategy(symbol, strategy, start_date, end_date, 
                                          initial_capital, **strategy_params)
            if result:
                results.append(result)
        
        # 按总收益率排序
        results.sort(key=lambda x: x['total_return'], reverse=True)
        
        print(f"✅ {symbol} 策略比较完成")
        return results
    
    def _calculate_stock_performance(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        计算股票表现数据
        
        Args:
            results: 回测结果列表
            
        Returns:
            Dict[str, Any]: 股票表现数据
        """
        if not results:
            return None
        
        first_result = results[0]
        hist_data = first_result.get('historical_data')
        
        if hist_data is None or hist_data.empty:
            return None
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return None
        
        # 计算股票买入并持有的表现
        stock_total_return = ReturnCalculator.calculate_sector_return(hist_data[close_col])
        
        # 计算股票年化收益率
        data_points = len(hist_data)
        stock_annualized_return = ReturnCalculator.calculate_annualized_return(stock_total_return, data_points)
        
        # 计算股票波动率
        stock_returns = ReturnCalculator.calculate_daily_returns(hist_data[close_col])
        stock_volatility = RiskCalculator.calculate_volatility(stock_returns)
        
        # 计算股票夏普比率
        stock_sharpe_ratio = RiskCalculator.calculate_sharpe_ratio(stock_returns)
        
        # 计算股票最大回撤
        stock_max_drawdown = RiskCalculator.calculate_max_drawdown(hist_data[close_col])
        
        # 计算初始和最终价值（假设初始资金100000）
        initial_capital = 100000
        final_value = initial_capital * (1 + stock_total_return)
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': stock_total_return,
            'annualized_return': stock_annualized_return,
            'volatility': stock_volatility,
            'sharpe_ratio': stock_sharpe_ratio,
            'max_drawdown': stock_max_drawdown,
            'data_points': data_points
        }
    
    def _calculate_stock_returns(self, results: List[Dict[str, Any]]) -> Tuple[List[float], List[float]]:
        """
        计算股票收益率数据
        
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
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return [], []
        
        # 计算股票日收益率和累计收益率
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
    
    def print_backtest_results(self, results: List[Dict[str, Any]]):
        """
        打印回测结果
        
        Args:
            results: 回测结果列表
        """
        if not results:
            print("❌ 无回测结果可显示")
            return
        
        # 创建回测结果目录
        backtest_date = datetime.now().strftime('%Y%m%d')
        symbol = results[0].get('symbol', 'Unknown')
        
        # 创建目录
        reports_dir = f"reports/backtest/{backtest_date}/individual"
        images_dir = f"reports/images/{backtest_date}"
        os.makedirs(reports_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%H%M%S')
        
        # 计算股票表现数据
        stock_performance = self._calculate_stock_performance(results)
        
        # 计算股票收益率数据
        stock_daily_returns, stock_cumulative_returns = self._calculate_stock_returns(results)
        
        # 计算策略收益率数据
        self._calculate_strategy_returns(results)
        
        # 打印结果摘要
        print("=" * 80)
        print(f"📊 {symbol} 个股策略回测结果")
        print("=" * 80)
        
        if stock_performance:
            print(f"\n📈 股票买入并持有表现:")
            print(f"  初始资金: {stock_performance['initial_capital']:,.2f}")
            print(f"  最终价值: {stock_performance['final_value']:,.2f}")
            print(f"  总收益率: {stock_performance['total_return']:.2%}")
            print(f"  年化收益率: {stock_performance['annualized_return']:.2%}")
            print(f"  波动率: {stock_performance['volatility']:.2%}")
            print(f"  夏普比率: {stock_performance['sharpe_ratio']:.2f}")
            print(f"  最大回撤: {stock_performance['max_drawdown']:.2%}")
        
        print(f"\n📊 策略表现对比:")
        print(f"{'策略名称':<15} {'总收益率':<10} {'年化收益率':<12} {'夏普比率':<10} {'最大回撤':<10} {'交易次数':<8}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['strategy_name']:<15} "
                  f"{result['total_return']:<10.2%} "
                  f"{result['annualized_return']:<12.2%} "
                  f"{result['sharpe_ratio']:<10.2f} "
                  f"{result['max_drawdown']:<10.2%} "
                  f"{result['total_trades']:<8}")
        
        # 生成详细报告
        self._generate_detailed_report(results, reports_dir, symbol, timestamp, 
                                     stock_performance, stock_daily_returns, stock_cumulative_returns)
        
        # 生成图表
        self._generate_charts(results, images_dir, symbol, timestamp, 
                            stock_daily_returns, stock_cumulative_returns)
        
        print("=" * 80)
    
    def _generate_detailed_report(self, results: List[Dict[str, Any]], reports_dir: str, 
                                 symbol: str, timestamp: str, stock_performance: Dict[str, Any],
                                 stock_daily_returns: List[float], stock_cumulative_returns: List[float]):
        """
        生成详细回测报告
        
        Args:
            results: 回测结果列表
            reports_dir: 报告目录
            symbol: 股票代码
            timestamp: 时间戳
            stock_performance: 股票表现数据
            stock_daily_returns: 股票日收益率
            stock_cumulative_returns: 股票累计收益率
        """
        try:
            report_file = f"{reports_dir}/{symbol}_个股策略回测报告_{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# {symbol} 个股策略回测报告\n\n")
                f.write(f"**回测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**股票代码**: {symbol}\n")
                f.write(f"**回测期间**: {results[0]['start_date']} - {results[0]['end_date']}\n\n")
                
                # 股票表现
                if stock_performance:
                    f.write("## 股票买入并持有表现\n\n")
                    f.write(f"- **初始资金**: {stock_performance['initial_capital']:,.2f} 元\n")
                    f.write(f"- **最终价值**: {stock_performance['final_value']:,.2f} 元\n")
                    f.write(f"- **总收益率**: {stock_performance['total_return']:.2%}\n")
                    f.write(f"- **年化收益率**: {stock_performance['annualized_return']:.2%}\n")
                    f.write(f"- **波动率**: {stock_performance['volatility']:.2%}\n")
                    f.write(f"- **夏普比率**: {stock_performance['sharpe_ratio']:.2f}\n")
                    f.write(f"- **最大回撤**: {stock_performance['max_drawdown']:.2%}\n\n")
                
                # 策略对比
                f.write("## 策略表现对比\n\n")
                f.write("| 策略名称 | 总收益率 | 年化收益率 | 夏普比率 | 最大回撤 | 交易次数 |\n")
                f.write("|---------|---------|-----------|---------|---------|---------|\n")
                
                for result in results:
                    f.write(f"| {result['strategy_name']} | "
                           f"{result['total_return']:.2%} | "
                           f"{result['annualized_return']:.2%} | "
                           f"{result['sharpe_ratio']:.2f} | "
                           f"{result['max_drawdown']:.2%} | "
                           f"{result['total_trades']} |\n")
                
                f.write("\n")
                
                # 详细策略分析
                for i, result in enumerate(results, 1):
                    f.write(f"## {i}. {result['strategy_name']} 策略详细分析\n\n")
                    f.write(f"### 策略参数\n")
                    for key, value in result['strategy_params'].items():
                        f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
                    
                    f.write(f"### 交易统计\n")
                    f.write(f"- **买入交易**: {result['buy_trades']} 次\n")
                    f.write(f"- **卖出交易**: {result['sell_trades']} 次\n")
                    f.write(f"- **总交易次数**: {result['total_trades']} 次\n")
                    f.write(f"- **交易频率**: {result['trade_statistics'].get('trading_frequency', 0):.2f} 次/月\n\n")
                    
                    # 最近交易记录
                    if result['trades']:
                        f.write(f"### 最近交易记录\n\n")
                        f.write("| 日期 | 操作 | 价格 | 数量 | 金额 |\n")
                        f.write("|------|------|------|------|------|\n")
                        
                        for trade in result['trades'][-10:]:  # 显示最近10笔交易
                            f.write(f"| {trade['date']} | {trade['action']} | "
                                   f"{trade['price']:.2f} | {trade['shares']} | "
                                   f"{trade['amount']:.2f} |\n")
                        f.write("\n")
            
            print(f"✅ 详细回测报告已生成: {report_file}")
            
        except Exception as e:
            print(f"❌ 生成详细回测报告失败: {e}")
    
    def _generate_charts(self, results: List[Dict[str, Any]], images_dir: str, symbol: str, 
                        timestamp: str, stock_daily_returns: List[float], stock_cumulative_returns: List[float]):
        """
        生成回测图表
        
        Args:
            results: 回测结果列表
            images_dir: 图片目录
            symbol: 股票代码
            timestamp: 时间戳
            stock_daily_returns: 股票日收益率
            stock_cumulative_returns: 股票累计收益率
        """
        try:
            # 这里可以调用图表生成器生成各种图表
            # 由于图表生成器可能需要特定的数据格式，这里先预留接口
            print(f"✅ 图表生成功能待实现")
            
        except Exception as e:
            print(f"❌ 生成图表失败: {e}")
    
    def analyze_multiple_stocks(self, symbols: List[str], strategies: List[str], 
                              start_date: str, end_date: str, initial_capital: float = 100000) -> Dict[str, List[Dict[str, Any]]]:
        """
        分析多个股票的多种策略
        
        Args:
            symbols: 股票代码列表
            strategies: 策略名称列表
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            
        Returns:
            Dict[str, List[Dict]]: 按股票分组的回测结果
        """
        all_results = {}
        
        print(f"🔍 开始分析 {len(symbols)} 个股票的 {len(strategies)} 种策略...")
        
        for symbol in symbols:
            print(f"\n📊 分析股票: {symbol}")
            results = self.compare_strategies(symbol, strategies, start_date, end_date, initial_capital)
            if results:
                all_results[symbol] = results
        
        print(f"\n✅ 多股票策略分析完成")
        return all_results
