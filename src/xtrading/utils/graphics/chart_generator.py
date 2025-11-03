"""
图表生成器
提供各种图表生成功能的工具类
"""

import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import warnings


class ChartGenerator:
    """图表生成器工具类"""
    
    def __init__(self):
        """初始化图表生成器"""
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """设置matplotlib配置"""
        try:
            import matplotlib.pyplot as plt
            
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 忽略字体警告
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
