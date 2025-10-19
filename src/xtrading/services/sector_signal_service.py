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
        
        print("✅ 板块信号计算服务初始化成功")
    
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
        
        print(f"🔍 开始计算 {len(sector_list)} 个板块的 {len(strategies)} 种策略信号...")
        print(f"📅 日期范围: {start_date} 至 {end_date}")
        
        results = {
            'calculation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_sectors': len(sector_list),
            'strategies_used': strategies,
            'date_range': {'start_date': start_date, 'end_date': end_date},
            'sector_signals': {}
        }
        
        # 为每个板块计算信号
        for sector in sector_list:
            print(f"📊 正在计算 {sector} 的信号...")
            
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
        
        print(f"✅ 板块信号计算完成，共处理 {len(sector_list)} 个板块")
        return results
    
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
    
    def get_signal_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成信号汇总统计
        
        Args:
            results: 信号计算结果
            
        Returns:
            Dict: 汇总统计信息
        """
        if not results or 'sector_signals' not in results:
            return {}
        
        summary = {
            'total_sectors': results['total_sectors'],
            'strategies_used': results['strategies_used'],
            'calculation_time': results['calculation_time'],
            'date_range': results.get('date_range', {}),
            'signal_statistics': {},
            'sector_summary': {}
        }
        
        # 统计各策略的信号分布
        for strategy in results['strategies_used']:
            signal_counts = {'BUY': 0, 'SELL': 0, 'STRONG_BUY': 0, 'STRONG_SELL': 0, 'HOLD': 0, 'ERROR': 0}
            
            for sector_name, sector_data in results['sector_signals'].items():
                if 'strategies' in sector_data and strategy in sector_data['strategies']:
                    strategy_data = sector_data['strategies'][strategy]
                    if 'error' in strategy_data:
                        signal_counts['ERROR'] += 1
                    else:
                        signal_type = strategy_data.get('signal_type', 'HOLD')
                        signal_counts[signal_type] += 1
            
            summary['signal_statistics'][strategy] = signal_counts
        
        # 统计各板块的信号情况
        for sector_name, sector_data in results['sector_signals'].items():
            sector_summary = {
                'category': sector_data.get('category', 'Unknown'),
                'total_strategies': len(results['strategies_used']),
                'successful_strategies': 0,
                'failed_strategies': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'hold_signals': 0
            }
            
            if 'strategies' in sector_data:
                for strategy_name, strategy_data in sector_data['strategies'].items():
                    if 'error' in strategy_data:
                        sector_summary['failed_strategies'] += 1
                    else:
                        sector_summary['successful_strategies'] += 1
                        signal_type = strategy_data.get('signal_type', 'HOLD')
                        if signal_type in ['BUY', 'STRONG_BUY']:
                            sector_summary['buy_signals'] += 1
                        elif signal_type in ['SELL', 'STRONG_SELL']:
                            sector_summary['sell_signals'] += 1
                        else:
                            sector_summary['hold_signals'] += 1
            
            summary['sector_summary'][sector_name] = sector_summary
        
        return summary
    
