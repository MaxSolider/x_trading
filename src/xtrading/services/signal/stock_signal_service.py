"""
个股信号计算服务
为多个股票计算不同策略的买卖信号
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...strategies.individual_stock.trend_tracking_strategy import IndividualTrendTrackingStrategy
from ...strategies.individual_stock.breakout_strategy import IndividualBreakoutStrategy
from ...strategies.individual_stock.oversold_rebound_strategy import IndividualOversoldReboundStrategy
from ...repositories.stock.stock_query import StockQuery
from ...static.stock_strategy_params import StockStrategyParams
from ...utils.docs.signal_report_generator import SignalReportGenerator


class StockSignalService:
    """个股信号计算服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.stock_query = StockQuery()
        self.trend_strategy = IndividualTrendTrackingStrategy()
        self.breakout_strategy = IndividualBreakoutStrategy()
        self.oversold_strategy = IndividualOversoldReboundStrategy()
        
        # 支持的策略列表
        self.supported_strategies = ["TrendTracking", "Breakout", "OversoldRebound"]
        self.report_generator = SignalReportGenerator()

    def calculate_stock_signals(self, stock_list: List[str], 
                               strategies: List[str] = None,
                               start_date: str = None, 
                               end_date: str = None) -> Dict[str, Any]:
        """
        计算多个股票在不同策略下的买卖信号
        
        Args:
            stock_list: 股票代码列表
            strategies: 策略名称列表，默认为所有支持的策略
            start_date: 开始日期 (YYYYMMDD格式)，默认为最近三个月
            end_date: 结束日期 (YYYYMMDD格式)，默认为今天
            
        Returns:
            Dict: 包含每个股票各策略信号的结果字典
        """
        if not stock_list:
            print("❌ 股票列表不能为空")
            return {}
        
        # 使用默认策略列表
        if strategies is None:
            strategies = self.supported_strategies.copy()
        
        # 验证策略是否支持
        invalid_strategies = [s for s in strategies if s not in self.supported_strategies]
        if invalid_strategies:
            print(f"❌ 不支持的策略: {invalid_strategies}")
            return {}
        
        # 使用默认日期范围（最近三个月）
        if start_date is None or end_date is None:
            default_start, default_end = StockStrategyParams.get_default_date_range()
            start_date = start_date or default_start
            end_date = end_date or default_end

        results = {
            'calculation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': len(stock_list),
            'strategies_used': strategies,
            'date_range': {'start_date': start_date, 'end_date': end_date},
            'stock_signals': {}
        }
        
        # 为每个股票计算信号
        for stock_code in stock_list:
            stock_result = {
                'stock_code': stock_code,
                'strategies': {}
            }
            
            # 获取股票历史数据
            hist_data = self._get_historical_data(stock_code, start_date, end_date)
            if hist_data is None:
                print(f"❌ 无法获取 {stock_code} 的历史数据，跳过该股票")
                stock_result['error'] = "无法获取历史数据"
                results['stock_signals'][stock_code] = stock_result
                continue
            
            # 为每个策略计算信号
            for strategy in strategies:
                try:
                    signal_data = self._calculate_strategy_signal(
                        hist_data, strategy
                    )
                    
                    if signal_data is not None:
                        # 提取最新信号信息
                        latest_signal = self._extract_latest_signal(signal_data, strategy)
                        stock_result['strategies'][strategy] = latest_signal
                    else:
                        stock_result['strategies'][strategy] = {
                            'error': f"无法计算 {strategy} 策略信号"
                        }
                        
                except Exception as e:
                    print(f"❌ 计算 {stock_code} 的 {strategy} 策略信号失败: {e}")
                    stock_result['strategies'][strategy] = {
                        'error': f"计算失败: {str(e)}"
                    }
            
            results['stock_signals'][stock_code] = stock_result
        
        return results

    def print_signal_summary(self, results: Dict[str, Any]) -> Optional[str]:
        """
        生成并输出股票信号总结报告
        
        Args:
            results: 计算得到的信号原始结果（calculate_stock_signals返回值）

        Returns:
            Optional[str]: 生成的报告文件路径
        """
        if not results:
            print("❌ 无结果数据可生成报告")
            return None
        
        # 1) 元信息
        meta = {
            'calculation_time': results.get('calculation_time'),
            'total_stocks': results.get('total_stocks', 0),
            'strategies_used': results.get('strategies_used', []),
            'date_range': results.get('date_range', {})
        }
        
        strategies_used = meta['strategies_used']
        stock_signals = results.get('stock_signals', {})
        
        # 2) 整体汇总统计
        total_signals = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
        successful_stocks = 0
        failed_stocks = 0
        
        # 策略信号分布统计
        strategy_signal_counts = {s: {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0} for s in strategies_used}
        
        def translate(signal_type: str) -> str:
            mapping = {
                'BUY': '买入',
                'SELL': '卖出',
                'HOLD': '持有',
                'STRONG_BUY': '强势买入',
                'STRONG_SELL': '强势卖出',
                'ERROR': '错误'
            }
            return mapping.get(signal_type, signal_type)
        
        for stock_code, stock_data in stock_signals.items():
            if 'error' in stock_data:
                failed_stocks += 1
                continue
            successful_stocks += 1
            strategies = stock_data.get('strategies', {})
            for strategy in strategies_used:
                if strategy in strategies:
                    sd = strategies[strategy]
                    if 'error' in sd:
                        total_signals['错误'] += 1
                        strategy_signal_counts[strategy]['错误'] += 1
                    else:
                        t = translate(sd.get('signal_type', 'HOLD'))
                        total_signals[t] += 1
                        strategy_signal_counts[strategy][t] += 1
        
        overall_summary = {
            'successful_stocks': successful_stocks,
            'failed_stocks': failed_stocks,
            'total_signals': total_signals
        }
        
        # 3) 股票明细表数据
        stock_rows = []
        for stock_code, stock_data in stock_signals.items():
            if 'error' in stock_data:
                # 标记错误行
                stock_rows.append({
                    'stock_code': stock_code,
                    'signals': {s: '❌ 错误' for s in strategies_used},
                    'total_buy_sell_signals': 0
                })
                continue
            
            row_signals = {}
            total_buy_sell_signals = 0
            strategies = stock_data.get('strategies', {})
            for strategy in strategies_used:
                if strategy in strategies:
                    sd = strategies[strategy]
                    if 'error' in sd:
                        row_signals[strategy] = '❌ 错误'
                    else:
                        st = sd.get('signal_type', 'HOLD')
                        if st == 'HOLD':
                            row_signals[strategy] = '-'
                        else:
                            translated_signal = translate(st)
                            row_signals[strategy] = translated_signal
                            # 统计买入卖出信号数量
                            if translated_signal in ['买入', '卖出']:
                                total_buy_sell_signals += 1
                else:
                    row_signals[strategy] = '-'
            stock_rows.append({
                'stock_code': stock_code,
                'signals': row_signals,
                'total_buy_sell_signals': total_buy_sell_signals
            })
        
        # 按买入卖出信号总量降序排序
        stock_rows.sort(key=lambda x: x['total_buy_sell_signals'], reverse=True)
        
        stock_details = {
            'strategies_used': strategies_used,
            'rows': stock_rows
        }
        
        # 4) 策略分析数据
        strategy_analysis = {}
        for strategy in strategies_used:
            strategy_analysis[strategy] = {
                'buy_signals': 0,
                'sell_signals': 0,
                'strong_buy_signals': 0,
                'strong_sell_signals': 0,
                'hold_signals': 0,
                'error_signals': 0,
                'stocks_with_signals': []
            }
        
        for stock_code, stock_data in stock_signals.items():
            if 'error' in stock_data:
                continue
            strategies = stock_data.get('strategies', {})
            for strategy in strategies_used:
                if strategy in strategies:
                    sd = strategies[strategy]
                    if 'error' in sd:
                        strategy_analysis[strategy]['error_signals'] += 1
                    else:
                        st = sd.get('signal_type', 'HOLD')
                        if st == 'BUY':
                            strategy_analysis[strategy]['buy_signals'] += 1
                            strategy_analysis[strategy]['stocks_with_signals'].append(stock_code)
                        elif st == 'SELL':
                            strategy_analysis[strategy]['sell_signals'] += 1
                            strategy_analysis[strategy]['stocks_with_signals'].append(stock_code)
                        elif st == 'STRONG_BUY':
                            strategy_analysis[strategy]['strong_buy_signals'] += 1
                            strategy_analysis[strategy]['stocks_with_signals'].append(stock_code)
                        elif st == 'STRONG_SELL':
                            strategy_analysis[strategy]['strong_sell_signals'] += 1
                            strategy_analysis[strategy]['stocks_with_signals'].append(stock_code)
                        else:
                            strategy_analysis[strategy]['hold_signals'] += 1
        
        # 5) 汇总为sections传给生成器
        sections = {
            'meta': meta,
            'overall_summary': overall_summary,
            'strategy_distribution': {
                'strategies_used': strategies_used,
                'strategy_signal_counts': strategy_signal_counts
            },
            'strategy_analysis': strategy_analysis,
            'stock_details': stock_details
        }
        
        return self._generate_stock_report(sections)
    
    def _get_historical_data(self, stock_code: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 历史数据
        """
        try:
            hist_data = self.stock_query.get_historical_quotes(stock_code, start_date, end_date)
            if hist_data is None or hist_data.empty:
                return None
            return hist_data
        except Exception as e:
            print(f"❌ 获取 {stock_code} 历史数据失败: {e}")
            return None
    
    def _calculate_strategy_signal(self, data: pd.DataFrame, strategy_name: str) -> Optional[pd.DataFrame]:
        """
        计算单个策略的交易信号
        
        Args:
            data: 历史数据
            strategy_name: 策略名称
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        try:
            # 获取策略参数
            strategy_params = StockStrategyParams.get_strategy_params(strategy_name)
            
            if strategy_name == "TrendTracking":
                # 提取移动平均线参数
                ma_params = {
                    'short_period': strategy_params.get('short_period', 5),
                    'medium_period': strategy_params.get('medium_period', 20),
                    'long_period': strategy_params.get('long_period', 60)
                }
                
                # 提取MACD参数
                macd_params = {
                    'fast_period': strategy_params.get('fast_period', 12),
                    'slow_period': strategy_params.get('slow_period', 26),
                    'signal_period': strategy_params.get('signal_period', 9)
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
                    'period': strategy_params.get('period', 20),
                    'std_dev': strategy_params.get('std_dev', 2.0)
                }
                
                # 提取量比参数
                volume_params = {
                    'period': strategy_params.get('volume_period', 5)
                }
                
                # 提取阻力位参数
                resistance_params = {
                    'lookback_period': strategy_params.get('resistance_lookback_period', 60)
                }
                
                # 提取突破信号参数
                signal_params = {
                    'volume_threshold': strategy_params.get('volume_threshold', 1.2)
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
                    'k_period': strategy_params.get('k_period', 9),
                    'd_period': strategy_params.get('d_period', 3),
                    'j_period': strategy_params.get('j_period', 3)
                }
                
                # 提取RSI参数
                rsi_params = {
                    'period': strategy_params.get('rsi_period', 14)
                }
                
                # 提取价格跌幅参数
                decline_params = {
                    'period': strategy_params.get('decline_period', 20)
                }
                
                # 提取超卖信号参数
                signal_params = {
                    'kdj_oversold': strategy_params.get('kdj_oversold', 20),
                    'rsi_oversold': strategy_params.get('rsi_oversold', 30),
                    'decline_threshold': strategy_params.get('decline_threshold', 15)
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
    
    def _extract_latest_signal(self, signal_data: pd.DataFrame, strategy_name: str) -> Dict[str, Any]:
        """
        从信号数据中提取最新信号信息
        
        Args:
            signal_data: 包含信号的DataFrame
            strategy_name: 策略名称
            
        Returns:
            Dict: 最新信号信息
        """
        if signal_data is None or signal_data.empty:
            return {'error': '无信号数据'}
        
        # 获取最新数据
        latest_data = signal_data.iloc[-1]
        
        # 基础信号信息
        signal_info = {
            'signal_value': int(latest_data.get('Signal', 0)),
            'signal_type': latest_data.get('Signal_Type', 'HOLD'),
            'analysis_date': latest_data.get('日期', 'Unknown'),
            'data_points': len(signal_data)
        }
        
        # 根据策略添加特定指标
        if strategy_name == "TrendTracking":
            signal_info.update({
                'close_price': self._get_close_price(latest_data),
                'sma_5': float(latest_data.get('SMA_5', 0)),
                'sma_20': float(latest_data.get('SMA_20', 0)),
                'sma_60': float(latest_data.get('SMA_60', 0)),
                'dif': float(latest_data.get('DIF', 0)),
                'dea': float(latest_data.get('DEA', 0)),
                'macd': float(latest_data.get('MACD', 0)),
                'trend_status': latest_data.get('Trend_Status', 'SIDEWAYS'),
                'macd_status': latest_data.get('MACD_Status', 'NEUTRAL'),
                'trend_strength': self._calculate_trend_strength(signal_data)
            })
            
        elif strategy_name == "Breakout":
            signal_info.update({
                'close_price': self._get_close_price(latest_data),
                'upper_band': float(latest_data.get('Upper_Band', 0)),
                'lower_band': float(latest_data.get('Lower_Band', 0)),
                'resistance_20': float(latest_data.get('Resistance_20', 0)),
                'resistance_60': float(latest_data.get('Resistance_60', 0)),
                'year_line': float(latest_data.get('Year_Line', 0)),
                'volume_ratio': float(latest_data.get('Volume_Ratio', 0)),
                'breakout_type': latest_data.get('Breakout_Type', 'NONE'),
                'volume_status': latest_data.get('Volume_Status', 'NORMAL'),
                'breakout_strength': self._calculate_breakout_strength(signal_data)
            })
            
        elif strategy_name == "OversoldRebound":
            signal_info.update({
                'close_price': self._get_close_price(latest_data),
                'k_value': float(latest_data.get('K', 0)),
                'd_value': float(latest_data.get('D', 0)),
                'j_value': float(latest_data.get('J', 0)),
                'rsi_value': float(latest_data.get('RSI', 0)),
                'decline_20': float(latest_data.get('Decline_20', 0)),
                'oversold_type': latest_data.get('Oversold_Type', 'NONE'),
                'kdj_status': latest_data.get('KDJ_Status', 'NORMAL'),
                'rsi_status': latest_data.get('RSI_Status', 'NORMAL'),
                'decline_status': latest_data.get('Decline_Status', 'NORMAL'),
                'oversold_strength': self._calculate_oversold_strength(signal_data)
            })
        
        return signal_info
    
    def _get_close_price(self, latest_data: pd.Series) -> Optional[float]:
        """获取收盘价"""
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in latest_data.index:
                return float(latest_data[col])
        return None
    
    def _calculate_trend_strength(self, signal_data: pd.DataFrame) -> float:
        """计算趋势强度"""
        try:
            if signal_data is None or signal_data.empty:
                return 0.0
            
            # 计算均线斜率
            sma_5_slope = signal_data['SMA_5'].pct_change().rolling(5).mean().iloc[-1]
            sma_20_slope = signal_data['SMA_20'].pct_change().rolling(5).mean().iloc[-1]
            
            # 计算MACD强度
            macd_strength = abs(signal_data['MACD'].iloc[-1]) / signal_data['MACD'].rolling(20).std().iloc[-1] if signal_data['MACD'].rolling(20).std().iloc[-1] != 0 else 0
            
            # 综合趋势强度
            trend_strength = (abs(sma_5_slope) + abs(sma_20_slope) + macd_strength) / 3
            
            return min(trend_strength, 1.0)  # 限制在0-1之间
        except:
            return 0.0
    
    def _calculate_breakout_strength(self, signal_data: pd.DataFrame) -> float:
        """计算突破强度"""
        try:
            if signal_data is None or signal_data.empty:
                return 0.0
            
            # 计算价格突破幅度
            close_price = signal_data['收盘'].iloc[-1]
            upper_band = signal_data['Upper_Band'].iloc[-1]
            resistance_60 = signal_data['Resistance_60'].iloc[-1]
            
            # 布林带突破幅度
            bb_breakout_ratio = (close_price - upper_band) / upper_band if upper_band != 0 else 0
            
            # 阻力位突破幅度
            resistance_breakout_ratio = (close_price - resistance_60) / resistance_60 if resistance_60 != 0 else 0
            
            # 量比强度
            volume_strength = min(signal_data['Volume_Ratio'].iloc[-1] / 2.0, 1.0)  # 量比2倍为满分
            
            # 综合突破强度
            breakout_strength = (abs(bb_breakout_ratio) + abs(resistance_breakout_ratio) + volume_strength) / 3
            
            return min(breakout_strength, 1.0)  # 限制在0-1之间
        except:
            return 0.0
    
    def _calculate_oversold_strength(self, signal_data: pd.DataFrame) -> float:
        """计算超跌强度"""
        try:
            if signal_data is None or signal_data.empty:
                return 0.0
            
            # 计算KDJ超卖程度
            kdj_oversold_ratio = (20 - signal_data['K'].iloc[-1]) / 20 if signal_data['K'].iloc[-1] < 20 else 0
            
            # 计算RSI超卖程度
            rsi_oversold_ratio = (30 - signal_data['RSI'].iloc[-1]) / 30 if signal_data['RSI'].iloc[-1] < 30 else 0
            
            # 计算价格超跌程度
            price_oversold_ratio = min(signal_data['Decline_20'].iloc[-1] / 30, 1.0)  # 30%跌幅为满分
            
            # 综合超跌强度
            oversold_strength = (kdj_oversold_ratio + rsi_oversold_ratio + price_oversold_ratio) / 3
            
            return min(oversold_strength, 1.0)  # 限制在0-1之间
        except:
            return 0.0
    
    def _generate_stock_report(self, sections: Dict[str, Any]) -> Optional[str]:
        """
        生成股票信号报告
        
        Args:
            sections: 预先聚合好的各报告部分数据
            
        Returns:
            Optional[str]: 生成的报告文件路径
        """
        try:
            # 生成文件名
            now = datetime.now()
            date_str = now.strftime('%Y%m%d')
            time_str = now.strftime('%H%M%S')
            output_file = f"reports/sector_signals/股票信号报告_{date_str}_{time_str}.md"
            
            # 确保目录存在
            import os
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 生成报告内容
            content = []
            content.append("# 股票信号综合分析报告")
            content.append("")
            content.append("> 本报告包含股票信号分析报告和汇总报告两部分内容")
            content.append("")
            
            # 基本信息
            meta = sections.get('meta', {})
            content.append("## 📊 基本信息")
            content.append("")
            content.append(f"- **计算时间**: {meta.get('calculation_time', 'Unknown')}")
            content.append(f"- **分析股票数量**: {meta.get('total_stocks', 0)}")
            content.append(f"- **使用策略**: {', '.join(meta.get('strategies_used', []))}")
            content.append(f"- **分析期间**: {meta.get('date_range', {}).get('start_date', 'Unknown')} - {meta.get('date_range', {}).get('end_date', 'Unknown')}")
            content.append("")
            
            # 整体汇总
            overall_summary = sections.get('overall_summary', {})
            content.append("## 📈 整体汇总")
            content.append("")
            content.append(f"- **成功分析股票**: {overall_summary.get('successful_stocks', 0)}")
            content.append(f"- **失败股票**: {overall_summary.get('failed_stocks', 0)}")
            content.append("")
            
            total_signals = overall_summary.get('total_signals', {})
            content.append("### 信号统计")
            content.append("")
            content.append("| 信号类型 | 数量 |")
            content.append("|---------|------|")
            for signal_type, count in total_signals.items():
                content.append(f"| {signal_type} | {count} |")
            content.append("")
            
            # 策略分布
            strategy_distribution = sections.get('strategy_distribution', {})
            content.append("## 🎯 策略信号分布")
            content.append("")
            strategies_used = strategy_distribution.get('strategies_used', [])
            strategy_signal_counts = strategy_distribution.get('strategy_signal_counts', {})
            
            content.append("| 策略 | 买入 | 卖出 | 持有 | 强势买入 | 强势卖出 | 错误 |")
            content.append("|------|------|------|------|----------|----------|------|")
            for strategy in strategies_used:
                counts = strategy_signal_counts.get(strategy, {})
                content.append(f"| {strategy} | {counts.get('买入', 0)} | {counts.get('卖出', 0)} | {counts.get('持有', 0)} | {counts.get('强势买入', 0)} | {counts.get('强势卖出', 0)} | {counts.get('错误', 0)} |")
            content.append("")
            
            # 股票明细
            stock_details = sections.get('stock_details', {})
            content.append("## 📋 股票明细")
            content.append("")
            
            rows = stock_details.get('rows', [])
            if rows:
                # 表头
                header = "| 股票代码 |"
                for strategy in strategies_used:
                    header += f" {strategy} |"
                header += " 信号总数 |"
                content.append(header)
                
                # 分隔线
                separator = "|" + "|".join(["------"] * (len(strategies_used) + 2))
                content.append(separator)
                
                # 数据行
                for row in rows[:20]:  # 只显示前20个
                    stock_code = row['stock_code']
                    signals = row['signals']
                    total_signals = row['total_buy_sell_signals']
                    
                    data_row = f"| {stock_code} |"
                    for strategy in strategies_used:
                        signal = signals.get(strategy, '-')
                        data_row += f" {signal} |"
                    data_row += f" {total_signals} |"
                    content.append(data_row)
                
                if len(rows) > 20:
                    content.append(f"\n*注：仅显示前20个股票，共{len(rows)}个股票*")
            
            content.append("")
            
            # 策略分析
            strategy_analysis = sections.get('strategy_analysis', {})
            content.append("## 🔍 策略分析")
            content.append("")
            
            for strategy, analysis in strategy_analysis.items():
                content.append(f"### {strategy} 策略")
                content.append("")
                content.append(f"- **买入信号**: {analysis.get('buy_signals', 0)}")
                content.append(f"- **卖出信号**: {analysis.get('sell_signals', 0)}")
                content.append(f"- **强势买入**: {analysis.get('strong_buy_signals', 0)}")
                content.append(f"- **强势卖出**: {analysis.get('strong_sell_signals', 0)}")
                content.append(f"- **持有信号**: {analysis.get('hold_signals', 0)}")
                content.append(f"- **错误信号**: {analysis.get('error_signals', 0)}")
                
                stocks_with_signals = analysis.get('stocks_with_signals', [])
                if stocks_with_signals:
                    content.append(f"- **有信号的股票**: {', '.join(stocks_with_signals[:10])}")
                    if len(stocks_with_signals) > 10:
                        content.append(f"  *等{len(stocks_with_signals)}个股票*")
                content.append("")
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            print(f"✅ 股票信号报告已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 生成股票信号报告失败: {e}")
            return None
