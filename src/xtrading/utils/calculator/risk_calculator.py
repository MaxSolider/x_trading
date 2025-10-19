"""
风险指标计算工具类
提供各种风险相关的计算方法
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional


class RiskCalculator:
    """风险指标计算工具类"""
    
    @staticmethod
    def calculate_volatility(returns: Union[pd.Series, List[float]], 
                            annualization_factor: int = 252) -> float:
        """
        计算波动率（年化）
        
        Args:
            returns: 收益率序列
            annualization_factor: 年化因子（默认252个交易日）
            
        Returns:
            float: 年化波动率
        """
        if isinstance(returns, list):
            returns = pd.Series(returns)
        
        if len(returns) < 2:
            return 0.0
        
        return returns.std() * np.sqrt(annualization_factor)
    
    @staticmethod
    def calculate_max_drawdown(values: Union[pd.Series, List[float]]) -> float:
        """
        计算最大回撤
        
        Args:
            values: 价值序列（价格或组合价值）
            
        Returns:
            float: 最大回撤（负值）
        """
        if isinstance(values, list):
            values = pd.Series(values)
        
        if len(values) < 2:
            return 0.0
        
        # 计算历史最高点
        peak = values.expanding().max()
        
        # 计算回撤：(当前值 - 历史最高点) / 历史最高点
        # 避免除零错误
        drawdown = np.where(peak != 0, (values - peak) / peak, 0)
        
        return drawdown.min()
    
    @staticmethod
    def calculate_sharpe_ratio(returns: Union[pd.Series, List[float]], 
                             risk_free_rate: float = 0.0,
                             annualization_factor: int = 252) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            annualization_factor: 年化因子
            
        Returns:
            float: 夏普比率
        """
        if isinstance(returns, list):
            returns = pd.Series(returns)
        
        if len(returns) < 2:
            return 0.0
        
        # 计算超额收益率
        excess_returns = returns - risk_free_rate / annualization_factor
        
        # 计算年化收益率和波动率
        annualized_return = excess_returns.mean() * annualization_factor
        volatility = RiskCalculator.calculate_volatility(returns, annualization_factor)
        
        if volatility == 0:
            return 0.0
        
        return annualized_return / volatility
