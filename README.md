# XTrading - 智能股票交易策略分析平台

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AKShare](https://img.shields.io/badge/data%20source-AKShare-orange.svg)](https://akshare.akfamily.xyz/)

XTrading 是一个基于 AKShare 数据源的智能股票交易策略分析平台，专注于行业板块和个股的技术分析、策略回测、市场情绪分析和投资机会挖掘。通过多种技术指标、量化策略和市场情绪分析，为投资者提供专业的股票分析工具和投资决策支持。

## ✨ 主要特性

### 📊 多策略技术分析
- **MACD策略**: 基于指数移动平均线的趋势跟踪策略
- **RSI策略**: 相对强弱指标的超买超卖信号
- **布林带策略**: 基于价格波动性的均值回归策略
- **移动平均策略**: 多周期移动平均线交叉策略

### 🏢 行业板块全覆盖
- 支持 **90+** 个行业板块分析
- 涵盖能源、材料、工业、消费、金融、科技等主要行业
- 按行业分类进行批量分析和对比

### 🎯 个股策略分析
- **趋势追踪策略**: 基于均线多头排列和MACD多头市场的趋势跟踪
- **突破买入策略**: 基于价格突破关键压力位、放量配合和布林带突破
- **超跌反弹策略**: 基于KDJ超卖和RSI超卖的超跌反弹机会捕捉
- 支持个股历史数据回测和策略性能对比

### 🔍 智能信号服务
- **板块信号服务**: 批量分析多个行业板块的交易信号
- **股票信号服务**: 批量分析多个个股的交易信号
- **明日机会投影服务**: 基于板块信号筛选投资机会，结合个股分析提供综合投资建议
- 支持多策略信号汇总和对比分析
- 自动生成详细的信号分析报告

### 📈 市场情绪分析
- **多维度情绪指标**: 基于市场活跃度、个股赚钱效应、风险偏好、市场参与意愿等维度
- **情绪指数计算**: 综合计算市场整体情绪指数和情绪等级
- **雷达图可视化**: 生成四维市场情绪雷达图，直观展示市场情绪状态
- **历史情绪追踪**: 支持市场情绪历史数据记录和分析
- **情绪数据源**: 整合市场概览、个股突破、融资融券、资金流向等多源数据

### 🎯 明日机会投影服务
- **智能机会筛选**: 基于板块信号自动筛选有投资机会的行业
- **个股深度分析**: 对筛选出的板块进行个股级别的详细分析
- **多策略综合**: 结合板块策略和个股策略提供综合投资建议
- **投资机会报告**: 自动生成包含具体股票代码和买入理由的详细报告
- **风险控制**: 支持设置买入信号阈值和每板块最大股票数量

### ⚙️ 策略参数管理
- **默认参数配置**: 为所有策略提供经过优化的默认参数
- **参数统一管理**: 集中管理策略参数，便于维护和调整
- **参数灵活使用**: 支持使用默认参数或自定义参数
- **参数验证**: 确保参数的有效性和合理性

### 📈 专业回测系统
- 历史数据回测验证
- 多策略性能对比
- 风险收益分析
- 可视化图表生成

### 📋 智能报告生成
- 自动生成板块信号分析报告
- 多板块策略回测总结报告
- 支持 Markdown 格式输出
- 包含详细的技术指标分析

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 网络连接（用于数据获取）
- 推荐使用虚拟环境

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/xtrading/xtrading.git
cd xtrading
```

2. **运行启动脚本**
```bash
python run.py
```

启动脚本会自动：
- 创建虚拟环境
- 安装/升级依赖包
- 配置运行环境
- 启动主程序

### 手动安装（可选）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 📖 使用指南

### 基本使用

```python
from src.xtrading.main import main

# 运行主程序
main()
```

### 单个板块分析

```python
from src.xtrading.strategies.industry_sector.backtest import StrategyBacktest

# 创建回测实例
backtest = StrategyBacktest()

# 分析半导体板块
results = backtest.compare_strategies(
    industry_name="半导体",
    strategies=["MACD", "RSI", "BollingerBands", "MovingAverage"],
    start_date="20250101",
    end_date="20251217",
    initial_capital=100000
)

# 打印结果
backtest.print_backtest_results(results)
```

### 板块信号分析

```python
from src.xtrading.services.sector_signal_service import SectorSignalService

# 创建信号服务
service = SectorSignalService()

# 分析多个板块
results = service.calculate_sector_signals(
    sector_list=["半导体", "新能源", "医药"],
    strategies=["MACD", "RSI"],
    start_date="20250722",
    end_date="20251020"
)

# 生成报告
report = service.generate_signal_report(results)
print(report)
```

### 个股策略分析

```python
from src.xtrading.strategies.individual_stock import (
    IndividualTrendTrackingStrategy,
    IndividualBreakoutStrategy,
    IndividualOversoldReboundStrategy,
    IndividualStockBacktest
)

# 趋势追踪策略
trend_strategy = IndividualTrendTrackingStrategy()
analysis = trend_strategy.analyze_stock_trend("000001", "20240101", "20241217")
trend_strategy.print_trend_analysis(analysis)

# 突破买入策略
breakout_strategy = IndividualBreakoutStrategy()
analysis = breakout_strategy.analyze_stock_breakout("000001", "20240101", "20241217")
breakout_strategy.print_breakout_analysis(analysis)

# 超跌反弹策略
oversold_strategy = IndividualOversoldReboundStrategy()
analysis = oversold_strategy.analyze_stock_oversold("000001", "20240101", "20241217")
oversold_strategy.print_oversold_analysis(analysis)

# 个股策略回测
backtest = IndividualStockBacktest()
results = backtest.compare_strategies(
    symbol="000001",
    strategies=["TrendTracking", "Breakout", "OversoldRebound"],
    start_date="20240101",
    end_date="20241217",
    initial_capital=100000
)
backtest.print_backtest_results(results)
```

### 股票信号分析

```python
from src.xtrading.services.signal.stock_signal_service import StockSignalService

# 创建股票信号服务
service = StockSignalService()

# 分析多个股票
results = service.calculate_stock_signals(
    stock_list=["000001", "000002", "600000", "600036"],
    strategies=["TrendTracking", "Breakout", "OversoldRebound"],
    start_date="20240101",
    end_date="20241217"
)

# 生成信号报告
report_file = service.print_signal_summary(results)
print(f"报告已生成: {report_file}")
```

### 明日机会投影分析

```python
from src.xtrading.services.projection.projection_service import ProjectionService

# 创建投影服务
projection_service = ProjectionService()

# 分析明日投资机会（使用默认参数）
results = projection_service.calculate_tomorrow_opportunities()

# 打印汇总信息
projection_service.print_opportunity_summary(results)

# 生成详细报告
report_file = projection_service.generate_opportunity_report(results)
print(f"投资机会报告已生成: {report_file}")

# 自定义参数分析
custom_results = projection_service.calculate_tomorrow_opportunities(
    sector_list=["半导体", "新能源", "医药"],
    sector_strategies=["MACD", "RSI"],
    stock_strategies=["TrendTracking", "Breakout"],
    min_buy_signals=2,
    max_stocks_per_sector=5
)
```

### 市场情绪分析

```python
from src.xtrading.strategies.market_sentiment.market_sentiment_strategy import MarketSentimentStrategy

# 创建市场情绪分析策略
sentiment_strategy = MarketSentimentStrategy()

# 分析市场情绪（使用默认日期）
sentiment_result = sentiment_strategy.analyze_market_sentiment()

# 打印情绪分析结果
print(f"分析日期: {sentiment_result['analysis_date']}")
print(f"综合情绪指数: {sentiment_result['overall_sentiment']:.2f}")
print(f"情绪等级: {sentiment_result['sentiment_level']}")

# 打印各维度分数
sentiment_scores = sentiment_result['sentiment_scores']
print("各维度情绪分数:")
for dimension, score in sentiment_scores.items():
    print(f"  {dimension}: {score:.2f}")

# 生成市场情绪雷达图
radar_chart_path = sentiment_strategy._generate_sentiment_radar_chart(sentiment_result)
if radar_chart_path:
    print(f"市场情绪雷达图已生成: {radar_chart_path}")

# 保存情绪历史数据
history_path = sentiment_strategy._save_sentiment_history(sentiment_result)
if history_path:
    print(f"情绪历史数据已保存: {history_path}")

# 分析指定日期的市场情绪
custom_sentiment = sentiment_strategy.analyze_market_sentiment("20251020")
```

### 策略参数配置

```python
from src.xtrading.static.stock_strategy_params import StockStrategyParams
from src.xtrading.static.sector_strategy_params import StrategyParams

# 获取个股策略默认参数
trend_params = StockStrategyParams.get_trend_tracking_params()
breakout_params = StockStrategyParams.get_breakout_params()
oversold_params = StockStrategyParams.get_oversold_rebound_params()

# 获取板块策略默认参数
macd_params = StrategyParams.get_macd_params()
rsi_params = StrategyParams.get_rsi_params()
bb_params = StrategyParams.get_bollinger_bands_params()
ma_params = StrategyParams.get_moving_average_params()

# 查看所有策略参数
all_stock_params = StockStrategyParams.get_all_strategy_params()
all_sector_params = StrategyParams.get_all_strategy_params()

# 获取默认日期范围
start_date, end_date = StockStrategyParams.get_default_date_range()
```

## 🏗️ 项目结构

```
XTrading/
├── src/xtrading/                    # 核心代码
│   ├── repositories/               # 数据访问层
│   │   └── stock/                  # 股票数据查询
│   │       ├── stock_query.py      # 个股数据查询
│   │       ├── industry_info_query.py # 行业信息查询
│   │       ├── market_overview_query.py # 市场概览查询
│   │       └── concept_info_query.py # 概念信息查询
│   ├── strategies/                 # 交易策略
│   │   ├── industry_sector/        # 行业板块策略
│   │   │   ├── macd_strategy.py    # MACD策略
│   │   │   ├── rsi_strategy.py     # RSI策略
│   │   │   ├── bollinger_bands_strategy.py # 布林带策略
│   │   │   ├── moving_average_strategy.py # 移动平均策略
│   │   │   └── backtest.py         # 板块回测
│   │   ├── individual_stock/       # 个股策略
│   │   │   ├── trend_tracking_strategy.py # 趋势追踪策略
│   │   │   ├── breakout_strategy.py # 突破买入策略
│   │   │   ├── oversold_rebound_strategy.py # 超跌反弹策略
│   │   │   └── backtest.py         # 个股回测
│   │   └── market_sentiment/       # 市场情绪分析
│   │       └── market_sentiment_strategy.py # 市场情绪策略
│   ├── services/                   # 业务服务层
│   │   ├── signal/                 # 信号服务
│   │   │   ├── sector_signal_service.py    # 板块信号服务
│   │   │   └── stock_signal_service.py     # 股票信号服务
│   │   └── projection/             # 投影服务
│   │       └── projection_service.py       # 明日机会投影服务
│   ├── utils/                      # 工具类
│   │   ├── calculator/            # 计算工具
│   │   ├── docs/                  # 文档生成
│   │   ├── graphics/              # 图表生成
│   │   │   ├── chart_generator.py # 图表生成器
│   │   │   └── radar_chart_generator.py # 雷达图生成器
│   │   ├── limiter/               # 限流控制
│   │   └── pandas/                # pandas配置
│   └── static/                     # 静态配置
│       ├── industry_sectors.py     # 行业板块配置
│       ├── sector_strategy_params.py # 板块策略参数
│       └── stock_strategy_params.py  # 个股策略参数
├── reports/                        # 生成的报告
│   ├── backtest/                   # 回测报告
│   │   ├── sector/                 # 板块回测报告
│   │   └── summary/                # 回测总结报告
│   ├── images/                     # 图表图片
│   │   ├── sentiment/              # 市场情绪图表
│   │   └── 20251020/              # 按日期分类的图表
│   ├── sector_signals/             # 板块信号报告
│   ├── projection/                 # 明日机会投影报告
│   └── history/                    # 历史数据
│       └── market_sentiment_history.csv # 市场情绪历史
├── tests/                          # 测试代码
│   ├── backtest/                   # 回测测试
│   ├── repository_test.py          # 数据访问测试
│   └── strategies_test.py          # 策略测试
├── docs/                           # 文档
├── run.py                          # 启动脚本
├── requirements.txt                # 依赖列表
└── pyproject.toml                  # 项目配置
```

## 📊 支持的行业板块

### 主要分类
- **能源**: 煤炭、燃气、石油、电力、电池、风电、光伏等
- **材料**: 钢铁、有色金属、化工、建材、玻璃等
- **工业**: 机械、设备、汽车、航空、船舶等
- **消费**: 食品饮料、纺织服装、家电、汽车等
- **金融**: 银行、证券、保险、多元金融等
- **科技**: 半导体、软件、通信、电子等
- **医疗**: 医药、医疗器械、医疗服务等

### 完整列表
项目支持 90+ 个行业板块，包括但不限于：
- 半导体、新能源、人工智能
- 医药生物、医疗器械
- 银行、证券、保险
- 汽车、航空、船舶
- 钢铁、有色金属、化工
- 食品饮料、纺织服装
- 房地产、建筑、建材
- 等等...

## 🔧 配置说明

### 策略参数配置

#### 板块策略参数

```python
# MACD 策略参数
macd_params = {
    "fast_period": 12,      # 快线周期
    "slow_period": 26,      # 慢线周期
    "signal_period": 9      # 信号线周期
}

# RSI 策略参数
rsi_params = {
    "period": 14,           # RSI 计算周期
    "oversold": 30,         # 超卖阈值
    "overbought": 70        # 超买阈值
}

# 布林带策略参数
bb_params = {
    "period": 20,           # 移动平均周期
    "std_dev": 2.0          # 标准差倍数
}

# 移动平均策略参数
ma_params = {
    "short_period": 5,      # 短期周期
    "medium_period": 20,    # 中期周期
    "long_period": 60       # 长期周期
}
```

#### 个股策略参数

```python
# 趋势追踪策略参数
trend_params = {
    "short_period": 5,      # 短期移动平均周期
    "medium_period": 20,    # 中期移动平均周期
    "long_period": 60,      # 长期移动平均周期
    "fast_period": 12,      # MACD快线周期
    "slow_period": 26,      # MACD慢线周期
    "signal_period": 9      # MACD信号线周期
}

# 突破买入策略参数
breakout_params = {
    "period": 20,           # 布林带移动平均周期
    "std_dev": 2.0,         # 布林带标准差倍数
    "volume_period": 5,     # 量比计算周期
    "resistance_lookback_period": 60,  # 阻力位回望周期
    "volume_threshold": 1.2  # 量比阈值
}

# 超跌反弹策略参数
oversold_params = {
    "k_period": 9,          # K值计算周期
    "d_period": 3,          # D值计算周期
    "j_period": 3,          # J值计算周期
    "rsi_period": 14,       # RSI计算周期
    "kdj_oversold": 20,     # KDJ超卖阈值
    "rsi_oversold": 30      # RSI超卖阈值
}
```

### 市场情绪分析配置

市场情绪分析基于以下数据源和指标：

```python
# 市场情绪分析维度
sentiment_dimensions = {
    'market_activity': '市场活跃度',      # 基于市场成交量和涨跌家数
    'profit_effect': '个股赚钱效应',     # 基于个股突破和涨停情况
    'risk_preference': '风险偏好',       # 基于融资融券数据
    'participation_willingness': '市场参与意愿'  # 基于资金流向数据
}

# 情绪等级划分
sentiment_levels = {
    '极度悲观': (0, 2),
    '悲观': (2, 4),
    '中性': (4, 6),
    '乐观': (6, 8),
    '极度乐观': (8, 10)
}
```

### 数据源配置

项目使用 AKShare 作为数据源，支持：
- 实时行情数据
- 历史K线数据
- 板块成分股数据
- 市场概览数据
- 融资融券数据
- 资金流向数据
- 个股突破数据

## 📈 报告示例

### 板块信号报告
- 多策略信号汇总
- 板块分类分析
- 买卖信号统计
- 技术指标详情

### 个股信号报告
- 多策略个股分析
- 买卖信号汇总
- 技术指标详情
- 投资建议

### 市场情绪分析报告
- 四维情绪指标分析
- 综合情绪指数
- 情绪等级评估
- 雷达图可视化
- 历史情绪对比

### 明日机会投影报告
- 板块机会筛选
- 个股深度分析
- 多策略综合建议
- 风险提示

### 回测报告
- 策略性能对比
- 收益率分析
- 风险指标评估
- 可视化图表

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发说明

### 代码规范
- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码规范
- 添加适当的类型注解
- 编写清晰的文档字符串

### 测试
```bash
# 运行测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/strategies_test.py
```

### 代码质量
```bash
# 代码格式化
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/
```

## 📦 主要依赖

项目主要依赖以下Python包：

- **akshare>=1.17.68** - 金融数据接口
- **pandas>=1.3.0** - 数据处理和分析
- **numpy>=1.21.0** - 数值计算
- **openpyxl>=3.0.0** - Excel文件处理
- **matplotlib>=3.5.0** - 图表绘制和雷达图生成

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [AKShare](https://akshare.akfamily.xyz/) - 提供免费的金融数据接口
- [pandas](https://pandas.pydata.org/) - 数据处理和分析
- [matplotlib](https://matplotlib.org/) - 图表绘制
- [numpy](https://numpy.org/) - 数值计算

## 📞 联系方式

- 项目主页: [https://github.com/xtrading/xtrading](https://github.com/xtrading/xtrading)
- 问题反馈: [Issues](https://github.com/xtrading/xtrading/issues)
- 邮箱: team@xtrading.com

## 🔮 未来计划

### 已完成功能 ✅
- [x] 支持个股分析功能
- [x] 实现明日机会投影服务
- [x] 完善策略参数管理系统
- [x] 实现市场情绪分析功能
- [x] 添加雷达图可视化功能
- [x] 支持多策略信号服务
- [x] 完善板块和个股回测系统

### 计划中功能 🚧
- [ ] 增加更多技术指标策略
- [ ] 添加机器学习预测模型
- [ ] 开发 Web 界面
- [ ] 支持实时数据推送
- [ ] 增加风险管理模块
- [ ] 支持多市场数据源
- [ ] 添加更多技术指标（KDJ、CCI、威廉指标等）
- [ ] 实现策略组合优化
- [ ] 添加回测报告可视化增强
- [ ] 支持期货和期权分析
- [ ] 添加情绪预警系统
- [ ] 实现多时间框架分析

---

**⚠️ 风险提示**: 本工具仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
