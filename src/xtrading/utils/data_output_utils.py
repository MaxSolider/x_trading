"""
数据输出工具类
提供数据打印和格式化输出功能
"""

import pandas as pd
from typing import Any, Optional


class DataOutputUtils:
    """数据输出工具类"""
    
    def __init__(self):
        """初始化工具类"""
        print("✅ 数据输出工具初始化成功")
    
    def print_data(self, data: Any, title: str = "数据"):
        """
        打印数据
        
        Args:
            data: 要打印的数据
            title: 数据标题
        """
        print(f"\n📊 {title}")
        print("=" * 60)
        
        if data is None:
            print("❌ 数据为空")
            return
        
        if isinstance(data, pd.DataFrame):
            if data.empty:
                print("❌ DataFrame为空")
            else:
                print(f"数据形状: {data.shape}")
                print("\n前5行数据:")
                print(data.head())
                if len(data) > 5:
                    print(f"\n... 还有 {len(data) - 5} 行数据")
        elif isinstance(data, pd.Series):
            if data.empty:
                print("❌ Series为空")
            else:
                print(f"数据长度: {len(data)}")
                print("\n数据内容:")
                print(data)
        elif isinstance(data, (list, tuple)):
            if not data:
                print("❌ 列表/元组为空")
            else:
                print(f"数据长度: {len(data)}")
                print("\n数据内容:")
                for i, item in enumerate(data[:10]):  # 只显示前10个
                    print(f"  {i+1}: {item}")
                if len(data) > 10:
                    print(f"\n... 还有 {len(data) - 10} 个数据项")
        elif isinstance(data, dict):
            if not data:
                print("❌ 字典为空")
            else:
                print(f"字典键数量: {len(data)}")
                print("\n字典内容:")
                for key, value in list(data.items())[:10]:  # 只显示前10个
                    print(f"  {key}: {value}")
                if len(data) > 10:
                    print(f"\n... 还有 {len(data) - 10} 个键值对")
        else:
            print(f"数据类型: {type(data)}")
            print(f"数据内容: {data}")
    
    def print_data_details(self, data: Any, title: str = "详细数据"):
        """
        打印详细数据
        
        Args:
            data: 要打印的数据
            title: 数据标题
        """
        print(f"\n📋 {title}")
        print("=" * 80)
        
        if data is None:
            print("❌ 数据为空")
            return
        
        if isinstance(data, pd.DataFrame):
            if data.empty:
                print("❌ DataFrame为空")
            else:
                print(f"数据形状: {data.shape}")
                print(f"列名: {list(data.columns)}")
                print(f"数据类型:")
                print(data.dtypes)
                print("\n完整数据:")
                print(data)
        elif isinstance(data, pd.Series):
            if data.empty:
                print("❌ Series为空")
            else:
                print(f"数据长度: {len(data)}")
                print(f"数据类型: {data.dtype}")
                print(f"索引类型: {type(data.index)}")
                print("\n完整数据:")
                print(data)
        elif isinstance(data, (list, tuple)):
            if not data:
                print("❌ 列表/元组为空")
            else:
                print(f"数据长度: {len(data)}")
                print(f"数据类型: {type(data)}")
                print("\n完整数据:")
                for i, item in enumerate(data):
                    print(f"  {i+1}: {item}")
        elif isinstance(data, dict):
            if not data:
                print("❌ 字典为空")
            else:
                print(f"字典键数量: {len(data)}")
                print("\n完整字典:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
        else:
            print(f"数据类型: {type(data)}")
            print(f"数据内容: {data}")
    
    def print_data_summary(self, data: Any, title: str = "数据摘要"):
        """
        打印数据摘要
        
        Args:
            data: 要打印的数据
            title: 数据标题
        """
        print(f"\n📈 {title}")
        print("=" * 50)
        
        if data is None:
            print("❌ 数据为空")
            return
        
        if isinstance(data, pd.DataFrame):
            if data.empty:
                print("❌ DataFrame为空")
            else:
                print(f"数据形状: {data.shape}")
                print(f"列数: {len(data.columns)}")
                print(f"行数: {len(data)}")
                print(f"列名: {list(data.columns)}")
                print("\n数据统计:")
                print(data.describe())
        elif isinstance(data, pd.Series):
            if data.empty:
                print("❌ Series为空")
            else:
                print(f"数据长度: {len(data)}")
                print(f"数据类型: {data.dtype}")
                print("\n数据统计:")
                print(data.describe())
        else:
            print(f"数据类型: {type(data)}")
            print(f"数据内容: {data}")
