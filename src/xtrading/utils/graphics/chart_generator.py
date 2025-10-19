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
    
    def generate_daily_returns_chart(self, 
                                   daily_data: List[Dict[str, Any]], 
                                   results: List[Dict[str, Any]], 
                                   industry_name: str,
                                   category: str,
                                   output_dir: str,
                                   timestamp: str) -> Optional[str]:
        """
        生成日收益明细表的折线图
        
        Args:
            daily_data: 日收益数据列表
            results: 回测结果列表
            industry_name: 行业名称
            category: 行业分类
            output_dir: 输出目录
            timestamp: 时间戳
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        if not daily_data or not results:
            print("❌ 无日收益数据可生成折线图")
            return None
        
        try:
            import matplotlib.pyplot as plt
            
            # 生成带时间戳的文件名
            filename = f"{output_dir}/{category}_{industry_name}_每日收益率_{timestamp}.png"
            
            # 数据读取与预处理
            df = pd.DataFrame(daily_data)
            
            # 处理日期列 - 转换为datetime格式
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            
            # 处理百分比数据 - 去除%符号并转换为浮点数
            numeric_columns = ['板块实际收益率']
            for result in results:
                strategy_name = result['strategy_name']
                numeric_columns.append(f'{strategy_name}收益率')
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].str.replace('%', '').astype(float)
            
            # 可视化处理
            plt.figure(figsize=(14, 8))  # 设置合适的图表尺寸
            
            # 绘制多系列折线图
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # 绘制板块实际收益率
            plt.plot(df['日期'], df['板块实际收益率'], 
                    label='板块实际收益率', linewidth=2.5, color=colors[0], marker='o', markersize=6)
            
            # 绘制各策略收益率
            for i, result in enumerate(results):
                strategy_name = result['strategy_name']
                col_name = f'{strategy_name}收益率'
                if col_name in df.columns:
                    plt.plot(df['日期'], df[col_name], 
                            label=f'{strategy_name}收益率', linewidth=2, 
                            color=colors[(i + 1) % len(colors)], marker='s', markersize=5)
            
            # 添加图表元素
            plt.title(f'{industry_name}板块日收益率对比图', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('日期', fontsize=12, fontweight='bold')
            plt.ylabel('收益率 (%)', fontsize=12, fontweight='bold')
            
            # 添加图例
            plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # 调整x轴标签旋转角度(45度)避免重叠
            plt.xticks(rotation=45)
            
            # 添加网格线提高可读性
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 设置y轴零线
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # 关闭图表以释放内存
            
            print(f"✅ 日收益折线图已保存: {filename}")
            return filename
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
            return None
        except Exception as e:
            print(f"❌ 生成日收益折线图失败: {e}")
            return None
    
    def generate_cumulative_returns_chart(self, 
                                       cumulative_data: List[Dict[str, Any]], 
                                       results: List[Dict[str, Any]], 
                                       industry_name: str,
                                       category: str,
                                       output_dir: str,
                                       timestamp: str) -> Optional[str]:
        """
        生成累计收益明细表的折线图
        
        Args:
            cumulative_data: 累计收益数据列表
            results: 回测结果列表
            industry_name: 行业名称
            category: 行业分类
            output_dir: 输出目录
            timestamp: 时间戳
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        if not cumulative_data or not results:
            print("❌ 无累计收益数据可生成折线图")
            return None
        
        try:
            import matplotlib.pyplot as plt
            
            # 生成带时间戳的文件名
            filename = f"{output_dir}/{category}_{industry_name}_累计收益率_{timestamp}.png"
            
            # 数据读取与预处理
            df = pd.DataFrame(cumulative_data)
            
            # 处理日期列 - 转换为datetime格式
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            
            # 处理百分比数据 - 去除%符号并转换为浮点数
            numeric_columns = ['板块累计收益率']
            for result in results:
                strategy_name = result['strategy_name']
                numeric_columns.append(f'{strategy_name}累计收益率')
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].str.replace('%', '').astype(float)
            
            # 可视化处理
            plt.figure(figsize=(14, 8))  # 设置合适的图表尺寸
            
            # 绘制多系列折线图
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # 绘制板块累计收益率
            plt.plot(df['日期'], df['板块累计收益率'], 
                    label='板块累计收益率', linewidth=2.5, color=colors[0], marker='o', markersize=6)
            
            # 绘制各策略累计收益率
            for i, result in enumerate(results):
                strategy_name = result['strategy_name']
                col_name = f'{strategy_name}累计收益率'
                if col_name in df.columns:
                    plt.plot(df['日期'], df[col_name], 
                            label=f'{strategy_name}累计收益率', linewidth=2, 
                            color=colors[(i + 1) % len(colors)], marker='s', markersize=5)
            
            # 添加图表元素
            plt.title(f'{industry_name}板块累计收益率对比图', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('日期', fontsize=12, fontweight='bold')
            plt.ylabel('累计收益率 (%)', fontsize=12, fontweight='bold')
            
            # 添加图例
            plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # 调整x轴标签旋转角度(45度)避免重叠
            plt.xticks(rotation=45)
            
            # 添加网格线提高可读性
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 设置y轴零线
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # 关闭图表以释放内存
            
            print(f"✅ 累计收益折线图已保存: {filename}")
            return filename
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
            return None
        except Exception as e:
            print(f"❌ 生成累计收益折线图失败: {e}")
            return None
    
    def generate_custom_chart(self, 
                            data: pd.DataFrame,
                            chart_type: str = 'line',
                            title: str = '',
                            x_label: str = '',
                            y_label: str = '',
                            output_path: str = '',
                            **kwargs) -> Optional[str]:
        """
        生成自定义图表
        
        Args:
            data: 数据DataFrame
            chart_type: 图表类型 ('line', 'bar', 'scatter', 'hist')
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            output_path: 输出文件路径
            **kwargs: 其他图表参数
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=kwargs.get('figsize', (12, 8)))
            
            if chart_type == 'line':
                plt.plot(data.index, data.iloc[:, 0], **kwargs.get('plot_kwargs', {}))
            elif chart_type == 'bar':
                plt.bar(data.index, data.iloc[:, 0], **kwargs.get('bar_kwargs', {}))
            elif chart_type == 'scatter':
                plt.scatter(data.iloc[:, 0], data.iloc[:, 1], **kwargs.get('scatter_kwargs', {}))
            elif chart_type == 'hist':
                plt.hist(data.iloc[:, 0], **kwargs.get('hist_kwargs', {}))
            else:
                print(f"❌ 不支持的图表类型: {chart_type}")
                return None
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            
            if kwargs.get('grid', True):
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ 自定义图表已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 生成自定义图表失败: {e}")
            return None
