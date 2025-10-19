"""
策略参数配置
包含所有策略的默认参数设置
"""

from datetime import datetime, timedelta
from typing import Dict, Any


class StrategyConfig:
    """策略参数配置类"""
    
    # MACD策略参数
    MACD_PARAMS = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    }
    
    # RSI策略参数
    RSI_PARAMS = {
        'period': 14,
        'oversold': 30,
        'overbought': 70
    }
    
    # 布林带策略参数
    BOLLINGER_BANDS_PARAMS = {
        'period': 20,
        'std_dev': 2.0
    }
    
    # 移动平均策略参数
    MOVING_AVERAGE_PARAMS = {
        'short_period': 5,
        'medium_period': 20,
        'long_period': 60
    }
    
    # 默认日期范围（最近三个月）
    DEFAULT_DATE_RANGE_DAYS = 90
    
    @classmethod
    def get_default_date_range(cls) -> tuple[str, str]:
        """
        获取默认日期范围（最近三个月）
        
        Returns:
            tuple: (开始日期, 结束日期) 格式为 YYYYMMDD
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=cls.DEFAULT_DATE_RANGE_DAYS)
        
        return start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    
    @classmethod
    def get_strategy_params(cls, strategy_name: str) -> Dict[str, Any]:
        """
        获取指定策略的参数
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            Dict: 策略参数字典
        """
        strategy_params_map = {
            'MACD': cls.MACD_PARAMS,
            'RSI': cls.RSI_PARAMS,
            'BollingerBands': cls.BOLLINGER_BANDS_PARAMS,
            'MovingAverage': cls.MOVING_AVERAGE_PARAMS
        }
        
        return strategy_params_map.get(strategy_name, {})
    
    @classmethod
    def get_all_strategy_params(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有策略的参数
        
        Returns:
            Dict: 所有策略参数字典
        """
        return {
            'MACD': cls.MACD_PARAMS,
            'RSI': cls.RSI_PARAMS,
            'BollingerBands': cls.BOLLINGER_BANDS_PARAMS,
            'MovingAverage': cls.MOVING_AVERAGE_PARAMS
        }
    
    @classmethod
    def print_config(cls):
        """打印当前配置信息"""
        print("📋 策略参数配置")
        print("=" * 50)
        
        print(f"\n📅 默认日期范围: 最近 {cls.DEFAULT_DATE_RANGE_DAYS} 天")
        start_date, end_date = cls.get_default_date_range()
        print(f"   开始日期: {start_date}")
        print(f"   结束日期: {end_date}")
        
        print(f"\n📊 MACD策略参数:")
        for key, value in cls.MACD_PARAMS.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 RSI策略参数:")
        for key, value in cls.RSI_PARAMS.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 布林带策略参数:")
        for key, value in cls.BOLLINGER_BANDS_PARAMS.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 移动平均策略参数:")
        for key, value in cls.MOVING_AVERAGE_PARAMS.items():
            print(f"   {key}: {value}")


# 导出配置实例
strategy_config = StrategyConfig()
