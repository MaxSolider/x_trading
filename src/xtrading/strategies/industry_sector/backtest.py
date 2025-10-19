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
from ...static import INDUSTRY_CATEGORIES

class StrategyBacktest:
    """策略回测验证类"""
    
    def __init__(self):
        """初始化回测类"""
        self.industry_query = IndustryInfoQuery()
        self.macd_strategy = IndustryMACDStrategy()
        self.rsi_strategy = IndustryRSIStrategy()
        self.bb_strategy = IndustryBollingerBandsStrategy()
        self.ma_strategy = IndustryMovingAverageStrategy()
    
    def get_industry_category(self, industry_name: str) -> str:
        """
        根据行业名称获取对应的分类
        
        Args:
            industry_name: 行业板块名称
            
        Returns:
            str: 行业分类名称
        """
        for category, sectors in INDUSTRY_CATEGORIES.items():
            if industry_name in sectors:
                return category
        return "其他"  # 如果找不到分类，默认为"其他"
    
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
        final_value = capital + (position * final_price)
        
        # 计算统计指标
        portfolio_df = pd.DataFrame(portfolio_values)
        returns = portfolio_df['portfolio_value'].pct_change().dropna()
        
        total_return = (final_value - initial_capital) / initial_capital
        annualized_return = (1 + total_return) ** (252 / len(signal_data)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        max_drawdown = self.calculate_max_drawdown(portfolio_df['portfolio_value'])
        
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
    
    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            portfolio_values: 组合价值序列
            
        Returns:
            float: 最大回撤
        """
        peak = portfolio_values.expanding().max()
        # 避免除零错误
        drawdown = np.where(peak != 0, (portfolio_values - peak) / peak, 0)
        return drawdown.min()
    
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
        category = self.get_industry_category(industry_name)
        
        # 创建新的目录结构
        reports_dir = f"backtest/reports/{backtest_date}"
        images_dir = f"backtest/images/{backtest_date}"
        os.makedirs(reports_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        # 生成统一的时间戳，确保报告和图片使用相同的时间戳
        timestamp = datetime.now().strftime('%H%M%S')
        
        # 3. 保存Markdown报告
        self._save_markdown_report(results, reports_dir, category, industry_name, timestamp)
        
        # 4. 生成折线图
        self._generate_line_chart(results, images_dir, category, industry_name, timestamp)
        
        # 5. 生成累计收益折线图
        self._generate_cumulative_returns_chart(results, images_dir, category, industry_name, timestamp)
        
        print("=" * 80)
    
    def _save_markdown_report(self, results: List[Dict[str, Any]], reports_dir: str = None, category: str = None, industry_name: str = None, timestamp: str = None):
        """保存Markdown格式的报告到文件"""
        if not results:
            print("❌ 无数据可保存")
            return
        
        # 获取行业名称
        if industry_name is None:
            industry_name = results[0].get('industry_name', 'Unknown')
        if category is None:
            category = self.get_industry_category(industry_name)
        if timestamp is None:
            timestamp = datetime.now().strftime('%H%M%S')
        
        # 如果没有提供目录，创建新的回测结果目录
        if reports_dir is None:
            backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
            reports_dir = f"backtest/reports/{backtest_date}"
            os.makedirs(reports_dir, exist_ok=True)
        
        # 生成带时间戳的文件名
        filename = f"{reports_dir}/{category}_{industry_name}_{timestamp}.md"
        
        # 生成图片的相对路径
        backtest_date = datetime.now().strftime('%Y%m%d')
        daily_chart_path = f"../../images/{backtest_date}/{category}_{industry_name}_每日收益率_{timestamp}.png"
        cumulative_chart_path = f"../../images/{backtest_date}/{category}_{industry_name}_累计收益率_{timestamp}.png"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入报告标题
                f.write(f"# 策略回测结果报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**行业板块**: {industry_name}\n")
                f.write(f"**回测期间**: {results[0]['start_date']} 至 {results[0]['end_date']}\n")
                f.write(f"**策略数量**: {len(results)}\n\n")

                # 写入分析结论
                f.write("## 📈 分析结论\n\n")
                f.write(self._generate_analysis_conclusion(results))
                f.write("\n")

                # 写入综合结果表
                f.write("## 📊 综合结果表\n\n")
                comprehensive_data = self._get_comprehensive_data(results)
                if comprehensive_data:
                    comprehensive_df = pd.DataFrame(comprehensive_data)
                    f.write(comprehensive_df.to_markdown(index=False))
                    f.write("\n\n")

                # 插入每日收益率折线图
                f.write("## 📊 每日收益率走势图\n\n")
                f.write(f"![每日收益率走势图]({daily_chart_path})\n\n")
                f.write(f"*图1: {industry_name}板块每日收益率走势对比*\n\n")

                # 插入累计收益率折线图
                f.write("## 📈 累计收益率走势图\n\n")
                f.write(f"![累计收益率走势图]({cumulative_chart_path})\n\n")
                f.write(f"*图2: {industry_name}板块累计收益率走势对比*\n\n")

                # 写入日收益明细表
                f.write("## 📅 日收益明细表\n\n")
                daily_data = self._get_daily_returns_data(results)
                if daily_data:
                    daily_df = pd.DataFrame(daily_data)
                    f.write(daily_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入日收益统计摘要
                f.write("## 📊 日收益统计摘要\n\n")
                summary_data = self._get_daily_returns_summary_data(daily_data, results)
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    f.write(summary_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入累计收益明细表
                f.write("## 📈 累计收益明细表\n\n")
                cumulative_data = self._get_cumulative_returns_data(results)
                if cumulative_data:
                    cumulative_df = pd.DataFrame(cumulative_data)
                    f.write(cumulative_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入累计收益统计摘要
                f.write("## 📊 累计收益统计摘要\n\n")
                cumulative_summary_data = self._get_cumulative_returns_summary_data(cumulative_data, results)
                if cumulative_summary_data:
                    cumulative_summary_df = pd.DataFrame(cumulative_summary_data)
                    f.write(cumulative_summary_df.to_markdown(index=False))
                    f.write("\n\n")
            
        except Exception as e:
            print(f"❌ 保存Markdown报告失败: {e}")
    
    def _get_comprehensive_data(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取综合结果表数据"""
        comprehensive_data = []
        
        # 添加板块实际表现数据
        if results:
            first_result = results[0]
            industry_name = first_result.get('industry_name', '')
            start_date = first_result.get('start_date', '')
            end_date = first_result.get('end_date', '')
            
            # 使用回测结果中的历史数据，避免重复调用
            hist_data = first_result.get('historical_data')
            if hist_data is not None and not hist_data.empty:
                # 找到收盘价列
                close_col = None
                for col in ['收盘价', 'close', 'Close']:
                    if col in hist_data.columns:
                        close_col = col
                        break
                
                if close_col is not None:
                    # 计算板块买入并持有的表现
                    initial_price = hist_data.iloc[0][close_col]
                    final_price = hist_data.iloc[-1][close_col]
                    sector_total_return = (final_price - initial_price) / initial_price
                    
                    # 计算板块年化收益率
                    data_points = len(hist_data)
                    sector_annualized_return = (1 + sector_total_return) ** (252 / data_points) - 1
                    
                    # 计算板块波动率
                    returns = hist_data[close_col].pct_change().dropna()
                    sector_volatility = returns.std() * np.sqrt(252)
                    
                    # 计算板块夏普比率
                    sector_sharpe_ratio = sector_annualized_return / sector_volatility if sector_volatility > 0 else 0
                    
                    # 计算板块最大回撤
                    sector_max_drawdown = self.calculate_max_drawdown(hist_data[close_col])
                    
                    # 计算初始和最终价值（假设初始资金100000）
                    initial_capital = 100000
                    final_value = initial_capital * (1 + sector_total_return)
                    
                    # 添加板块实际表现行
                    comprehensive_data.append({
                        '策略名称': '板块实际表现',
                        '初始资金': f"¥{initial_capital:,.0f}",
                        '最终价值': f"¥{final_value:,.0f}",
                        '总收益率': f"{sector_total_return:.2%}",
                        '年化收益率': f"{sector_annualized_return:.2%}",
                        '波动率': f"{sector_volatility:.2%}",
                        '夏普比率': f"{sector_sharpe_ratio:.4f}",
                        '最大回撤': f"{sector_max_drawdown:.2%}",
                        '总交易次数': 'N/A',
                        '买入次数': 'N/A',
                        '卖出次数': 'N/A',
                        '总交易金额': 'N/A',
                        '平均交易金额': 'N/A',
                        '交易频率': 'N/A',
                        '数据点数': data_points
                    })
        
        # 添加各策略数据
        for result in results:
            trades = result.get('trades', [])
            buy_trades = len([t for t in trades if t['action'] in ['BUY', 'STRONG_BUY']])
            sell_trades = len([t for t in trades if t['action'] in ['SELL', 'STRONG_SELL']])
            
            # 计算平均交易金额
            total_trade_amount = sum(trade['amount'] for trade in trades)
            avg_trade_amount = total_trade_amount / len(trades) if trades else 0
            
            comprehensive_data.append({
                '策略名称': result['strategy_name'],
                '初始资金': f"¥{result['initial_capital']:,.0f}",
                '最终价值': f"¥{result['final_value']:,.0f}",
                '总收益率': f"{result['total_return']:.2%}",
                '年化收益率': f"{result['annualized_return']:.2%}",
                '波动率': f"{result['volatility']:.2%}",
                '夏普比率': f"{result['sharpe_ratio']:.4f}",
                '最大回撤': f"{result['max_drawdown']:.2%}",
                '总交易次数': result['total_trades'],
                '买入次数': buy_trades,
                '卖出次数': sell_trades,
                '总交易金额': f"¥{total_trade_amount:,.0f}",
                '平均交易金额': f"¥{avg_trade_amount:,.0f}",
                '交易频率': f"{result['total_trades'] / result['data_points']:.2f}" if result['data_points'] > 0 else "0.00",
                '数据点数': result['data_points']
            })
        
        return comprehensive_data
    
    def _get_daily_returns_data(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取日收益明细数据"""
        if not results:
            return []
        
        # 获取第一个结果的数据作为基准
        first_result = results[0]
        industry_name = first_result.get('industry_name', '')
        start_date = first_result.get('start_date', '')
        end_date = first_result.get('end_date', '')
        
        # 使用回测结果中的历史数据，避免重复调用
        hist_data = first_result.get('historical_data')
        if hist_data is None or hist_data.empty:
            return []
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return []
        
        # 计算板块实际日收益率
        hist_data['板块实际收益率'] = hist_data[close_col].pct_change() * 100
        
        # 准备日收益明细数据
        daily_data = []
        
        for _, row in hist_data.iterrows():
            date_str = row.get('日期', f'Day_{_}')
            if '日期' not in row:
                # 如果没有日期列，使用索引
                date_str = f'Day_{_}'
            
            sector_return = row['板块实际收益率']
            
            # 初始化行数据
            row_data = {
                '日期': date_str,
                '板块实际收益率': f"{sector_return:.2f}%" if not pd.isna(sector_return) else "0.00%"
            }
            
            # 添加每个策略的日收益率
            for result in results:
                strategy_name = result['strategy_name']
                strategy_portfolio = result.get('portfolio_values', [])
                
                # 计算策略日收益率
                strategy_daily_return = "0.00%"
                
                if strategy_portfolio and len(strategy_portfolio) > 0:
                    # 通过索引匹配，因为portfolio_values和历史数据的顺序是一致的
                    current_portfolio = None
                    prev_portfolio = None
                    
                    if _ < len(strategy_portfolio):
                        current_portfolio = strategy_portfolio[_]
                        # 找到前一个交易日
                        if _ > 0:
                            prev_portfolio = strategy_portfolio[_ - 1]
                        
                        # 计算日收益率
                        if current_portfolio and prev_portfolio:
                            current_value = current_portfolio['portfolio_value']
                            prev_value = prev_portfolio['portfolio_value']
                            
                            if prev_value != 0:
                                daily_return = (current_value - prev_value) / prev_value * 100
                                strategy_daily_return = f"{daily_return:.2f}%"
                
                row_data[f'{strategy_name}收益率'] = strategy_daily_return
            
            daily_data.append(row_data)
        
        return daily_data
    
    def _get_cumulative_returns_data(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取每日累计收益率数据"""
        if not results:
            return []
        
        # 获取第一个结果的数据作为基准
        first_result = results[0]
        industry_name = first_result.get('industry_name', '')
        start_date = first_result.get('start_date', '')
        end_date = first_result.get('end_date', '')
        
        # 使用回测结果中的历史数据，避免重复调用
        hist_data = first_result.get('historical_data')
        if hist_data is None or hist_data.empty:
            return []
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return []
        
        # 计算板块实际累计收益率
        hist_data['板块实际收益率'] = hist_data[close_col].pct_change() * 100
        # 避免除零错误
        initial_price = hist_data[close_col].iloc[0]
        hist_data['板块累计收益率'] = np.where(initial_price != 0, 
                                               (hist_data[close_col] / initial_price - 1) * 100, 0)
        
        # 准备累计收益明细数据
        cumulative_data = []
        
        for _, row in hist_data.iterrows():
            date_str = row.get('日期', f'Day_{_}')
            if '日期' not in row:
                # 如果没有日期列，使用索引
                date_str = f'Day_{_}'
            
            sector_cumulative = row['板块累计收益率']
            
            # 初始化行数据
            row_data = {
                '日期': date_str,
                '板块累计收益率': f"{sector_cumulative:.2f}%" if not pd.isna(sector_cumulative) else "0.00%"
            }
            
            # 添加每个策略的累计收益率
            for result in results:
                strategy_name = result['strategy_name']
                strategy_portfolio = result.get('portfolio_values', [])
                
                # 计算策略累计收益率
                strategy_cumulative_return = "0.00%"
                
                if strategy_portfolio and len(strategy_portfolio) > 0:
                    # 通过索引匹配，因为portfolio_values和历史数据的顺序是一致的
                    current_portfolio = None
                    
                    if _ < len(strategy_portfolio):
                        current_portfolio = strategy_portfolio[_]
                        
                        # 计算累计收益率
                        if current_portfolio:
                            initial_capital = result.get('initial_capital', 100000)
                            current_value = current_portfolio['portfolio_value']
                            
                            if initial_capital != 0:
                                cumulative_return = (current_value - initial_capital) / initial_capital * 100
                                strategy_cumulative_return = f"{cumulative_return:.2f}%"
                
                row_data[f'{strategy_name}累计收益率'] = strategy_cumulative_return
            
            cumulative_data.append(row_data)
        
        return cumulative_data
    
    def _get_daily_returns_summary_data(self, daily_data: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取日收益统计摘要数据"""
        if not daily_data:
            return []
        
        summary_data = []
        
        # 板块实际收益率统计
        sector_returns = []
        for val in daily_data:
            try:
                sector_returns.append(float(val['板块实际收益率'].replace('%', '')))
            except:
                sector_returns.append(0.0)
        
        summary_data.append({
            '指标': '板块实际收益率',
            '平均日收益率': f"{sum(sector_returns) / len(sector_returns):.2f}%",
            '最大日收益率': f"{max(sector_returns):.2f}%",
            '最小日收益率': f"{min(sector_returns):.2f}%",
            '正收益天数': f"{len([r for r in sector_returns if r > 0])}天",
            '负收益天数': f"{len([r for r in sector_returns if r < 0])}天"
        })
        
        # 各策略收益率统计
        for result in results:
            strategy_name = result['strategy_name']
            col_name = f'{strategy_name}收益率'
            
            if col_name in daily_data[0] if daily_data else False:
                strategy_returns = []
                for val in daily_data:
                    try:
                        strategy_returns.append(float(val[col_name].replace('%', '')))
                    except:
                        strategy_returns.append(0.0)
                
                summary_data.append({
                    '指标': f'{strategy_name}收益率',
                    '平均日收益率': f"{sum(strategy_returns) / len(strategy_returns):.2f}%",
                    '最大日收益率': f"{max(strategy_returns):.2f}%",
                    '最小日收益率': f"{min(strategy_returns):.2f}%",
                    '正收益天数': f"{len([r for r in strategy_returns if r > 0])}天",
                    '负收益天数': f"{len([r for r in strategy_returns if r < 0])}天"
                })
        
        return summary_data
    
    def _generate_analysis_conclusion(self, results: List[Dict[str, Any]]) -> str:
        """生成分析结论"""
        if not results:
            return "无数据可分析"
        
        conclusion = []
        
        # 找出表现最好的策略
        best_strategy = max(results, key=lambda x: x['total_return'])
        worst_strategy = min(results, key=lambda x: x['total_return'])
        
        conclusion.append(f"### 策略表现分析\n")
        conclusion.append(f"- **最佳策略**: {best_strategy['strategy_name']} (总收益率: {best_strategy['total_return']:.2%})\n")
        conclusion.append(f"- **最差策略**: {worst_strategy['strategy_name']} (总收益率: {worst_strategy['total_return']:.2%})\n")
        
        # 交易活跃度分析
        active_strategies = [r for r in results if r['total_trades'] > 0]
        inactive_strategies = [r for r in results if r['total_trades'] == 0]
        
        conclusion.append(f"### 交易活跃度分析\n")
        conclusion.append(f"- **活跃策略**: {len(active_strategies)} 个\n")
        conclusion.append(f"- **非活跃策略**: {len(inactive_strategies)} 个\n")
        
        if active_strategies:
            most_active = max(active_strategies, key=lambda x: x['total_trades'])
            conclusion.append(f"- **最活跃策略**: {most_active['strategy_name']} (交易次数: {most_active['total_trades']})\n")

        # 异动提醒分析
        conclusion.append(f"### 🚨 异动提醒分析\n")
        anomaly_alerts = self._detect_anomalies(results)
        if anomaly_alerts:
            conclusion.extend(anomaly_alerts)
        else:
            conclusion.append("- 未检测到明显异动情况\n")

        # 风险分析
        conclusion.append(f"### 风险分析\n")
        for result in results:
            conclusion.append(f"- **{result['strategy_name']}**: 最大回撤 {result['max_drawdown']:.2%}, 夏普比率 {result['sharpe_ratio']:.4f}\n")

        return "".join(conclusion)
    
    def _detect_anomalies(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        检测板块和策略的异动情况
        
        Args:
            results: 回测结果列表
            
        Returns:
            List[str]: 异动提醒信息列表
        """
        if not results:
            return []
        
        alerts = []
        
        # 获取历史数据用于分析
        first_result = results[0]
        industry_name = first_result.get('industry_name', '')
        start_date = first_result.get('start_date', '')
        end_date = first_result.get('end_date', '')
        
        # 使用回测结果中的历史数据，避免重复调用
        hist_data = first_result.get('historical_data')
        if hist_data is None or hist_data.empty:
            return []
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return []
        
        # 计算板块收益率
        hist_data['daily_return'] = hist_data[close_col].pct_change()
        
        # 检测板块异动
        sector_alerts = self._detect_sector_anomalies(hist_data, industry_name)
        alerts.extend(sector_alerts)
        
        # 检测策略异动
        strategy_alerts = self._detect_strategy_anomalies(results, hist_data)
        alerts.extend(strategy_alerts)
        
        return alerts
    
    def _detect_sector_anomalies(self, hist_data: pd.DataFrame, industry_name: str) -> List[str]:
        """
        检测板块异动
        
        Args:
            hist_data: 历史数据
            industry_name: 行业名称
            
        Returns:
            List[str]: 板块异动提醒
        """
        alerts = []
        
        if len(hist_data) < 14:  # 至少需要14天数据
            return alerts
        
        # 计算近两周（14天）的收益率
        recent_14_days = hist_data.tail(14)
        recent_returns = recent_14_days['daily_return'].dropna()
        
        if len(recent_returns) < 7:  # 至少需要7个有效数据点
            return alerts
        
        # 计算整体期间收益率
        overall_returns = hist_data['daily_return'].dropna()
        
        if len(overall_returns) < 14:
            return alerts
        
        # 计算统计指标
        recent_mean = recent_returns.mean()
        recent_std = recent_returns.std()
        overall_mean = overall_returns.mean()
        overall_std = overall_returns.std()
        
        # 检测陡增/陡降
        recent_volatility = recent_std
        overall_volatility = overall_std
        
        # 波动率异常检测（近两周波动率是整体波动率的1.5倍以上）
        if recent_volatility > overall_volatility * 1.5:
            alerts.append(f"- **板块异动**: {industry_name} 近两周波动率异常 (近期: {recent_volatility:.2%}, 整体: {overall_volatility:.2%})\n")
        
        # 收益率偏离检测（近两周平均收益率偏离整体平均收益率超过1.5个标准差）
        deviation_threshold = overall_std * 1.5
        deviation = abs(recent_mean - overall_mean)
        
        if deviation > deviation_threshold:
            if recent_mean > overall_mean:
                alerts.append(f"- **板块异动**: {industry_name} 近两周收益率显著上升 (近期: {recent_mean:.2%}, 整体: {overall_mean:.2%})\n")
            else:
                alerts.append(f"- **板块异动**: {industry_name} 近两周收益率显著下降 (近期: {recent_mean:.2%}, 整体: {overall_mean:.2%})\n")
        
        # 检测极端单日收益（2.5个标准差）
        extreme_threshold = overall_std * 2.5
        extreme_days = recent_returns[abs(recent_returns) > extreme_threshold]
        
        if len(extreme_days) > 0:
            max_extreme = extreme_days.max()
            min_extreme = extreme_days.min()
            alerts.append(f"- **板块异动**: {industry_name} 近两周出现极端波动 (最大单日: {max_extreme:.2%}, 最小单日: {min_extreme:.2%})\n")
        
        # 检测大幅波动（近两周最大单日波动超过3%）
        max_daily_volatility = abs(recent_returns).max()
        if max_daily_volatility > 0.03:  # 3%
            alerts.append(f"- **板块异动**: {industry_name} 近两周出现大幅波动 (最大单日: {max_daily_volatility:.2%})\n")
        
        # 检测连续波动（近两周正负波动交替频繁）
        if len(recent_returns) >= 10:
            sign_changes = 0
            for i in range(1, len(recent_returns)):
                if (recent_returns.iloc[i] > 0) != (recent_returns.iloc[i-1] > 0):
                    sign_changes += 1
            
            volatility_frequency = sign_changes / len(recent_returns)
            if volatility_frequency > 0.6:  # 60%以上的交易日出现方向变化
                alerts.append(f"- **板块异动**: {industry_name} 近两周波动频繁 (方向变化频率: {volatility_frequency:.1%})\n")
        
        return alerts
    
    def _detect_strategy_anomalies(self, results: List[Dict[str, Any]], hist_data: pd.DataFrame) -> List[str]:
        """
        检测策略异动
        
        Args:
            results: 回测结果列表
            hist_data: 历史数据
            
        Returns:
            List[str]: 策略异动提醒
        """
        alerts = []
        
        if len(hist_data) < 14:  # 至少需要14天数据
            return alerts
        
        # 计算整体期间收益率作为基准
        hist_data['daily_return'] = hist_data['收盘价'].pct_change() if '收盘价' in hist_data.columns else hist_data['close'].pct_change()
        overall_returns = hist_data['daily_return'].dropna()
        
        if len(overall_returns) < 14:
            return alerts
        
        overall_mean = overall_returns.mean()
        overall_std = overall_returns.std()
        
        for result in results:
            strategy_name = result['strategy_name']
            portfolio_values = result.get('portfolio_values', [])
            
            if len(portfolio_values) < 14:
                continue
            
            # 计算策略近两周收益率
            recent_portfolio = portfolio_values[-14:]  # 近14天
            strategy_recent_returns = []
            
            for i in range(1, len(recent_portfolio)):
                current_value = recent_portfolio[i]['portfolio_value']
                prev_value = recent_portfolio[i-1]['portfolio_value']
                if prev_value != 0:
                    daily_return = (current_value - prev_value) / prev_value
                    strategy_recent_returns.append(daily_return)
            
            if len(strategy_recent_returns) < 7:  # 至少需要7个有效数据点
                continue
            
            # 计算策略统计指标
            strategy_recent_mean = np.mean(strategy_recent_returns)
            strategy_recent_std = np.std(strategy_recent_returns)
            
            # 检测策略波动率异常（1.5倍阈值）
            if strategy_recent_std > overall_std * 1.5:
                alerts.append(f"- **策略异动**: {strategy_name} 近两周波动率异常 (策略: {strategy_recent_std:.2%}, 板块: {overall_std:.2%})\n")
            
            # 检测策略收益率偏离（1.5倍阈值）
            deviation_threshold = overall_std * 1.5
            deviation = abs(strategy_recent_mean - overall_mean)
            
            if deviation > deviation_threshold:
                if strategy_recent_mean > overall_mean:
                    alerts.append(f"- **策略异动**: {strategy_name} 近两周收益率显著超越板块 (策略: {strategy_recent_mean:.2%}, 板块: {overall_mean:.2%})\n")
                else:
                    alerts.append(f"- **策略异动**: {strategy_name} 近两周收益率显著低于板块 (策略: {strategy_recent_mean:.2%}, 板块: {overall_mean:.2%})\n")
            
            # 检测策略极端表现（2.5倍阈值）
            extreme_threshold = overall_std * 2.5
            strategy_extreme_days = [r for r in strategy_recent_returns if abs(r) > extreme_threshold]
            
            if len(strategy_extreme_days) > 0:
                max_extreme = max(strategy_extreme_days)
                min_extreme = min(strategy_extreme_days)
                alerts.append(f"- **策略异动**: {strategy_name} 近两周出现极端表现 (最大单日: {max_extreme:.2%}, 最小单日: {min_extreme:.2%})\n")
            
            # 检测策略大幅波动（超过3%）
            max_strategy_volatility = max(abs(r) for r in strategy_recent_returns)
            if max_strategy_volatility > 0.03:  # 3%
                alerts.append(f"- **策略异动**: {strategy_name} 近两周出现大幅波动 (最大单日: {max_strategy_volatility:.2%})\n")
            
            # 检测策略与板块相关性异常
            if len(strategy_recent_returns) >= 7:
                try:
                    # 检查数据是否有变化（避免标准差为0的情况）
                    strategy_std = np.std(strategy_recent_returns)
                    overall_std = np.std(overall_returns.tail(len(strategy_recent_returns)))
                    
                    if strategy_std > 1e-10 and overall_std > 1e-10:  # 避免除零错误
                        correlation = np.corrcoef(strategy_recent_returns, overall_returns.tail(len(strategy_recent_returns)))[0, 1]
                        if not np.isnan(correlation) and abs(correlation) < 0.3:  # 相关性过低
                            alerts.append(f"- **策略异动**: {strategy_name} 与板块走势相关性异常 (相关系数: {correlation:.3f})\n")
                except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                    pass  # 忽略相关性计算错误
        
        return alerts
    
    def _generate_line_chart(self, results: List[Dict[str, Any]], images_dir: str = None, category: str = None, industry_name: str = None, timestamp: str = None):
        """生成日收益明细表的折线图"""
        if not results:
            print("❌ 无数据可生成折线图")
            return
        
        try:
            # 导入matplotlib
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            import warnings
            
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 忽略字体警告
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            
            # 获取行业名称
            if industry_name is None:
                industry_name = results[0].get('industry_name', 'Unknown')
            if category is None:
                category = self.get_industry_category(industry_name)
            if timestamp is None:
                timestamp = datetime.now().strftime('%H%M%S')
            
            # 如果没有提供目录，创建新的回测结果目录
            if images_dir is None:
                backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
                images_dir = f"backtest/images/{backtest_date}"
                os.makedirs(images_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            filename = f"{images_dir}/{category}_{industry_name}_每日收益率_{timestamp}.png"
            
            # 获取日收益数据
            daily_data = self._get_daily_returns_data(results)
            if not daily_data:
                print("❌ 无日收益数据可生成折线图")
                return
            
            # 数据读取与预处理
            df = pd.DataFrame(daily_data)
            
            # 处理日期列 - 转换为datetime格式
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            
            # 处理百分比数据 - 去除%符号并转换为浮点数
            numeric_columns = ['板块实际收益率']
            for result in results:
                strategy_name = result['strategy_name']
                numeric_columns.append(f'{strategy_name}收益率')
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].str.replace('%', '').astype(float)
            
            # 可视化处理
            plt.figure(figsize=(14, 8))  # 设置合适的图表尺寸
            
            # 绘制多系列折线图
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # 绘制板块实际收益率
            plt.plot(df['日期'], df['板块实际收益率'], 
                    label='板块实际收益率', linewidth=2.5, color=colors[0], marker='o', markersize=6)
            
            # 绘制各策略收益率
            for i, result in enumerate(results):
                strategy_name = result['strategy_name']
                col_name = f'{strategy_name}收益率'
                if col_name in df.columns:
                    plt.plot(df['日期'], df[col_name], 
                            label=f'{strategy_name}收益率', linewidth=2, 
                            color=colors[(i + 1) % len(colors)], marker='s', markersize=5)
            
            # 添加图表元素
            plt.title(f'{industry_name}板块日收益率对比图', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('日期', fontsize=12, fontweight='bold')
            plt.ylabel('收益率 (%)', fontsize=12, fontweight='bold')
            
            # 添加图例
            plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # 调整x轴标签旋转角度(45度)避免重叠
            plt.xticks(rotation=45)
            
            # 添加网格线提高可读性
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 设置y轴零线
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # 关闭图表以释放内存
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
        except Exception as e:
            print(f"❌ 生成折线图失败: {e}")
    
    def _generate_cumulative_returns_chart(self, results: List[Dict[str, Any]], images_dir: str = None, category: str = None, industry_name: str = None, timestamp: str = None):
        """生成累计收益明细表的折线图"""
        if not results:
            print("❌ 无数据可生成累计收益折线图")
            return
        
        try:
            # 导入matplotlib
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            import warnings
            
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 忽略字体警告
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            
            # 获取行业名称
            if industry_name is None:
                industry_name = results[0].get('industry_name', 'Unknown')
            if category is None:
                category = self.get_industry_category(industry_name)
            if timestamp is None:
                timestamp = datetime.now().strftime('%H%M%S')
            
            # 如果没有提供目录，创建新的回测结果目录
            if images_dir is None:
                backtest_date = datetime.now().strftime('%Y%m%d')  # 只使用日期，不包含时间
                images_dir = f"backtest/images/{backtest_date}"
                os.makedirs(images_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            filename = f"{images_dir}/{category}_{industry_name}_累计收益率_{timestamp}.png"
            
            # 获取累计收益数据
            cumulative_data = self._get_cumulative_returns_data(results)
            if not cumulative_data:
                print("❌ 无累计收益数据可生成折线图")
                return
            
            # 数据读取与预处理
            df = pd.DataFrame(cumulative_data)
            
            # 处理日期列 - 转换为datetime格式
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            
            # 处理百分比数据 - 去除%符号并转换为浮点数
            numeric_columns = ['板块累计收益率']
            for result in results:
                strategy_name = result['strategy_name']
                numeric_columns.append(f'{strategy_name}累计收益率')
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].str.replace('%', '').astype(float)
            
            # 可视化处理
            plt.figure(figsize=(14, 8))  # 设置合适的图表尺寸
            
            # 绘制多系列折线图
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # 绘制板块累计收益率
            plt.plot(df['日期'], df['板块累计收益率'], 
                    label='板块累计收益率', linewidth=2.5, color=colors[0], marker='o', markersize=6)
            
            # 绘制各策略累计收益率
            for i, result in enumerate(results):
                strategy_name = result['strategy_name']
                col_name = f'{strategy_name}累计收益率'
                if col_name in df.columns:
                    plt.plot(df['日期'], df[col_name], 
                            label=f'{strategy_name}累计收益率', linewidth=2, 
                            color=colors[(i + 1) % len(colors)], marker='s', markersize=5)
            
            # 添加图表元素
            plt.title(f'{industry_name}板块累计收益率对比图', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('日期', fontsize=12, fontweight='bold')
            plt.ylabel('累计收益率 (%)', fontsize=12, fontweight='bold')
            
            # 添加图例
            plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # 调整x轴标签旋转角度(45度)避免重叠
            plt.xticks(rotation=45)
            
            # 添加网格线提高可读性
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 设置y轴零线
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # 关闭图表以释放内存
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
        except Exception as e:
            print(f"❌ 生成累计收益折线图失败: {e}")
    
    def _get_cumulative_returns_summary_data(self, cumulative_data: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取累计收益统计摘要数据"""
        if not cumulative_data:
            return []
        
        summary_data = []
        
        # 板块实际累计收益率统计
        sector_cumulative = []
        for val in cumulative_data:
            try:
                sector_cumulative.append(float(val['板块累计收益率'].replace('%', '')))
            except:
                sector_cumulative.append(0.0)
        
        summary_data.append({
            '指标': '板块累计收益率',
            '最终累计收益率': f"{sector_cumulative[-1]:.2f}%",
            '最大累计收益率': f"{max(sector_cumulative):.2f}%",
            '最小累计收益率': f"{min(sector_cumulative):.2f}%",
            '累计收益波动': f"{max(sector_cumulative) - min(sector_cumulative):.2f}%",
            '收益稳定性': f"{'稳定' if max(sector_cumulative) - min(sector_cumulative) < 20 else '波动'}"
        })
        
        # 各策略累计收益率统计
        for result in results:
            strategy_name = result['strategy_name']
            col_name = f'{strategy_name}累计收益率'
            
            if col_name in cumulative_data[0] if cumulative_data else False:
                strategy_cumulative = []
                for val in cumulative_data:
                    try:
                        strategy_cumulative.append(float(val[col_name].replace('%', '')))
                    except:
                        strategy_cumulative.append(0.0)
                
                summary_data.append({
                    '指标': f'{strategy_name}累计收益率',
                    '最终累计收益率': f"{strategy_cumulative[-1]:.2f}%",
                    '最大累计收益率': f"{max(strategy_cumulative):.2f}%",
                    '最小累计收益率': f"{min(strategy_cumulative):.2f}%",
                    '累计收益波动': f"{max(strategy_cumulative) - min(strategy_cumulative):.2f}%",
                    '收益稳定性': f"{'稳定' if max(strategy_cumulative) - min(strategy_cumulative) < 20 else '波动'}"
                })
        
        return summary_data

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
        summary_dir = f"backtest/reports/{backtest_date}"
        os.makedirs(summary_dir, exist_ok=True)
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{summary_dir}/多板块策略回测总结_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入报告标题
                f.write(f"# 多行业板块策略回测总结报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**回测板块数量**: {len(all_results)}\n")
                f.write(f"**总策略数量**: {sum(len(results) for results in all_results)}\n\n")
                
                # 1. 市场整体分析
                f.write("## 📊 市场整体分析\n\n")
                market_analysis = self._generate_market_overall_analysis(all_results)
                f.write(market_analysis)
                f.write("\n")
                
                # 2. 板块分类分析
                f.write("## 🏢 板块分类分析\n\n")
                sector_analysis = self._generate_sector_category_analysis(all_results)
                f.write(sector_analysis)
                f.write("\n")
                
                # 3. 行业明细分析
                f.write("## 📈 行业明细分析\n\n")
                industry_analysis = self._generate_industry_detail_analysis(all_results)
                f.write(industry_analysis)
                f.write("\n")
                
                # 4. 策略表现排行
                f.write("## 🏆 策略表现排行\n\n")
                strategy_ranking = self._generate_strategy_ranking(all_results)
                f.write(strategy_ranking)
                f.write("\n")
                
                # 5. 风险收益分析
                f.write("## ⚖️ 风险收益分析\n\n")
                risk_return_analysis = self._generate_risk_return_analysis(all_results)
                f.write(risk_return_analysis)
                f.write("\n")
                
                # 6. 异动检测汇总
                f.write("## 🚨 异动检测汇总\n\n")
                anomaly_summary = self._generate_anomaly_summary(all_results)
                f.write(anomaly_summary)
                f.write("\n")
                
                # 7. 投资建议
                f.write("## 💡 投资建议\n\n")
                investment_recommendations = self._generate_investment_recommendations(all_results)
                f.write(investment_recommendations)
                f.write("\n")
            
        except Exception as e:
            print(f"❌ 生成整体回测报告失败: {e}")
    
    def _generate_market_overall_analysis(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成市场整体分析"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 统计基本信息
        total_industries = len(all_results)
        total_strategies = sum(len(results) for results in all_results)
        
        # 收集所有策略数据
        all_strategy_results = []
        for results in all_results:
            all_strategy_results.extend(results)
        
        if not all_strategy_results:
            return "无策略数据可分析"
        
        # 计算市场整体指标
        total_returns = [r['total_return'] for r in all_strategy_results]
        annualized_returns = [r['annualized_return'] for r in all_strategy_results]
        sharpe_ratios = [r['sharpe_ratio'] for r in all_strategy_results]
        max_drawdowns = [r['max_drawdown'] for r in all_strategy_results]
        volatilities = [r['volatility'] for r in all_strategy_results]
        
        # 计算统计指标
        avg_total_return = np.mean(total_returns)
        median_total_return = np.median(total_returns)
        best_return = max(total_returns)
        worst_return = min(total_returns)
        
        avg_annualized_return = np.mean(annualized_returns)
        avg_sharpe_ratio = np.mean(sharpe_ratios)
        avg_max_drawdown = np.mean(max_drawdowns)
        avg_volatility = np.mean(volatilities)
        
        # 计算胜率
        positive_returns = len([r for r in total_returns if r > 0])
        win_rate = positive_returns / len(total_returns)
        
        # 计算超越基准的比例
        benchmark_beating = len([r for r in total_returns if r > 0.1])  # 假设10%为基准
        benchmark_beating_rate = benchmark_beating / len(total_returns)
        
        # 使用表格展示市场概况
        analysis.append(f"### 📈 市场概况\n\n")
        market_overview_data = [
            {
                '指标': '回测板块数量',
                '数值': f"{total_industries} 个",
                '说明': '参与回测的行业板块总数'
            },
            {
                '指标': '总策略数量',
                '数值': f"{total_strategies} 个",
                '说明': '所有策略实例的总数'
            },
            {
                '指标': '策略胜率',
                '数值': f"{win_rate:.1%}",
                '说明': '获得正收益的策略比例'
            },
            {
                '指标': '超越基准比例',
                '数值': f"{benchmark_beating_rate:.1%}",
                '说明': '收益率超过10%的策略比例'
            }
        ]
        
        market_overview_df = pd.DataFrame(market_overview_data)
        analysis.append(market_overview_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示收益率统计
        analysis.append(f"### 📊 收益率统计\n\n")
        
        # 找到最佳和最差策略的具体信息
        best_strategy = max(all_strategy_results, key=lambda x: x['total_return'])
        worst_strategy = min(all_strategy_results, key=lambda x: x['total_return'])
        
        returns_stats_data = [
            {
                '指标': '平均总收益率',
                '数值': f"{avg_total_return:.2%}",
                '说明': '所有策略的平均表现'
            },
            {
                '指标': '中位数总收益率',
                '数值': f"{median_total_return:.2%}",
                '说明': '策略收益率的中位数'
            },
            {
                '指标': '最佳策略收益率',
                '数值': f"{best_return:.2%}",
                '说明': f"{best_strategy['industry_name']} - {best_strategy['strategy_name']}"
            },
            {
                '指标': '最差策略收益率',
                '数值': f"{worst_return:.2%}",
                '说明': f"{worst_strategy['industry_name']} - {worst_strategy['strategy_name']}"
            }
        ]
        
        returns_stats_df = pd.DataFrame(returns_stats_data)
        analysis.append(returns_stats_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def _generate_sector_category_analysis(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成板块分类分析"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 按板块分类统计
        category_stats = {}
        
        for results in all_results:
            if not results:
                continue
                
            industry_name = results[0].get('industry_name', 'Unknown')
            category = self.get_industry_category(industry_name)
            
            if category not in category_stats:
                category_stats[category] = {
                    'industries': [],
                    'strategies': [],
                    'total_returns': [],
                    'annualized_returns': [],
                    'sharpe_ratios': [],
                    'max_drawdowns': []
                }
            
            category_stats[category]['industries'].append(industry_name)
            category_stats[category]['strategies'].extend(results)
            
            for result in results:
                category_stats[category]['total_returns'].append(result['total_return'])
                category_stats[category]['annualized_returns'].append(result['annualized_return'])
                category_stats[category]['sharpe_ratios'].append(result['sharpe_ratio'])
                category_stats[category]['max_drawdowns'].append(result['max_drawdown'])
        
        # 按平均收益率排序
        sorted_categories = sorted(category_stats.items(), 
                                key=lambda x: np.mean(x[1]['total_returns']), 
                                reverse=True)
        
        # 使用表格展示板块分类表现对比
        analysis.append(f"### 🏢 板块分类表现对比\n\n")
        category_comparison_data = []
        
        for i, (category, stats) in enumerate(sorted_categories, 1):
            avg_return = np.mean(stats['total_returns'])
            avg_sharpe = np.mean(stats['sharpe_ratios'])
            avg_drawdown = np.mean(stats['max_drawdowns'])
            industry_count = len(stats['industries'])
            strategy_count = len(stats['strategies'])
            
            # 计算胜率
            positive_count = len([r for r in stats['total_returns'] if r > 0])
            win_rate = positive_count / len(stats['total_returns']) if stats['total_returns'] else 0
            
            category_comparison_data.append({
                '排名': f"#{i}",
                '板块分类': category,
                '包含板块数': f"{industry_count} 个",
                '策略数量': f"{strategy_count} 个",
                '平均总收益率': f"{avg_return:.2%}",
                '平均夏普比率': f"{avg_sharpe:.4f}",
                '平均最大回撤': f"{avg_drawdown:.2%}",
                '策略胜率': f"{win_rate:.1%}"
            })
        
        category_comparison_df = pd.DataFrame(category_comparison_data)
        analysis.append(category_comparison_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def _generate_industry_detail_analysis(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成行业明细分析"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 收集所有行业数据
        industry_stats = []
        
        for results in all_results:
            if not results:
                continue
                
            industry_name = results[0].get('industry_name', 'Unknown')
            category = self.get_industry_category(industry_name)
            
            # 计算行业整体表现
            industry_returns = [r['total_return'] for r in results]
            industry_sharpe = [r['sharpe_ratio'] for r in results]
            industry_drawdown = [r['max_drawdown'] for r in results]
            
            avg_return = np.mean(industry_returns)
            avg_sharpe = np.mean(industry_sharpe)
            avg_drawdown = np.mean(industry_drawdown)
            best_strategy = max(results, key=lambda x: x['total_return'])
            worst_strategy = min(results, key=lambda x: x['total_return'])
            
            industry_stats.append({
                'industry': industry_name,
                'category': category,
                'strategy_count': len(results),
                'avg_return': avg_return,
                'avg_sharpe': avg_sharpe,
                'avg_drawdown': avg_drawdown,
                'best_strategy': best_strategy['strategy_name'],
                'best_return': best_strategy['total_return'],
                'worst_strategy': worst_strategy['strategy_name'],
                'worst_return': worst_strategy['total_return']
            })
        
        # 按平均收益率排序
        industry_stats.sort(key=lambda x: x['avg_return'], reverse=True)
        
        # 使用表格展示行业表现排行榜
        analysis.append(f"### 📈 行业表现排行榜\n\n")
        industry_ranking_data = []
        
        for i, stats in enumerate(industry_stats, 1):
            # 计算胜率
            industry_results = [r for results in all_results if results and results[0].get('industry_name') == stats['industry'] for r in results]
            positive_count = len([r for r in industry_results if r['total_return'] > 0])
            win_rate = positive_count / len(industry_results) if industry_results else 0
            
            industry_ranking_data.append({
                '排名': f"#{i}",
                '行业板块': stats['industry'],
                '分类': stats['category'],
                '策略数量': f"{stats['strategy_count']} 个",
                '平均总收益率': f"{stats['avg_return']:.2%}",
                '平均夏普比率': f"{stats['avg_sharpe']:.4f}",
                '平均最大回撤': f"{stats['avg_drawdown']:.2%}",
                '策略胜率': f"{win_rate:.1%}",
                '最佳策略': f"{stats['best_strategy']} ({stats['best_return']:.2%})"
            })
        
        industry_ranking_df = pd.DataFrame(industry_ranking_data)
        analysis.append(industry_ranking_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示Top 10行业详细分析（合并表格）
        analysis.append(f"### 🏆 Top 10 行业详细分析\n\n")
        top_industries = industry_stats[:10]
        
        # 创建合并的表格数据
        top10_combined_data = []
        for i, stats in enumerate(top_industries, 1):
            top10_combined_data.append({
                '排名': f"#{i}",
                '行业板块': stats['industry'],
                '分类': stats['category'],
                '策略数量': f"{stats['strategy_count']} 个",
                '平均总收益率': f"{stats['avg_return']:.2%}",
                '平均夏普比率': f"{stats['avg_sharpe']:.4f}",
                '平均最大回撤': f"{stats['avg_drawdown']:.2%}",
                '最佳策略': f"{stats['best_strategy']} ({stats['best_return']:.2%})",
                '最差策略': f"{stats['worst_strategy']} ({stats['worst_return']:.2%})"
            })
        
        top10_combined_df = pd.DataFrame(top10_combined_data)
        analysis.append(top10_combined_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def _generate_strategy_ranking(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成策略表现排行"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            for result in results:
                all_strategies.append(result)
        
        if not all_strategies:
            return "无策略数据可分析"
        
        # 按总收益率排序
        all_strategies.sort(key=lambda x: x['total_return'], reverse=True)
        
        # 使用表格展示策略表现排行榜（Top 20）
        analysis.append(f"### 🏆 策略表现排行榜（Top 20）\n\n")
        top_strategies = all_strategies[:20]
        
        strategy_ranking_data = []
        for i, strategy in enumerate(top_strategies, 1):
            strategy_ranking_data.append({
                '排名': f"#{i}",
                '策略名称': strategy['strategy_name'],
                '行业板块': strategy['industry_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '年化收益率': f"{strategy['annualized_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        strategy_ranking_df = pd.DataFrame(strategy_ranking_data)
        analysis.append(strategy_ranking_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示策略类型表现统计
        analysis.append(f"### 📊 策略类型表现统计\n\n")
        
        strategy_type_stats = {}
        for strategy in all_strategies:
            strategy_name = strategy['strategy_name']
            if strategy_name not in strategy_type_stats:
                strategy_type_stats[strategy_name] = []
            strategy_type_stats[strategy_name].append(strategy['total_return'])
        
        strategy_type_data = []
        for strategy_type, returns in strategy_type_stats.items():
            avg_return = np.mean(returns)
            max_return = max(returns)
            min_return = min(returns)
            count = len(returns)
            win_rate = len([r for r in returns if r > 0]) / count
            
            strategy_type_data.append({
                '策略类型': strategy_type,
                '实例数量': f"{count} 个",
                '平均收益率': f"{avg_return:.2%}",
                '最佳收益率': f"{max_return:.2%}",
                '最差收益率': f"{min_return:.2%}",
                '胜率': f"{win_rate:.1%}"
            })
        
        # 按平均收益率排序
        strategy_type_data.sort(key=lambda x: float(x['平均收益率'].replace('%', '')), reverse=True)
        
        strategy_type_df = pd.DataFrame(strategy_type_data)
        analysis.append(strategy_type_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def _generate_risk_return_analysis(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成风险收益分析"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            all_strategies.extend(results)
        
        if not all_strategies:
            return "无策略数据可分析"
        
        # 计算风险收益指标
        returns = [s['total_return'] for s in all_strategies]
        volatilities = [s['volatility'] for s in all_strategies]
        sharpe_ratios = [s['sharpe_ratio'] for s in all_strategies]
        max_drawdowns = [s['max_drawdown'] for s in all_strategies]
        
        # 使用表格展示收益率分布
        analysis.append(f"### 📊 收益率分布\n\n")
        returns_distribution_data = [
            {
                '指标': '收益率范围',
                '数值': f"{min(returns):.2%} ~ {max(returns):.2%}",
                '说明': '策略收益率的最小值和最大值'
            },
            {
                '指标': '收益率标准差',
                '数值': f"{np.std(returns):.2%}",
                '说明': '收益率离散程度'
            },
            {
                '指标': '收益率偏度',
                '数值': f"{self._calculate_skewness(returns):.4f}",
                '说明': '收益率分布的不对称性'
            },
            {
                '指标': '收益率峰度',
                '数值': f"{self._calculate_kurtosis(returns):.4f}",
                '说明': '收益率分布的尖锐程度'
            }
        ]
        
        returns_distribution_df = pd.DataFrame(returns_distribution_data)
        analysis.append(returns_distribution_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示风险分布
        analysis.append(f"### ⚠️ 风险分布\n\n")
        risk_distribution_data = [
            {
                '风险指标': '波动率',
                '范围': f"{min(volatilities):.2%} ~ {max(volatilities):.2%}",
                '平均值': f"{np.mean(volatilities):.2%}",
                '风险等级': '中等'
            },
            {
                '风险指标': '最大回撤',
                '范围': f"{min(max_drawdowns):.2%} ~ {max(max_drawdowns):.2%}",
                '平均值': f"{np.mean(max_drawdowns):.2%}",
                '风险等级': '中等'
            },
            {
                '风险指标': '夏普比率',
                '范围': f"{min(sharpe_ratios):.4f} ~ {max(sharpe_ratios):.4f}",
                '平均值': f"{np.mean(sharpe_ratios):.4f}",
                '风险等级': '中等'
            }
        ]
        
        risk_distribution_df = pd.DataFrame(risk_distribution_data)
        analysis.append(risk_distribution_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示风险收益象限分析
        analysis.append(f"### 🎯 风险收益象限分析\n\n")
        high_return_high_risk = len([s for s in all_strategies if s['total_return'] > np.mean(returns) and s['volatility'] > np.mean(volatilities)])
        high_return_low_risk = len([s for s in all_strategies if s['total_return'] > np.mean(returns) and s['volatility'] <= np.mean(volatilities)])
        low_return_high_risk = len([s for s in all_strategies if s['total_return'] <= np.mean(returns) and s['volatility'] > np.mean(volatilities)])
        low_return_low_risk = len([s for s in all_strategies if s['total_return'] <= np.mean(returns) and s['volatility'] <= np.mean(volatilities)])
        
        # 收集各象限的具体策略明细
        high_return_high_risk_strategies = [s for s in all_strategies if s['total_return'] > np.mean(returns) and s['volatility'] > np.mean(volatilities)]
        high_return_low_risk_strategies = [s for s in all_strategies if s['total_return'] > np.mean(returns) and s['volatility'] <= np.mean(volatilities)]
        low_return_high_risk_strategies = [s for s in all_strategies if s['total_return'] <= np.mean(returns) and s['volatility'] > np.mean(volatilities)]
        low_return_low_risk_strategies = [s for s in all_strategies if s['total_return'] <= np.mean(returns) and s['volatility'] <= np.mean(volatilities)]
        
        def format_strategy_details(strategies):
            if not strategies:
                return "无"
            details = []
            for s in strategies[:3]:  # 只显示前3个
                details.append(f"{s['industry_name']}-{s['strategy_name']}({s['total_return']:.1%})")
            if len(strategies) > 3:
                details.append(f"...等{len(strategies)}个")
            return ", ".join(details)
        
        quadrant_data = [
            {
                '象限': '高收益高风险',
                '策略数量': f"{high_return_high_risk} 个",
                '占比': f"{high_return_high_risk/len(all_strategies):.1%}",
                '特征': '收益和风险都较高',
                '建议': '适合风险偏好较高的投资者',
                '明细': format_strategy_details(high_return_high_risk_strategies)
            },
            {
                '象限': '高收益低风险',
                '策略数量': f"{high_return_low_risk} 个",
                '占比': f"{high_return_low_risk/len(all_strategies):.1%}",
                '特征': '理想投资组合',
                '建议': '优先推荐',
                '明细': format_strategy_details(high_return_low_risk_strategies)
            },
            {
                '象限': '低收益高风险',
                '策略数量': f"{low_return_high_risk} 个",
                '占比': f"{low_return_high_risk/len(all_strategies):.1%}",
                '特征': '收益低但风险高',
                '建议': '不推荐',
                '明细': format_strategy_details(low_return_high_risk_strategies)
            },
            {
                '象限': '低收益低风险',
                '策略数量': f"{low_return_low_risk} 个",
                '占比': f"{low_return_low_risk/len(all_strategies):.1%}",
                '特征': '保守型投资',
                '建议': '适合风险厌恶型投资者',
                '明细': format_strategy_details(low_return_low_risk_strategies)
            }
        ]
        
        quadrant_df = pd.DataFrame(quadrant_data)
        analysis.append(quadrant_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    
    def _generate_anomaly_summary(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成异动检测汇总"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        all_anomalies = []
        
        # 收集所有异动
        for results in all_results:
            if results:
                anomalies = self._detect_anomalies(results)
                all_anomalies.extend(anomalies)
        
        analysis.append(f"### 异动检测汇总\n\n")
        
        if not all_anomalies:
            analysis.append("✅ 未检测到明显异动情况\n\n")
        else:
            analysis.append(f"🚨 共检测到 {len(all_anomalies)} 个异动情况：\n\n")
            
            # 按类型分类异动
            sector_anomalies = [a for a in all_anomalies if '板块异动' in a]
            strategy_anomalies = [a for a in all_anomalies if '策略异动' in a]
            
            if sector_anomalies:
                analysis.append(f"#### 板块异动 ({len(sector_anomalies)}个)\n")
                for anomaly in sector_anomalies:
                    analysis.append(f"- {anomaly.strip()}\n")
                analysis.append("\n")
            
            if strategy_anomalies:
                analysis.append(f"#### 策略异动 ({len(strategy_anomalies)}个)\n")
                for anomaly in strategy_anomalies:
                    analysis.append(f"- {anomaly.strip()}\n")
                analysis.append("\n")
        
        return "".join(analysis)
    
    def _generate_investment_recommendations(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """生成投资建议"""
        if not all_results:
            return "无数据可分析"
        
        analysis = []
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            all_strategies.extend(results)
        
        if not all_strategies:
            return "无策略数据可分析"
        
        # 找出表现最好的策略
        best_strategies = sorted(all_strategies, key=lambda x: x['total_return'], reverse=True)[:5]
        
        # 按行业分类找出最佳策略
        industry_best = {}
        for strategy in all_strategies:
            industry = strategy['industry_name']
            if industry not in industry_best or strategy['total_return'] > industry_best[industry]['total_return']:
                industry_best[industry] = strategy
        
        analysis.append(f"### 💡 投资建议\n\n")
        
        # 使用表格展示推荐策略（Top 5）
        analysis.append(f"#### 🏆 推荐策略（Top 5）\n\n")
        top5_data = []
        for i, strategy in enumerate(best_strategies, 1):
            top5_data.append({
                '排名': f"#{i}",
                '策略名称': strategy['strategy_name'],
                '行业板块': strategy['industry_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        top5_df = pd.DataFrame(top5_data)
        analysis.append(top5_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示各行业推荐策略
        analysis.append(f"#### 🏢 各行业推荐策略\n\n")
        industry_recommendations_data = []
        for industry, strategy in industry_best.items():
            industry_recommendations_data.append({
                '行业板块': industry,
                '推荐策略': strategy['strategy_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        industry_recommendations_df = pd.DataFrame(industry_recommendations_data)
        analysis.append(industry_recommendations_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def _calculate_skewness(self, data: List[float]) -> float:
        """计算偏度"""
        if len(data) < 3:
            return 0.0
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0.0
        return np.mean([(x - mean_val) ** 3 for x in data]) / (std_val ** 3)
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """计算峰度"""
        if len(data) < 4:
            return 0.0
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0.0
        return np.mean([(x - mean_val) ** 4 for x in data]) / (std_val ** 4) - 3
    
