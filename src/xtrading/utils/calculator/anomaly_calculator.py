"""
异动检测计算器
负责计算板块和策略的异动检测相关指标
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .return_calculator import ReturnCalculator
from .statistics_calculator import StatisticsCalculator
from .trading_calculator import TradingCalculator


class AnomalyCalculator:
    """异动检测计算器 - 专注于异动检测相关的数据计算"""
    
    @staticmethod
    def calculate_sector_anomaly_metrics(hist_data: pd.DataFrame, industry_name: str) -> Dict[str, Any]:
        """
        计算板块异动检测指标
        
        Args:
            hist_data: 历史数据
            industry_name: 行业名称
            
        Returns:
            Dict[str, Any]: 板块异动指标字典
        """
        metrics = {
            'industry_name': industry_name,
            'has_anomaly': False,
            'anomaly_types': [],
            'volatility_anomaly': False,
            'return_deviation_anomaly': False,
            'extreme_volatility_anomaly': False,
            'high_volatility_anomaly': False,
            'frequent_volatility_anomaly': False,
            'metrics': {}
        }
        
        if len(hist_data) < 14:  # 至少需要14天数据
            return metrics
        
        # 找到收盘价列
        close_col = None
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in hist_data.columns:
                close_col = col
                break
        
        if close_col is None:
            return metrics
        
        # 计算板块收益率
        daily_returns = ReturnCalculator.calculate_daily_returns(hist_data[close_col])
        hist_data['daily_return'] = daily_returns
        
        # 计算近两周（14天）的收益率
        recent_14_days = hist_data.tail(14)
        recent_returns = recent_14_days['daily_return'].dropna()
        
        if len(recent_returns) < 7:  # 至少需要7个有效数据点
            return metrics
        
        # 计算整体期间收益率
        overall_returns = hist_data['daily_return'].dropna()
        
        if len(overall_returns) < 14:
            return metrics
        
        # 计算统计指标
        recent_mean = StatisticsCalculator.calculate_mean(recent_returns)
        recent_std = StatisticsCalculator.calculate_std(recent_returns)
        overall_mean = StatisticsCalculator.calculate_mean(overall_returns)
        overall_std = StatisticsCalculator.calculate_std(overall_returns)
        
        # 存储基础指标
        metrics['metrics'] = {
            'recent_mean': recent_mean,
            'recent_std': recent_std,
            'overall_mean': overall_mean,
            'overall_std': overall_std,
            'recent_returns': recent_returns.tolist(),
            'overall_returns': overall_returns.tolist()
        }
        
        # 检测波动率异常（近两周波动率是整体波动率的1.5倍以上）
        if recent_std > overall_std * 1.5:
            metrics['volatility_anomaly'] = True
            metrics['anomaly_types'].append('volatility')
            metrics['has_anomaly'] = True
        
        # 收益率偏离检测（近两周平均收益率偏离整体平均收益率超过1.5个标准差）
        deviation_threshold = overall_std * 1.5
        deviation = abs(recent_mean - overall_mean)
        
        if deviation > deviation_threshold:
            metrics['return_deviation_anomaly'] = True
            metrics['anomaly_types'].append('return_deviation')
            metrics['has_anomaly'] = True
            metrics['metrics']['deviation_direction'] = 'up' if recent_mean > overall_mean else 'down'
        
        # 检测极端单日收益（2.5个标准差）
        extreme_threshold = overall_std * 2.5
        extreme_days = recent_returns[abs(recent_returns) > extreme_threshold]
        
        if len(extreme_days) > 0:
            metrics['extreme_volatility_anomaly'] = True
            metrics['anomaly_types'].append('extreme_volatility')
            metrics['has_anomaly'] = True
            metrics['metrics']['max_extreme'] = extreme_days.max()
            metrics['metrics']['min_extreme'] = extreme_days.min()
        
        # 检测大幅波动（近两周最大单日波动超过3%）
        max_daily_volatility = abs(recent_returns).max()
        if max_daily_volatility > 0.03:  # 3%
            metrics['high_volatility_anomaly'] = True
            metrics['anomaly_types'].append('high_volatility')
            metrics['has_anomaly'] = True
            metrics['metrics']['max_daily_volatility'] = max_daily_volatility
        
        # 检测连续波动（近两周正负波动交替频繁）
        if len(recent_returns) >= 10:
            sign_changes = 0
            for i in range(1, len(recent_returns)):
                if (recent_returns.iloc[i] > 0) != (recent_returns.iloc[i-1] > 0):
                    sign_changes += 1
            
            volatility_frequency = sign_changes / len(recent_returns)
            if volatility_frequency > 0.6:  # 60%以上的交易日出现方向变化
                metrics['frequent_volatility_anomaly'] = True
                metrics['anomaly_types'].append('frequent_volatility')
                metrics['has_anomaly'] = True
                metrics['metrics']['volatility_frequency'] = volatility_frequency
        
        return metrics
    
    @staticmethod
    def calculate_strategy_anomaly_metrics(results: List[Dict[str, Any]], hist_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        计算策略异动检测指标
        
        Args:
            results: 回测结果列表
            hist_data: 历史数据
            
        Returns:
            List[Dict[str, Any]]: 策略异动指标列表
        """
        strategy_metrics = []
        
        if len(hist_data) < 14:  # 至少需要14天数据
            return strategy_metrics
        
        # 计算整体期间收益率作为基准
        close_col = '收盘' if '收盘' in hist_data.columns else ('收盘价' if '收盘价' in hist_data.columns else 'close')
        daily_returns = ReturnCalculator.calculate_daily_returns(hist_data[close_col])
        hist_data['daily_return'] = daily_returns
        overall_returns = daily_returns.dropna()
        
        if len(overall_returns) < 14:
            return strategy_metrics
        
        overall_mean = StatisticsCalculator.calculate_mean(overall_returns)
        overall_std = StatisticsCalculator.calculate_std(overall_returns)
        
        for result in results:
            strategy_name = result['strategy_name']
            portfolio_values = result.get('portfolio_values', [])
            
            if len(portfolio_values) < 14:
                continue
            
            # 计算策略近两周收益率
            recent_portfolio = portfolio_values[-14:]  # 近14天
            strategy_recent_returns = TradingCalculator.calculate_portfolio_daily_returns(
                [p['portfolio_value'] for p in recent_portfolio]
            )
            
            if len(strategy_recent_returns) < 7:  # 至少需要7个有效数据点
                continue
            
            # 计算策略统计指标
            strategy_recent_mean = StatisticsCalculator.calculate_mean(strategy_recent_returns)
            strategy_recent_std = StatisticsCalculator.calculate_std(strategy_recent_returns)
            
            # 创建策略指标字典
            strategy_metric = {
                'strategy_name': strategy_name,
                'has_anomaly': False,
                'anomaly_types': [],
                'volatility_anomaly': False,
                'return_deviation_anomaly': False,
                'extreme_performance_anomaly': False,
                'high_volatility_anomaly': False,
                'correlation_anomaly': False,
                'metrics': {
                    'strategy_recent_mean': strategy_recent_mean,
                    'strategy_recent_std': strategy_recent_std,
                    'overall_mean': overall_mean,
                    'overall_std': overall_std,
                    'strategy_recent_returns': strategy_recent_returns
                }
            }
            
            # 检测策略波动率异常（1.5倍阈值）
            if strategy_recent_std > overall_std * 1.5:
                strategy_metric['volatility_anomaly'] = True
                strategy_metric['anomaly_types'].append('volatility')
                strategy_metric['has_anomaly'] = True
            
            # 检测策略收益率偏离（1.5倍阈值）
            deviation_threshold = overall_std * 1.5
            deviation = abs(strategy_recent_mean - overall_mean)
            
            if deviation > deviation_threshold:
                strategy_metric['return_deviation_anomaly'] = True
                strategy_metric['anomaly_types'].append('return_deviation')
                strategy_metric['has_anomaly'] = True
                strategy_metric['metrics']['deviation_direction'] = 'up' if strategy_recent_mean > overall_mean else 'down'
            
            # 检测策略极端表现（2.5倍阈值）
            extreme_threshold = overall_std * 2.5
            strategy_extreme_days = [r for r in strategy_recent_returns if abs(r) > extreme_threshold]
            
            if len(strategy_extreme_days) > 0:
                strategy_metric['extreme_performance_anomaly'] = True
                strategy_metric['anomaly_types'].append('extreme_performance')
                strategy_metric['has_anomaly'] = True
                strategy_metric['metrics']['max_extreme'] = max(strategy_extreme_days)
                strategy_metric['metrics']['min_extreme'] = min(strategy_extreme_days)
            
            # 检测策略大幅波动（超过3%）
            max_strategy_volatility = max(abs(r) for r in strategy_recent_returns)
            if max_strategy_volatility > 0.03:  # 3%
                strategy_metric['high_volatility_anomaly'] = True
                strategy_metric['anomaly_types'].append('high_volatility')
                strategy_metric['has_anomaly'] = True
                strategy_metric['metrics']['max_strategy_volatility'] = max_strategy_volatility
            
            # 检测策略与板块相关性异常
            if len(strategy_recent_returns) >= 7:
                try:
                    # 检查数据是否有变化（避免标准差为0的情况）
                    strategy_std = StatisticsCalculator.calculate_std(strategy_recent_returns)
                    overall_std_tail = StatisticsCalculator.calculate_std(overall_returns.tail(len(strategy_recent_returns)))
                    
                    if strategy_std > 1e-10 and overall_std_tail > 1e-10:  # 避免除零错误
                        correlation = StatisticsCalculator.calculate_correlation(
                            strategy_recent_returns, 
                            overall_returns.tail(len(strategy_recent_returns))
                        )
                        strategy_metric['metrics']['correlation'] = correlation
                        
                        if abs(correlation) < 0.3:  # 相关性过低
                            strategy_metric['correlation_anomaly'] = True
                            strategy_metric['anomaly_types'].append('correlation')
                            strategy_metric['has_anomaly'] = True
                except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                    pass  # 忽略相关性计算错误
            
            strategy_metrics.append(strategy_metric)
        
        return strategy_metrics
    
    @staticmethod
    def calculate_anomaly_summary(sector_metrics: Dict[str, Any], strategy_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算异动检测总结
        
        Args:
            sector_metrics: 板块异动指标
            strategy_metrics: 策略异动指标列表
            
        Returns:
            Dict[str, Any]: 异动检测总结
        """
        summary = {
            'total_anomalies': 0,
            'sector_anomalies': 0,
            'strategy_anomalies': 0,
            'anomaly_types': set(),
            'has_any_anomaly': False
        }
        
        # 统计板块异动
        if sector_metrics.get('has_anomaly', False):
            summary['sector_anomalies'] = len(sector_metrics.get('anomaly_types', []))
            summary['anomaly_types'].update(sector_metrics.get('anomaly_types', []))
            summary['has_any_anomaly'] = True
        
        # 统计策略异动
        for strategy_metric in strategy_metrics:
            if strategy_metric.get('has_anomaly', False):
                summary['strategy_anomalies'] += len(strategy_metric.get('anomaly_types', []))
                summary['anomaly_types'].update(strategy_metric.get('anomaly_types', []))
                summary['has_any_anomaly'] = True
        
        summary['total_anomalies'] = summary['sector_anomalies'] + summary['strategy_anomalies']
        summary['anomaly_types'] = list(summary['anomaly_types'])
        
        return summary
