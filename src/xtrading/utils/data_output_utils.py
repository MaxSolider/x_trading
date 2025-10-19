"""
数据输出工具类
提供数据展示和格式化输出功能
"""

import pandas as pd
from typing import Optional, Dict, Any, List
import json


class DataOutputUtils:
    """数据输出工具类"""
    
    def __init__(self):
        """初始化工具类"""
        print("✅ 数据输出工具类初始化成功")
    
    def print_data(self, data: pd.DataFrame, title: str):
        """
        打印数据详细信息
        
        Args:
            data: 要显示的数据
            title: 数据标题
        """
        if data is not None and not data.empty:
            print("=" * 60)
            print(f"📊 {title}")
            print(f"数据行数: {len(data)}")
            print(f"数据列数: {len(data.columns)}")

            print(data.head(len(data)))
        else:
            print(f"❌ {title} 数据为空")

    def print_data_statistics(self, data: pd.DataFrame, title: str):
        """
        打印数据统计信息
        
        Args:
            data: 要显示的数据
            title: 数据标题
        """
        if data is not None and not data.empty:
            print(f"\n📈 {title} - 统计信息")
            print("-" * 50)
            print(f"数据行数: {len(data)}")
            print(f"数据列数: {len(data.columns)}")
            
            # 数值列的统计信息
            numeric_columns = data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                print(f"\n数值列统计:")
                print(data[numeric_columns].describe())
            
            # 缺失值统计
            missing_values = data.isnull().sum()
            if missing_values.sum() > 0:
                print(f"\n缺失值统计:")
                print(missing_values[missing_values > 0])
            else:
                print(f"\n✅ 无缺失值")
        else:
            print(f"❌ {title} 数据为空")
    
    def print_data_preview(self, data: pd.DataFrame, title: str, rows: int = 3):
        """
        打印数据预览
        
        Args:
            data: 要显示的数据
            title: 数据标题
            rows: 显示行数
        """
        if data is not None and not data.empty:
            print(f"\n👀 {title} - 预览")
            print("-" * 30)
            print(f"数据行数: {len(data)}")
            print(f"数据列数: {len(data.columns)}")
            print(f"\n前{rows}行数据:")
            print(data.head(rows))
        else:
            print(f"❌ {title} 数据为空")
    
    def format_data_to_json(self, data: pd.DataFrame, title: str = "数据") -> Optional[str]:
        """
        将数据格式化为JSON字符串
        
        Args:
            data: 要格式化的数据
            title: 数据标题
            
        Returns:
            str: JSON格式的字符串
        """
        if data is not None and not data.empty:
            try:
                # 将DataFrame转换为字典
                data_dict = {
                    "title": title,
                    "rows": len(data),
                    "columns": len(data.columns),
                    "column_names": list(data.columns),
                    "data": data.to_dict('records')
                }
                return json.dumps(data_dict, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ 格式化JSON失败: {e}")
                return None
        else:
            print(f"❌ {title} 数据为空，无法格式化")
            return None
    
    def print_data_comparison(self, data_list: List[pd.DataFrame], titles: List[str]):
        """
        打印多个数据的对比信息
        
        Args:
            data_list: 数据列表
            titles: 标题列表
        """
        if len(data_list) != len(titles):
            print("❌ 数据列表和标题列表长度不匹配")
            return
        
        print(f"\n📊 数据对比")
        print("=" * 60)
        
        for i, (data, title) in enumerate(zip(data_list, titles)):
            if data is not None and not data.empty:
                print(f"\n{i+1}. {title}")
                print(f"   数据行数: {len(data)}")
                print(f"   数据列数: {len(data.columns)}")
            else:
                print(f"\n{i+1}. {title}")
                print(f"   ❌ 数据为空")
    
    def save_data_to_file(self, data: pd.DataFrame, filename: str, format_type: str = 'csv'):
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
            format_type: 文件格式 (csv, excel, json)
        """
        if data is not None and not data.empty:
            try:
                if format_type.lower() == 'csv':
                    data.to_csv(filename, index=False, encoding='utf-8-sig')
                elif format_type.lower() == 'excel':
                    data.to_excel(filename, index=False)
                elif format_type.lower() == 'json':
                    data.to_json(filename, orient='records', force_ascii=False, indent=2)
                else:
                    print(f"❌ 不支持的文件格式: {format_type}")
                    return
                
                print(f"✅ 数据已保存到 {filename}")
            except Exception as e:
                print(f"❌ 保存文件失败: {e}")
        else:
            print(f"❌ 数据为空，无法保存")
    
    def print_table_summary(self, data: pd.DataFrame, title: str):
        """
        打印表格摘要
        
        Args:
            data: 要显示的数据
            title: 数据标题
        """
        if data is not None and not data.empty:
            print(f"\n📋 {title}")
            print("=" * 60)
            print(f"表格大小: {len(data)} 行 × {len(data.columns)} 列")
            print(f"列名: {', '.join(data.columns)}")
            
            # 显示前几行
            print(f"\n数据预览:")
            print(data.head())
            
            # 如果有数值列，显示基本统计
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\n数值列统计:")
                for col in numeric_cols[:3]:  # 只显示前3个数值列
                    print(f"  {col}: 均值={data[col].mean():.2f}, 最大值={data[col].max():.2f}, 最小值={data[col].min():.2f}")
        else:
            print(f"❌ {title} 数据为空")
