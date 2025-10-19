"""
统计指标计算工具类
提供各种统计相关的计算方法
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional, Tuple, Dict, Any


class StatisticsCalculator:
    """统计指标计算工具类"""
    
    @staticmethod
    def calculate_mean(data: Union[pd.Series, List[float]]) -> float:
        """
        计算均值
        
        Args:
            data: 数据序列
            
        Returns:
            float: 均值
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if len(data) == 0:
            return 0.0
        
        return data.mean()
    
    @staticmethod
    def calculate_median(data: Union[pd.Series, List[float]]) -> float:
        """
        计算中位数
        
        Args:
            data: 数据序列
            
        Returns:
            float: 中位数
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if len(data) == 0:
            return 0.0
        
        return data.median()
    
    @staticmethod
    def calculate_std(data: Union[pd.Series, List[float]]) -> float:
        """
        计算标准差
        
        Args:
            data: 数据序列
            
        Returns:
            float: 标准差
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if len(data) < 2:
            return 0.0
        
        return data.std()

    @staticmethod
    def calculate_skewness(data: Union[pd.Series, List[float]]) -> float:
        """
        计算偏度
        
        Args:
            data: 数据序列
            
        Returns:
            float: 偏度
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if len(data) < 3:
            return 0.0
        
        mean_val = data.mean()
        std_val = data.std()
        
        if std_val == 0:
            return 0.0
        
        return np.mean([(x - mean_val) ** 3 for x in data]) / (std_val ** 3)
    
    @staticmethod
    def calculate_kurtosis(data: Union[pd.Series, List[float]]) -> float:
        """
        计算峰度
        
        Args:
            data: 数据序列
            
        Returns:
            float: 峰度
        """
        if isinstance(data, list):
            data = pd.Series(data)
        
        if len(data) < 4:
            return 0.0
        
        mean_val = data.mean()
        std_val = data.std()
        
        if std_val == 0:
            return 0.0
        
        return np.mean([(x - mean_val) ** 4 for x in data]) / (std_val ** 4) - 3
    
    @staticmethod
    def calculate_correlation(x: Union[pd.Series, List[float]], 
                           y: Union[pd.Series, List[float]]) -> float:
        """
        计算相关系数
        
        Args:
            x: 第一个数据序列
            y: 第二个数据序列
            
        Returns:
            float: 相关系数
        """
        if isinstance(x, list):
            x = pd.Series(x)
        if isinstance(y, list):
            y = pd.Series(y)
        
        if len(x) < 2 or len(y) < 2:
            return 0.0
        
        # 确保两个序列长度一致
        min_length = min(len(x), len(y))
        x = x.iloc[:min_length]
        y = y.iloc[:min_length]
        
        try:
            correlation = np.corrcoef(x, y)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except (ValueError, np.linalg.LinAlgError):
            return 0.0
    
    @staticmethod
    def calculate_win_rate(returns: Union[pd.Series, List[float]]) -> float:
        """
        计算胜率
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 胜率（0-1之间）
        """
        if isinstance(returns, list):
            returns = pd.Series(returns)
        
        if len(returns) == 0:
            return 0.0
        
        positive_count = len(returns[returns > 0])
        return positive_count / len(returns)
    
    @staticmethod
    def calculate_return_summary(returns: Union[pd.Series, List[float]]) -> Dict[str, float]:
        """
        计算收益率统计摘要
        
        Args:
            returns: 收益率序列
            
        Returns:
            Dict[str, float]: 包含统计摘要的字典
        """
        if isinstance(returns, list):
            returns = pd.Series(returns)
        
        if len(returns) == 0:
            return {
                'mean_return': 0.0,
                'max_return': 0.0,
                'min_return': 0.0,
                'positive_days': 0,
                'negative_days': 0
            }
        
        return {
            'mean_return': returns.mean(),
            'max_return': returns.max(),
            'min_return': returns.min(),
            'positive_days': len(returns[returns > 0]),
            'negative_days': len(returns[returns < 0])
        }
    
    @staticmethod
    def calculate_cumulative_summary(cumulative_returns: Union[pd.Series, List[float]]) -> Dict[str, Any]:
        """
        计算累计收益率统计摘要
        
        Args:
            cumulative_returns: 累计收益率序列
            
        Returns:
            Dict[str, Any]: 包含累计收益统计摘要的字典
        """
        if isinstance(cumulative_returns, list):
            cumulative_returns = pd.Series(cumulative_returns)
        
        if len(cumulative_returns) == 0:
            return {
                'final_return': 0.0,
                'max_return': 0.0,
                'min_return': 0.0,
                'volatility_range': 0.0,
                'stability': '稳定'
            }
        
        final_return = cumulative_returns.iloc[-1]
        max_return = cumulative_returns.max()
        min_return = cumulative_returns.min()
        volatility_range = max_return - min_return
        stability = '稳定' if volatility_range < 20 else '波动'
        
        return {
            'final_return': final_return,
            'max_return': max_return,
            'min_return': min_return,
            'volatility_range': volatility_range,
            'stability': stability
        }