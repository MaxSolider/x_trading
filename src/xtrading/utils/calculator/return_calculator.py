"""
收益率计算工具类
提供各种收益率相关的计算方法
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional, Dict, Any


class ReturnCalculator:
    """收益率计算工具类"""
    
    @staticmethod
    def calculate_total_return(initial_value: float, final_value: float) -> float:
        """
        计算总收益率
        
        Args:
            initial_value: 初始价值
            final_value: 最终价值
            
        Returns:
            float: 总收益率
        """
        if initial_value == 0:
            return 0.0
        return (final_value - initial_value) / initial_value
    
    @staticmethod
    def calculate_annualized_return(total_return: float, periods: int, trading_days_per_year: int = 252) -> float:
        """
        计算年化收益率
        
        Args:
            total_return: 总收益率
            periods: 总期数
            trading_days_per_year: 每年交易日数
            
        Returns:
            float: 年化收益率
        """
        if periods <= 0:
            return 0.0
        return (1 + total_return) ** (trading_days_per_year / periods) - 1
    
    @staticmethod
    def calculate_daily_returns(price_series: Union[pd.Series, List[float]]) -> pd.Series:
        """
        计算日收益率序列
        
        Args:
            price_series: 价格序列
            
        Returns:
            pd.Series: 日收益率序列
        """
        if isinstance(price_series, list):
            price_series = pd.Series(price_series)
        
        return price_series.pct_change().dropna()
    
    @staticmethod
    def calculate_cumulative_returns(price_series: Union[pd.Series, List[float]], 
                                   initial_value: Optional[float] = None) -> pd.Series:
        """
        计算累计收益率序列
        
        Args:
            price_series: 价格序列
            initial_value: 初始价值，如果为None则使用第一个价格
            
        Returns:
            pd.Series: 累计收益率序列
        """
        if isinstance(price_series, list):
            price_series = pd.Series(price_series)
        
        if initial_value is None:
            initial_value = price_series.iloc[0]
        
        if initial_value == 0:
            return pd.Series([0.0] * len(price_series), index=price_series.index)
        
        return (price_series / initial_value - 1)

    @staticmethod
    def calculate_sector_return(price_series: Union[pd.Series, List[float]]) -> float:
        """
        计算板块收益率（买入并持有策略）
        
        Args:
            price_series: 价格序列
            
        Returns:
            float: 板块总收益率
        """
        if isinstance(price_series, list):
            price_series = pd.Series(price_series)
        
        if len(price_series) < 2:
            return 0.0
        
        initial_price = price_series.iloc[0]
        final_price = price_series.iloc[-1]
        
        return ReturnCalculator.calculate_total_return(initial_price, final_price)
    
    @staticmethod
    def calculate_strategy_daily_return(portfolio_values: List[Dict[str, Any]], 
                                      current_index: int) -> float:
        """
        计算策略在特定日期的日收益率
        
        Args:
            portfolio_values: 组合价值序列
            current_index: 当前索引
            
        Returns:
            float: 日收益率
        """
        if not portfolio_values or current_index >= len(portfolio_values) or current_index <= 0:
            return 0.0
        
        current_portfolio = portfolio_values[current_index]
        prev_portfolio = portfolio_values[current_index - 1]
        
        if not current_portfolio or not prev_portfolio:
            return 0.0
        
        current_value = current_portfolio.get('portfolio_value', 0)
        prev_value = prev_portfolio.get('portfolio_value', 0)
        
        if prev_value == 0:
            return 0.0
        
        return ReturnCalculator.calculate_total_return(prev_value, current_value)
    
    @staticmethod
    def calculate_strategy_cumulative_return(portfolio_values: List[Dict[str, Any]], 
                                           current_index: int, 
                                           initial_capital: float) -> float:
        """
        计算策略在特定日期的累计收益率
        
        Args:
            portfolio_values: 组合价值序列
            current_index: 当前索引
            initial_capital: 初始资金
            
        Returns:
            float: 累计收益率
        """
        if not portfolio_values or current_index >= len(portfolio_values):
            return 0.0
        
        current_portfolio = portfolio_values[current_index]
        if not current_portfolio:
            return 0.0
        
        current_value = current_portfolio.get('portfolio_value', 0)
        
        if initial_capital == 0:
            return 0.0
        
        return ReturnCalculator.calculate_total_return(initial_capital, current_value)