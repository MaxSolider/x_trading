"""
AKShare频控工具类
实现全局API调用频率控制，避免被第三方封禁
"""

import time
import threading
from typing import Dict, Optional
from functools import wraps


class AKShareRateLimiter:
    """AKShare频控器 - 全局限流策略"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AKShareRateLimiter, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化频控器"""
        if not self._initialized:
            self._last_call_time: float = 0.0  # 全局最后调用时间
            self._global_interval = 1.0  # 全局调用间隔1秒
            self._lock = threading.Lock()
            self._initialized = True
            print("✅ AKShare全局频控器初始化成功 - 所有接口间隔1秒")
    
    def set_global_interval(self, interval: float):
        """
        设置全局调用间隔
        
        Args:
            interval: 全局调用间隔（秒）
        """
        with self._lock:
            self._global_interval = interval
            print(f"✅ 设置全局调用间隔为 {interval} 秒")
    
    def wait_if_needed(self):
        """
        如果需要，等待到可以调用API的时间
        全局限流：所有AKShare接口共享同一个时间间隔
        """
        with self._lock:
            current_time = time.time()
            
            # 检查距离上次调用的时间
            if self._last_call_time > 0:
                elapsed_time = current_time - self._last_call_time
                
                if elapsed_time < self._global_interval:
                    wait_time = self._global_interval - elapsed_time
                    print(f"⏱️ AKShare接口需要等待 {wait_time:.2f} 秒")
                    time.sleep(wait_time)
            
            # 更新全局最后调用时间
            self._last_call_time = time.time()
    
    def get_global_status(self) -> Dict[str, float]:
        """
        获取全局调用状态
        
        Returns:
            Dict: 包含全局调用状态信息的字典
        """
        with self._lock:
            current_time = time.time()
            
            if self._last_call_time > 0:
                elapsed_time = current_time - self._last_call_time
                remaining_time = max(0, self._global_interval - elapsed_time)
                
                return {
                    'last_call_time': self._last_call_time,
                    'elapsed_time': elapsed_time,
                    'global_interval': self._global_interval,
                    'remaining_time': remaining_time,
                    'can_call_now': remaining_time <= 0
                }
            else:
                return {
                    'last_call_time': None,
                    'elapsed_time': 0,
                    'global_interval': self._global_interval,
                    'remaining_time': 0,
                    'can_call_now': True
                }
    
    def print_status(self):
        """打印全局调用状态"""
        print("\n📊 AKShare全局频控状态")
        print("=" * 60)
        print(f"全局调用间隔: {self._global_interval} 秒")
        
        status = self.get_global_status()
        if status['last_call_time']:
            print(f"上次调用时间: {status['elapsed_time']:.2f} 秒前")
            print(f"剩余等待时间: {status['remaining_time']:.2f} 秒")
            print(f"可以立即调用: {'是' if status['can_call_now'] else '否'}")
        else:
            print("尚未调用过任何接口")


def rate_limit(interval: Optional[float] = None):
    """
    频控装饰器 - 全局限流策略
    
    Args:
        interval: 调用间隔（秒），如果为None则使用全局间隔
        
    Usage:
        @rate_limit()
        def get_industry_names():
            return ak.stock_board_industry_name_em()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = AKShareRateLimiter()
            
            # 设置全局间隔（如果指定）
            if interval is not None:
                limiter.set_global_interval(interval)
            
            # 等待到可以调用
            limiter.wait_if_needed()
            
            # 执行函数
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_manual(interval: Optional[float] = None):
    """
    手动频控函数，用于在函数内部调用
    全局限流：所有AKShare接口共享同一个时间间隔
    
    Args:
        interval: 调用间隔（秒）
        
    Usage:
        def get_data():
            rate_limit_manual()
            return ak.stock_board_industry_name_em()
    """
    limiter = AKShareRateLimiter()
    
    # 设置全局间隔（如果指定）
    if interval is not None:
        limiter.set_global_interval(interval)
    
    # 等待到可以调用
    limiter.wait_if_needed()


# 全局频控器实例
akshare_rate_limiter = AKShareRateLimiter()
