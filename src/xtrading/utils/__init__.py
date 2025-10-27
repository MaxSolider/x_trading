"""
工具模块
包含各种实用工具类
"""

# 延迟导入，避免在模块初始化时导入pandas
def _lazy_import():
    """延迟导入函数"""
    from .rules.stock_code_utils import StockCodeUtils
    from .pandas.pandas_config import configure_pandas_display, reset_pandas_display, show_pandas_config
    from .limiter.akshare_rate_limiter import AKShareRateLimiter, rate_limit, rate_limit_manual, akshare_rate_limiter
    from .calculator import ReturnCalculator, RiskCalculator, StatisticsCalculator, TradingCalculator
    from .date.date_utils import DateUtils
    from .thread_cleanup import setup_thread_cleanup, suppress_thread_warnings
    
    return {
        'StockCodeUtils': StockCodeUtils,
        'configure_pandas_display': configure_pandas_display,
        'reset_pandas_display': reset_pandas_display,
        'show_pandas_config': show_pandas_config,
        'AKShareRateLimiter': AKShareRateLimiter,
        'rate_limit': rate_limit,
        'rate_limit_manual': rate_limit_manual,
        'akshare_rate_limiter': akshare_rate_limiter,
        'ReturnCalculator': ReturnCalculator,
        'RiskCalculator': RiskCalculator,
        'StatisticsCalculator': StatisticsCalculator,
        'TradingCalculator': TradingCalculator,
        'DateUtils': DateUtils,
        'setup_thread_cleanup': setup_thread_cleanup,
        'suppress_thread_warnings': suppress_thread_warnings
    }

# 延迟导入，避免在模块初始化时导入依赖numpy的模块
# from .calculator import ReturnCalculator, RiskCalculator, StatisticsCalculator, TradingCalculator

__all__ = [
    'ReturnCalculator',
    'RiskCalculator',
    'StatisticsCalculator',
    'TradingCalculator',
    'DateUtils',
    'setup_thread_cleanup',
    'suppress_thread_warnings'
]
