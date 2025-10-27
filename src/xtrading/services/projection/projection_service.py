"""
明日股市机会策略投影服务
通过行业板块信号分析，筛选有买入机会的板块，再分析该板块下的个股买卖信号
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os

from ..signal.sector_signal_service import SectorSignalService
from ..signal.stock_signal_service import StockSignalService
from ...repositories.stock.industry_info_query import IndustryInfoQuery
from ...static.industry_sectors import get_industry_sectors, get_industry_categories
from ...static.sector_strategy_params import StrategyParams
from ...static.stock_strategy_params import StockStrategyParams


class ProjectionService:
    """明日股市机会策略投影服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.sector_service = SectorSignalService()
        self.stock_service = StockSignalService()
        self.industry_query = IndustryInfoQuery()
        
        # 支持的板块策略
        self.sector_strategies = ["MACD", "RSI", "BollingerBands", "MovingAverage"]
        # 支持的个股策略
        self.stock_strategies = ["TrendTracking", "Breakout", "OversoldRebound"]
        
        # 买入信号类型
        self.buy_signal_types = ["BUY", "STRONG_BUY"]
        
        # 报告生成目录
        self.reports_dir = "reports/projection"
        os.makedirs(self.reports_dir, exist_ok=True)

    def calculate_tomorrow_opportunities(self,
                                        sector_list: List[str] = None,
                                        sector_strategies: List[str] = None,
                                        stock_strategies: List[str] = None,
                                        start_date: str = None,
                                        end_date: str = None,
                                        min_buy_signals: int = 2,
                                        max_stocks_per_sector: int = 10) -> Dict[str, Any]:
        """
        计算明日股市机会策略
        
        Args:
            sector_list: 要分析的板块列表，默认为所有板块
            sector_strategies: 板块分析策略列表，默认为所有支持的策略
            stock_strategies: 个股分析策略列表，默认为所有支持的策略
            start_date: 开始日期 (YYYYMMDD格式)，默认为最近三个月
            end_date: 结束日期 (YYYYMMDD格式)，默认为今天
            min_buy_signals: 板块最少买入信号数量阈值，默认为2
            max_stocks_per_sector: 每个板块最多分析的股票数量，默认为10
            
        Returns:
            Dict: 包含板块信号分析和个股信号分析的结果字典
        """
        print("🚀 开始计算明日股市机会策略...")
        
        # 使用默认参数
        if sector_list is None:
            sector_list = get_industry_sectors()
        if sector_strategies is None:
            sector_strategies = self.sector_strategies.copy()
        if stock_strategies is None:
            stock_strategies = self.stock_strategies.copy()
        
        # 使用默认日期范围
        if start_date is None or end_date is None:
            default_start, default_end = StrategyParams.get_default_date_range()
            start_date = start_date or default_start
            end_date = end_date or default_end
        
        results = {
            'calculation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_date': end_date,
            'parameters': {
                'total_sectors': len(sector_list),
                'sector_strategies': sector_strategies,
                'stock_strategies': stock_strategies,
                'date_range': {'start_date': start_date, 'end_date': end_date},
                'min_buy_signals': min_buy_signals,
                'max_stocks_per_sector': max_stocks_per_sector
            },
            'sector_analysis': {},
            'stock_analysis': {},
            'opportunity_summary': {}
        }
        
        # 第一步：分析板块信号
        print("📊 第一步：分析行业板块买卖信号...")
        sector_results = self.sector_service.calculate_sector_signals(
            sector_list=sector_list,
            strategies=sector_strategies,
            start_date=start_date,
            end_date=end_date
        )
        
        if not sector_results:
            print("❌ 板块信号分析失败")
            return results
        
        results['sector_analysis'] = sector_results
        
        # 第二步：筛选有买入机会的板块
        print("🎯 第二步：筛选有买入机会的板块...")
        buy_opportunity_sectors = self._filter_buy_opportunity_sectors(
            sector_results, min_buy_signals
        )
        
        if not buy_opportunity_sectors:
            print("⚠️ 未发现符合条件的买入机会板块")
            results['opportunity_summary'] = {
                'buy_opportunity_sectors': [],
                'total_opportunity_sectors': 0,
                'analysis_message': '未发现符合条件的买入机会板块'
            }
            return results
        
        print(f"✅ 发现 {len(buy_opportunity_sectors)} 个有买入机会的板块")
        
        # 第三步：分析有买入机会板块的个股信号
        print("📈 第三步：分析个股买卖信号...")
        stock_analysis_results = {}
        
        for sector_info in buy_opportunity_sectors:
            sector_name = sector_info['sector_name']
            print(f"   分析板块: {sector_name}")
            
            # 获取板块成分股
            sector_stocks = self._get_sector_stocks(sector_name, max_stocks_per_sector)
            
            if not sector_stocks:
                print(f"   ⚠️ 无法获取 {sector_name} 板块的成分股")
                continue
            
            # 分析个股信号
            stock_results = self.stock_service.calculate_stock_signals(
                stock_list=sector_stocks,
                strategies=stock_strategies,
                start_date=start_date,
                end_date=end_date
            )
            
            if stock_results:
                stock_analysis_results[sector_name] = {
                    'sector_name': sector_name,
                    'stock_list': sector_stocks,
                    'stock_signals': stock_results
                }
                print(f"   ✅ 完成 {sector_name} 板块个股分析，共 {len(sector_stocks)} 只股票")
            else:
                print(f"   ❌ {sector_name} 板块个股分析失败")
        
        results['stock_analysis'] = stock_analysis_results
        
        # 第四步：生成机会汇总
        print("📋 第四步：生成机会汇总...")
        opportunity_summary = self._generate_opportunity_summary(
            buy_opportunity_sectors, stock_analysis_results
        )
        results['opportunity_summary'] = opportunity_summary
        
        print("🎉 明日股市机会策略计算完成！")
        return results

    def generate_opportunity_report(self, results: Dict[str, Any]) -> Optional[str]:
        """
        生成明日股市机会分析报告

        Args:
            results: 计算得到的结果字典

        Returns:
            Optional[str]: 生成的报告文件路径
        """
        if not results:
            print("❌ 无结果数据可生成报告")
            return None

        try:
            # 生成文件名
            now = datetime.now()
            date_str = now.strftime('%Y%m%d')
            time_str = now.strftime('%H%M%S')
            output_file = f"{self.reports_dir}/明日股市机会分析_{date_str}_{time_str}.md"

            # 生成报告内容
            content = []
            content.append("# 明日股市机会策略分析报告")
            content.append("")
            content.append("> 本报告基于技术分析策略，为明日股市投资提供参考建议")
            content.append("")

            # 基本信息
            content.append("## 📊 基本信息")
            content.append("")
            content.append(f"- **分析时间**: {results.get('calculation_time', 'Unknown')}")
            content.append(f"- **分析日期**: {results.get('analysis_date', 'Unknown')}")

            params = results.get('parameters', {})
            content.append(f"- **分析板块数量**: {params.get('total_sectors', 0)}")
            content.append(f"- **板块策略**: {', '.join(params.get('sector_strategies', []))}")
            content.append(f"- **个股策略**: {', '.join(params.get('stock_strategies', []))}")
            content.append(f"- **分析期间**: {params.get('date_range', {}).get('start_date', 'Unknown')} - {params.get('date_range', {}).get('end_date', 'Unknown')}")
            content.append(f"- **买入信号阈值**: {params.get('min_buy_signals', 0)}")
            content.append(f"- **每板块最大股票数**: {params.get('max_stocks_per_sector', 0)}")
            content.append("")

            # 机会汇总
            opportunity_summary = results.get('opportunity_summary', {})
            content.append("## 🎯 机会汇总")
            content.append("")
            content.append(f"- **买入机会板块数量**: {opportunity_summary.get('total_opportunity_sectors', 0)}")
            content.append(f"- **分析状态**: {opportunity_summary.get('analysis_message', 'Unknown')}")
            content.append("")

            buy_opportunity_sectors = opportunity_summary.get('buy_opportunity_sectors', [])
            if buy_opportunity_sectors:
                content.append("### 买入机会板块列表")
                content.append("")
                for i, sector_info in enumerate(buy_opportunity_sectors, 1):
                    content.append(f"{i}. **{sector_info['sector_name']}** ({sector_info['category']})")
                    content.append(f"   - 买入信号数量: {sector_info['buy_signals']}")
                    content.append(f"   - 信号强度: {sector_info['signal_strength']:.2f}")
                    content.append(f"   - 推荐策略: {', '.join(sector_info['recommended_strategies'])}")
                    content.append("")

            # 板块信号分析
            sector_analysis = results.get('sector_analysis', {})
            if sector_analysis:
                content.append("## 📊 板块信号分析")
                content.append("")

                sector_signals = sector_analysis.get('sector_signals', {})
                successful_sectors = 0
                failed_sectors = 0

                for sector_name, sector_data in sector_signals.items():
                    if 'error' in sector_data:
                        failed_sectors += 1
                    else:
                        successful_sectors += 1

                content.append(f"- **成功分析板块**: {successful_sectors}")
                content.append(f"- **失败板块**: {failed_sectors}")
                content.append("")

                # 显示买入机会板块的详细信号
                if buy_opportunity_sectors:
                    content.append("### 买入机会板块详细信号")
                    content.append("")

                    for sector_info in buy_opportunity_sectors:
                        sector_name = sector_info['sector_name']
                        if sector_name in sector_signals:
                            sector_data = sector_signals[sector_name]
                            content.append(f"#### {sector_name}")
                            content.append("")

                            strategies = sector_data.get('strategies', {})
                            for strategy, signal_data in strategies.items():
                                if 'error' not in signal_data:
                                    signal_type = signal_data.get('signal_type', 'HOLD')
                                    if signal_type in self.buy_signal_types:
                                        content.append(f"- **{strategy}**: {signal_type}")
                                        if strategy == "MACD":
                                            content.append(f"  - MACD值: {signal_data.get('macd_value', 0):.4f}")
                                            content.append(f"  - 信号线: {signal_data.get('signal_line', 0):.4f}")
                                        elif strategy == "RSI":
                                            content.append(f"  - RSI值: {signal_data.get('rsi_value', 0):.2f}")
                                        elif strategy == "BollingerBands":
                                            content.append(f"  - 收盘价: {signal_data.get('close_price', 0):.2f}")
                                            content.append(f"  - 上轨: {signal_data.get('upper_band', 0):.2f}")
                                        elif strategy == "MovingAverage":
                                            content.append(f"  - 收盘价: {signal_data.get('close_price', 0):.2f}")
                                            content.append(f"  - 短期均线: {signal_data.get('sma_short', 0):.2f}")
                            content.append("")

            # 个股信号分析
            stock_analysis = results.get('stock_analysis', {})
            if stock_analysis:
                content.append("## 📈 个股信号分析")
                content.append("")

                total_analyzed_stocks = 0
                total_buy_signals = 0

                for sector_name, sector_stock_data in stock_analysis.items():
                    stock_signals = sector_stock_data.get('stock_signals', {})
                    stock_list = sector_stock_data.get('stock_list', [])

                    content.append(f"### {sector_name} 板块个股分析")
                    content.append("")
                    content.append(f"- **分析股票数量**: {len(stock_list)}")

                    stock_signals_data = stock_signals.get('stock_signals', {})
                    successful_stocks = 0
                    buy_signal_stocks = []

                    for stock_code, stock_data in stock_signals_data.items():
                        if 'error' not in stock_data:
                            successful_stocks += 1
                            total_analyzed_stocks += 1

                            strategies = stock_data.get('strategies', {})
                            stock_buy_signals = 0

                            for strategy, signal_data in strategies.items():
                                if 'error' not in signal_data:
                                    signal_type = signal_data.get('signal_type', 'HOLD')
                                    if signal_type in self.buy_signal_types:
                                        stock_buy_signals += 1
                                        total_buy_signals += 1

                            if stock_buy_signals > 0:
                                buy_signal_stocks.append({
                                    'stock_code': stock_code,
                                    'buy_signals': stock_buy_signals,
                                    'strategies': strategies
                                })

                    content.append(f"- **成功分析股票**: {successful_stocks}")
                    content.append(f"- **有买入信号股票**: {len(buy_signal_stocks)}")
                    content.append("")

                    # 显示有买入信号的股票
                    if buy_signal_stocks:
                        content.append("#### 推荐关注股票")
                        content.append("")
                        content.append("| 股票代码 | 买入信号数 | 推荐策略 | 信号详情 |")
                        content.append("|---------|-----------|----------|----------|")

                        for stock_info in buy_signal_stocks[:5]:  # 只显示前5个
                            stock_code = stock_info['stock_code']
                            buy_signals = stock_info['buy_signals']
                            strategies = stock_info['strategies']

                            # 收集推荐策略
                            recommended_strategies = []
                            signal_details = []

                            for strategy, signal_data in strategies.items():
                                if 'error' not in signal_data:
                                    signal_type = signal_data.get('signal_type', 'HOLD')
                                    if signal_type in self.buy_signal_types:
                                        recommended_strategies.append(strategy)

                                        if strategy == "TrendTracking":
                                            trend_strength = signal_data.get('trend_strength', 0)
                                            signal_details.append(f"趋势强度:{trend_strength:.2f}")
                                        elif strategy == "Breakout":
                                            breakout_strength = signal_data.get('breakout_strength', 0)
                                            signal_details.append(f"突破强度:{breakout_strength:.2f}")
                                        elif strategy == "OversoldRebound":
                                            oversold_strength = signal_data.get('oversold_strength', 0)
                                            signal_details.append(f"超跌强度:{oversold_strength:.2f}")

                            content.append(f"| {stock_code} | {buy_signals} | {', '.join(recommended_strategies)} | {', '.join(signal_details)} |")

                        if len(buy_signal_stocks) > 5:
                            content.append(f"\n*注：仅显示前5个推荐股票，共{len(buy_signal_stocks)}个有买入信号*")

                    content.append("")

                content.append("### 个股分析汇总")
                content.append("")
                content.append(f"- **总分析股票数**: {total_analyzed_stocks}")
                content.append(f"- **总买入信号数**: {total_buy_signals}")
                content.append("")

            # 投资建议
            content.append("## 💡 投资建议")
            content.append("")
            content.append("### 板块投资建议")
            content.append("")
            if buy_opportunity_sectors:
                content.append("基于技术分析，以下板块具有较好的买入机会：")
                content.append("")
                for sector_info in buy_opportunity_sectors[:3]:  # 只显示前3个
                    content.append(f"1. **{sector_info['sector_name']}**")
                    content.append(f"   - 买入信号数量: {sector_info['buy_signals']}")
                    content.append(f"   - 信号强度: {sector_info['signal_strength']:.2f}")
                    content.append(f"   - 建议关注该板块的龙头个股")
                    content.append("")
            else:
                content.append("当前市场环境下，未发现明显的板块买入机会，建议谨慎操作。")
                content.append("")

            content.append("### 个股投资建议")
            content.append("")
            content.append("1. **趋势跟踪策略**: 适合中长期投资，关注均线多头排列的个股")
            content.append("2. **突破买入策略**: 适合短期操作，关注放量突破阻力位的个股")
            content.append("3. **超跌反弹策略**: 适合抄底操作，关注技术指标超卖的个股")
            content.append("")
            content.append("### 风险提示")
            content.append("")
            content.append("- 本分析基于历史数据和技术指标，不构成投资建议")
            content.append("- 股市有风险，投资需谨慎")
            content.append("- 建议结合基本面分析和其他技术指标综合判断")
            content.append("- 严格控制仓位，设置止损点")
            content.append("")

            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))

            print(f"✅ 明日股市机会分析报告已生成: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return None

    def _filter_buy_opportunity_sectors(self, sector_results: Dict[str, Any], min_buy_signals: int) -> List[Dict[str, Any]]:
        """
        筛选有买入机会的板块

        Args:
            sector_results: 板块信号分析结果
            min_buy_signals: 最少买入信号数量阈值

        Returns:
            List[Dict]: 有买入机会的板块信息列表
        """
        buy_opportunity_sectors = []
        sector_signals = sector_results.get('sector_signals', {})

        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                continue

            strategies = sector_data.get('strategies', {})
            buy_signals = 0
            signal_strength = 0.0
            recommended_strategies = []

            for strategy, signal_data in strategies.items():
                if 'error' not in signal_data:
                    signal_type = signal_data.get('signal_type', 'HOLD')
                    if signal_type in self.buy_signal_types:
                        buy_signals += 1
                        recommended_strategies.append(strategy)

                        # 计算信号强度
                        if strategy == "MACD":
                            macd_value = abs(signal_data.get('macd_value', 0))
                            signal_strength += macd_value * 0.3
                        elif strategy == "RSI":
                            rsi_value = signal_data.get('rsi_value', 50)
                            # RSI越低，超卖信号越强
                            if rsi_value < 30:
                                signal_strength += (30 - rsi_value) / 30 * 0.3
                        elif strategy == "BollingerBands":
                            bb_position = signal_data.get('bb_position', 0.5)
                            # 布林带位置越低，买入信号越强
                            if bb_position < 0.2:
                                signal_strength += (0.2 - bb_position) / 0.2 * 0.2
                        elif strategy == "MovingAverage":
                            close_price = signal_data.get('close_price', 0)
                            sma_short = signal_data.get('sma_short', 0)
                            if sma_short > 0:
                                ma_ratio = (close_price - sma_short) / sma_short
                                signal_strength += max(0, ma_ratio) * 0.2

            # 如果买入信号数量达到阈值，加入机会列表
            if buy_signals >= min_buy_signals:
                buy_opportunity_sectors.append({
                    'sector_name': sector_name,
                    'category': sector_data.get('category', 'Unknown'),
                    'buy_signals': buy_signals,
                    'signal_strength': signal_strength,
                    'recommended_strategies': recommended_strategies
                })

        # 按信号强度降序排序
        buy_opportunity_sectors.sort(key=lambda x: x['signal_strength'], reverse=True)

        return buy_opportunity_sectors

    def _get_sector_code(self, sector_name: str) -> Optional[str]:
        """
        根据板块名称获取板块代码

        Args:
            sector_name: 板块名称

        Returns:
            Optional[str]: 板块代码
        """
        try:
            # 获取所有板块列表
            industry_names = self.industry_query.get_board_industry_name()

            if industry_names is None or industry_names.empty:
                return None

            # 查找匹配的板块
            for _, row in industry_names.iterrows():
                if row.get('板块名称', '') == sector_name:
                    return row.get('板块代码', None)

            return None

        except Exception as e:
            print(f"❌ 获取 {sector_name} 板块代码失败: {e}")
            return None

    def _get_sector_stocks(self, sector_name: str, max_stocks: int) -> List[str]:
        """
        获取板块成分股

        Args:
            sector_name: 板块名称
            max_stocks: 最大股票数量

        Returns:
            List[str]: 股票代码列表
        """
        try:
            # 先获取板块代码
            sector_code = self._get_sector_code(sector_name)
            if not sector_code:
                print(f"❌ 无法获取 {sector_name} 的板块代码")
                return []

            # 获取板块成分股
            stocks = self.industry_query.get_board_industry_cons(sector_code)

            if stocks is None or stocks.empty:
                return []

            # 提取股票代码
            stock_codes = []
            if '代码' in stocks.columns:
                stock_codes = stocks['代码'].tolist()
            elif 'symbol' in stocks.columns:
                stock_codes = stocks['symbol'].tolist()
            else:
                # 如果没有找到代码列，尝试其他可能的列名
                for col in stocks.columns:
                    if '代码' in col or 'code' in col.lower() or 'symbol' in col.lower():
                        stock_codes = stocks[col].tolist()
                        break

            # 限制股票数量
            return stock_codes[:max_stocks] if stock_codes else []

        except Exception as e:
            print(f"❌ 获取 {sector_name} 板块成分股失败: {e}")
            return []

    def _generate_opportunity_summary(self, buy_opportunity_sectors: List[Dict[str, Any]],
                                    stock_analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成机会汇总信息

        Args:
            buy_opportunity_sectors: 有买入机会的板块列表
            stock_analysis_results: 个股分析结果

        Returns:
            Dict: 机会汇总信息
        """
        total_opportunity_sectors = len(buy_opportunity_sectors)

        # 统计个股分析情况
        total_analyzed_stocks = 0
        total_buy_signals = 0

        for sector_name, sector_stock_data in stock_analysis_results.items():
            stock_signals = sector_stock_data.get('stock_signals', {})
            stock_signals_data = stock_signals.get('stock_signals', {})

            for stock_code, stock_data in stock_signals_data.items():
                if 'error' not in stock_data:
                    total_analyzed_stocks += 1

                    strategies = stock_data.get('strategies', {})
                    for strategy, signal_data in strategies.items():
                        if 'error' not in signal_data:
                            signal_type = signal_data.get('signal_type', 'HOLD')
                            if signal_type in self.buy_signal_types:
                                total_buy_signals += 1

        # 生成分析消息
        if total_opportunity_sectors > 0:
            analysis_message = f"发现 {total_opportunity_sectors} 个有买入机会的板块，共分析 {total_analyzed_stocks} 只个股，产生 {total_buy_signals} 个买入信号"
        else:
            analysis_message = "未发现符合条件的买入机会板块"

        return {
            'buy_opportunity_sectors': buy_opportunity_sectors,
            'total_opportunity_sectors': total_opportunity_sectors,
            'total_analyzed_stocks': total_analyzed_stocks,
            'total_buy_signals': total_buy_signals,
            'analysis_message': analysis_message
        }

    def print_opportunity_summary(self, results: Dict[str, Any]) -> None:
        """
        打印机会汇总信息

        Args:
            results: 计算得到的结果字典
        """
        if not results:
            print("❌ 无结果数据可打印")
            return

        print("\n" + "="*60)
        print("🎯 明日股市机会策略汇总")
        print("="*60)

        # 基本信息
        params = results.get('parameters', {})
        print(f"📊 分析参数:")
        print(f"   - 分析板块数量: {params.get('total_sectors', 0)}")
        print(f"   - 板块策略: {', '.join(params.get('sector_strategies', []))}")
        print(f"   - 个股策略: {', '.join(params.get('stock_strategies', []))}")
        print(f"   - 买入信号阈值: {params.get('min_buy_signals', 0)}")

        # 机会汇总
        opportunity_summary = results.get('opportunity_summary', {})
        print(f"\n🎯 机会汇总:")
        print(f"   - 买入机会板块: {opportunity_summary.get('total_opportunity_sectors', 0)}")
        print(f"   - 分析股票数量: {opportunity_summary.get('total_analyzed_stocks', 0)}")
        print(f"   - 总买入信号数: {opportunity_summary.get('total_buy_signals', 0)}")
        print(f"   - 分析状态: {opportunity_summary.get('analysis_message', 'Unknown')}")

        # 买入机会板块
        buy_opportunity_sectors = opportunity_summary.get('buy_opportunity_sectors', [])
        if buy_opportunity_sectors:
            print(f"\n📈 买入机会板块 (前5个):")
            for i, sector_info in enumerate(buy_opportunity_sectors[:5], 1):
                print(f"   {i}. {sector_info['sector_name']} ({sector_info['category']})")
                print(f"      - 买入信号: {sector_info['buy_signals']}")
                print(f"      - 信号强度: {sector_info['signal_strength']:.2f}")
                print(f"      - 推荐策略: {', '.join(sector_info['recommended_strategies'])}")

        print("="*60)
