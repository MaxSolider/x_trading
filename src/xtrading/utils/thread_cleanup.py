#!/usr/bin/env python3
"""
线程清理工具
解决Python程序退出时的线程清理问题
"""

import threading
import atexit
import sys
import warnings


def setup_thread_cleanup():
    """设置线程清理"""
    # 忽略线程相关的警告
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='threading')
    
    def cleanup_threads():
        """清理线程资源"""
        try:
            # 等待所有非守护线程结束
            for thread in threading.enumerate():
                if thread != threading.current_thread() and not thread.daemon:
                    if thread.is_alive():
                        thread.join(timeout=0.1)
        except Exception:
            # 忽略清理过程中的异常
            pass
    
    # 注册清理函数
    atexit.register(cleanup_threads)


def suppress_thread_warnings():
    """抑制线程相关的警告"""
    import warnings
    
    # 抑制线程相关的警告
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='threading')
    warnings.filterwarnings('ignore', message='.*threading.*')
    warnings.filterwarnings('ignore', message='.*_DeleteDummyThreadOnDel.*')


# 自动设置
setup_thread_cleanup()
suppress_thread_warnings()
