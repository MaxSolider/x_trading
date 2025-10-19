"""
市场分析计算工具类
提供市场分析相关的计算方法
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .statistics_calculator import StatisticsCalculator


class MarketCalculator:
    """市场分析计算工具类"""
    
    @staticmethod
    def calculate_market_overview_stats(all_results: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        计算市场整体统计指标
        
        Args:
            all_results: 所有行业板块的回测结果
            
        Returns:
            Dict[str, Any]: 市场整体统计指标
        """
        if not all_results:
            return {
                'total_industries': 0,
                'total_strategies': 0,
                'avg_total_return': 0.0,
                'median_total_return': 0.0,
                'best_return': 0.0,
                'worst_return': 0.0,
                'win_rate': 0.0,
                'benchmark_beating_rate': 0.0,
                'best_strategy': None,
                'worst_strategy': None
            }
        
        # 统计基本信息
        total_industries = len(all_results)
        total_strategies = sum(len(results) for results in all_results)
        
        # 收集所有策略数据
        all_strategy_results = []
        for results in all_results:
            all_strategy_results.extend(results)
        
        if not all_strategy_results:
            return {
                'total_industries': total_industries,
                'total_strategies': 0,
                'avg_total_return': 0.0,
                'median_total_return': 0.0,
                'best_return': 0.0,
                'worst_return': 0.0,
                'win_rate': 0.0,
                'benchmark_beating_rate': 0.0,
                'best_strategy': None,
                'worst_strategy': None
            }
        
        # 计算市场整体指标
        total_returns = [r['total_return'] for r in all_strategy_results]
        
        # 计算统计指标
        avg_total_return = StatisticsCalculator.calculate_mean(total_returns)
        median_total_return = StatisticsCalculator.calculate_median(total_returns)
        best_return = max(total_returns)
        worst_return = min(total_returns)
        
        # 计算胜率
        win_rate = StatisticsCalculator.calculate_win_rate(total_returns)
        
        # 计算超越基准的比例
        benchmark_beating = len([r for r in total_returns if r > 0.1])  # 假设10%为基准
        benchmark_beating_rate = benchmark_beating / len(total_returns)
        
        # 找到最佳和最差策略
        best_strategy = max(all_strategy_results, key=lambda x: x['total_return'])
        worst_strategy = min(all_strategy_results, key=lambda x: x['total_return'])
        
        return {
            'total_industries': total_industries,
            'total_strategies': total_strategies,
            'avg_total_return': avg_total_return,
            'median_total_return': median_total_return,
            'best_return': best_return,
            'worst_return': worst_return,
            'win_rate': win_rate,
            'benchmark_beating_rate': benchmark_beating_rate,
            'best_strategy': best_strategy,
            'worst_strategy': worst_strategy
        }
    
    @staticmethod
    def calculate_sector_category_stats(all_results: List[List[Dict[str, Any]]], 
                                     get_industry_category_func) -> List[Dict[str, Any]]:
        """
        计算板块分类统计指标
        
        Args:
            all_results: 所有行业板块的回测结果
            get_industry_category_func: 获取行业分类的函数
            
        Returns:
            List[Dict[str, Any]]: 板块分类统计指标列表
        """
        if not all_results:
            return []
        
        # 按板块分类统计
        category_stats = {}
        
        for results in all_results:
            if not results:
                continue
                
            industry_name = results[0].get('industry_name', 'Unknown')
            category = get_industry_category_func(industry_name)
            
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
        
        # 按平均收益率排序并生成结果
        sorted_categories = sorted(category_stats.items(), 
                                key=lambda x: StatisticsCalculator.calculate_mean(x[1]['total_returns']), 
                                reverse=True)
        
        category_comparison_data = []
        for i, (category, stats) in enumerate(sorted_categories, 1):
            avg_return = StatisticsCalculator.calculate_mean(stats['total_returns'])
            avg_sharpe = StatisticsCalculator.calculate_mean(stats['sharpe_ratios'])
            avg_drawdown = StatisticsCalculator.calculate_mean(stats['max_drawdowns'])
            industry_count = len(stats['industries'])
            strategy_count = len(stats['strategies'])
            
            # 计算胜率
            win_rate = StatisticsCalculator.calculate_win_rate(stats['total_returns'])
            
            category_comparison_data.append({
                'ranking': i,
                'category': category,
                'industry_count': industry_count,
                'strategy_count': strategy_count,
                'avg_return': avg_return,
                'avg_sharpe': avg_sharpe,
                'avg_drawdown': avg_drawdown,
                'win_rate': win_rate
            })
        
        return category_comparison_data
    
    @staticmethod
    def calculate_industry_stats(all_results: List[List[Dict[str, Any]]], 
                               get_industry_category_func) -> List[Dict[str, Any]]:
        """
        计算行业统计指标
        
        Args:
            all_results: 所有行业板块的回测结果
            get_industry_category_func: 获取行业分类的函数
            
        Returns:
            List[Dict[str, Any]]: 行业统计指标列表
        """
        if not all_results:
            return []
        
        # 收集所有行业数据
        industry_stats = []
        
        for results in all_results:
            if not results:
                continue
                
            industry_name = results[0].get('industry_name', 'Unknown')
            category = get_industry_category_func(industry_name)
            
            # 计算行业整体表现
            industry_returns = [r['total_return'] for r in results]
            industry_sharpe = [r['sharpe_ratio'] for r in results]
            industry_drawdown = [r['max_drawdown'] for r in results]
            
            avg_return = StatisticsCalculator.calculate_mean(industry_returns)
            avg_sharpe = StatisticsCalculator.calculate_mean(industry_sharpe)
            avg_drawdown = StatisticsCalculator.calculate_mean(industry_drawdown)
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
        
        return industry_stats
    
    @staticmethod
    def calculate_strategy_ranking_stats(all_results: List[List[Dict[str, Any]]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        计算策略排行统计指标
        
        Args:
            all_results: 所有行业板块的回测结果
            
        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: (策略排行列表, 策略类型统计列表)
        """
        if not all_results:
            return [], []
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            for result in results:
                all_strategies.append(result)
        
        if not all_strategies:
            return [], []
        
        # 按总收益率排序
        all_strategies.sort(key=lambda x: x['total_return'], reverse=True)
        
        # 策略类型统计
        strategy_type_stats = {}
        for strategy in all_strategies:
            strategy_name = strategy['strategy_name']
            if strategy_name not in strategy_type_stats:
                strategy_type_stats[strategy_name] = []
            strategy_type_stats[strategy_name].append(strategy['total_return'])
        
        strategy_type_data = []
        for strategy_type, returns in strategy_type_stats.items():
            avg_return = StatisticsCalculator.calculate_mean(returns)
            max_return = max(returns)
            min_return = min(returns)
            count = len(returns)
            win_rate = StatisticsCalculator.calculate_win_rate(returns)
            
            strategy_type_data.append({
                'strategy_type': strategy_type,
                'count': count,
                'avg_return': avg_return,
                'max_return': max_return,
                'min_return': min_return,
                'win_rate': win_rate
            })
        
        # 按平均收益率排序
        strategy_type_data.sort(key=lambda x: x['avg_return'], reverse=True)
        
        return all_strategies, strategy_type_data
    
    @staticmethod
    def calculate_risk_return_stats(all_results: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        计算风险收益统计指标
        
        Args:
            all_results: 所有行业板块的回测结果
            
        Returns:
            Dict[str, Any]: 风险收益统计指标
        """
        if not all_results:
            return {
                'returns_distribution': {},
                'risk_distribution': {},
                'quadrant_analysis': {}
            }
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            all_strategies.extend(results)
        
        if not all_strategies:
            return {
                'returns_distribution': {},
                'risk_distribution': {},
                'quadrant_analysis': {}
            }
        
        # 计算风险收益指标
        returns = [s['total_return'] for s in all_strategies]
        volatilities = [s['volatility'] for s in all_strategies]
        sharpe_ratios = [s['sharpe_ratio'] for s in all_strategies]
        max_drawdowns = [s['max_drawdown'] for s in all_strategies]
        
        # 收益率分布统计
        returns_distribution = {
            'min_return': min(returns),
            'max_return': max(returns),
            'std_return': StatisticsCalculator.calculate_std(returns),
            'skewness': StatisticsCalculator.calculate_skewness(returns),
            'kurtosis': StatisticsCalculator.calculate_kurtosis(returns)
        }
        
        # 风险分布统计
        risk_distribution = {
            'volatility_range': (min(volatilities), max(volatilities)),
            'volatility_mean': StatisticsCalculator.calculate_mean(volatilities),
            'max_drawdown_range': (min(max_drawdowns), max(max_drawdowns)),
            'max_drawdown_mean': StatisticsCalculator.calculate_mean(max_drawdowns),
            'sharpe_range': (min(sharpe_ratios), max(sharpe_ratios)),
            'sharpe_mean': StatisticsCalculator.calculate_mean(sharpe_ratios)
        }
        
        # 风险收益象限分析
        avg_return = StatisticsCalculator.calculate_mean(returns)
        avg_volatility = StatisticsCalculator.calculate_mean(volatilities)
        
        high_return_high_risk = [s for s in all_strategies if s['total_return'] > avg_return and s['volatility'] > avg_volatility]
        high_return_low_risk = [s for s in all_strategies if s['total_return'] > avg_return and s['volatility'] <= avg_volatility]
        low_return_high_risk = [s for s in all_strategies if s['total_return'] <= avg_return and s['volatility'] > avg_volatility]
        low_return_low_risk = [s for s in all_strategies if s['total_return'] <= avg_return and s['volatility'] <= avg_volatility]
        
        quadrant_analysis = {
            'high_return_high_risk': {
                'count': len(high_return_high_risk),
                'strategies': high_return_high_risk
            },
            'high_return_low_risk': {
                'count': len(high_return_low_risk),
                'strategies': high_return_low_risk
            },
            'low_return_high_risk': {
                'count': len(low_return_high_risk),
                'strategies': low_return_high_risk
            },
            'low_return_low_risk': {
                'count': len(low_return_low_risk),
                'strategies': low_return_low_risk
            },
            'total_strategies': len(all_strategies),
            'avg_return': avg_return,
            'avg_volatility': avg_volatility
        }
        
        return {
            'returns_distribution': returns_distribution,
            'risk_distribution': risk_distribution,
            'quadrant_analysis': quadrant_analysis
        }
    
    @staticmethod
    def calculate_investment_recommendations(all_results: List[List[Dict[str, Any]]]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        计算投资建议数据
        
        Args:
            all_results: 所有行业板块的回测结果
            
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: (推荐策略列表, 各行业最佳策略字典)
        """
        if not all_results:
            return [], {}
        
        # 收集所有策略数据
        all_strategies = []
        for results in all_results:
            all_strategies.extend(results)
        
        if not all_strategies:
            return [], {}
        
        # 找出表现最好的策略
        best_strategies = sorted(all_strategies, key=lambda x: x['total_return'], reverse=True)[:5]
        
        # 按行业分类找出最佳策略
        industry_best = {}
        for strategy in all_strategies:
            industry = strategy['industry_name']
            if industry not in industry_best or strategy['total_return'] > industry_best[industry]['total_return']:
                industry_best[industry] = strategy
        
        return best_strategies, industry_best
    
    @staticmethod
    def calculate_industry_win_rate(all_results: List[List[Dict[str, Any]]], industry_name: str) -> float:
        """
        计算特定行业的胜率
        
        Args:
            all_results: 所有行业板块的回测结果
            industry_name: 行业名称
            
        Returns:
            float: 胜率
        """
        industry_results = []
        for results in all_results:
            if results and results[0].get('industry_name') == industry_name:
                industry_results.extend(results)
        
        if not industry_results:
            return 0.0
        
        industry_returns = [r['total_return'] for r in industry_results]
        return StatisticsCalculator.calculate_win_rate(industry_returns)
