"""
信号报告生成器
负责将信号数据汇总生成markdown格式的总结报告
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..static.strategy_config import StrategyConfig


class SignalReportGenerator:
    """板块信号报告生成器类"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.report_dir = "reports/sector_signals"
        os.makedirs(self.report_dir, exist_ok=True)
        print("✅ 板块信号报告生成器初始化成功")
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """
        生成完整的信号报告（包含分析报告和汇总报告）
        
        Args:
            results: 信号计算结果
            output_file: 输出文件路径，默认为自动生成
            
        Returns:
            str: 生成的报告文件路径
        """
        if not results:
            print("❌ 无结果数据可生成报告")
            return None
        
        # 生成文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.report_dir, f"sector_signals_comprehensive_report_{timestamp}.md")
        
        # 生成报告内容
        report_content = self._generate_comprehensive_report_content(results)
        
        # 写入文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 综合信号报告已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 生成报告文件失败: {e}")
            return None
    
    def _generate_comprehensive_report_content(self, results: Dict[str, Any]) -> str:
        """
        生成综合报告内容（包含分析报告和汇总报告）
        
        Args:
            results: 信号计算结果
            
        Returns:
            str: 报告内容
        """
        content = []
        
        # 报告标题
        content.append("# 板块信号综合分析报告")
        content.append("")
        content.append("> 本报告包含板块信号分析报告和汇总报告两部分内容")
        content.append("")
        
        # 目录
        content.extend(self._generate_table_of_contents())
        
        # 第一部分：汇总报告
        content.extend(self._generate_summary_section(results))
        
        # 第二部分：详细分析报告
        content.extend(self._generate_analysis_section(results))
        
        return "\n".join(content)
    
    def _generate_table_of_contents(self) -> List[str]:
        """生成目录"""
        content = []
        
        content.append("## 📋 目录")
        content.append("")
        content.append("### 📊 汇总报告")
        content.append("- [基本信息](#基本信息)")
        content.append("- [整体汇总](#整体汇总)")
        content.append("- [策略信号分布](#策略信号分布)")
        content.append("- [板块分类分析](#板块分类分析)")
        content.append("")
        content.append("### 📈 详细分析报告")
        content.append("- [板块明细](#板块明细)")
        content.append("- [附录：板块分类信息](#附录板块分类信息)")
        content.append("")
        content.append("---")
        content.append("")
        
        return content
    
    def _generate_summary_section(self, results: Dict[str, Any]) -> List[str]:
        """生成汇总报告部分"""
        content = []
        
        content.append("# 📊 汇总报告")
        content.append("")
        content.extend(self._generate_basic_info_with_config(results))
        
        # 整体汇总
        content.extend(self._generate_overall_summary(results))
        
        # 策略信号分布
        content.extend(self._generate_strategy_distribution(results))
        
        # 板块分类分析
        content.extend(self._generate_category_analysis(results))
        
        content.append("---")
        content.append("")
        
        return content
    
    def _generate_analysis_section(self, results: Dict[str, Any]) -> List[str]:
        """生成详细分析报告部分"""
        content = []
        
        content.append("# 📈 详细分析报告")
        content.append("")
        
        # 板块明细
        content.extend(self._generate_sector_details(results))
        
        # 附录：板块分类信息
        content.extend(self._generate_appendix(results))
        
        return content
    
    def _generate_report_content(self, results: Dict[str, Any]) -> str:
        """
        生成报告内容（保留原方法用于向后兼容）
        
        Args:
            results: 信号计算结果
            
        Returns:
            str: 报告内容
        """
        content = []
        
        # 报告标题
        content.append("# 板块信号分析报告")
        content.append("")
        
        # 基本信息
        content.extend(self._generate_basic_info(results))
        
        # 整体汇总
        content.extend(self._generate_overall_summary(results))
        
        # 策略信号分布
        content.extend(self._generate_strategy_distribution(results))
        
        # 板块明细
        content.extend(self._generate_sector_details(results))
        
        # 配置信息
        content.extend(self._generate_config_info())
        
        return "\n".join(content)
    
    def _generate_basic_info(self, results: Dict[str, Any]) -> List[str]:
        """生成基本信息"""
        content = []
        
        content.append("## 📊 基本信息")
        content.append("")
        content.append(f"- **计算时间**: {results.get('calculation_time', 'Unknown')}")
        content.append(f"- **板块数量**: {results.get('total_sectors', 0)}")
        content.append(f"- **使用策略**: {', '.join(results.get('strategies_used', []))}")
        
        if 'date_range' in results:
            date_range = results['date_range']
            content.append(f"- **分析期间**: {date_range.get('start_date', '')} 至 {date_range.get('end_date', '')}")
        
        content.append("")
        return content
    
    def _generate_basic_info_with_config(self, results: Dict[str, Any]) -> List[str]:
        """生成包含策略配置的基本信息"""
        content = []
        
        content.append("## 📋 基本信息")
        content.append("")
        content.append(f"- **计算时间**: {results.get('calculation_time', 'Unknown')}")
        content.append(f"- **板块数量**: {results.get('total_sectors', 0)}")
        content.append(f"- **使用策略**: {', '.join(results.get('strategies_used', []))}")
        
        if 'date_range' in results:
            date_range = results['date_range']
            content.append(f"- **分析期间**: {date_range.get('start_date', '')} 至 {date_range.get('end_date', '')}")
        
        content.append("")
        
        return content
    
    def _generate_overall_summary(self, results: Dict[str, Any]) -> List[str]:
        """生成整体汇总（表格行列互换）"""
        content = []
        
        content.append("## 📈 整体汇总")
        content.append("")
        
        # 统计总体信号分布
        total_signals = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
        successful_sectors = 0
        failed_sectors = 0
        
        for sector_name, sector_data in results.get('sector_signals', {}).items():
            if 'error' in sector_data:
                failed_sectors += 1
                continue
            
            successful_sectors += 1
            
            if 'strategies' in sector_data:
                for strategy_name, strategy_data in sector_data['strategies'].items():
                    if 'error' in strategy_data:
                        total_signals['错误'] += 1
                    else:
                        signal_type = self._translate_signal_type(strategy_data.get('signal_type', 'HOLD'))
                        total_signals[signal_type] += 1
        
        # 生成汇总表格（行列互换）
        content.append("| 分类 | 数量 |")
        content.append("|------|------|")
        content.append(f"| 成功分析板块 | {successful_sectors} |")
        content.append(f"| 失败板块 | {failed_sectors} |")
        content.append(f"| 买入信号 | {total_signals['买入']} |")
        content.append(f"| 卖出信号 | {total_signals['卖出']} |")
        content.append(f"| 持有信号 | {total_signals['持有']} |")
        content.append(f"| 强势买入 | {total_signals['强势买入']} |")
        content.append(f"| 强势卖出 | {total_signals['强势卖出']} |")
        content.append(f"| 错误信号 | {total_signals['错误']} |")
        content.append("")
        
        return content
    
    def _translate_signal_type(self, signal_type: str) -> str:
        """将英文信号类型翻译为中文"""
        translation_map = {
            'BUY': '买入',
            'SELL': '卖出',
            'HOLD': '持有',
            'STRONG_BUY': '强势买入',
            'STRONG_SELL': '强势卖出',
            'ERROR': '错误'
        }
        return translation_map.get(signal_type, signal_type)
    
    def _generate_strategy_distribution(self, results: Dict[str, Any]) -> List[str]:
        """生成策略信号分布（合并到一个表格中）"""
        content = []
        
        content.append("## 📊 策略信号分布")
        content.append("")
        
        strategies_used = results.get('strategies_used', [])
        
        # 统计所有策略的信号分布
        signal_counts = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
        strategy_signal_counts = {}
        
        for strategy in strategies_used:
            strategy_signal_counts[strategy] = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
            
            for sector_name, sector_data in results.get('sector_signals', {}).items():
                if 'strategies' in sector_data and strategy in sector_data['strategies']:
                    strategy_data = sector_data['strategies'][strategy]
                    if 'error' in strategy_data:
                        strategy_signal_counts[strategy]['错误'] += 1
                        signal_counts['错误'] += 1
                    else:
                        signal_type = self._translate_signal_type(strategy_data.get('signal_type', 'HOLD'))
                        strategy_signal_counts[strategy][signal_type] += 1
                        signal_counts[signal_type] += 1
        
        # 生成合并的策略信号分布表格（删除总计列）
        content.append("| 信号类型 | " + " | ".join(strategies_used) + " |")
        content.append("|----------|" + "|".join(["------"] * len(strategies_used)) + "|")
        
        for signal_type in ['买入', '卖出', '持有', '强势买入', '强势卖出', '错误']:
            if signal_counts[signal_type] > 0:  # 只显示有数据的信号类型
                row = [signal_type]
                for strategy in strategies_used:
                    row.append(str(strategy_signal_counts[strategy][signal_type]))
                content.append("| " + " | ".join(row) + " |")
        
        content.append("")
        
        return content
    
    def _generate_sector_details(self, results: Dict[str, Any]) -> List[str]:
        """生成板块明细（合并到一个表格中）"""
        content = []
        
        content.append("## 🏢 板块明细")
        content.append("")
        
        sector_signals = results.get('sector_signals', {})
        strategies_used = results.get('strategies_used', [])
        
        # 生成板块明细表格
        content.append("| 板块名称 | 分类 | " + " | ".join(strategies_used) + " |")
        content.append("|----------|------|" + "|".join(["------"] * len(strategies_used)) + "|")
        
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                # 处理错误的板块
                error_row = [sector_name, "错误", "❌ 错误"] * len(strategies_used)
                content.append("| " + " | ".join(error_row) + " |")
            else:
                category = sector_data.get('category', 'Unknown')
                row = [sector_name, category]
                
                if 'strategies' in sector_data:
                    for strategy in strategies_used:
                        if strategy in sector_data['strategies']:
                            strategy_data = sector_data['strategies'][strategy]
                            if 'error' in strategy_data:
                                row.append("❌ 错误")
                            else:
                                signal_type = strategy_data.get('signal_type', 'HOLD')
                                # 如果是持有信号，显示为"-"
                                if signal_type == 'HOLD':
                                    row.append("-")
                                else:
                                    translated_signal = self._translate_signal_type(signal_type)
                                    row.append(translated_signal)
                        else:
                            row.append("-")
                else:
                    row.extend(["-"] * len(strategies_used))
                
                content.append("| " + " | ".join(row) + " |")
        
        content.append("")
        
        return content
    
    def _generate_category_analysis(self, results: Dict[str, Any]) -> List[str]:
        """生成板块分类分析"""
        content = []
        
        content.append("## 🏷️ 板块分类分析")
        content.append("")
        
        sector_signals = results.get('sector_signals', {})
        strategies_used = results.get('strategies_used', [])
        
        # 按分类统计板块
        category_stats = {}
        
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                continue
                
            category = sector_data.get('category', 'Unknown')
            if category not in category_stats:
                category_stats[category] = {
                    'sectors': [],
                    'signal_counts': {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0},
                    'strategy_signals': {}
                }
            
            category_stats[category]['sectors'].append(sector_name)
            
            # 统计该分类下各策略的信号
            if 'strategies' in sector_data:
                for strategy in strategies_used:
                    if strategy not in category_stats[category]['strategy_signals']:
                        category_stats[category]['strategy_signals'][strategy] = {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0}
                    
                    if strategy in sector_data['strategies']:
                        strategy_data = sector_data['strategies'][strategy]
                        if 'error' in strategy_data:
                            signal_type = '错误'
                        else:
                            signal_type = self._translate_signal_type(strategy_data.get('signal_type', 'HOLD'))
                        
                        category_stats[category]['strategy_signals'][strategy][signal_type] += 1
                        category_stats[category]['signal_counts'][signal_type] += 1
        
        # 生成分类分析表格
        if category_stats:
            content.append("### 📊 分类信号统计")
            content.append("")
            
            # 表头
            header = ["分类", "板块数量"]
            for strategy in strategies_used:
                header.extend([f"{strategy}-买入", f"{strategy}-卖出"])
            content.append("| " + " | ".join(header) + " |")
            content.append("|" + "|".join(["------"] * len(header)) + "|")
            
            # 数据行
            for category, stats in category_stats.items():
                row = [category, str(len(stats['sectors']))]
                
                for strategy in strategies_used:
                    buy_count = stats['strategy_signals'].get(strategy, {}).get('买入', 0)
                    sell_count = stats['strategy_signals'].get(strategy, {}).get('卖出', 0)
                    row.extend([str(buy_count), str(sell_count)])
                
                content.append("| " + " | ".join(row) + " |")
            
            content.append("")
        else:
            content.append("暂无板块分类数据")
            content.append("")
        
        return content
    
    def _generate_appendix(self, results: Dict[str, Any]) -> List[str]:
        """生成附录：板块分类信息"""
        content = []
        
        content.append("## 📋 附录：板块分类信息")
        content.append("")
        
        sector_signals = results.get('sector_signals', {})
        
        # 按分类统计板块
        category_sectors = {}
        
        for sector_name, sector_data in sector_signals.items():
            if 'error' in sector_data:
                continue
                
            category = sector_data.get('category', 'Unknown')
            if category not in category_sectors:
                category_sectors[category] = []
            
            category_sectors[category].append(sector_name)
        
        # 生成分类信息表格
        if category_sectors:
            content.append("| 分类 | 板块数量 | 包含板块 |")
            content.append("|------|----------|----------|")
            
            for category, sectors in category_sectors.items():
                content.append(f"| {category} | {len(sectors)} | {', '.join(sectors)} |")
            
            content.append("")
        else:
            content.append("暂无板块分类数据")
            content.append("")
        
        return content
    
    def _generate_strategy_details(self, strategy_name: str, strategy_data: Dict[str, Any]) -> str:
        """生成策略详细信息"""
        details = []
        
        if strategy_name == "MACD":
            if 'macd_value' in strategy_data:
                details.append(f"MACD: {strategy_data['macd_value']:.4f}")
            if 'signal_line' in strategy_data:
                details.append(f"信号线: {strategy_data['signal_line']:.4f}")
            if 'histogram' in strategy_data:
                details.append(f"柱状图: {strategy_data['histogram']:.4f}")
            if 'zero_cross_status' in strategy_data:
                details.append(f"零轴状态: {strategy_data['zero_cross_status']}")
                
        elif strategy_name == "RSI":
            if 'rsi_value' in strategy_data:
                details.append(f"RSI: {strategy_data['rsi_value']:.2f}")
            if 'rsi_status' in strategy_data:
                details.append(f"状态: {strategy_data['rsi_status']}")
                
        elif strategy_name == "BollingerBands":
            if 'bb_position' in strategy_data:
                details.append(f"位置: {strategy_data['bb_position']:.2f}")
            if 'bb_status' in strategy_data:
                details.append(f"状态: {strategy_data['bb_status']}")
            if 'close_price' in strategy_data:
                details.append(f"收盘价: {strategy_data['close_price']:.2f}")
                
        elif strategy_name == "MovingAverage":
            if 'ma_trend' in strategy_data:
                details.append(f"趋势: {strategy_data['ma_trend']}")
            if 'ma_spread' in strategy_data:
                details.append(f"价差: {strategy_data['ma_spread']:.2f}")
            if 'close_price' in strategy_data:
                details.append(f"收盘价: {strategy_data['close_price']:.2f}")
        
        return " | ".join(details) if details else "-"
    
    def _generate_config_info(self) -> List[str]:
        """生成配置信息"""
        content = []
        
        content.append("## ⚙️ 策略配置信息")
        content.append("")
        
        # 默认日期范围
        start_date, end_date = StrategyConfig.get_default_date_range()
        content.append(f"- **默认分析期间**: {start_date} 至 {end_date} (最近90天)")
        content.append("")
        
        # 策略参数
        all_params = StrategyConfig.get_all_strategy_params()
        
        for strategy_name, params in all_params.items():
            content.append(f"### {strategy_name} 参数")
            content.append("")
            
            content.append("| 参数 | 值 |")
            content.append("|------|---|")
            
            for param_name, param_value in params.items():
                content.append(f"| {param_name} | {param_value} |")
            
            content.append("")
        
        return content
    
    def generate_summary_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """
        生成汇总报告（现在调用综合报告生成方法）
        
        Args:
            results: 信号计算结果
            output_file: 输出文件路径
            
        Returns:
            str: 生成的报告文件路径
        """
        # 直接调用综合报告生成方法
        return self.generate_report(results, output_file)
    
    def generate_summary_only_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """
        生成纯汇总报告（仅包含汇总信息，不包含详细分析）
        
        Args:
            results: 信号计算结果
            output_file: 输出文件路径
            
        Returns:
            str: 生成的报告文件路径
        """
        if not results:
            print("❌ 无结果数据可生成汇总报告")
            return None
        
        # 生成文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.report_dir, f"sector_signals_summary_only_{timestamp}.md")
        
        # 生成汇总报告内容
        content = []
        
        # 标题
        content.append("# 板块信号汇总报告")
        content.append("")
        
        # 基本信息
        content.extend(self._generate_basic_info(results))
        
        # 整体汇总
        content.extend(self._generate_overall_summary(results))
        
        # 策略信号分布
        content.extend(self._generate_strategy_distribution(results))
        
        # 写入文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            print(f"✅ 纯汇总报告已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 生成纯汇总报告文件失败: {e}")
            return None
    
    def print_report_preview(self, results: Dict[str, Any]):
        """
        打印报告预览
        
        Args:
            results: 信号计算结果
        """
        if not results:
            print("❌ 无结果数据可预览")
            return
        
        print("\n📋 板块信号报告预览")
        print("=" * 80)
        
        # 基本信息
        print(f"计算时间: {results.get('calculation_time', 'Unknown')}")
        print(f"板块数量: {results.get('total_sectors', 0)}")
        print(f"使用策略: {', '.join(results.get('strategies_used', []))}")
        
        if 'date_range' in results:
            date_range = results['date_range']
            print(f"分析期间: {date_range.get('start_date', '')} 至 {date_range.get('end_date', '')}")
        
        print("\n📊 信号分布预览:")
        
        # 统计信号分布
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'STRONG_BUY': 0, 'STRONG_SELL': 0, 'ERROR': 0}
        
        for sector_name, sector_data in results.get('sector_signals', {}).items():
            if 'strategies' in sector_data:
                for strategy_name, strategy_data in sector_data['strategies'].items():
                    if 'error' in strategy_data:
                        signal_counts['ERROR'] += 1
                    else:
                        signal_type = strategy_data.get('signal_type', 'HOLD')
                        signal_counts[signal_type] += 1
        
        for signal_type, count in signal_counts.items():
            if count > 0:
                print(f"  {signal_type}: {count}")
        
        print("\n🏢 板块预览:")
        sector_signals = results.get('sector_signals', {})
        for i, (sector_name, sector_data) in enumerate(sector_signals.items()):
            if i >= 3:  # 只显示前3个板块
                print(f"  ... 还有 {len(sector_signals) - 3} 个板块")
                break
            
            category = sector_data.get('category', 'Unknown')
            print(f"  {sector_name} ({category})")
            
            if 'strategies' in sector_data:
                for strategy_name, strategy_data in sector_data['strategies'].items():
                    if 'error' not in strategy_data:
                        signal_type = strategy_data.get('signal_type', 'HOLD')
                        print(f"    {strategy_name}: {signal_type}")
        
        print("=" * 80)
