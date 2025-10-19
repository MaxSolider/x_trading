"""
图形处理工具使用示例

本模块提供了图形处理的公共工具类，用于生成各种图表。
主要功能包括：
1. 日收益折线图生成
2. 累计收益折线图生成  
3. 自定义图表生成

使用示例：
```python
from xtrading.utils.graphics import ChartGenerator

# 创建图表生成器
chart_gen = ChartGenerator()

# 生成日收益图表
daily_chart_path = chart_gen.generate_daily_returns_chart(
    daily_data=daily_data,  # 日收益数据列表
    results=results,        # 回测结果列表
    industry_name='行业名称',
    category='行业分类',
    output_dir='输出目录',
    timestamp='时间戳'
)

# 生成累计收益图表
cumulative_chart_path = chart_gen.generate_cumulative_returns_chart(
    cumulative_data=cumulative_data,  # 累计收益数据列表
    results=results,                  # 回测结果列表
    industry_name='行业名称',
    category='行业分类', 
    output_dir='输出目录',
    timestamp='时间戳'
)

# 生成自定义图表
custom_chart_path = chart_gen.generate_custom_chart(
    data=dataframe,           # 数据DataFrame
    chart_type='line',        # 图表类型
    title='图表标题',
    x_label='X轴标签',
    y_label='Y轴标签',
    output_path='输出路径'
)
```
"""

from .chart_generator import ChartGenerator

__all__ = ['ChartGenerator']
