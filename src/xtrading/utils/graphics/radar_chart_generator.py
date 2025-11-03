"""
雷达图生成工具
提供六边雷达图生成功能，用于市场情绪分析可视化
"""

import numpy as np
import matplotlib
# 设置matplotlib后端，避免线程问题
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Any, Optional
import os
from datetime import datetime


class RadarChartGenerator:
    """雷达图生成器工具类"""
    
    def __init__(self):
        """初始化雷达图生成器"""
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """设置matplotlib配置"""
        try:
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 忽略字体警告
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            
        except ImportError:
            print("❌ 需要安装matplotlib库: pip install matplotlib")
    
    def generate_market_sentiment_radar(self, 
                                     sentiment_data: Dict[str, float],
                                     output_path: str,
                                     title: str = "市场情绪雷达图") -> Optional[str]:
        """
        生成市场情绪四边雷达图
        
        Args:
            sentiment_data: 市场情绪数据字典，包含4个维度的分数
            output_path: 输出文件路径
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
            
        市场情绪数据格式：
        {
            '市场活跃度': 7.5,
            '个股赚钱效应': 6.8,
            '风险偏好': 5.2,
            '市场参与意愿': 8.1,
            '综合情绪指数': 7.0
        }
        """
        try:
            # 定义4个维度
            dimensions = [
                '市场活跃度',
                '个股赚钱效应', 
                '风险偏好',
                '市场参与意愿'
            ]
            
            # 检查数据完整性
            if not all(dim in sentiment_data for dim in dimensions):
                print("❌ 市场情绪数据不完整，缺少必要维度")
                return None
            
            # 提取数值
            values = [sentiment_data[dim] for dim in dimensions]
            
            # 验证数值范围 (0-10)
            if not all(0 <= v <= 10 for v in values):
                print("❌ 市场情绪数值超出范围 (0-10)")
                return None
            
            # 创建雷达图
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            # 添加数值到角度列表末尾以闭合图形
            values += values[:1]
            
            # 绘制雷达图
            ax.plot(angles, values, 'o-', linewidth=2, color='#1f77b4', markersize=8)
            ax.fill(angles, values, alpha=0.25, color='#1f77b4')
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimensions, fontsize=12, fontweight='bold')
            
            # 设置y轴范围和标签
            ax.set_ylim(0, 10)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
            ax.set_yticklabels(['0', '2', '4', '6', '8', '10'], fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # 添加数值标签
            for angle, value, dimension in zip(angles[:-1], values[:-1], dimensions):
                ax.text(angle, value + 0.5, f'{value:.1f}', 
                       ha='center', va='center', fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # 设置标题
            plt.title(title, size=16, fontweight='bold', pad=20)
            
            # 添加情绪等级说明
            overall_sentiment = sentiment_data.get('综合情绪指数', 0)
            sentiment_level = self._get_sentiment_level(overall_sentiment)
            plt.figtext(0.5, 0.02, f'综合情绪指数: {overall_sentiment:.1f}/10.0 ({sentiment_level})', 
                       ha='center', fontsize=12, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            
            # 显式关闭图形，避免内存泄漏
            plt.close(fig)
            matplotlib.pyplot.close('all')
            
            print(f"✅ 市场情绪雷达图已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 生成市场情绪雷达图失败: {e}")
            return None
    
    def generate_comprehensive_sentiment_chart(self, 
                                             sentiment_data: Dict[str, float],
                                             trend_data: Dict[str, list],
                                             output_path: str,
                                             title: str = "市场情绪综合分析图") -> Optional[str]:
        """
        生成市场情绪综合分析图（雷达图+趋势图）
        
        Args:
            sentiment_data: 市场情绪数据字典，包含4个维度的分数
            trend_data: 趋势数据字典，包含各维度的历史数据
            output_path: 输出文件路径
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        try:
            import matplotlib.dates as mdates
            from datetime import datetime
            
            # 定义4个维度
            dimensions = [
                '市场活跃度',
                '个股赚钱效应', 
                '风险偏好',
                '市场参与意愿'
            ]
            
            # 检查数据完整性
            if not all(dim in sentiment_data for dim in dimensions):
                print("❌ 市场情绪数据不完整，缺少必要维度")
                return None
            
            # 提取数值
            values = [sentiment_data[dim] for dim in dimensions]
            
            # 验证数值范围 (0-10)
            if not all(0 <= v <= 10 for v in values):
                print("❌ 市场情绪数值超出范围 (0-10)")
                return None
            
            # 创建综合图表 (3x2布局)
            fig = plt.figure(figsize=(20, 12))
            
            # 1. 雷达图 (左上)
            ax1 = plt.subplot(3, 2, 1, projection='polar')
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            # 添加数值到角度列表末尾以闭合图形
            values += values[:1]
            
            # 绘制雷达图
            ax1.plot(angles, values, 'o-', linewidth=2, color='#1f77b4', markersize=8)
            ax1.fill(angles, values, alpha=0.25, color='#1f77b4')
            
            # 设置标签
            ax1.set_xticks(angles[:-1])
            ax1.set_xticklabels(dimensions, fontsize=10, fontweight='bold')
            
            # 设置y轴范围和标签
            ax1.set_ylim(0, 10)
            ax1.set_yticks([0, 2, 4, 6, 8, 10])
            ax1.set_yticklabels(['0', '2', '4', '6', '8', '10'], fontsize=8)
            ax1.grid(True, alpha=0.3)
            
            # 添加数值标签
            for angle, value, dimension in zip(angles[:-1], values[:-1], dimensions):
                ax1.text(angle, value + 0.5, f'{value:.1f}', 
                       ha='center', va='center', fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            
            # 设置标题
            ax1.set_title('市场情绪雷达图', size=12, fontweight='bold', pad=20)
            
            # 2. 综合情绪指数趋势图 (右上)
            ax2 = plt.subplot(3, 2, 2)
            if 'overall_sentiment' in trend_data and trend_data['overall_sentiment']:
                self._plot_trend_chart(ax2, trend_data['overall_sentiment'], '综合情绪指数趋势', '#d62728')
            
            # 3. 市场活跃度趋势图 (第二行左)
            ax3 = plt.subplot(3, 2, 3)
            if 'market_activity' in trend_data and trend_data['market_activity']:
                self._plot_trend_chart(ax3, trend_data['market_activity'], '市场活跃度趋势', '#1f77b4')
            
            # 4. 个股赚钱效应趋势图 (第二行右)
            ax4 = plt.subplot(3, 2, 4)
            if 'profit_effect' in trend_data and trend_data['profit_effect']:
                self._plot_trend_chart(ax4, trend_data['profit_effect'], '个股赚钱效应趋势', '#ff7f0e')
            
            # 5. 风险偏好趋势图 (第三行左)
            ax5 = plt.subplot(3, 2, 5)
            if 'risk_preference' in trend_data and trend_data['risk_preference']:
                self._plot_trend_chart(ax5, trend_data['risk_preference'], '风险偏好趋势', '#2ca02c')
            
            # 6. 市场参与意愿趋势图 (第三行右)
            ax6 = plt.subplot(3, 2, 6)
            if 'participation_willingness' in trend_data and trend_data['participation_willingness']:
                self._plot_trend_chart(ax6, trend_data['participation_willingness'], '市场参与意愿趋势', '#9467bd')
            
            # 添加综合情绪指数说明
            overall_sentiment = sentiment_data.get('综合情绪指数', 0)
            sentiment_level = self._get_sentiment_level(overall_sentiment)
            fig.suptitle(f'{title} - 综合情绪指数: {overall_sentiment:.1f}/10.0 ({sentiment_level})', 
                        fontsize=16, fontweight='bold', y=0.95)
            
            # 调整布局
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            
            # 保存图表
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            
            # 显式关闭图形，避免内存泄漏
            plt.close(fig)
            matplotlib.pyplot.close('all')
            
            print(f"✅ 市场情绪综合分析图已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 生成市场情绪综合分析图失败: {e}")
            return None
    
    def _plot_trend_chart(self, ax, trend_data: Dict[str, list], title: str, color: str):
        """
        绘制趋势图（包含均线）
        
        Args:
            ax: matplotlib轴对象
            trend_data: 趋势数据字典，包含dates和values
            title: 图表标题
            color: 主色调
        """
        try:
            import matplotlib.dates as mdates
            import numpy as np
            
            dates = trend_data['dates']
            values = trend_data['values']
            
            if not dates or not values:
                return
            
            # 绘制主趋势线
            ax.plot(dates, values, marker='o', linewidth=2, markersize=4, color=color, label='趋势线')
            
            # 在曲线上添加数值标签
            for date, value in zip(dates, values):
                # 计算标签位置，避免标签重叠
                ax.annotate(f'{value:.1f}', 
                          xy=(date, value),
                          xytext=(0, 10),  # 标签位置在点的上方
                          textcoords='offset points',
                          ha='center',
                          va='bottom',
                          fontsize=8,
                          fontweight='bold',
                          color='black',
                          bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))
            
            # 绘制填充区域
            ax.fill_between(dates, values, alpha=0.3, color=color)
            
            # 计算并绘制均线（5日均线）
            if len(values) >= 5:
                ma_values = []
                for i in range(len(values)):
                    if i < 4:
                        # 前4个点使用可用数据计算均线
                        ma_values.append(np.mean(values[:i+1]))
                    else:
                        # 从第5个点开始使用5日均线
                        ma_values.append(np.mean(values[i-4:i+1]))
                
                # 绘制均线
                ax.plot(dates, ma_values, linewidth=2, color='red', linestyle='--', alpha=0.8, label='5日均线')
            
            # 设置标题和标签
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_ylim(0, 10)
            ax.grid(True, alpha=0.3)
            
            # 设置x轴格式为月-日
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.set_xticks(dates)  # 只显示数据中实际存在的日期
            ax.tick_params(axis='x', rotation=45)
            
            # 添加图例
            ax.legend(fontsize=8, loc='upper right')
            
        except Exception as e:
            print(f"❌ 绘制趋势图失败: {e}")
    
    def _get_sentiment_level(self, score: float) -> str:
        """
        根据分数获取情绪等级
        
        Args:
            score: 情绪分数 (0-10)
            
        Returns:
            str: 情绪等级描述
        """
        if score >= 7.0:
            return "极度乐观"
        elif score >= 5.5:
            return "乐观"
        elif score >= 4.5:
            return "中性"
        elif score >= 2.5:
            return "悲观"
        else:
            return "极度悲观"
    
    def generate_comparison_radar(self, 
                                sentiment_data_list: List[Dict[str, Dict[str, float]]],
                                output_path: str,
                                title: str = "市场情绪对比雷达图") -> Optional[str]:
        """
        生成多个时期的市场情绪对比雷达图
        
        Args:
            sentiment_data_list: 多个时期的市场情绪数据列表
            output_path: 输出文件路径
            title: 图表标题
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        try:
            if not sentiment_data_list:
                print("❌ 没有对比数据")
                return None
            
            # 定义6个维度
            dimensions = [
                '市场活跃度',
                '个股赚钱效应', 
                '风险偏好',
                '市场参与意愿',
                '投资者行为',
                '综合情绪指数'
            ]
            
            # 创建雷达图
            fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            # 定义颜色
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # 绘制每个时期的数据
            for i, (period, data) in enumerate(sentiment_data_list):
                values = [data[dim] for dim in dimensions]
                values += values[:1]  # 闭合图形
                
                color = colors[i % len(colors)]
                ax.plot(angles, values, 'o-', linewidth=2, color=color, 
                       markersize=6, label=period)
                ax.fill(angles, values, alpha=0.1, color=color)
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimensions, fontsize=12, fontweight='bold')
            
            # 设置y轴范围和标签
            ax.set_ylim(0, 10)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
            ax.set_yticklabels(['0', '2', '4', '6', '8', '10'], fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # 设置标题和图例
            plt.title(title, size=16, fontweight='bold', pad=20)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ 市场情绪对比雷达图已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 生成市场情绪对比雷达图失败: {e}")
            return None
