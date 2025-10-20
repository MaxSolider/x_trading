# XTrading - 智能股票交易策略分析平台

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AKShare](https://img.shields.io/badge/data%20source-AKShare-orange.svg)](https://akshare.akfamily.xyz/)

XTrading 是一个基于 AKShare 数据源的智能股票交易策略分析平台，专注于行业板块的技术分析和策略回测。通过多种技术指标和机器学习方法，为投资者提供专业的量化分析工具。

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

## 🏗️ 项目结构

```
XTrading/
├── src/xtrading/                    # 核心代码
│   ├── repositories/               # 数据访问层
│   │   └── stock/                  # 股票数据查询
│   ├── strategies/                 # 交易策略
│   │   └── industry_sector/        # 行业板块策略
│   ├── services/                   # 业务服务层
│   ├── utils/                      # 工具类
│   │   ├── calculator/            # 计算工具
│   │   ├── docs/                  # 文档生成
│   │   ├── graphics/              # 图表生成
│   │   └── limiter/               # 限流控制
│   └── static/                     # 静态配置
├── reports/                        # 生成的报告
│   ├── backtest/                   # 回测报告
│   ├── images/                     # 图表图片
│   └── sector_signals/              # 板块信号报告
├── tests/                          # 测试代码
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

### 数据源配置

项目使用 AKShare 作为数据源，支持：
- 实时行情数据
- 历史K线数据
- 板块成分股数据
- 市场概览数据

## 📈 报告示例

### 板块信号报告
- 多策略信号汇总
- 板块分类分析
- 买卖信号统计
- 技术指标详情

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

- [ ] 增加更多技术指标策略
- [ ] 支持个股分析功能
- [ ] 添加机器学习预测模型
- [ ] 开发 Web 界面
- [ ] 支持实时数据推送
- [ ] 增加风险管理模块
- [ ] 支持多市场数据源

---

**⚠️ 风险提示**: 本工具仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
