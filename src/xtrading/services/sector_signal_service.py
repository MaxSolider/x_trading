"""
板块信号计算服务
为多个板块计算不同策略的买卖信号
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..strategies.industry_sector.macd_strategy import IndustryMACDStrategy
from ..strategies.industry_sector.rsi_strategy import IndustryRSIStrategy
from ..strategies.industry_sector.bollinger_bands_strategy import IndustryBollingerBandsStrategy
from ..strategies.industry_sector.moving_average_strategy import IndustryMovingAverageStrategy
from ..repositories.stock.industry_info_query import IndustryInfoQuery
from ..static.industry_sectors import get_industry_category
from ..static.strategy_config import StrategyConfig
from ..utils.docs.signal_report_generator import SignalReportGenerator


class SectorSignalService:
    """板块信号计算服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.industry_query = IndustryInfoQuery()
        self.macd_strategy = IndustryMACDStrategy()
        self.rsi_strategy = IndustryRSIStrategy()
        self.bb_strategy = IndustryBollingerBandsStrategy()
        self.ma_strategy = IndustryMovingAverageStrategy()
        
        # 支持的策略列表
        self.supported_strategies = ["MACD", "RSI", "BollingerBands", "MovingAverage"]
        self.report_generator = SignalReportGenerator()

    def calculate_sector_signals(self, sector_list: List[str], 
                               strategies: List[str] = None,
                               start_date: str = None, 
                               end_date: str = None) -> Dict[str, Any]:
        """
        计算多个板块在不同策略下的买卖信号
        
        Args:
            sector_list: 板块名称列表
            strategies: 策略名称列表，默认为所有支持的策略
            start_date: 开始日期 (YYYYMMDD格式)，默认为最近三个月
            end_date: 结束日期 (YYYYMMDD格式)，默认为今天
            
        Returns:
            Dict: 包含每个板块各策略信号的结果字典
        """
        if not sector_list:
            print("❌ 板块列表不能为空")
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
            default_start, default_end = StrategyConfig.get_default_date_range()
            start_date = start_date or default_start
            end_date = end_date or default_end

        results = {
            'calculation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_sectors': len(sector_list),
            'strategies_used': strategies,
            'date_range': {'start_date': start_date, 'end_date': end_date},
            'sector_signals': {}
        }
        
        # 为每个板块计算信号
        for sector in sector_list:

            sector_result = {
                'sector_name': sector,
                'category': get_industry_category(sector),
                'strategies': {}
            }
            
            # 获取板块历史数据
            hist_data = self._get_historical_data(sector, start_date, end_date)
            if hist_data is None:
                print(f"❌ 无法获取 {sector} 的历史数据，跳过该板块")
                sector_result['error'] = "无法获取历史数据"
                results['sector_signals'][sector] = sector_result
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
                        sector_result['strategies'][strategy] = latest_signal
                    else:
                        sector_result['strategies'][strategy] = {
                            'error': f"无法计算 {strategy} 策略信号"
                        }
                        
                except Exception as e:
                    print(f"❌ 计算 {sector} 的 {strategy} 策略信号失败: {e}")
                    sector_result['strategies'][strategy] = {
                        'error': f"计算失败: {str(e)}"
                    }
            
            results['sector_signals'][sector] = sector_result
        
        return results

    def print_signal_summary(self, results: Dict[str, Any]) -> Optional[str]:
        """
        生成并输出板块信号总结报告（服务层完成统计聚合，生成器仅负责文档拼接）
        
        Args:
            results: 计算得到的信号原始结果（calculate_sector_signals返回值）

        Returns:
            Optional[str]: 生成的报告文件路径
        """
        if not results:
            print("❌ 无结果数据可生成报告")
            return None
        
        # 1) 元信息
        meta = {
            'calculation_time': results.get('calculation_time'),
            'total_sectors': results.get('total_sectors', 0),
            'strategies_used': results.get('strategies_used', []),
            'date_range': results.get('date_range', {})
        }
        
        strategies_used = meta['strategies_used']
        sector_signals = results.get('sector_signals', {})
        
        # 2) 整体汇总统计
        total_signals = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
        successful_sectors = 0
        failed_sectors = 0
        
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
        
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                failed_sectors += 1
                continue
            successful_sectors += 1
            strategies = sector_data.get('strategies', {})
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
            'successful_sectors': successful_sectors,
            'failed_sectors': failed_sectors,
            'total_signals': total_signals
        }
        
        # 3) 板块明细表数据
        sector_rows = []
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                # 标记错误行
                sector_rows.append({
                    'sector_name': sector_name,
                    'category': '错误',
                    'signals': {s: '❌ 错误' for s in strategies_used},
                    'total_buy_sell_signals': 0
                })
                continue
            category = sector_data.get('category', 'Unknown')
            row_signals = {}
            total_buy_sell_signals = 0
            strategies = sector_data.get('strategies', {})
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
            sector_rows.append({
                'sector_name': sector_name,
                'category': category,
                'signals': row_signals,
                'total_buy_sell_signals': total_buy_sell_signals
            })
        
        # 按买入卖出信号总量降序排序
        sector_rows.sort(key=lambda x: x['total_buy_sell_signals'], reverse=True)
        
        sector_details = {
            'strategies_used': strategies_used,
            'rows': sector_rows
        }
        
        # 4) 分类分析数据
        categories = {}
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                continue
            category = sector_data.get('category', 'Unknown')
            if category not in categories:
                categories[category] = {
                    'sectors': [],
                    'strategy_signals': {s: {'买入': 0, '卖出': 0} for s in strategies_used}
                }
            categories[category]['sectors'].append(sector_name)
            strategies = sector_data.get('strategies', {})
            for strategy in strategies_used:
                if strategy in strategies:
                    sd = strategies[strategy]
                    if 'error' in sd:
                        continue
                    t = translate(sd.get('signal_type', 'HOLD'))
                    if t in ['买入', '卖出']:
                        categories[category]['strategy_signals'][strategy][t] += 1
        
        # 计算每个分类的买入卖出信号总量，用于排序
        for category, stats in categories.items():
            total_buy_sell_signals = 0
            for strategy in strategies_used:
                total_buy_sell_signals += stats['strategy_signals'][strategy]['买入'] + stats['strategy_signals'][strategy]['卖出']
            stats['total_buy_sell_signals'] = total_buy_sell_signals
        
        category_analysis = {
            'strategies_used': strategies_used,
            'categories': categories
        }
        
        # 5) 附录数据
        category_sectors = {}
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                continue
            category = sector_data.get('category', 'Unknown')
            category_sectors.setdefault(category, []).append(sector_name)
        appendix = {'category_sectors': category_sectors}
        
        # 6) 汇总为sections传给生成器
        sections = {
            'meta': meta,
            'overall_summary': overall_summary,
            'strategy_distribution': {
                'strategies_used': strategies_used,
                'strategy_signal_counts': strategy_signal_counts
            },
            'category_analysis': category_analysis,
            'sector_details': sector_details,
            'appendix': appendix
        }
        
        return self.report_generator.generate_precomputed_report(sections)
    
    def _get_historical_data(self, sector_name: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取板块历史数据
        
        Args:
            sector_name: 板块名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 历史数据
        """
        try:
            hist_data = self.industry_query.get_board_industry_hist(sector_name, start_date, end_date)
            if hist_data is None or hist_data.empty:
                return None
            return hist_data
        except Exception as e:
            print(f"❌ 获取 {sector_name} 历史数据失败: {e}")
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
            strategy_params = StrategyConfig.get_strategy_params(strategy_name)
            
            if strategy_name == "MACD":
                # 计算MACD指标
                macd_data = self.macd_strategy.calculate_macd(data, **strategy_params)
                if macd_data is None:
                    return None
                # 生成交易信号
                return self.macd_strategy.generate_macd_signals(macd_data)
                
            elif strategy_name == "RSI":
                # 分离RSI计算参数和信号参数
                rsi_params = {'period': strategy_params['period']}
                signal_params = {
                    'oversold': strategy_params['oversold'],
                    'overbought': strategy_params['overbought']
                }
                # 计算RSI指标
                rsi_data = self.rsi_strategy.calculate_rsi(data, **rsi_params)
                if rsi_data is None:
                    return None
                # 生成交易信号
                return self.rsi_strategy.generate_rsi_signals(rsi_data, **signal_params)
                
            elif strategy_name == "BollingerBands":
                # 计算布林带指标
                bb_data = self.bb_strategy.calculate_bollinger_bands(data, **strategy_params)
                if bb_data is None:
                    return None
                # 生成交易信号
                return self.bb_strategy.generate_bollinger_signals(bb_data)
                
            elif strategy_name == "MovingAverage":
                # 计算移动平均指标
                ma_data = self.ma_strategy.calculate_moving_averages(data, **strategy_params)
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
        if strategy_name == "MACD":
            signal_info.update({
                'macd_value': float(latest_data.get('MACD', 0)),
                'signal_line': float(latest_data.get('Signal', 0)),
                'histogram': float(latest_data.get('Histogram', 0)),
                'zero_cross_status': latest_data.get('Zero_Cross', 'NONE')
            })
            
        elif strategy_name == "RSI":
            signal_info.update({
                'rsi_value': float(latest_data.get('RSI', 0)),
                'rsi_status': latest_data.get('RSI_Status', 'NORMAL')
            })
            
        elif strategy_name == "BollingerBands":
            # 获取收盘价
            close_price = None
            for col in ['收盘价', 'close', 'Close']:
                if col in latest_data.index:
                    close_price = float(latest_data[col])
                    break
            
            signal_info.update({
                'close_price': close_price,
                'sma': float(latest_data.get('SMA', 0)),
                'upper_band': float(latest_data.get('Upper_Band', 0)),
                'lower_band': float(latest_data.get('Lower_Band', 0)),
                'bb_width': float(latest_data.get('BB_Width', 0)),
                'bb_position': float(latest_data.get('BB_Position', 0.5)),
                'bb_status': latest_data.get('BB_Status', 'NORMAL')
            })
            
        elif strategy_name == "MovingAverage":
            # 获取收盘价
            close_price = None
            for col in ['收盘价', 'close', 'Close']:
                if col in latest_data.index:
                    close_price = float(latest_data[col])
                    break
            
            signal_info.update({
                'close_price': close_price,
                'sma_short': float(latest_data.get('SMA_Short', 0)),
                'sma_medium': float(latest_data.get('SMA_Medium', 0)),
                'sma_long': float(latest_data.get('SMA_Long', 0)),
                'ma_spread': float(latest_data.get('MA_Spread_Short_Medium', 0)),
                'ma_trend': latest_data.get('MA_Trend', 'SIDEWAYS')
            })
        
        return signal_info
