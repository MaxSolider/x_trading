"""
个股策略参数配置
包含所有个股策略的默认参数设置
"""

from datetime import datetime, timedelta
from typing import Dict, Any


class StockStrategyParams:
    """个股策略参数配置类"""
    
    # 趋势追踪策略参数
    TREND_TRACKING_PARAMS = {
        # 移动平均线参数
        'short_period': 5,      # 短期移动平均周期
        'medium_period': 20,    # 中期移动平均周期
        'long_period': 60,      # 长期移动平均周期
        
        # MACD参数
        'fast_period': 12,      # MACD快线周期
        'slow_period': 26,      # MACD慢线周期
        'signal_period': 9      # MACD信号线周期
    }
    
    # 突破买入策略参数
    BREAKOUT_PARAMS = {
        # 布林带参数
        'period': 20,           # 布林带移动平均周期
        'std_dev': 2.0,         # 布林带标准差倍数
        
        # 量比参数
        'volume_period': 5,     # 量比计算周期
        
        # 阻力位参数
        'resistance_lookback_period': 60,  # 阻力位回望周期
        
        # 突破信号参数
        'volume_threshold': 1.2  # 量比阈值
    }
    
    # 超跌反弹策略参数
    OVERSOLD_REBOUND_PARAMS = {
        # KDJ参数
        'k_period': 9,          # K值计算周期
        'd_period': 3,           # D值计算周期
        'j_period': 3,           # J值计算周期
        
        # RSI参数
        'rsi_period': 14,        # RSI计算周期
        
        # 价格跌幅参数
        'decline_period': 20,    # 跌幅计算周期
        
        # 超卖信号参数
        'kdj_oversold': 20,      # KDJ超卖阈值
        'rsi_oversold': 30,      # RSI超卖阈值
        'decline_threshold': 15  # 跌幅阈值（百分比）
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
            'TrendTracking': cls.TREND_TRACKING_PARAMS,
            'Breakout': cls.BREAKOUT_PARAMS,
            'OversoldRebound': cls.OVERSOLD_REBOUND_PARAMS
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
            'TrendTracking': cls.TREND_TRACKING_PARAMS,
            'Breakout': cls.BREAKOUT_PARAMS,
            'OversoldRebound': cls.OVERSOLD_REBOUND_PARAMS
        }
    
    @classmethod
    def get_trend_tracking_params(cls) -> Dict[str, Any]:
        """
        获取趋势追踪策略参数
        
        Returns:
            Dict: 趋势追踪策略参数字典
        """
        return cls.TREND_TRACKING_PARAMS.copy()
    
    @classmethod
    def get_breakout_params(cls) -> Dict[str, Any]:
        """
        获取突破买入策略参数
        
        Returns:
            Dict: 突破买入策略参数字典
        """
        return cls.BREAKOUT_PARAMS.copy()
    
    @classmethod
    def get_oversold_rebound_params(cls) -> Dict[str, Any]:
        """
        获取超跌反弹策略参数
        
        Returns:
            Dict: 超跌反弹策略参数字典
        """
        return cls.OVERSOLD_REBOUND_PARAMS.copy()
    
    @classmethod
    def print_config(cls):
        """打印当前配置信息"""
        print("📋 个股策略参数配置")
        print("=" * 50)
        
        print(f"\n📅 默认日期范围: 最近 {cls.DEFAULT_DATE_RANGE_DAYS} 天")
        start_date, end_date = cls.get_default_date_range()
        print(f"   开始日期: {start_date}")
        print(f"   结束日期: {end_date}")
        
        print(f"\n📊 趋势追踪策略参数:")
        print(f"   移动平均线:")
        print(f"     短期周期: {cls.TREND_TRACKING_PARAMS['short_period']}")
        print(f"     中期周期: {cls.TREND_TRACKING_PARAMS['medium_period']}")
        print(f"     长期周期: {cls.TREND_TRACKING_PARAMS['long_period']}")
        print(f"   MACD:")
        print(f"     快线周期: {cls.TREND_TRACKING_PARAMS['fast_period']}")
        print(f"     慢线周期: {cls.TREND_TRACKING_PARAMS['slow_period']}")
        print(f"     信号线周期: {cls.TREND_TRACKING_PARAMS['signal_period']}")
        
        print(f"\n📊 突破买入策略参数:")
        print(f"   布林带:")
        print(f"     周期: {cls.BREAKOUT_PARAMS['period']}")
        print(f"     标准差倍数: {cls.BREAKOUT_PARAMS['std_dev']}")
        print(f"   量比:")
        print(f"     计算周期: {cls.BREAKOUT_PARAMS['volume_period']}")
        print(f"     阈值: {cls.BREAKOUT_PARAMS['volume_threshold']}")
        print(f"   阻力位:")
        print(f"     回望周期: {cls.BREAKOUT_PARAMS['resistance_lookback_period']}")
        
        print(f"\n📊 超跌反弹策略参数:")
        print(f"   KDJ:")
        print(f"     K值周期: {cls.OVERSOLD_REBOUND_PARAMS['k_period']}")
        print(f"     D值周期: {cls.OVERSOLD_REBOUND_PARAMS['d_period']}")
        print(f"     J值周期: {cls.OVERSOLD_REBOUND_PARAMS['j_period']}")
        print(f"     超卖阈值: {cls.OVERSOLD_REBOUND_PARAMS['kdj_oversold']}")
        print(f"   RSI:")
        print(f"     计算周期: {cls.OVERSOLD_REBOUND_PARAMS['rsi_period']}")
        print(f"     超卖阈值: {cls.OVERSOLD_REBOUND_PARAMS['rsi_oversold']}")
        print(f"   价格跌幅:")
        print(f"     计算周期: {cls.OVERSOLD_REBOUND_PARAMS['decline_period']}")
        print(f"     跌幅阈值: {cls.OVERSOLD_REBOUND_PARAMS['decline_threshold']}%")


# 导出配置实例
stock_strategy_config = StockStrategyParams()
