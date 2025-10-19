"""
Pandas全局配置模块
设置pandas的全局显示选项
"""

import pandas as pd
import warnings


def configure_pandas_display():
    """
    配置pandas全局显示选项
    确保能够显示所有列和完整内容
    """
    # 设置pandas显示选项
    pd.set_option('display.max_columns', None)      # 显示所有列
    pd.set_option('display.max_rows', None)         # 显示所有行
    pd.set_option('display.width', None)            # 不限制显示宽度
    pd.set_option('display.max_colwidth', None)     # 不限制列内容宽度
    pd.set_option('display.expand_frame_repr', False)  # 不换行显示DataFrame
    pd.set_option('display.large_repr', 'truncate')    # 大数据集使用截断模式
    
    # 设置浮点数显示精度
    pd.set_option('display.precision', 2)           # 浮点数显示2位小数
    
    # 设置科学计数法阈值
    pd.set_option('display.float_format', '{:.2f}'.format)  # 浮点数格式
    
    print("✅ Pandas全局显示配置已设置")


def reset_pandas_display():
    """
    重置pandas显示选项为默认值
    """
    pd.reset_option('display.max_columns')
    pd.reset_option('display.max_rows')
    pd.reset_option('display.width')
    pd.reset_option('display.max_colwidth')
    pd.reset_option('display.expand_frame_repr')
    pd.reset_option('display.large_repr')
    pd.reset_option('display.precision')
    pd.reset_option('display.float_format')
    
    print("✅ Pandas显示配置已重置为默认值")


def show_pandas_config():
    """
    显示当前pandas配置
    """
    print("\n📊 当前Pandas显示配置:")
    print("-" * 40)
    print(f"最大列数: {pd.get_option('display.max_columns')}")
    print(f"最大行数: {pd.get_option('display.max_rows')}")
    print(f"显示宽度: {pd.get_option('display.width')}")
    print(f"最大列宽: {pd.get_option('display.max_colwidth')}")
    print(f"展开框架: {pd.get_option('display.expand_frame_repr')}")
    print(f"大表模式: {pd.get_option('display.large_repr')}")
    print(f"精度: {pd.get_option('display.precision')}")


# 自动配置pandas显示选项
configure_pandas_display()
