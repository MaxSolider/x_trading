"""
交易相关计算工具类
提供各种交易相关的计算方法
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional, Dict, Any, Tuple


class TradingCalculator:
    """交易相关计算工具类"""
    
    @staticmethod
    def calculate_portfolio_value(capital: float, position: float, current_price: float) -> float:
        """
        计算组合价值
        
        Args:
            capital: 现金
            position: 持仓数量
            current_price: 当前价格
            
        Returns:
            float: 组合总价值
        """
        return capital + (position * current_price)

    @staticmethod
    def calculate_trade_cost(shares: int, price: float, commission_rate: float = 0.0) -> float:
        """
        计算交易成本
        
        Args:
            shares: 交易股数
            price: 交易价格
            commission_rate: 佣金费率
            
        Returns:
            float: 交易成本
        """
        trade_amount = shares * price
        return trade_amount * commission_rate

    @staticmethod
    def calculate_portfolio_daily_returns(portfolio_values: List[float]) -> List[float]:
        """
        计算组合日收益率
        
        Args:
            portfolio_values: 组合价值序列
            
        Returns:
            List[float]: 日收益率序列
        """
        if len(portfolio_values) < 2:
            return []
        
        returns = []
        for i in range(1, len(portfolio_values)):
            prev_value = portfolio_values[i-1]
            current_value = portfolio_values[i]
            
            if prev_value != 0:
                daily_return = (current_value - prev_value) / prev_value
                returns.append(daily_return)
            else:
                returns.append(0.0)
        
        return returns
    
    @staticmethod
    def calculate_trade_statistics(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算交易统计信息
        
        Args:
            trades: 交易记录列表
            
        Returns:
            Dict[str, Any]: 包含交易统计信息的字典
        """
        if not trades:
            return {
                'total_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'total_trade_amount': 0.0,
                'avg_trade_amount': 0.0
            }
        
        buy_trades = len([t for t in trades if t.get('action', '').upper() in ['BUY', 'STRONG_BUY']])
        sell_trades = len([t for t in trades if t.get('action', '').upper() in ['SELL', 'STRONG_SELL']])
        total_trade_amount = sum(trade.get('amount', 0) for trade in trades)
        avg_trade_amount = total_trade_amount / len(trades) if trades else 0
        
        return {
            'total_trades': len(trades),
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_trade_amount': total_trade_amount,
            'avg_trade_amount': avg_trade_amount
        }
    
    @staticmethod
    def calculate_trading_frequency(total_trades: int, data_points: int) -> float:
        """
        计算交易频率
        
        Args:
            total_trades: 总交易次数
            data_points: 数据点数
            
        Returns:
            float: 交易频率
        """
        if data_points <= 0:
            return 0.0
        return total_trades / data_points